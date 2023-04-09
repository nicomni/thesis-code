from collections.abc import Sequence
from typing import Dict, Hashable, NamedTuple

import pytest
from shapely import LineString, Point

from geomdiff.myers import Diff, diff, myers_length_of_shortest_edit_script


class Expected(NamedTuple):
    edit_length: int
    edit_script: Diff


class Scenario(NamedTuple):
    name: str
    id: int
    seq_1: Sequence[Hashable]
    seq_2: Sequence[Hashable]
    expected: Expected


def idfn(val):
    return val.name


class TestMyersStrings:
    def test_NoneInput_raisesTypeError(self):
        with pytest.raises(TypeError):
            diff(None, [])
        with pytest.raises(TypeError):
            diff([], None)
        with pytest.raises(TypeError):
            diff(None, None)

    scenarios = [
        (Scenario("2 empty strings", 1, "", "", Expected(0, []))),
        (
            Scenario(
                "single char and empty string", 2, "a", "", Expected(1, [(0, "delete")])
            )
        ),
        (
            Scenario(
                "empty string and single char",
                3,
                "",
                "a",
                Expected(1, [(-1, "insert", "a")]),
            )
        ),
        (Scenario("two equal chars", 4, "a", "a", Expected(0, []))),
        (
            Scenario(
                "2 different single chars",
                5,
                "a",
                "b",
                Expected(2, [(0, "delete"), (0, "insert", "b")]),
            )
        ),
        (
            Scenario(
                "remove first char 2-string", 6, "ab", "b", Expected(1, [(0, "delete")])
            )
        ),
        (
            Scenario(
                "remove last char 2-string", 7, "ab", "a", Expected(1, [(1, "delete")])
            )
        ),
        (
            Scenario(
                "add char in front 1-string",
                8,
                "b",
                "ab",
                Expected(1, [(-1, "insert", "a")]),
            )
        ),
        (
            Scenario(
                "add char at back 1-string",
                9,
                "a",
                "ab",
                Expected(1, [(0, "insert", "b")]),
            )
        ),
        (
            Scenario(
                "change last char",
                10,
                "ab",
                "ac",
                Expected(2, [(1, "delete"), (1, "insert", "c")]),
            )
        ),
        (
            Scenario(
                "example from article",
                11,
                "abcabba",
                "cbabac",
                Expected(
                    5,
                    [
                        (0, "delete"),
                        (0, "insert", "c"),
                        (2, "delete"),
                        (5, "delete"),
                        (6, "insert", "c"),
                    ],
                ),
            )
        ),
    ]

    @pytest.mark.parametrize(argnames="scenario", argvalues=scenarios, ids=idfn)
    def test_scenarios(self, scenario: Scenario):
        res = list(diff(scenario.seq_1, scenario.seq_2))
        assert res is not None
        assert len(res) == scenario.expected.edit_length
        for i, command in enumerate(res):
            assert command == scenario.expected.edit_script[i]
