from datetime import datetime
from re import Pattern

import pytest
from google.protobuf.timestamp_pb2 import Timestamp
from osgeo.ogr import Feature

from thesis import protobuf
from thesis.main import create_mod_event, get_geom_patch


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
