from typing import NamedTuple

import pytest
from shapely import LineString, Point

from geomdiff.myers import Diff, _diff


class Expected(NamedTuple):
    edit_length: int
    edit_script: Diff


class Scenario(NamedTuple):
    name: str
    id: int
    ls1: LineString | Point | None
    ls2: LineString | Point | None
    expected: Expected


def idfn(val):
    return val.name


class TestMyersLineString:
    scenarios = [
        (Scenario("2 empty sequences", 1, None, None, Expected(0, []))),
        (
            Scenario(
                "single point and empty sequence",
                2,
                Point(0, 0),
                None,
                Expected(1, [(0, "delete")]),
            )
        ),
        (
            Scenario(
                "empty seq and single point",
                3,
                None,
                Point(0, 0),
                Expected(1, [(-1, "insert", (0, 0))]),
            )
        ),
        (Scenario("two equal points", 4, Point(1, 1), Point(1, 1), Expected(0, []))),
        (
            Scenario(
                "2 different single points",
                5,
                Point(1, 1),
                Point(2, 2),
                Expected(2, [(0, "delete"), (0, "insert", (2, 2))]),
            )
        ),
        (
            Scenario(
                "remove first point 2-string",
                6,
                LineString([(1, 1), (2, 2)]),
                Point(2, 2),
                Expected(1, [(0, "delete")]),
            )
        ),
        (
            Scenario(
                "remove last point 2-string",
                7,
                LineString([(1, 1), (2, 2)]),
                Point(1, 1),
                Expected(1, [(1, "delete")]),
            )
        ),
        (
            Scenario(
                "add point in front",
                8,
                Point(2, 2),
                LineString([(1, 1), (2, 2)]),
                Expected(1, [(-1, "insert", (1, 1))]),
            )
        ),
        (
            Scenario(
                "add point at back",
                9,
                Point(1, 1),
                LineString([(1, 1), (2, 2)]),
                Expected(1, [(0, "insert", (2.0, 2.0))]),
            )
        ),
        (
            Scenario(
                "change first point",
                10,
                LineString([(1, 1), (2, 2)]),
                LineString([(3, 3), (2, 2)]),
                Expected(2, [(0, "delete"), (0, "insert", (3, 3))]),
            )
        ),
        (
            Scenario(
                "change last point",
                11,
                LineString([(1, 1), (2, 2)]),
                LineString([(1, 1), (3, 3)]),
                Expected(2, [(1, "delete"), (1, "insert", (3, 3))]),
            )
        ),
    ]

    @pytest.mark.parametrize(argnames="scenario", argvalues=scenarios, ids=idfn)
    def test_scenarios(self, scenario: Scenario):
        ls1 = scenario.ls1
        ls2 = scenario.ls2
        seq1 = []
        seq2 = []
        if ls1 is not None:
            seq1 = list(ls1.coords)
        if ls2 is not None:
            seq2 = list(ls2.coords)
        res = list(_diff(seq1, seq2, 0, 0))
        assert res is not None
        assert len(res) == scenario.expected.edit_length
        expected_script = list(scenario.expected.edit_script)
        for i, command in enumerate(res):
            assert command == expected_script[i]
