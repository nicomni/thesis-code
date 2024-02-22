# vim: foldlevel=0

import pytest

from thesis.geodiff import geodiff
from thesis.geodiff.types import EditScript, PointSequence

# TODO: Use scenarios

TestId = str
Input = tuple[PointSequence, PointSequence]
Expected = EditScript

Scenario = tuple[TestId, Input, Expected]

Scenarios = list[Scenario]

scenarios: Scenarios = [
    ("nil -> nil", ([], []), []),
    ("nil -> a", ([], [(0, 0)]), [(-1, "insert", (0, 0))]),
    ("a -> nil", ([(0, 0)], []), [(0, "delete")]),
    ("a -> a", ([(0, 0)], [(0, 0)]), []),
    ("a -> b", ([(0, 0)], [(1, 1)]), [(0, "delete"), (0, "insert", (1, 1))]),
    (
        "nil -> ab",
        ([], [(0, 0), (1, 1)]),
        [(-1, "insert", (0, 0)), (-1, "insert", (1, 1))],
    ),
    ("ab -> nil", ([(0, 0), (1, 1)], []), [(0, "delete"), (1, "delete")]),
    ("b -> ab", ([(1, 1)], [(0, 0), (1, 1)]), [(-1, "insert", (0, 0))]),
    ("ab -> b", ([(1, 1), (2, 2)], [(2, 2)]), [(0, "delete")]),
    (
        "ab -> cb",
        ([(1, 1), (2, 2)], [(3, 3), (2, 2)]),
        [(0, "delete"), (0, "insert", (3, 3))],
    ),
    ("ab -> a", ([(1, 1), (2, 2)], [(1, 1)]), [(1, "delete")]),
    ("a -> ab", ([(1, 1)], [(1, 1), (2, 2)]), [(0, "insert", (2, 2))]),
    (
        "ab -> ac",
        ([(1, 1), (2, 2)], [(1, 1), (3, 3)]),
        [(1, "delete"), (1, "insert", (3, 3))],
    ),
    (
        "bc -> abc",
        ([(1, 1), (2, 2)], [(0, 0), (1, 1), (2, 2)]),
        [(-1, "insert", (0, 0))],
    ),
    ("abc -> bc", ([(0, 0), (1, 1), (2, 2)], [(1, 1), (2, 2)]), [(0, "delete")]),
    (
        "abc -> dbc",
        ([(0, 0), (1, 1), (2, 2)], [(3, 3), (1, 1), (2, 2)]),
        [(0, "delete"), (0, "insert", (3, 3))],
    ),
    ("abc -> ac", ([(0, 0), (1, 1), (2, 2)], [(0, 0), (2, 2)]), [(1, "delete")]),
    (
        "ac -> abc",
        ([(1, 1), (3, 3)], [(1, 1), (2, 2), (3, 3)]),
        [(0, "insert", (2, 2))],
    ),
    (
        "abc -> adc",
        ([(1, 1), (2, 2), (3, 3)], [(1, 1), (4, 4), (3, 3)]),
        [(1, "delete"), (1, "insert", (4, 4))],
    ),
    ("abc -> ab", ([(1, 1), (2, 2), (3, 3)], [(1, 1), (2, 2)]), [(2, "delete")]),
    (
        "ab -> abc",
        ([(1, 1), (2, 2)], [(1, 1), (2, 2), (3, 3)]),
        [(1, "insert", (3, 3))],
    ),
    (
        "abc -> abd",
        ([(1, 1), (2, 2), (3, 3)], [(1, 1), (2, 2), (4, 4)]),
        [(2, "delete"), (2, "insert", (4, 4))],
    ),
    (
        "ab -> c",
        ([(1, 1), (2, 2)], [(3, 3)]),
        [(0, "delete"), (0, "insert", (3, 3)), (1, "delete")],
    ),
    (
        "abcabba -> cbabac",
        (
            [(1, 1), (2, 2), (3, 3), (1, 1), (2, 2), (2, 2), (1, 1)],
            [(3, 3), (2, 2), (1, 1), (2, 2), (1, 1), (3, 3)],
        ),
        [
            (0, "delete"),
            (0, "insert", (3, 3)),
            (2, "delete"),
            (5, "delete"),
            (6, "insert", (3, 3)),
        ],
    ),
    (
        "abcd -> bc",
        ([(1, 1), (2, 2), (3, 3), (4, 4)], [(2, 2), (3, 3)]),
        [(0, "delete"), (3, "delete")],
    ),
    (
        "abcde -> fgcd",
        ([(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], [(6, 6), (7, 7), (3, 3), (4, 4)]),
        [
            (-1, "insert", (6, 6)),
            (-1, "insert", (7, 7)),
            (0, "delete"),
            (1, "delete"),
            (4, "delete"),
        ],
    ),
    (
        "abcd -> cefc",
        ([(1, 1), (2, 2), (3, 3), (4, 4)], [(2, 2), (8, 8), (9, 9), (3, 3)]),
        [(0, "delete"), (1, "insert", (8, 8)), (1, "insert", (9, 9)), (3, "delete")],
    ),
]


def idfn(val: Scenario):
    return val[0]


@pytest.mark.parametrize("scenario", scenarios, ids=idfn)
def test_shortest_edit_script(scenario: Scenario):
    a, b = scenario[1]
    want = scenario[2]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want
