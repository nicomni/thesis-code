
import pytest
from osgeo.ogr import Feature

from thesis.utils import get_geom_patch


class TestGetGeomPatch:
    def test_mismatching_geom_type_raises(
        self, point_feature_1: Feature, linestring_feature_0: Feature
    ):
        with pytest.raises(TypeError, match="Geometry type mismatch"):
            get_geom_patch(point_feature_1, linestring_feature_0)

    def test_equal_geometries_returns_none(self, point_feature_1: Feature):
        assert get_geom_patch(point_feature_1, point_feature_1) is None

    def test_unsupported_geometry_type_raises(
        self, polygon_feature_1, polygon_feature_2
    ):
        with pytest.raises(TypeError, match="Unsupported geometry type"):
            get_geom_patch(polygon_feature_1, polygon_feature_2)
