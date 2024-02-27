# Fixtures are defined in conftest.py

from datetime import datetime
import json
from osgeo import ogr

import pytest
from google.protobuf.timestamp_pb2 import Timestamp
from osgeo.ogr import Feature

import thesis.events as events
from thesis import gisevents, geodiff


class TestCreateCreationEvent:
    def test_validate_feature_without_version_should_raise(
        self, point_feature_without_version
    ):
        with pytest.raises(ValueError):
            events._validate_creation_event_args(point_feature_without_version)

    def test_creation_event_point(self, base_featdef: ogr.FeatureDefn):
        # Arrange
        point = ogr.CreateGeometryFromWkt("POINT (1 2)")
        fid = 5
        timestamp = "2023-01-01T00:00:00Z"
        version = 2
        properties = {"testKey": "testValue"}
        feat = ogr.Feature(base_featdef)
        feat.SetFID(fid)
        feat.SetField("osm_timestamp", timestamp)
        feat.SetField("osm_version", version)
        feat.SetField("all_tags", json.dumps(properties))
        feat.SetGeometry(point)

        # Act
        got = events.creation_event(feat)

        # Assert
        assert got.id == fid
        assert got.version == version
        assert got.properties.key == list(properties.keys())
        assert got.properties.value == list(properties.values())
        assert got.point.lon == 10000000
        assert got.point.lat == 20000000
        assert got.timestamp.ToJsonString() == timestamp

    def test_create_linestring(self, base_featdef: ogr.FeatureDefn):
        # Arrange
        line = ogr.CreateGeometryFromWkt("LINESTRING (1 2, 2 2)")

        fid = 4
        timestamp = "2023-01-01T00:00:00Z"
        version = 3
        properties = {"testKey": "testValue"}

        feat = ogr.Feature(base_featdef)
        feat.SetFID(fid)
        feat.SetField("osm_timestamp", timestamp)
        feat.SetField("osm_version", version)
        feat.SetField("all_tags", json.dumps(properties))
        feat.SetGeometry(line)

        # Act
        got = events.creation_event(feat)

        # Assert
        assert got.id == fid
        assert got.version == version
        assert got.properties.key == list(properties.keys())
        assert got.properties.value == list(properties.values())
        assert got.linestring.lon == [10000000, 10000000]
        assert got.linestring.lat == [20000000, 0]
        assert got.timestamp.ToJsonString() == timestamp

    def test_create_polygon(self, base_featdef: ogr.FeatureDefn):
        polygon = ogr.CreateGeometryFromWkt("POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))")
        fid = 3
        timestamp = "2023-01-01T00:00:00Z"
        version = 14
        properties = {"testKey": "testValue"}

        feat = ogr.Feature(base_featdef)
        feat.SetFID(fid)
        feat.SetField("osm_timestamp", timestamp)
        feat.SetField("osm_version", version)
        feat.SetField("all_tags", json.dumps(properties))
        feat.SetGeometry(polygon)

        # Act
        got = events.creation_event(feat)

        assert got.id == fid
        assert got.version == version
        assert got.timestamp.ToJsonString() == timestamp
        assert got.properties.key == list(properties.keys())
        assert got.properties.value == list(properties.values())
        assert got.polygon.lon == [0, 0, 10000000, 0, -10000000]
        assert got.polygon.lat == [0, 10000000, 0, -10000000, 0]


class TestCreateModEvent:
    def test_validate_mismatching_fid_raises(
        self, point_feature_1: Feature, point_feature_2: Feature
    ):
        with pytest.raises(ValueError, match="FID mismatch"):
            events._validate_modification_args(point_feature_1, point_feature_2)

    def test_validate_mismatching_geom_type_raises(
        self, point_feature_2: Feature, linestring_feature_2_v1: Feature
    ):
        with pytest.raises(
            geodiff.GeometryTypeMismatchError,
            match="Geometry type mismatch: POINT != LINESTRING",
        ):
            events._validate_modification_args(point_feature_2, linestring_feature_2_v1)

    def test_validate_mismatching_version_raises(self, point_feature_1: Feature):
        with pytest.raises(
            ValueError,
            match=r"Version number of the second feature argument must be "
            + r"one more than the first argument's. Versions were \d+ and \d+",
        ):
            events.modification_event(point_feature_1, point_feature_1)

    def test_modification_event_point(
        self, point_feature_1: Feature, point_feature_1_v2: Feature
    ):
        got = events.modification_event(point_feature_1, point_feature_1_v2)

        assert got.id == 1
        assert (
            got.timestamp.ToDatetime().isoformat()
            == datetime(2023, 1, 1, 0, 0, 0).isoformat()
        )
        assert got.version == 2
        assert got.HasField("point_patch")
        assert got.HasField("prop_patch")
        assert got.prop_patch.prop_update.key == ["key1"]
        assert got.prop_patch.prop_update.value == ["value_v2"]

    def test_create_modification_event_linesstring(
        self, linestring_feature_2_v1: Feature, linestring_feature_2_v2: Feature
    ):
        got = events.modification_event(
            linestring_feature_2_v1, linestring_feature_2_v2
        )
        assert got.id == 2
        assert got.version == 2
        assert got.timestamp.ToDatetime().isoformat() == "2023-01-02T00:00:00"
        assert got.HasField("linestring_patch")
        assert got.HasField("prop_patch")


class TestCreateDeletionEvent:
    def test_deletion_event_point(self, point_feature_1: Feature):
        timestamp = datetime(2023, 1, 1, 0, 0, 0)
        got = events.deletion_event(point_feature_1, timestamp)
        assert got.id == 1
        assert (
            got.timestamp.ToDatetime().isoformat()
            == datetime(2023, 1, 1, 0, 0, 0).isoformat()
        )
        assert got.version == 1
