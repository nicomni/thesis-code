from collections.abc import Iterable
import pytest
from thesis.osm import ElementType
from thesis import properties, utils, geodiff, gisevents


def test_get_search_layers_for_node():
    assert utils.get_search_layers(ElementType.NODE) == ["points"]


def test_get_search_layers_for_way():
    assert utils.get_search_layers(ElementType.WAY) == ["lines", "rings"]


def test_get_search_layers_for_relation():
    assert utils.get_search_layers(ElementType.RELATION) == ["lines", "rings"]


def test_to_point_message():
    point = (1.0, 2.0)
    got = utils.to_point_message(point)
    assert got.lon == 10000000
    assert got.lat == 20000000


def test_to_linestringpatch_message():
    patch: geodiff.LSPatch = [
        (0, "change", (2, 2)),
        (2, "delete"),
        (5, "delete"),
        (6, "insert", (2, 2)),
    ]

    got = utils.to_lspatch_message(patch)
    assert got.command == [
        gisevents.LineStringPatch.CHANGE,
        gisevents.LineStringPatch.DELETE,
        gisevents.LineStringPatch.DELETE,
        gisevents.LineStringPatch.INSERT,
    ]
    assert got.index == [0, 2, 5, 6]
    assert list(got.vector) == [
        gisevents.Point(lon=20000000, lat=20000000),
        gisevents.Point(lon=0, lat=0),
        gisevents.Point(lon=0, lat=0),
        gisevents.Point(lon=20000000, lat=20000000),
    ]


def test_to_prop_patch_message():
    patch: Iterable[properties.PatchCommand] = [
        (properties.ChangeType.UPDATE, "key1", "value2"),
        (properties.ChangeType.DELETE, "key3"),
        (properties.ChangeType.INSERT, "key4", "value4"),
        (properties.ChangeType.DELETE, "key5"),
    ]
    got = utils.to_prop_patch_msg(patch)
    assert got.prop_delete.key == ["key3", "key5"]
    assert got.prop_update.key == ["key1"]
    assert got.prop_update.value == ["value2"]
    assert got.prop_insert.key == ["key4"]
    assert got.prop_insert.value == ["value4"]


@pytest.mark.xfail(reason="Not implemented")
def test_to_polygonpatch_message():
    assert False
