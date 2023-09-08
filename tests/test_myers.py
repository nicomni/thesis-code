from typing import Literal, NamedTuple

import pytest
from numpy import who
from shapely import LineString, Point

from geomdiff.myers import Diff, _diff, _find_middle_snake, diff_clean

# TESTS for _find_middle_snake


def test_find_middle_snake_empty_to_empty():
    want = (0, 0, 0, 0, 0)
    got = _find_middle_snake([], [], 0, 0)
    assert got == want


def test_find_middle_snake_empty_to_point():
    want = (1, 0, 1, 0, 1)
    got = _find_middle_snake([], [(0, 0)], 0, 1)
    assert got == want


def test_find_middle_snake_point_to_empty():
    want = (1, 1, 0, 1, 0)
    got = _find_middle_snake([(0, 0)], [], 1, 0)
    assert got == want


def test_find_middle_snake_point_a_to_point_a():
    seq1 = [(0, 0)]
    seq2 = [(0, 0)]
    want = (0, 0, 0, 1, 1)
    got = _find_middle_snake(seq1, seq2, 1, 1)
    assert got == want


def test_find_middle_snake_point_a_to_point_b():
    seq1 = [(0, 0)]
    seq2 = [(1, 1)]
    want = (2, 1, 0, 1, 0)
    got = _find_middle_snake(seq1, seq2, 1, 1)
    assert got == want


def test_find_middle_snake_empty_to_linestring_even():
    seq1 = []
    seq2 = [(0, 0), (1, 1)]
    want = (2, 0, 1, 0, 1)
    got = _find_middle_snake(seq1, seq2, 0, 2)
    assert got == want


def test_find_middle_snake_empty_to_linestring_odd():
    seq1 = []
    seq2 = [(0, 0), (1, 1), (2, 2)]
    want = (3, 0, 2, 0, 2)
    got = _find_middle_snake(seq1, seq2, 0, 3)
    assert got == want


def test_find_middle_snake_linestring_to_empty_even():
    seq1 = [(0, 0), (1, 1)]
    seq2 = []
    want = (2, 1, 0, 1, 0)
    got = _find_middle_snake(seq1, seq2, 2, 0)
    assert got == want


def test_find_middle_snake_linestring_to_empty_odd():
    seq1 = [(0, 0), (1, 1), (2, 2)]
    seq2 = []
    want = (3, 2, 0, 2, 0)
    got = _find_middle_snake(seq1, seq2, 3, 0)
    assert got == want


def test_find_middle_snake_linestring_to_equal():
    seq1 = [(0, 0), (1, 1), (2, 2)]
    seq2 = [(0, 0), (1, 1), (2, 2)]
    want = (0, 0, 0, 3, 3)
    got = _find_middle_snake(seq1, seq2, 3, 3)
    assert got == want


def test_find_middle_snake_linestring_change_first():
    seq1 = [(0, 0), (1, 1), (2, 2), (3, 3)]
    seq2 = [(4, 4), (1, 1), (2, 2), (3, 3)]
    want = (2, 1, 0, 1, 0)
    got = _find_middle_snake(seq1, seq2, 4, 4)
    assert got == want


def test_find_middle_snake_linestring_change_second():
    seq1 = [(0, 0), (1, 1), (2, 2), (3, 3)]
    seq2 = [(0, 0), (4, 4), (2, 2), (3, 3)]
    want = (2, 2, 1, 2, 1)
    got = _find_middle_snake(seq1, seq2, 4, 4)
    assert got == want


def test_find_middle_snake_linestring_change_middle_two():
    seq1 = [(0, 0), (1, 1), (2, 2), (3, 3)]
    seq2 = [(0, 0), (4, 4), (5, 5), (3, 3)]
    want = (4, 1, 1, 3, 3)
    got = _find_middle_snake(seq1, seq2, 4, 4)


def test_find_middle_snake_delta_even():
    seq1 = ["a", "b", "c", "d"]
    seq2 = ["b", "c"]
    want = (2, 1, 0, 3, 2)
    got = _find_middle_snake(seq1, seq2, 4, 2)
    assert got == want


def test_find_middle_snake_delta_odd():
    seq1 = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
    seq2 = [(1, 1), (2, 2)]
    want = (3, 4, 2, 4, 2)
    got = _find_middle_snake(seq1, seq2, 5, 2)
    assert got == want


def test_diff_empty_to_empty():
    want = []
    got = _diff([], [], 0, 0)
    assert got == want


def test_diff_empty_to_point():
    p = (0, 0)
    want = [(-1, "insert", p)]
    got = _diff([], [p], 0, 0)
    assert got == want


def test_diff_point_to_empty():
    p = (0, 0)
    want = [(0, "delete")]
    got = _diff([p], [], 0, 0)
    assert got == want


