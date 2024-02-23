from thesis.osm import ElementType
from thesis import utils
from thesis import geodiff


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
