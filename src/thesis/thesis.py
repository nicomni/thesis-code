import argparse
from collections.abc import Iterator
from datetime import datetime
import logging
import os
import pathlib
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Sequence, cast
from alive_progress import alive_bar

from osgeo import ogr
from thesis import events
from thesis.api import event_store

from thesis.api.ogr import convert_osm_to_gpkg, apply_changes
from thesis.geo import (
    polygon_has_holes,
)

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def _get_simplified_polygon_features(layer: ogr.Layer) -> Iterator[ogr.Feature]:
    """Simplify multipolygons in the dataset.

    Find all multi-polygon features where the multi-polygon only contains a
    single polygon and that polygon has no holes. Copy the resulting features
    and replace the multi-polygons with the polygons.

    Return an iterator of the new features.

    """
    features = filter(lambda feature: feature.geometry().GetGeometryCount() == 1, layer)
    features = filter(
        lambda feature: not polygon_has_holes(feature.geometry().GetGeometryRef(0)),
        features,
    )

    def replace_mp_with_polygon(feat: ogr.Feature):
        poly = feat.geometry().GetGeometryRef(0).Clone()
        new_feat = feat.Clone()
        new_feat.SetGeometry(poly)
        return new_feat

    features = map(replace_mp_with_polygon, features)
    return features


def simplify_data(gpkg_file_path: Path):
    """Clean up gpkg file.

    1.  Extract all simple polygons from multipolygon layer and add them as
        LineString in 'lines' layer.
    2.  Remove all redundant layers.
    """
    _logger.debug(f"Pruning GPKG file {gpkg_file_path}")
    with cast(ogr.DataSource, ogr.Open(str(gpkg_file_path), 1)) as ds:
        mp_layer = cast(ogr.Layer, ds.GetLayerByName("multipolygons"))
        poly_feats = _get_simplified_polygon_features(mp_layer)

        # Create a new layer for polygons
        poly_layer = cast(
            ogr.Layer | None,
            ds.CreateLayer(
                "polygons", srs=mp_layer.GetSpatialRef(), geom_type=ogr.wkbPolygon
            ),
        )
        if poly_layer is None:
            raise RuntimeError("Failed to create layer 'polygons' in gpkg file.")

        # Copy schema from multipolygon layer to polygon layer
        layer_defn = cast(ogr.FeatureDefn, mp_layer.GetLayerDefn())
        for i in range(layer_defn.GetFieldCount()):
            field_defn = layer_defn.GetFieldDefn(i)
            poly_layer.CreateField(field_defn)

        # Write all polygon features to the new layer
        poly_count = 0
        with alive_bar(title="Converting multipolygons to polygons") as bar:
            for feat in poly_feats:
                poly_layer.CreateFeature(feat)
                poly_count += 1
                bar()

        _logger.debug(
            f"Successfully wrote {poly_count} polygon features to layer 'polygons'."
        )

        _logger.debug("Removing redundant layers from datasource")
        i = 0
        while i < ds.GetLayerCount():
            layer = cast(ogr.Layer, ds.GetLayer(i))
            if layer.GetName() not in ["lines", "points", "polygons"]:
                _logger.debug(f"Deleting layer {layer.GetName()}")
                ds.DeleteLayer(i)
            else:
                i += 1

        _logger.debug("Successfully pruned GPKG file.")


def process_changes(gpkg_a: Path, gpkg_b: Path):
    """
    NOTE:
    There are three relevant layers in each dataset:
      * points
      * lines
      * polygons

    We can assume that all changes in the 'points' layer have been recorded
    in the relavant OSMChange file as changes to corresponding '<node>'
    elements.
    For this reason we can safely use information from the OSMChange file
    to speed up the search for changed points.
    However, we cannot assume that all <node>'s have been converted to points
    in the 'points' layer. That requires the <node> to have what is called
    'significant' tags or attributes. Many <nodes> exists only to be
    referenced by <way>'s or <relation>'s, and are for that reason not
    converted to points by the `ogr2ogr` tool.

    For lines and polygons, it is another story...

    Ways and relations are the basis for the resulting lines and polygons
    after converting the OSM data to GPKG. Unclosed ways are converted to
    lines, while closed ways are converted to polygons.
    Relations are more complex, but can be converted to lines(??), polygons and
    multipolygons.
    Note that changes to nodes that
    are referenced by ways, and changes to ways that are referenced by
    relations, are not recorded as changes to the corresponding ways and
    relations in the resulting OSMChange file. This means that we cannot
    assume that changes to lines and polygons can be inferred from the
    contents of the OSMChange file.
    """
    with (
        cast(ogr.DataSource, ogr.Open(str(gpkg_a))) as ds_a,
        cast(ogr.DataSource, ogr.Open(str(gpkg_b))) as ds_b,
    ):
        assert ds_a.GetLayerCount() == ds_b.GetLayerCount()

        for i in range(ds_a.GetLayerCount()):
            layer_a = ds_a.GetLayer(i)
            layer_b = ds_b.GetLayer(i)
            fids_a = set(map(lambda f: f.GetFID(), layer_a))
            fids_b = set(map(lambda f: f.GetFID(), layer_b))
            common_fids = fids_a & fids_b
            with alive_bar(title="Searching for and writing change events") as bar:
                for fid in common_fids:
                    feature_a = cast(ogr.Feature, layer_a.GetFeature(fid))
                    feature_b = cast(ogr.Feature, layer_b.GetFeature(fid))
                    if not feature_a.Equal(feature_b):
                        event = events.modification_event(feature_a, feature_b)
                        event_store.write_events(event)
                    bar()

            with alive_bar(title="Writing delete events") as bar:
                for fid in fids_a - fids_b:
                    feature_a = cast(ogr.Feature, layer_a.GetFeature(fid))
                    event = events.deletion_event(feature_a)
                    event_store.write_events(event)
                    bar()

            with alive_bar(title="Writing creation events") as bar:
                for fid in fids_b - fids_a:
                    feature_b = cast(ogr.Feature, layer_b.GetFeature(fid))
                    event = events.creation_event(feature_b)
                    event_store.write_events(event)
                    bar()


