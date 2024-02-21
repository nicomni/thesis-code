import argparse
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Sequence

from alive_progress import alive_bar
from osgeo import ogr

from thesis.api.event_store import write_events
from thesis.api.ogr import (find_changes, get_all_features, osm2gpkg,
                            osmium_apply_changes, remove_layers)
from thesis.api.osc import get_change_info
from thesis.geo import (mp_has_single_polygon, multipolygon_to_polygon_feature,
                        polygon_has_holes)

logger = logging.getLogger(__name__)


def prune_gpkg_file(gpkg_file_path: str):
    """Clean up gpkg file.

    1.  Extract all simple polygons from multipolygon layer and add them as
        LineString in 'lines' layer.
    2.  Remove all other unwanted layers.
    """
    feats = get_all_features(gpkg_file_path, "multipolygons")
    feats = filter(lambda f: mp_has_single_polygon(f.geometry()), feats)
    feats = map(multipolygon_to_polygon_feature, feats)
    feats = filter(lambda f: not polygon_has_holes(f.geometry()), feats)

    # TODO: Add simple polygons to a new layer in the gpkg file.

    remove_layers(
        gpkg_file_path, "multipolygons", "multilinestrings", "other_relations"
    )


def main(argv: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("osm_file_path", type=Path, metavar="OSM_FILE")
    parser.add_argument("osc_dir_path", type=Path, metavar="OSC_DIR")
    parser.add_argument("-o", "--outfile", type=Path, nargs=1)  # Optional
    args = parser.parse_args(argv)

    osm_file_path = args.osm_file_path
    osc_dir_path = args.osc_dir_path
    # events_file_path = args.outfile

    # File descriptors:
    osm_tmp_fd = None
    gpkg_tmp_a_fd = None
    gpkg_tmp_b_fd = None

    # File names (paths):
    osm_tmp = None
    gpkg_tmp_a = None
    gpkg_tmp_b = None
    try:
        osm_tmp_fd, osm_tmp = tempfile.mkstemp(suffix=".osm.pbf")
        gpkg_tmp_a_fd, gpkg_tmp_a = tempfile.mkstemp(suffix=".gpkg")
        gpkg_tmp_b_fd, gpkg_tmp_b = tempfile.mkstemp(suffix=".gpkg")
    finally:
        if osm_tmp_fd:
            os.close(osm_tmp_fd)
        if gpkg_tmp_a_fd:
            os.close(gpkg_tmp_a_fd)
        if gpkg_tmp_b_fd:
            os.close(gpkg_tmp_b_fd)

    # Copy input osm file to temparary file.
    shutil.copy(osm_file_path, osm_tmp)

    # Read .osc file
    # Store change type (create, modify, delete), entity type (node, way, relation), and id.
    # Apply changes, convert to gpkg and store in new file. Keep old gpkg file.
    # For each create event, create a new Creation event:
    #   For nodes:
    #    •  Might be part of a way or relation (line or polygon), and it could
    #       happen that it does not exist in the points layer of the gpkg file.
    #   For ways and relations:
    #    • Could either be a line or a polygon.
    #    • Complicated polygons might not have been extracted from the gpkg file, and will therefore not be found.

    # Setup initial state of osm data
    osm2gpkg(osm_tmp, gpkg_tmp_a)
    prune_gpkg_file(gpkg_tmp_a)
    # setup_eventstore(gpkg_tmp_a)

    with alive_bar(len(os.listdir(osc_dir_path))) as bar:
        # Process changes:
        for osc_fpath in os.listdir(osc_dir_path):
            osmium_apply_changes(osm_tmp, osc_fpath)
            osm2gpkg(osm_tmp, gpkg_tmp_b)
            prune_gpkg_file(gpkg_tmp_b)

            osc_info = get_change_info(osc_fpath)
            events = find_changes(gpkg_tmp_a, gpkg_tmp_b, osc_info)
            write_events(events)
            gpkg_tmp_a = gpkg_tmp_b
            bar()

    # FIXME: Delete temporary files.
    return 0


if __name__ == "__main__":
    exit(main())
