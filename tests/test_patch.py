import pytest

from thesis.geodiff.patch import apply_patch
from thesis.geodiff.types import LSPatch, PointSequence

Scenario = tuple[
    str, tuple[PointSequence, LSPatch, PointSequence]
]  # (id, (point_sequence, patch, expected_result))
testdata: list[Scenario] = [
    ("nil -> nil", ([], [], [])),
    ("nil -> a", ([], [(-1, "insert", (1, 1))], [(1, 1)])),
    (
        "nil -> ab",
        ([], [(-1, "insert", (1, 1)), (0, "insert", (2, 2))], [(1, 1), (2, 2)]),
    ),
    ("a -> ab", ([(1, 1)], [(0, "insert", (2, 2))], [(1, 1), (2, 2)])),
    ("b -> ab", ([(2, 2)], [(-1, "insert", (1, 1))], [(1, 1), (2, 2)])),
    (
        "ac -> abc",
        ([(1, 1), (3, 3)], [(0, "insert", (2, 2))], [(1, 1), (2, 2), (3, 3)]),
    ),
    ("a -> nil", ([(1, 1)], [(0, "delete")], [])),
    ("ab -> nil", ([(1, 1), (2, 2)], [(0, "delete"), (1, "delete")], [])),
    ("abc -> ac", ([(1, 1), (2, 2), (3, 3)], [(1, "delete")], [(1, 1), (3, 3)])),
    ("a -> b", ([(1, 1)], [(0, "change", (1, 1))], [(2, 2)])),
    (
        "abc -> adc",
        ([(1, 1), (2, 2), (3, 3)], [(1, "change", (2, 2))], [(1, 1), (4, 4), (3, 3)]),
    ),
    ("ab -> ac", ([(1, 1), (2, 2)], [(1, "change", (1, 1))], [(1, 1), (3, 3)])),
    (
        "ab -> cd",
        (
            [(1, 1), (2, 2)],
            [(0, "delete"), (1, "change", (1, 1)), (1, "insert", (4, 4))],
            [(3, 3), (4, 4)],
        ),
    ),
]


def idfn(val: Scenario):
    return val[0]


@pytest.mark.parametrize("scenario", testdata, ids=idfn)
def test_applyPatch(scenario, request):
    points, patch, want = scenario[1]
    got = apply_patch(patch, points)
    assert want == got
