from thesis.osm import ElementType
from thesis.utils import get_search_layers


def test_get_search_layers_for_node():
    assert get_search_layers(ElementType.NODE) == ["points"]


def test_get_search_layers_for_way():
    assert get_search_layers(ElementType.WAY) == ["lines", "rings"]


def test_get_search_layers_for_relation():
    assert get_search_layers(ElementType.RELATION) == ["lines", "rings"]
