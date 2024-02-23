# Fixtures are defined in conftest.py

from datetime import datetime

import pytest
from google.protobuf.timestamp_pb2 import Timestamp
from osgeo.ogr import Feature

import thesis.events as events
from thesis import protobuf


class TestCreateCreationEvent:
    def test_validate_feature_without_version_should_raise(
        self, point_feature_without_version
    ):
        with pytest.raises(ValueError):
            events._validate_creation_event_args(point_feature_without_version)

    def test_create_point_event(self, point_feature_1: Feature):
        ts_msg = Timestamp()
        ts_msg.FromDatetime(
            datetime.fromisoformat(
                point_feature_1.GetFieldAsISO8601DateTime("osm_timestamp")
            )
        )

        props = protobuf.Properties(key=["key"], value=["value"])

        want = protobuf.CreationEvent(
            id=1,
            point=protobuf.Point(lon=10000000, lat=10000000),
            version=1,
            properties=props,
            timestamp=ts_msg,
        )
        got = events.creation_event(point_feature_1)

        assert got.id == want.id
        assert got.version == want.version
        assert got.properties == want.properties
        assert got.point.lat == want.point.lat
        assert got.point.lon == want.point.lon
        assert got.timestamp.ToDatetime() == ts_msg.ToDatetime()

    def test_create_linestring(
        self, linestring_feature_0: Feature, timestamp_0: datetime
    ):
        # Delta-coded LineString
        ls = protobuf.LineString(lon=[10000000, 20000000], lat=[20000000, 20000000])

        want = protobuf.CreationEvent(
            id=1,
            linestring=ls,
            version=1,
            properties={"key": ["LSkey"], "value": ["LSvalue"]},
            timestamp=Timestamp(),
        )
        want.timestamp.FromDatetime(timestamp_0)
        got = events.creation_event(linestring_feature_0)

        assert got.id == want.id
        assert got.version == want.version
        assert got.timestamp.seconds == want.timestamp.seconds
        assert got.properties.key == want.properties.key
        assert got.properties.value == want.properties.value
        assert got.linestring.lon == want.linestring.lon
        assert got.linestring.lat == want.linestring.lat

    def test_create_polygon(self, polygon_feature_1: Feature):
        dt = datetime.fromisoformat(
            polygon_feature_1.GetFieldAsISO8601DateTime("osm_timestamp")
        )
        polygon_msg = protobuf.Polygon(
            lon=[0, 0, 10000000, 0, -10000000], lat=[0, 10000000, 0, -10000000, 0]
        )

        want = protobuf.CreationEvent(
            id=1,
            polygon=polygon_msg,
            version=1,
            properties={"key": ["key1", "key2"], "value": ["value1", "value2"]},
            timestamp=Timestamp(),
        )
        want.timestamp.FromDatetime(dt)

        got = events.creation_event(polygon_feature_1)

        assert got.id == want.id
        assert got.version == want.version
        assert got.timestamp.ToJsonString() == want.timestamp.ToJsonString()
        assert got.properties.key == want.properties.key
        assert got.properties.value == want.properties.value
        assert got.polygon.lat == want.polygon.lat
        assert got.polygon.lon == want.polygon.lon


class TestCreateModEvent:
    def test_validate_mismatching_fid_raises(
        self, point_feature_1: Feature, point_feature_2: Feature
    ):
        with pytest.raises(ValueError, match="FID mismatch"):
            events._validate_modification_args(point_feature_1, point_feature_2)

    def test_validate_mismatching_geom_type_raises(
        self, point_feature_1: Feature, linestring_feature_2_v2: Feature
    ):
        with pytest.raises(
            ValueError, match="Geometry type mismatch: POINT and LINESTRING"
        ):
            events._validate_modification_args(point_feature_1, linestring_feature_2_v2)

    def test_validate_mismatching_version_raises(self, point_feature_1: Feature):
        with pytest.raises(
            ValueError,
            match=r"Version number of the second feature argument must be "
            + r"one more than the first argument's. Versions were \d+ and \d+",
        ):
            events.modification_event(point_feature_1, point_feature_1)

    @pytest.mark.xfail(reason="Not fixed")
    def test_modification_event_point(
        self, point_feature_1: Feature, point_feature_1_v2: Feature
    ):
        want = protobuf.ModificationEvent(
            id=1,
            version=2,
            point_patch=protobuf.Point(lon=10000000, lat=10000000),
            timestamp=Timestamp(),
        )
        want.timestamp.FromDatetime(
            datetime.fromisoformat(
                point_feature_1_v2.GetFieldAsISO8601DateTime("osm_timestamp")
            )
        )
        got = events.modification_event(point_feature_1, point_feature_1_v2)
        assert got.id == want.id
        assert got.version == want.version
        assert got.point_patch.lat == want.point_patch.lat
        assert got.point_patch.lon == want.point_patch.lon
        assert not got.HasField("prop_patch")

    @pytest.mark.xfail(reason="Not fixed")
    def test_create_mod_event_changing_linestring_value(
        self, linestring_feature_2_v1: Feature, linestring_feature_2_v2: Feature
    ):
        want = protobuf.ModificationEvent(
            id=1,
            version=2,
            linestring_patch=protobuf.LineStringPatch(
                index=[0, 2, 5, 6],
                command=[
                    protobuf.LineStringPatch.CHANGE,
                    protobuf.LineStringPatch.DELETE,
                    protobuf.LineStringPatch.DELETE,
                    protobuf.LineStringPatch.INSERT,
                ],
                vector=[
                    protobuf.Point(lat=20000000, lon=20000000),
                    protobuf.Point(lat=0, lon=0),  # default NULL value
                    protobuf.Point(lat=0, lon=0),  # default NULL value
                    protobuf.Point(lat=20000000, lon=20000000),
                ],
            ),
            timestamp=Timestamp(),
        )
        want.timestamp.FromDatetime(
            datetime.fromisoformat(
                linestring_feature_2_v2.GetFieldAsISO8601DateTime("osm_timestamp")
            )
        )

        got = events.modification_event(
            linestring_feature_2_v1, linestring_feature_2_v2
        )
        assert got.linestring_patch.index == want.linestring_patch.index
        assert got.linestring_patch.command == want.linestring_patch.command
        assert got.linestring_patch.vector == want.linestring_patch.vector

    @pytest.mark.skip(reason="Not implemented")
    def test_create_mod_event_change_properties(
        self, point_feature_1_v2: Feature, point_
    ):
        # TODO: Implement this test
        assert False
