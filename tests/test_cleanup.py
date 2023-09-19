import pytest

import geomdiff.myers as geomdiff

CleanupScenario = tuple[
    str,
    tuple[
        geomdiff.PointSequence,
        geomdiff.PointSequence,
        geomdiff.EditScript,
        geomdiff.Patch,
    ],
]
testdata: list[CleanupScenario] = [
    ("nil -> nil", ([], [], [], [])),
    # 1-string
    ("nil -> a", ([], [(0, 0)], [(-1, "insert", (0, 0))], [(-1, "insert", (0, 0))])),
    ("a -> nil", ([(0, 0)], [], [(0, "delete")], [(0, "delete")])),
    ("a -> a", ([(0, 0)], [(0, 0)], [], [])),
    (
        "a -> b",
        (
            [(1, 1)],
            [(4, 4)],
            [(0, "delete"), (0, "insert", (4, 4))],
            [(0, "change", (3, 3))],
        ),
    ),
    # 2-string
    (
        "nil -> ab",
        (
            [],
            [(0, 0), (1, 1)],
            [(-1, "insert", (0, 0)), (-1, "insert", (1, 1))],
            [(-1, "insert", (0, 0)), (-1, "insert", (1, 1))],
        ),
    ),
    (
        "ab -> nil",
        (
            [(0, 0), (1, 1)],
            [],
            [(0, "delete"), (1, "delete")],
            [(0, "delete"), (1, "delete")],
        ),
    ),
    (
        "a -> ba",
        (
            [(0, 0)],
            [(3, 3), (0, 0)],
            [(-1, "insert", (3, 3))],
            [(-1, "insert", (3, 3))],
        ),
    ),
    (
        "a -> ab",
        ([(0, 0)], [(0, 0), (3, 3)], [(0, "insert", (3, 3))], [(0, "insert", (3, 3))]),
    ),
    (
        "a -> bc",
        (
            [(-1, -1)],
            [(3, 3), (4, 4)],
            [(-1, "insert", (3, 3)), (-1, "insert", (4, 4)), (0, "delete")],
            [(-1, "insert", (3, 3)), (0, "change", (5, 5))],
        ),
    ),
    ("ab -> ab", ([(0, 0), (1, 1)], [(0, 0), (1, 1)], [], [])),
    (
        "ab -> ac",
        (
            [(0, 0), (1, 1)],
            [(0, 0), (3, 3)],
            [(1, "delete"), (1, "insert", (3, 3))],
            [(1, "change", (2, 2))],
        ),
    ),
    (
        "ab -> cb",
        (
            [(0, 0), (1, 1)],
            [(3, 3), (1, 1)],
            [(0, "delete"), (0, "insert", (3, 3))],
            [(0, "change", (3, 3))],
        ),
    ),
    (
        "ab -> bc",
        (
            [(0, 0), (1, 1)],
            [(1, 1), (2, 2)],
            [(0, "delete"), (1, "insert", (2, 2))],
            [(0, "delete"), (1, "insert", (2, 2))],
        ),
    ),
    (
        "ab -> ca",
        (
            [(0, 0), (1, 1)],
            [(2, 2), (0, 0)],
            [(-1, "insert", (2, 2)), (1, "delete")],
            [(-1, "insert", (2, 2)), (1, "delete")],
        ),
    ),
    (
        "ab -> cd",
        (
            [(0, 0), (1, 1)],
            [(2, 2), (3, 3)],
            [
                (0, "delete"),
                (1, "delete"),
                (1, "insert", (2, 2)),
                (1, "insert", (3, 3)),
            ],
            [(0, "delete"), (1, "change", (1, 1)), (1, "insert", (3, 3))],
        ),
    ),
    (
        "abcabba -> cbabac",
        (
            [(0, 0), (1, 1), (2, 2), (0, 0), (1, 1), (1, 1), (0, 0)],
            [(2, 2), (1, 1), (0, 0), (1, 1), (0, 0), (2, 2)],
            [
                (0, "delete"),
                (0, "insert", (2, 2)),
                (2, "delete"),
                (5, "delete"),
                (6, "insert", (2, 2)),
            ],
            [
                (0, "change", (2, 2)),
                (2, "delete"),
                (5, "delete"),
                (6, "insert", (2, 2)),
            ],
        ),
    ),
]


def idfn(val: CleanupScenario):
    return val[0]


@pytest.mark.parametrize("scenario", testdata, ids=idfn)
def test_cleanup(scenario: CleanupScenario, request: pytest.FixtureRequest):
    data = scenario[1]
    a = data[0]
    # b = data[1]
    es = data[2]
    want = data[3]
    node = request.node
    _id = ""
    if type(node) == pytest.Function:
        _id = node.callspec.id
    got = geomdiff._clean_up_edit_script(es, a)
    assert want == got


def test_cleanup_raises_UnexpectedEditCommandTypeError():
    with pytest.raises(
        geomdiff.UnexpectedEditCommandTypeError,
        match="Unexpected command type 'foo'. Expected 'insert' or 'delete'",
    ):
        geomdiff._clean_up_edit_script([(0, "foo")], [(0, 0)])  # type: ignore
