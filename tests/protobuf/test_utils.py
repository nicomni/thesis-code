from osgeo import ogr

from thesis import protobuf
from thesis.protobuf import utils


def test_to_point_message():
    point = ogr.CreateGeometryFromWkt("POINT (1 2)")
    want = protobuf.Point(lon=10000000, lat=20000000)

    got = utils.to_point_message(point)

    assert got.lon == want.lon
    assert got.lat == want.lat


def test_to_linestring_message():
    linestring = ogr.CreateGeometryFromWkt("LINESTRING (0 0, 0 1, 1 1, 1 0)")
    want = protobuf.LineString(lon=[0, 0, 10000000, 0], lat=[0, 10000000, 0, -10000000])

    got = utils.to_linestring_message(linestring)

    assert got.lon == want.lon
    assert got.lat == want.lat


def test_toPolygonMessage():
    # Arrange
    polygon = ogr.CreateGeometryFromWkt("POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))")

    want = protobuf.Polygon(
        lon=[0, 0, 10000000, 0, -10000000], lat=[0, 10000000, 0, -10000000, 0]
    )
    # Act
    got = utils.to_polygon_message(polygon)

    # Assert
    assert got.lon == want.lon
    assert got.lat == want.lat