def test_diff_point_to_equal():
    p = (0, 0)
    want = []
    got = _diff([p], [p], 0, 0)
    assert got == want


def test_diff_point_a_to_point_b():
    a = (0, 0)
    b = (1, 1)
    want = [(0, "delete"), (0, "insert", b)]
    got = _diff([a], [b], 0, 0)
    assert got == want


def test_diff_empty_to_linestring():
    a = [(0, 0), (1, 1)]
    want = [(-1, "insert", (0, 0)), (-1, "insert", (1, 1))]
    got = _diff([], a, 0, 0)
    assert got == want


def test_diff_linestring_to_empty():
    a = [(0, 0), (1, 1)]
    want = [(0, "delete"), (1, "delete")]
    got = _diff(a, [], 0, 0)
    assert got == want


def test_diff_linestring_appendleft_2_string():
    a = [(1, 1)]
    b = [(0, 0), (1, 1)]
    want = [(-1, "insert", (0, 0))]
    got = _diff(a, b, 0, 0)
    assert got == want


def test_diff_linestring_popleft_2_string():
    a = [(1, 1), (2, 2)]
    b = [(2, 2)]
    want = [(0, "delete")]
    got = _diff(a, b, 0, 0)
    assert got == want


def test_diff_linestring_popnpushleft_2_string():  # change first
    a = [(1, 1), (2, 2)]
    b = [(3, 3), (2, 2)]
    want = [(0, "delete"), (0, "insert", (3, 3))]
    got = _diff(a, b, 0, 0)
    assert got == want


def test_diff_linestring_pop_2_string():
    a = [(1, 1), (2, 2)]
    b = [(1, 1)]
    want = [(1, "delete")]
    got = _diff(a, b, 0, 0)
    assert got == want


def test_diff_linestring_push_2_string():
    a = [(1, 1)]
    b = [(1, 1), (2, 2)]
    want = [(0, "insert", (2, 2))]
    got = _diff(a, b, 0, 0)
    assert got == want


def test_diff_linestring_poppush_2_string():
    a = [(1, 1), (2, 2)]
    b = [(1, 1), (3, 3)]
    want = [(1, "delete"), (1, "insert", (3, 3))]
    got = _diff(a, b, 0, 0)
    assert got == want


def test_diff_linestring_pushleft_3_string():
    a = [(1, 1), (2, 2)]
    b = [(0, 0), (1, 1), (2, 2)]
    want = [(-1, "insert", (0, 0))]
    got = _diff(a, b, 0, 0)
    assert got == want


def test_diff_linestring_popleft_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(2, 2), (3, 3)]
    want = [(0, "delete")]
    got = _diff(a, b, 0, 0)
    assert got == want


def test_diff_linestring_popnpushleft_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(4, 4), (2, 2), (3, 3)]
    want = [(0, "delete"), (0, "insert", (4, 4))]
    got = _diff(a, b, 0, 0)
    assert got == want


def test_diff_linestring_popmiddle_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(1, 1), (3, 3)]
    want = [(1, "delete")]
    got = _diff(a, b, 0, 0)
    assert got == want


def test_diff_linestring_pushmiddle_3_string():
    a = [(1, 1), (3, 3)]
    b = [(1, 1), (2, 2), (3, 3)]
    want = [(0, "insert", (2, 2))]
    got = _diff(a, b, 0, 0)
    assert got == want


def test_diff_linestring_popnpushmiddle_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(1, 1), (4, 4), (3, 3)]
    want = [(1, "delete"), (1, "insert", (4, 4))]
    got = _diff(a, b, 0, 0)
    assert got == want


def test_diff_linestring_pop_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(1, 1), (2, 2)]
    want = [(2, "delete")]
    got = _diff(a, b, 0, 0)
    assert got == want


def test_diff_linestring_push_3_string():
    a = [(1, 1), (2, 2)]
    b = [(1, 1), (2, 2), (3, 3)]
    want = [(1, "insert", (3, 3))]
    got = _diff(a, b, 0, 0)
    assert got == want


def test_diff_linestring_popnpush_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(1, 1), (2, 2), (4, 4)]
    want = [(2, "delete"), (2, "insert", (4, 4))]
    got = _diff(a, b, 0, 0)
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
    got = _diff(a, b, 0, 0)
    assert got == want


def test_diff_linestring_example1():
    a = [(1, 1), (2, 2), (3, 3), (4, 4)]
    b = [(2, 2), (3, 3)]
    want = [(0, "delete"), (3, "delete")]
    got = _diff(a, b, 0, 0)
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
    got = _diff(a, b, 0, 0)
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
    got = _diff(a, b, 0, 0)
    assert got == want


