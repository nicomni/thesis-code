import json

from osgeo import ogr
from shapely import GeometryType, LineString, Point, from_wkt, get_type_id
from shapely.geometry.base import BaseGeometry

from thesis import protobuf
from thesis.types import ElementType

from . import geo
from .geodiff import geodiff

# TODO: Remove shapely dependency


def get_search_layers(osm_type: ElementType):
    """Returns the search layers for the given OSM type."""
    match osm_type:
        case ElementType.NODE:
            return ["points"]
        case ElementType.WAY | ElementType.RELATION:
            return ["lines", "rings"]


def get_pointdiff_message(a: Point, b: Point) -> protobuf.Point:
    """Calculate the difference between two points.

    RETURNS:
        A protocol buffer Point message.
    """
    pointdiff = geodiff.diff_points(a, b)
    lat = pointdiff.x
    lon = pointdiff.y
    ilat = geo.to100nano(lat)
    ilon = geo.to100nano(lon)
    return protobuf.Point(lat=ilat, lon=ilon)


def get_linediff_message(a: LineString, b: LineString):
    patch = geodiff.diff_linestrings(a, b)
    N = len(patch)
    indeces = [0] * N
    commands = [protobuf.LineStringPatch.Command.CHANGE] * N
    diff_vectors = [protobuf.Point()] * N
    for i, cmd in enumerate(patch):
        index = cmd[0]
        indeces[i] = index
        name = cmd[1]
        if len(cmd) == 3:
            # Is insert or change command
            point = cmd[2]
            ilat, ilon = (geo.to100nano(point[0]), geo.to100nano(point[1]))
            diff_vector = protobuf.Point(lat=ilat, lon=ilon)
            diff_vectors[i] = diff_vector

        match name:
            case "insert":
                commands[i] = protobuf.LineStringPatch.Command.INSERT
            case "change":
                commands[i] = protobuf.LineStringPatch.Command.CHANGE
            case "delete":
                commands[i] = protobuf.LineStringPatch.Command.DELETE
            case _:
                raise ValueError(f"Unexpected command name: {name}")

    return protobuf.LineStringPatch(
        index=indeces, command=commands, vector=diff_vectors
    )


def get_geom_patch(prev_feature: ogr.Feature, curr_feature: ogr.Feature):
    # Check geometry types
    if (
        prev_feature.GetGeometryRef().GetGeometryType()
        != curr_feature.GetGeometryRef().GetGeometryType()
    ):
        raise TypeError("Geometry type mismatch.")
    # Check for geometry change
    prev_geom: BaseGeometry = from_wkt(prev_feature.GetGeometryRef().ExportToWkt())
    curr_geom: BaseGeometry = from_wkt(curr_feature.GetGeometryRef().ExportToWkt())
    if prev_geom.almost_equals(curr_geom, decimal=7):
        return None
    geom_type_id = get_type_id(prev_geom)
    match geom_type_id:
        case GeometryType.POINT:
            return get_pointdiff_message(prev_geom, curr_geom)
        case GeometryType.LINESTRING:
            return get_linediff_message(prev_geom, curr_geom)
        case _:
            raise TypeError(f"Unsupported geometry type: {prev_geom.geom_type}.")


def get_prop_patch(prev: ogr.Feature, curr: ogr.Feature):
    # Check properties
    prev_props: dict = json.loads(prev.GetFieldAsString("all_tags"))
    curr_props: dict = json.loads(curr.GetFieldAsString("all_tags"))
    if prev_props != curr_props:
        # TODO: Create a diff
        raise NotImplementedError()
