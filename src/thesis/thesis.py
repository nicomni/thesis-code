import os
import subprocess
import time

from alive_progress import alive_bar
from osgeo import ogr

extract = "sakskobing"  # sakskobing or denmark

osm_data_dir = "/Users/magganielsen/LocalDocs/Masterprosjekt/OSM"
src_path = os.path.join(osm_data_dir, f"{extract}", f"{extract}-230901.osm.pbf")
proj_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_dir = os.path.join(proj_root_dir, "output")
dst_path = os.path.join(out_dir, f"{extract}-230901.gpkg")


def convert_osm_to_gpkg():
    # ogr2ogr -f "GPKG" output.gpkg input.osm.pbf
    config = {
        "OSM_CONFIG_FILE": os.path.join(osm_data_dir, "osmconf.ini"),
        "OSM_MAX_TMPFILE_SIZE": "4000",
    }
    os.environ.update(config)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    command = "ogr2ogr"
    args = [
        "-f",
        "GPKG",
        "-preserve_fid",
        dst_path,
        src_path,
    ]
    if not os.path.exists(dst_path):
        with (
            alive_bar(
                monitor=False,
                elapsed="{elapsed}",
                stats=False,
                monitor_end=False,
                stats_end=False,
                elapsed_end="Total time: {elapsed}",
                dual_line=True,
            ) as bar,
            subprocess.Popen(
                [command] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=2,
            ) as proc,
        ):
            assert proc.stdout is not None
            bar.title("Converting OSM to GPKG")
            while proc.poll() is None:
                bar()
                time.sleep(0.02)
        # TODO: Handle incomplete linear ring error. See ogr2ogr stderr output.
        # TODO: Print output from ogr2ogr to console. Both stdout and stderr.


def create_polygon_layer(ds: ogr.DataSource, layer_name: str) -> ogr.Layer:
    """Create a new layer in the given data source.
    If a layer with the given name already exists, it will be deleted.
    """
    layer = ds.GetLayerByName(layer_name)
    if layer is not None:
        print(f"Layer `{layer_name}` already exists. Deleting...")
        ds.DeleteLayer(layer.GetLayerDefn().GetName())
    print(f"Creating layer {layer_name}...")
    layer = ds.CreateLayer(
        layer_name,
        srs=ds.GetLayerByName("multipolygons").GetSpatialRef(),
        geom_type=ogr.wkbPolygon,
    )
    print(f"Created layer {layer_name}.")
    return layer


def copy_schema(source_layer: ogr.Layer, target_layer: ogr.Layer):
    for field_defn in source_layer.schema:  # pyright:ignore
        assert isinstance(field_defn, ogr.FieldDefn)
        target_layer.CreateField(field_defn)


def clean_multipolygons(src_layer: ogr.Layer, dst_layer: ogr.Layer):
    """Extract all polygons from multipolygons and add them to the new polygon layer.
    Only extracts polygons with no holes.
    All attribute fields are copied. The FID is preserved.
    """
    with alive_bar() as bar:
        bar.title("Creating polygon features")
        for src_feat in src_layer:
            assert isinstance(src_feat, ogr.Feature)
            geom = src_feat.GetGeometryRef()
            assert isinstance(geom, ogr.Geometry)
            # if multipolygon contains only one polygon (true if geometry count of multipolygon is 1),
            # and that polygon do not contain any holes (true if geometry count of polygon is 1, i.e. only exterior ring)
            # then add it to the new polygon layer.
            if (
                geom.GetGeometryCount() == 1
                and geom.GetGeometryRef(0).GetGeometryCount() == 1
            ):
                polygon = geom.GetGeometryRef(0)
                dst_feat = ogr.Feature(dst_layer.GetLayerDefn())
                dst_feat.SetFID(src_feat.GetFID())
                dst_feat.SetGeometry(polygon)

                # Copy attributes (fields)
                for field in src_feat.keys():
                    dst_feat.SetField(field, src_feat.GetField(field))

                # Add the new feature to the destination layer
                dst_layer.CreateFeature(dst_feat)
                bar()


if __name__ == "__main__":
    ### STAGE 1: Convert OSM file to GeoPackage ###
    convert_osm_to_gpkg()
    ### STAGE 2: Clean feature types. Keep only simple points, lines adn polygons.
    ogr.UseExceptions()
    with ogr.Open(dst_path, 1) as ds_dirty:
        assert isinstance(ds_dirty, ogr.DataSource)
        src_layer_name = "multipolygons"
        dst_layer_name = "polygons"
        src_layer = ds_dirty.GetLayerByName(src_layer_name)
        assert isinstance(src_layer, ogr.Layer)
        if src_layer is None:
            raise ValueError(f"Could not find layer {src_layer_name} in {dst_path}")
        dst_layer = create_polygon_layer(ds_dirty, dst_layer_name)

        copy_schema(src_layer, dst_layer)

        clean_multipolygons(src_layer, dst_layer)
