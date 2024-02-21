# vim: foldlevel=0

from thesis.geodiff import geodiff

# TODO: Use scenarios


def test_ses_empty_to_empty():
    want = []
    got = geodiff._shortest_edit_script([], [], 0, 0)
    assert got == want


def test_ses_empty_to_point():
    p = (0, 0)
    want = [(-1, "insert", p)]
    got = geodiff._shortest_edit_script([], [p], 0, 0)
    assert got == want


def test_ses_point_to_empty():
    p = (0, 0)
    want = [(0, "delete")]
    got = geodiff._shortest_edit_script([p], [], 0, 0)
    assert got == want


def test_ses_point_to_equal():
    p = (0, 0)
    want = []
    got = geodiff._shortest_edit_script([p], [p], 0, 0)
    assert got == want


def test_ses_point_a_to_point_b():
    a = (0, 0)
    b = (1, 1)
    want = [(0, "delete"), (0, "insert", b)]
    got = geodiff._shortest_edit_script([a], [b], 0, 0)
    assert got == want


def test_ses_empty_to_linestring():
    a = [(0, 0), (1, 1)]
    want = [(-1, "insert", (0, 0)), (-1, "insert", (1, 1))]
    got = geodiff._shortest_edit_script([], a, 0, 0)
    assert got == want


def test_ses_linestring_to_empty():
    a = [(0, 0), (1, 1)]
    want = [(0, "delete"), (1, "delete")]
    got = geodiff._shortest_edit_script(a, [], 0, 0)
    assert got == want


def test_ses_linestring_appendleft_2_string():
    a = [(1, 1)]
    b = [(0, 0), (1, 1)]
    want = [(-1, "insert", (0, 0))]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_popleft_2_string():
    a = [(1, 1), (2, 2)]
    b = [(2, 2)]
    want = [(0, "delete")]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_popnpushleft_2_string():  # change first
    a = [(1, 1), (2, 2)]
    b = [(3, 3), (2, 2)]
    want = [(0, "delete"), (0, "insert", (3, 3))]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_pop_2_string():
    a = [(1, 1), (2, 2)]
    b = [(1, 1)]
    want = [(1, "delete")]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_push_2_string():
    a = [(1, 1)]
    b = [(1, 1), (2, 2)]
    want = [(0, "insert", (2, 2))]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_poppush_2_string():
    a = [(1, 1), (2, 2)]
    b = [(1, 1), (3, 3)]
    want = [(1, "delete"), (1, "insert", (3, 3))]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_pushleft_3_string():
    a = [(1, 1), (2, 2)]
    b = [(0, 0), (1, 1), (2, 2)]
    want = [(-1, "insert", (0, 0))]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_popleft_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(2, 2), (3, 3)]
    want = [(0, "delete")]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_popnpushleft_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(4, 4), (2, 2), (3, 3)]
    want = [(0, "delete"), (0, "insert", (4, 4))]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_popmiddle_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(1, 1), (3, 3)]
    want = [(1, "delete")]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_pushmiddle_3_string():
    a = [(1, 1), (3, 3)]
    b = [(1, 1), (2, 2), (3, 3)]
    want = [(0, "insert", (2, 2))]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_popnpushmiddle_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(1, 1), (4, 4), (3, 3)]
    want = [(1, "delete"), (1, "insert", (4, 4))]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_pop_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(1, 1), (2, 2)]
    want = [(2, "delete")]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_push_3_string():
    a = [(1, 1), (2, 2)]
    b = [(1, 1), (2, 2), (3, 3)]
    want = [(1, "insert", (3, 3))]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_popnpush_3_string():
    a = [(1, 1), (2, 2), (3, 3)]
    b = [(1, 1), (2, 2), (4, 4)]
    want = [(2, "delete"), (2, "insert", (4, 4))]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_popnchange_2_string():
    a = [(1, 1), (2, 2)]
    b = [(3, 3)]
    want = [(0, "delete"), (0, "insert", (3, 3)), (1, "delete")]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_example_from_article():
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
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_example1():
    a = [(1, 1), (2, 2), (3, 3), (4, 4)]
    b = [(2, 2), (3, 3)]
    want = [(0, "delete"), (3, "delete")]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_example2():
    a = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
    b = [(8, 8), (9, 9), (3, 3), (4, 4)]
    want = [
        (-1, "insert", (8, 8)),
        (-1, "insert", (9, 9)),
        (0, "delete"),
        (1, "delete"),
        (4, "delete"),
    ]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want


def test_ses_linestring_example3():
    a = [(1, 1), (2, 2), (3, 3), (4, 4)]
    b = [(2, 2), (8, 8), (9, 9), (3, 3)]
    want = [
        (0, "delete"),
        (1, "insert", (8, 8)),
        (1, "insert", (9, 9)),
        (3, "delete"),
    ]
    got = geodiff._shortest_edit_script(a, b, 0, 0)
    assert got == want
