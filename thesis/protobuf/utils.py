from typing import cast

from osgeo import ogr

from thesis import protobuf

from .. import geo


def to_point_message(geom: ogr.Geometry) -> protobuf.Point:
    try:
        geo.validate_point(geom)
    except Exception:
        raise

    return protobuf.Point(
        lon=geo.to100nano(geom.GetX()), lat=geo.to100nano(geom.GetY())
    )


def _get_deltas(geom: ogr.Geometry) -> tuple[list[int], list[int]]:
    if not (geo.is_linestring(geom) or geo.is_linearring(geom)):
        raise ValueError(f"Geometry type is not appropriate: {geom.GetGeometryName()}")

    lon: list[int] = []
    lat: list[int] = []

    for i in range(geom.GetPointCount()):
        lon.append(geo.to100nano(geom.GetX(i)))
        lat.append(geo.to100nano(geom.GetY(i)))
    delta_lon = geo.delta_encode(lon)
    delta_lat = geo.delta_encode(lat)
    return delta_lon, delta_lat


def to_linestring_message(geom: ogr.Geometry) -> protobuf.LineString:
    """Convert LineString geometry to a protobuf message.

    The coordinates are converted to units of 100 nano degrees and delta code coordinates.
    """
    try:
        geo.validate_linestring(geom)
    except Exception:
        raise

    delta_lon, delta_lat = _get_deltas(geom)
    return protobuf.LineString(lon=delta_lon, lat=delta_lat)


def to_polygon_message(geom: ogr.Geometry) -> protobuf.Polygon:
    try:
        geo.validate_polygon(geom)
    except Exception:
        raise

    ring = cast(ogr.Geometry, geom.GetGeometryRef(0))
    delta_lon, delta_lat = _get_deltas(ring)

    return protobuf.Polygon(lon=delta_lon, lat=delta_lat)
