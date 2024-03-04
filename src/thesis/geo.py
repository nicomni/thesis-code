from datetime import datetime
from functools import reduce
from typing import Sequence, TypeGuard, cast

from osgeo import ogr as _ogr


Coordinates = list[tuple[float, float]]
IntCoords = list[tuple[int, int]]


def has_field(feat_def: _ogr.FeatureDefn, field_name: str):
    """Check if a FeatureDefn object has field with the specified name."""
    for i in range(feat_def.GetFieldCount()):
        field_defn = feat_def.GetFieldDefn(i)
        if field_defn.GetName() == field_name:
            return True
    else:
        return False


def polygon_has_holes(geom: _ogr.Geometry) -> bool:
    """Check if a polygon has holes."""
    if not geom.GetGeometryType() == _ogr.wkbPolygon:
        raise ValueError("Input feature must be of type Polygon.")
    return geom.GetGeometryCount() > 1


def validate_osm_feature(feat: _ogr.Feature):
    """Validate a feature created from OSM data."""
    # raises if timestamp is not valid iso8601
    datetime.fromisoformat(feat.GetFieldAsISO8601DateTime("osm_timestamp"))

    osm_version = cast(int, feat.GetFieldAsInteger("osm_version"))
    if osm_version < 1:
        raise ValueError(
            f'Invalid or no value for "osm_version" on feature: {feat.ExportToJson()}.'
        )


def is_point(geom: _ogr.Geometry) -> bool:
    return geom.GetGeometryType() == _ogr.wkbPoint


def validate_point(geom: _ogr.Geometry):
    if not is_point(geom):
        raise ValueError("Geometry is not a Point")


def validate_linestring(geom: _ogr.Geometry):
    if geom.GetGeometryType() != _ogr.wkbLineString:
        raise ValueError("Geometry is not a LineString")


def validate_polygon(geom: _ogr.Geometry):
    if geom.GetGeometryType() != _ogr.wkbPolygon:
        raise ValueError("Geometry is not a polygon")

    if polygon_has_holes(geom):
        raise ValueError("Does not support polygons with holes.")


def to100nano(degree: float) -> int:
    """Convert degrees to units of 100 nano degrees."""
    return int(degree * 10**7)


def coordsTo100nano(coords: Coordinates) -> list[tuple[int, int]]:
    """Convert coordinates to units of 100 nano degrees."""
    return [(to100nano(x), to100nano(y)) for x, y in coords]


def delta_encode(seq: Sequence[int]):
    pairs = zip(seq, seq[1:])
    deltas = map(lambda pair: pair[1] - pair[0], pairs)
    return [seq[0]] + list(deltas)


def delta_code_coordinates(coords: IntCoords):
    """Convert coordinates to delta code coordinates."""
    delta_x = [coords[0][0]]
    delta_y = [coords[0][1]]

    for i in range(1, len(coords)):
        delta_x.append(coords[i][0] - coords[i - 1][0])
        delta_y.append(coords[i][1] - coords[i - 1][1])

    return delta_x, delta_y


def isCoordinates(coords) -> TypeGuard[Coordinates]:
    """Check if coordinates is a list of tuples of floats."""
    if not isinstance(coords, list):
        return False
    for coord in coords:
        if not isinstance(coord, tuple):
            return False
        if not len(coord) == 2:
            return False
        if not isinstance(coord[0], float) or not isinstance(coord[1], float):
            return False
    return True


def is_linestring(geom: _ogr.Geometry) -> bool:
    return geom.GetGeometryType() == _ogr.wkbLineString


def is_linearring(geom: _ogr.Geometry) -> bool:
    return geom.GetGeometryType() == _ogr.wkbLinearRing
