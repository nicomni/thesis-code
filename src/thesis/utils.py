import json

from osgeo import ogr

from thesis import geo, gisevents
from thesis.geodiff import geodiff
from thesis.osm import ElementType


def get_search_layers(osm_type: ElementType):
    """Returns the search layers for the given OSM type."""
    match osm_type:
        case ElementType.NODE:
            return ["points"]
        case ElementType.WAY | ElementType.RELATION:
            return ["lines", "rings"]


def to_point_message(point: tuple[float, float]) -> gisevents.Point:
    """Convert a point tuple to a gisevents message."""
    ilon = geo.to100nano(point[0])
    ilat = geo.to100nano(point[1])
    return gisevents.Point(lat=ilat, lon=ilon)


def to_lspatch_message(patch: geodiff.LSPatch) -> gisevents.LineStringPatch:
    command: list[gisevents.LineStringPatch.Command] = []
    index: list[int] = []
    vector: list[gisevents.Point] = []

    to_command = {
        "insert": gisevents.LineStringPatch.INSERT,
        "change": gisevents.LineStringPatch.CHANGE,
        "delete": gisevents.LineStringPatch.DELETE,
    }

    for patch_cmd in patch:
        index.append(patch_cmd[0])
        command.append(to_command[patch_cmd[1]])
        if patch_cmd[1] == "delete":
            vector.append(gisevents.Point(lon=0, lat=0))
        else:
            vector.append(to_point_message(patch_cmd[2]))

    result = gisevents.LineStringPatch(command=command, index=index, vector=vector)
    return result


def get_prop_patch(prev: ogr.Feature, curr: ogr.Feature):
    # Check properties
    prev_props: dict = json.loads(prev.GetFieldAsString("all_tags"))
    curr_props: dict = json.loads(curr.GetFieldAsString("all_tags"))
    if prev_props != curr_props:
        # TODO: Create a diff
        raise NotImplementedError()
