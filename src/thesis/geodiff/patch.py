from collections import deque
from typing import Deque

from thesis.geodiff.types import (LSPatch, PointSequence, Vector2D,
                                  is_change_command, is_delete_command,
                                  is_insert_command)


def apply_patch(patch: LSPatch, points: PointSequence) -> PointSequence:
    """Add a patch to a point sequence
    Parameters
    ----------
    point_sequence : PointSequence
        Sequence of points
    patch : Patch
        Sequence of patch commands
    Returns
    -------
    PointSequence
        The sequence of points after applying the patch
    """
    N = len(points)
    idxMap: dict[int, int] = {}
    result: Deque[Vector2D] = deque(points)
    # Reverse the patch
    for _, cmd in enumerate(reversed(patch)):
        i = cmd[0]
        if is_insert_command(cmd):
            # Insert cmd to result, after index i:
            result.insert(i + 1, cmd[2])
        if is_delete_command(cmd):
            del result[i]
        if is_change_command(cmd):
            # Change cmd to result at index i:
            diff = cmd[2]
            result[i] = add_difference(result[i], diff)
    return list(result)


def add_difference(point: Vector2D, diff: Vector2D) -> Vector2D:
    """Add a difference to a point
    Parameters
    ----------
    point : Point
        A point
    diff : Point
        A difference
    Returns
    -------
    Point
        The point after adding the difference
    """
    return (point[0] + diff[0], point[1] + diff[1])
