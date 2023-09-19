# vim: foldlevel=0
import pytest

import geomdiff.geomdiff as geomdiff

# TESTS for _find_middle_snake


MiddleSnakeScenario = tuple[
    str,
    tuple[
        geomdiff.PointSequence, geomdiff.PointSequence, tuple[int, int, int, int, int]
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
    got = geomdiff._find_middle_snake(a, b, N, M)
    assert want == got


# TODO: Use scenarios


def test_diff_empty_to_empty():
    want = []
    got = geomdiff._shortest_edit_script([], [], 0, 0)
    assert got == want


def test_diff_empty_to_point():
    p = (0, 0)
    want = [(-1, "insert", p)]
    got = geomdiff._shortest_edit_script([], [p], 0, 0)
    assert got == want


def test_diff_point_to_empty():
    p = (0, 0)
    want = [(0, "delete")]
    got = geomdiff._shortest_edit_script([p], [], 0, 0)
    assert got == want


def test_diff_point_to_equal():
    p = (0, 0)
    want = []
    got = geomdiff._shortest_edit_script([p], [p], 0, 0)
    assert got == want


def test_diff_point_a_to_point_b():
    a = (0, 0)
    b = (1, 1)
    want = [(0, "delete"), (0, "insert", b)]
    got = geomdiff._shortest_edit_script([a], [b], 0, 0)
    assert got == want


def test_diff_empty_to_linestring():
    a = [(0, 0), (1, 1)]
    want = [(-1, "insert", (0, 0)), (-1, "insert", (1, 1))]
    got = geomdiff._shortest_edit_script([], a, 0, 0)
    assert got == want


def test_diff_linestring_to_empty():
    a = [(0, 0), (1, 1)]
    want = [(0, "delete"), (1, "delete")]
    got = geomdiff._shortest_edit_script(a, [], 0, 0)
    assert got == want


def test_diff_linestring_appendleft_2_string():
    a = [(1, 1)]
    b = [(0, 0), (1, 1)]
    want = [(-1, "insert", (0, 0))]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_popleft_2_string():
    a = [(1, 1), (2, 2)]
    b = [(2, 2)]
    want = [(0, "delete")]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_popnpushleft_2_string():  # change first
    a = [(1, 1), (2, 2)]
    b = [(3, 3), (2, 2)]
    want = [(0, "delete"), (0, "insert", (3, 3))]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_pop_2_string():
    a = [(1, 1), (2, 2)]
    b = [(1, 1)]
    want = [(1, "delete")]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_push_2_string():
    a = [(1, 1)]
    b = [(1, 1), (2, 2)]
    want = [(0, "insert", (2, 2))]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_poppush_2_string():
    a = [(1, 1), (2, 2)]
    b = [(1, 1), (3, 3)]
    want = [(1, "delete"), (1, "insert", (3, 3))]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_pushleft_3_string():
    a = [(1, 1), (2, 2)]
    b = [(0, 0), (1, 1), (2, 2)]
    want = [(-1, "insert", (0, 0))]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_popleft_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(2, 2), (3, 3)]
    want = [(0, "delete")]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_popnpushleft_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(4, 4), (2, 2), (3, 3)]
    want = [(0, "delete"), (0, "insert", (4, 4))]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_popmiddle_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(1, 1), (3, 3)]
    want = [(1, "delete")]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_pushmiddle_3_string():
    a = [(1, 1), (3, 3)]
    b = [(1, 1), (2, 2), (3, 3)]
    want = [(0, "insert", (2, 2))]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_popnpushmiddle_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(1, 1), (4, 4), (3, 3)]
    want = [(1, "delete"), (1, "insert", (4, 4))]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_pop_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(1, 1), (2, 2)]
    want = [(2, "delete")]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_push_3_string():
    a = [(1, 1), (2, 2)]
    b = [(1, 1), (2, 2), (3, 3)]
    want = [(1, "insert", (3, 3))]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_popnpush_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(1, 1), (2, 2), (4, 4)]
    want = [(2, "delete"), (2, "insert", (4, 4))]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_popnchange_2_string():
    a = [(1, 1), (2, 2)]
    b = [(3, 3)]
    want = [(0, "delete"), (0, "insert", (3, 3)), (1, "delete")]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_example_from_article():
    # abcabba -> cbabac
    a = [(1, 1), (2, 2), (3, 3), (1, 1), (2, 2), (2, 2), (1, 1)]
    b = [(3, 3), (2, 2), (1, 1), (2, 2), (1, 1), (3, 3)]
    want = [
        (0, "delete"),
        (0, "insert", (3, 3)),
        (2, "delete"),
        (5, "delete"),
        (6, "insert", (3, 3)),
    ]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_example1():
    a = [(1, 1), (2, 2), (3, 3), (4, 4)]
    b = [(2, 2), (3, 3)]
    want = [(0, "delete"), (3, "delete")]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_example2():
    a = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
    b = [(8, 8), (9, 9), (3, 3), (4, 4)]
    want = [
        (-1, "insert", (8, 8)),
        (-1, "insert", (9, 9)),
        (0, "delete"),
        (1, "delete"),
        (4, "delete"),
    ]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_diff_linestring_example3():
    a = [(1, 1), (2, 2), (3, 3), (4, 4)]
    b = [(2, 2), (8, 8), (9, 9), (3, 3)]
    want = [
        (0, "delete"),
        (1, "insert", (8, 8)),
        (1, "insert", (9, 9)),
        (3, "delete"),
    ]
    got = geomdiff._shortest_edit_script(a, b, 0, 0)
    assert got == want