def _get_temp_file_paths():
    with (
        tempfile.NamedTemporaryFile(suffix=".osm.pbf") as osm_tmp,
        tempfile.NamedTemporaryFile(suffix=".gpkg") as gpkg_tmp_a,
        tempfile.NamedTemporaryFile(suffix=".gpkg") as gpkg_tmp_b,
    ):
        # These files are deleted upon return. We only want their path.
        return (
            pathlib.Path(osm_tmp.name),
            pathlib.Path(gpkg_tmp_a.name),
            pathlib.Path(gpkg_tmp_b.name),
        )


def _get_timestamp_from_statefile(state_file: str) -> datetime:
    # The state_file is a text file that among other lines contains exactly one line with "timestamp=YYYY-MM-DDTHH:MM:SSZ"
    # Get that timestamp and return it as a datetime object.
    with open(state_file, "r") as f:
        for line in f:
            if line.startswith("timestamp="):
                return datetime.strptime(line.split("=")[1], "%Y-%m-%dT%H\\:%M\\:%SZ\n")
        else:
            raise RuntimeError(f"Could not find timestamp in state file {state_file}.")


def _get_osm_date(osm_file_path: pathlib.Path) -> datetime:
    """Return the timestamp of the OSM dataset

    OSM files downloaded from Geofabrik contain the OSM replication date in
    their file name, e.g., 'norway-240101.osm.pbf'.

    This function extracts the date part of the file name, and returns it as
    a datetime object.
    """
    date_str = osm_file_path.name.split("-")[1].split(".")[0]
    return datetime.strptime(date_str, "%y%m%d")


def _initialize_events_from(gpkg: Path):
    with cast(ogr.DataSource, ogr.Open(str(gpkg))) as ds:
        for i in range(ds.GetLayerCount()):
            layer = ds.GetLayer(i)
            for feature in layer:
                yield events.creation_event(feature)


def main(argv: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("osm_file_path", type=Path, metavar="OSM_FILE")
    parser.add_argument("updates_dir_path", type=Path, metavar="UPDATES_DIR")
    args = parser.parse_args(argv)

    osm_file_path: Path = args.osm_file_path
    updates_dir_path: Path = args.updates_dir_path
    osm_date = _get_osm_date(osm_file_path)

    osm_tmp, gpkg_tmp_a, gpkg_tmp_b = _get_temp_file_paths()

    shutil.copy(osm_file_path, osm_tmp)

    _logger.info("Setting up initial data state")
    convert_osm_to_gpkg(osm_tmp, gpkg_tmp_a)
    # Simplify the dataset.
    simplify_data(gpkg_tmp_a)

    _logger.info("Finished setting up initial data state")

    try:
        events = _initialize_events_from(gpkg_tmp_a)
        event_store.init(events=events)
        osc_files = sorted(updates_dir_path.glob("*.osc*"))
        osc_counter = 1
        osc_total = len(osc_files)

        for osc_path in osc_files:
            # Remove fileextensions from osc_fpath_base
            seq_nr = osc_path.name.split(".")[0]
            state_file = os.path.join(updates_dir_path, f"{seq_nr}.state.txt")
            osc_date = _get_timestamp_from_statefile(state_file)
            if osc_date.date() <= osm_date.date():
                # skip this file
                osc_total -= 1
                continue
            _logger.info(f"Processing {osc_path}. File {osc_counter}/{osc_total}...")
            _logger.info("Applygin changes to OSM file")
            apply_changes(osm_tmp, osc_path)

            _logger.info("Converting OSM to GeoPackage")
            convert_osm_to_gpkg(osm_tmp, gpkg_tmp_b)
            _logger.info("Simplifying data")
            simplify_data(gpkg_tmp_b)

            _logger.info("Processing changes...")
            process_changes(gpkg_tmp_a, gpkg_tmp_b)
            _logger.info(f"Deleting tmp GPKG file: {gpkg_tmp_a}")
            gpkg_tmp_a.unlink()
            tmp = gpkg_tmp_a
            gpkg_tmp_a = gpkg_tmp_b
            gpkg_tmp_b = tmp
            osc_counter += 1
    except:
        raise
    finally:
        _logger.info("Tearing down")
        event_store.teardown()
        osm_tmp.unlink()
        gpkg_tmp_a.unlink()
        gpkg_tmp_b.unlink(missing_ok=True)


if __name__ == "__main__":
    exit(main())
