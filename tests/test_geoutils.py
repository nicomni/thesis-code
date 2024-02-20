import json
from datetime import datetime
from typing import cast

import pytest
from osgeo import ogr
from osgeo.ogr import (CreateGeometryFromWkt, Feature, Geometry, UseExceptions,
                       wkbMultiPolygon)


@pytest.fixture
def mp_feature(base_featdef: ogr.FeatureDefn):
    UseExceptions()
    feat = Feature(base_featdef)

    feat.SetFID(1)

    feat.SetField("osm_timestamp", "2023-01-01T00:00:00Z")
    feat.SetField("osm_version", 1)
    feat.SetField("all_tags", json.dumps({"testKey": "testValue"}))
    feat.SetField("osm_id", 1)
    feat.SetField("osm_way_id", 1)

    feat.SetGeometry(
        CreateGeometryFromWkt("MULTIPOLYGON (((1 1, 1 2, 2 2, 2 1, 1 1)))")
    )
    return feat


def test_multipolygon_to_polygon(mp_feature: Feature):
    UseExceptions()
    dt = datetime.fromisoformat("2023-01-01T00:00:00Z")
    expected_geom = CreateGeometryFromWkt("POLYGON ((1 1, 1 2, 2 2, 2 1, 1 1))")
    mp_geom = cast(Geometry, mp_feature.geometry())

    polygon = mp_geom.GetGeometryRef(0)
    new_feat: ogr.Feature = mp_feature.Clone()
    new_feat.SetGeometry(polygon)
    assert new_feat.GetGeometryRef().ExportToWkt() == expected_geom.ExportToWkt()
    assert (
        datetime.fromisoformat(
            new_feat.GetFieldAsISO8601DateTime("osm_timestamp")
        ).isoformat()
        == dt.isoformat()
    )
