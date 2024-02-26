import json
from datetime import datetime

import pytest
from osgeo.ogr import (
    CreateGeometryFromWkt,
    Feature,
    FeatureDefn,
    FieldDefn,
    Geometry,
    OFTDateTime,
    OFTInteger,
    OFTString,
)


@pytest.fixture
def timestamp_0():
    return datetime(2023, 1, 1, 0, 0, 0)


@pytest.fixture
def timestamp_1():
    return datetime(2023, 1, 2, 0, 0, 0)


@pytest.fixture
def base_featdef():
    featdef = FeatureDefn()
    featdef.AddFieldDefn(FieldDefn("osm_timestamp", OFTDateTime))
    featdef.AddFieldDefn(FieldDefn("osm_version", OFTInteger))
    featdef.AddFieldDefn(FieldDefn("all_tags", OFTString))
    featdef.AddFieldDefn(FieldDefn("osm_id", OFTInteger))
    featdef.AddFieldDefn(FieldDefn("osm_way_id", OFTInteger))
    return featdef


@pytest.fixture
def point_feature_1(base_featdef: FeatureDefn, timestamp_0: datetime):
    point = CreateGeometryFromWkt("POINT (1 2)")
    # Feature
    feat = Feature(base_featdef)
    feat.SetFID(1)
    feat.SetField("osm_timestamp", timestamp_0.isoformat())
    feat.SetField("osm_version", 1)
    feat.SetField("all_tags", json.dumps({"key": "value"}))
    feat.SetGeometry(point)
    return feat


@pytest.fixture
def point_feature_1_v2(base_featdef: FeatureDefn):
    point = CreateGeometryFromWkt("POINT (2 1)")
    timestamp = datetime(2023, 1, 1, 0, 0, 0)
    # Feature
    feat = Feature(base_featdef)
    feat.SetFID(1)
    feat.SetField("osm_timestamp", timestamp.isoformat())
    feat.SetField("osm_version", 2)
    feat.SetField("all_tags", json.dumps({"key": "value"}))
    feat.SetGeometry(point)
    return feat


@pytest.fixture
def point_feature_2(base_featdef: FeatureDefn, timestamp_1: datetime):
    point = CreateGeometryFromWkt("POINT (2 -2)")
    feat = Feature(base_featdef)
    feat.SetFID(2)
    feat.SetField("osm_timestamp", timestamp_1.isoformat())
    feat.SetField("osm_version", 1)
    feat.SetField("all_tags", json.dumps({"key": "value"}))
    feat.SetGeometry(point)
    return feat


@pytest.fixture
def point_feature_without_timestamp(
    base_featdef: Feature,
):
    point = CreateGeometryFromWkt("POINT (1 1)")
    feat = Feature(base_featdef)
    feat.SetFID(1)
    feat.SetField("osm_version", 1)
    feat.SetGeometry(point)
    return feat


@pytest.fixture
def point_feature_without_version(base_featdef):
    point = CreateGeometryFromWkt("POINT (1 1)")
    feat = Feature(base_featdef)
    feat.SetFID(1)
    feat.SetField("osm_timestamp", 2023, 1, 19, 0, 0, 0.0, 0)
    feat.SetGeometry(point)
    return feat


@pytest.fixture
def linestring_0():
    return CreateGeometryFromWkt("LINESTRING (1 2, 3 4)")


@pytest.fixture
def linestring_feature_0(base_featdef, linestring_0, timestamp_0):
    feat = Feature(base_featdef)
    feat.SetFID(1)
    feat.SetField("osm_timestamp", timestamp_0.isoformat())
    feat.SetField("osm_version", 1)
    feat.SetField("all_tags", json.dumps({"LSkey": "LSvalue"}))
    feat.SetGeometry(linestring_0)

    return feat


@pytest.fixture
def linestring_abcabba():
    return CreateGeometryFromWkt("LINESTRING (0 0, 1 1, 2 2, 0 0, 1 1, 1 1, 0 0)")


@pytest.fixture
def linestring_cbabac():
    return CreateGeometryFromWkt("LINESTRING (2 2, 1 1, 0 0, 1 1, 0 0, 2 2)")


@pytest.fixture
def linestring_feature_2_v1(base_featdef, linestring_abcabba, timestamp_0):
    feat = Feature(base_featdef)
    feat.SetFID(1)
    feat.SetField("osm_timestamp", timestamp_0.isoformat())
    feat.SetField("osm_version", 1)
    feat.SetField("all_tags", json.dumps({"LSkey": "LSvalue"}))
    feat.SetGeometry(linestring_abcabba)
    return feat


@pytest.fixture
def linestring_feature_2_v2(base_featdef, linestring_cbabac, timestamp_1):
    feat = Feature(base_featdef)
    feat.SetFID(1)
    feat.SetField("osm_timestamp", timestamp_1.isoformat())
    feat.SetField("osm_version", 2)
    feat.SetField("all_tags", json.dumps({"LSkey": "LSvalue"}))
    feat.SetGeometry(linestring_cbabac)
    return feat


@pytest.fixture
def polygon_1():
    return CreateGeometryFromWkt("POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))")


@pytest.fixture
def polygon_2():
    return CreateGeometryFromWkt("POLYGON ((1 1, 1 2, 2 2, 2 1, 1 1))")


@pytest.fixture
def polygon_feature_1(
    base_featdef: FeatureDefn, polygon_1: Geometry, timestamp_0: datetime
):
    feat = Feature(base_featdef)
    feat.SetFID(1)
    feat.SetField("osm_timestamp", timestamp_0.isoformat())
    feat.SetField("osm_version", 1)
    feat.SetField("all_tags", json.dumps({"key1": "value1", "key2": "value2"}))
    feat.SetField("osm_id", 1)
    feat.SetField("osm_way_id", 1)
    feat.SetGeometry(polygon_1)
    return feat


@pytest.fixture
def polygon_feature_2(base_featdef, polygon_2):
    feat = Feature(base_featdef)
    feat.SetFID(2)
    feat.SetGeometry(polygon_2)
    return feat
