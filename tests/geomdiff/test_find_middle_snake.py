# vim: foldlevel=0
import pytest

import thesis.geodiff.geodiff as geodiff

# TESTS for _find_middle_snake


MiddleSnakeScenario = tuple[
    str,
    tuple[
        geodiff.PointSequence, geodiff.PointSequence, tuple[int, int, int, int, int]
    ],
]
scenarios: list[MiddleSnakeScenario] = [
    ("nil -> nil", ([], [], (0, 0, 0, 0, 0))),
    ("nil -> a", ([], [(0, 0)], (1, 0, 1, 0, 1))),
    ("a -> nil", ([(0, 0)], [], (1, 1, 0, 1, 0))),
    ("a -> a", ([(0, 0)], [(0, 0)], (0, 0, 0, 1, 1))),
    ("a -> b", ([(0, 0)], [(1, 1)], (2, 1, 0, 1, 0))),
    ("nil -> ab", ([], [(0, 0), (1, 1)], (2, 0, 1, 0, 1))),
    ("nil -> abc", ([], [(0, 0), (1, 1), (2, 2)], (3, 0, 2, 0, 2))),
    ("ab -> nil", ([(0, 0), (1, 1)], [], (2, 1, 0, 1, 0))),
    ("abc -> nil", ([(0, 0), (1, 1), (2, 2)], [], (3, 2, 0, 2, 0))),
    (
        "abc -> abc",
        ([(0, 0), (1, 1), (2, 2)], [(0, 0), (1, 1), (2, 2)], (0, 0, 0, 3, 3)),
    ),
    (
        "abcd -> ebcd",
        (
            [(0, 0), (1, 1), (2, 2), (3, 3)],
            [(4, 4), (1, 1), (2, 2), (3, 3)],
            (2, 1, 0, 1, 0),
        ),
    ),
    (
        "abcd -> aecd",
        (
            [(0, 0), (1, 1), (2, 2), (3, 3)],
            [(0, 0), (4, 4), (2, 2), (3, 3)],
            (2, 2, 1, 2, 1),
        ),
    ),
    (
        "abcd -> aefd",
        (
            [(0, 0), (1, 1), (2, 2), (3, 3)],
            [(0, 0), (4, 4), (5, 5), (3, 3)],
            (4, 3, 1, 3, 1),
        ),
    ),
    (
        "abcd -> bc",
        ([(0, 0), (1, 1), (2, 2), (3, 3)], [(1, 1), (2, 2)], (2, 1, 0, 3, 2)),
    ),
    (
        "abcde -> bc",
        ([(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)], [(1, 1), (2, 2)], (3, 4, 2, 4, 2)),
    ),
]


def idfn(val: MiddleSnakeScenario):
    return val[0]


@pytest.mark.parametrize("scenario", scenarios, ids=idfn)
def test_find_middle_snake(scenario: MiddleSnakeScenario):
    data = scenario[1]
    a = data[0]
    b = data[1]
    want = data[2]
    N = len(a)
    M = len(b)
    got = geodiff._find_middle_snake(a, b, N, M)
    assert want == got
