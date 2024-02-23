from thesis.osm import ElementType
from thesis import utils, geodiff, protobuf


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
        protobuf.LineStringPatch.CHANGE,
        protobuf.LineStringPatch.DELETE,
        protobuf.LineStringPatch.DELETE,
        protobuf.LineStringPatch.INSERT,
    ]
    assert got.index == [0, 2, 5, 6]
    assert list(got.vector) == [
        protobuf.Point(lon=20000000, lat=20000000),
        protobuf.Point(lon=0, lat=0),
        protobuf.Point(lon=0, lat=0),
        protobuf.Point(lon=20000000, lat=20000000),
    ]
