import pytest

from thesis.geodiff import diff
from thesis.geodiff.errors import GeometryTypeMismatchError
from thesis.geodiff.geodiff import _validate_diff_input


def test_validate_diff_input_when_mismatching_geom_types_should_raise():
    a = "POINT (1 1)"
    b = "LINESTRING (1 1, 2 2)"
    with pytest.raises(GeometryTypeMismatchError):
        _validate_diff_input(a, b)


def test_diff_point():
    a = "POINT (1 1)"
    b = "POINT (3 3)"
    want = (2, 2)
    got = diff(a, b)
    assert got == want


def test_diff_linestring():
    a = "LINESTRING (1 1, 2 2)"
    b = "LINESTRING (1 1, 3 3)"
    want = [(1, "change", (1, 1))]
    got = diff(a, b)
    assert got == want


def test_diff_rings():
    a = "LINEARRING (0 0, 0 1, 1 1, 1 0, 0 0)"
    b = "LINEARRING (0 0, 1 1, 2 1, 0 0)"
    want = [(1, "delete"), (3, "change", (1, 1))]
    got = diff(a, b)
    assert got == want
