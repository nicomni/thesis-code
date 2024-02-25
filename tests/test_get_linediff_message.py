import pytest
from shapely import LineString

from thesis import gisevents
from thesis.utils import get_linediff_message

Title = str
Input = tuple[LineString, LineString]
Expected = gisevents.LineStringPatch

LineStringDiffScenario = tuple[Title, Input, Expected]
Scenarios = list[LineStringDiffScenario]

scenarios: Scenarios = [
    (
        "ab -> cb",
        (LineString([(0, 0), (1, 1)]), LineString([(2, 2), (1, 1)])),
        gisevents.LineStringPatch(
            index=[0],
            command=[gisevents.LineStringPatch.Command.CHANGE],
            vector=[gisevents.Point(lat=20000000, lon=20000000)],
        ),
    ),
    (
        "ab -> ac",
        (LineString([(0, 0), (1, 1)]), LineString([(0, 0), (2, 2)])),
        gisevents.LineStringPatch(
            index=[1],
            command=[gisevents.LineStringPatch.Command.CHANGE],
            vector=[gisevents.Point(lat=10000000, lon=10000000)],
        ),
    ),
    (
        "abcabba -> cbabac",
        (
            LineString([(0, 0), (1, 1), (2, 2), (0, 0), (1, 1), (1, 1), (0, 0)]),
            LineString([(2, 2), (1, 1), (0, 0), (1, 1), (0, 0), (2, 2)]),
        ),
        gisevents.LineStringPatch(
            index=[0, 2, 5, 6],
            command=[
                gisevents.LineStringPatch.CHANGE,
                gisevents.LineStringPatch.DELETE,
                gisevents.LineStringPatch.DELETE,
                gisevents.LineStringPatch.INSERT,
            ],
            vector=[
                gisevents.Point(lat=20000000, lon=20000000),
                gisevents.Point(lat=0, lon=0),  # default NULL value
                gisevents.Point(lat=0, lon=0),  # default NULL value
                gisevents.Point(lat=20000000, lon=20000000),
            ],
        ),
    ),
]


def idfn(val: LineStringDiffScenario):
    return val[0]  # the title


@pytest.mark.parametrize("scenario", scenarios, ids=idfn)
def test_get_linediff_message(scenario: LineStringDiffScenario):
    input = scenario[1]
    a = input[0]
    b = input[1]
    want = scenario[2]
    got = get_linediff_message(a, b)
    assert isinstance(got, gisevents.LineStringPatch)
    assert want.index == got.index
    assert want.command == got.command
    assert want.vector == got.vector
