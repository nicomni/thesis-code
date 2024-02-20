import click
from alive_progress import alive_bar
from osgeo import ogr


def _create_polygon_layer(ds: ogr.DataSource, layer_name: str) -> ogr.Layer:
    """Create a new layer in the given data source.
    If a layer with the given name already exists, it will be deleted.
    """
    layer = ds.GetLayerByName(layer_name)
    if layer is not None:
        click.echo(f"Layer `{layer_name}` already exists. Deleting...")
        ds.DeleteLayer(layer.GetLayerDefn().GetName())
    click.echo(f"Creating layer {layer_name}...")
    layer = ds.CreateLayer(
        layer_name,
        srs=ds.GetLayerByName("multipolygons").GetSpatialRef(),
        geom_type=ogr.wkbPolygon,
    )
    print(f"Created layer {layer_name}.")
    return layer


def _copy_schema(source_layer: ogr.Layer, target_layer: ogr.Layer):
    """Copy the schema (fields) from the source layer to the target layer."""
    for field_defn in source_layer.schema:  # pyright:ignore
        assert isinstance(field_defn, ogr.FieldDefn)
        target_layer.CreateField(field_defn)


def _extract_polygons(src_layer: ogr.Layer, dst_layer: ogr.Layer):
    feat_count = src_layer.GetFeatureCount()
    assert isinstance(feat_count, int)
    with alive_bar(feat_count, enrich_print=False) as bar:
        bar.title("Extracting simple polygons")
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


@click.command()
@click.argument("gpkg-file-path")
@click.option(
    "--layer-name",
    help="Name of multipolgon layer.",
    default="multipolygons",
    show_default=True,
)
def extract_polygons(gpkg_file_path: str, layer_name: str):
    """Extract all simple polygons from multipolygons and add them to the new polygon layer.
    Only extracts polygons with no holes.
    All attribute fields are copied. The FID is preserved.
    """
    ogr.UseExceptions()
    with ogr.Open(gpkg_file_path, 1) as ds_dirty:
        assert isinstance(ds_dirty, ogr.DataSource)
        src_layer = ds_dirty.GetLayerByName(layer_name)
        assert isinstance(src_layer, ogr.Layer)
        if src_layer is None:
            raise ValueError(f"Could not find layer {layer_name} in {gpkg_file_path}")
        dst_layer = _create_polygon_layer(ds_dirty, "polygons")
        _copy_schema(src_layer, dst_layer)
        _extract_polygons(src_layer, dst_layer)
