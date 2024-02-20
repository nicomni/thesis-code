import pytest
from osgeo import ogr

from thesis import geo


def test_validate_osm_feature_raises_on_invalid_timestamp(
    point_feature_without_timestamp: ogr.Feature,
):
    with pytest.raises(ValueError):
        geo.validate_osm_feature(point_feature_without_timestamp)


def test_delta_encode():
    # Arrange
    seq = [1, 2, 4, 7, 11]
    want = [1, 1, 2, 3, 4]
    # Act
    got = geo.delta_encode(seq)
    # Assert
    assert got == want
