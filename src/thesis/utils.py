from typing import Iterable

from thesis import geo, gisevents, properties as props
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


def to_prop_patch_msg(patch: Iterable[props.PatchCommand]) -> gisevents.PropPatch:
    deletes = []
    update_keys: list[str] = []
    update_vals: list[str] = []
    insert_keys: list[str] = []
    insert_vals: list[str] = []
    for cmd in patch:
        ch_type, key, *value = cmd
        if ch_type is props.ChangeType.DELETE:
            deletes.append(key)
        elif ch_type is props.ChangeType.UPDATE:
            update_keys.append(key)
            update_vals.append(*value)
        elif ch_type is props.ChangeType.INSERT:
            insert_keys.append(key)
            insert_vals.append(*value)
    prop_patch = gisevents.PropPatch()
    if len(deletes) > 0:
        prop_patch.prop_delete.CopyFrom(gisevents.PropDelete(key=deletes))
    if len(update_keys) > 0:
        prop_patch.prop_update.CopyFrom(
            gisevents.PropUpdate(key=update_keys, value=update_vals)
        )
    if len(insert_keys) > 0:
        prop_patch.prop_insert.CopyFrom(
            gisevents.PropInsert(key=insert_keys, value=insert_vals)
        )
    return prop_patch
