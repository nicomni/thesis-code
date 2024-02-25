from shapely import Point

from thesis import gisevents
from thesis.utils import get_pointdiff_message


def test_get_pointdiff_message():
    a = Point(1, 1)
    b = Point(2, 2)
    diff_lat = 10000000  # unit of 100 nanodegrees
    diff_lon = 10000000  # unit of 100 nanodegrees
    want = gisevents.Point(lat=diff_lat, lon=diff_lon)
    got = get_pointdiff_message(a, b)
    assert want == got
