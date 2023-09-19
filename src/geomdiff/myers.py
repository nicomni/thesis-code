# vim: foldlevel=0
from itertools import chain
from typing import Literal, Sequence, TypeGuard

from shapely import LineString

# TODO: Write documentation for Myers method.

Point = tuple[float, float]
InsertCommand = tuple[int, Literal["insert"], Point]
DeleteCommand = tuple[int, Literal["delete"]]
ChangeCommand = tuple[int, Literal["change"], Point]
EditCommand = InsertCommand | DeleteCommand
PatchCommand = EditCommand | ChangeCommand
EditScript = Sequence[EditCommand]
Patch = Sequence[PatchCommand]
PointSequence = Sequence[Point]


def myers_length_of_shortest_edit_script(a, b):
    """Calculate the length of shortest edit script

    This is the original algorithm as described on page 6 of
    "An O(N) Difference Algorithm and Its Variations" by Eugene W. Myers
    Hei

    """
    N = len(a)
    M = len(b)
    MAX = N + M
    v = [0] * (2 * MAX + 2)
    for D in range(0, MAX + 1):
        # Find all D-paths, using breadth first search.
        # A D-path is a path in the edit graph that consists of exactly D
        # non-diagonal, i.e., vertical or horizontal, edges.
        # Return early when the (N,M) point in the edit graph is reached.
        for k in range(-D, D + 1, 2):
            # Find the end point of the furthest reaching D-path in diagonal k

            # If diagonal k is on the lower k-bound (-D) then there exists no
            # value for v[k-1]. Hence, we allow for this.
            # Also,
            # if k is on the upper bound there are no value for v[k+1]. We
            # guard against this, and the case where the furthest reaching
            # D-path in the diagonal above is shorter than the path form the
            # diagonal above.
            if k == -D or (k != D and v[k - 1] < v[k + 1]):
                # continue search path from the same x-index as
                # the furthest reaching path in diagonal above
                x = v[k + 1]
            else:
                # Otherwise k==D or the x index of the furthest reaching D-path
                # on the diagonal below is greater or equal to the furthest reaching
                # path on the diagonal above. The result is that we start from the furthest
                # reaching point below and follow a horizontal edge by increasing x.
                x = v[k - 1] + 1
            y = x - k
            # Follow the snake (if any) while not reaching the lower or rightmost bound
            while x < N and y < M and a[x] == b[y]:
                x, y = x + 1, y + 1
            # record the new row index of the furthest reaching path in diagonal k
            v[k] = x
            if x >= N and y >= M:
                return D
    raise RuntimeError("Should not reach this point")


# TODO: Complete docstring for D
def _find_middle_snake(
    a: PointSequence, b: PointSequence, N: int, M: int
) -> tuple[int, int, int, int, int]:
    """Find the middle snake

    In an edit graph, a _snake_ is a non-diagonal edge followed by a possibly
    empty sequence of diagonal edges.

    Returns
    -------
    D, x, y, u, v : int
        Such that the middle snakes starts at (x,y) and ends at (u,v)
        in the edit graph. D is ...


    """
    max_D = (M + N + 1) // 2
    delta = N - M
    # row indexes for furthest reaching path in forward search
    vf = [-1] * (2 * max_D + 2)
    vf[1] = 0
    vb = vf[:]  # copy vf to initialize vector for reverse paths
    # By lemma 1 and 3 of [1] check for overlap only in forward direction
    # if delta is odd
    check_forward = delta % 2 == 1
    for D in range(0, max_D + 1):
        # Optimization: tighter bounds on diagonals that we search
        # A D-path will be off the bottom of the edit grid if k is lower
        # than kfstart, and off the right of the grid if k is higher than
        # kfend. Credit: Robert Elder
        kstart = -(D - 2 * max(0, D - M))  # inclusive
        kend = D - 2 * max(0, D - N) + 1  # exclusive
        # Make a step in forward search path
        for kf in range(kstart, kend, 2):
            # Find the end of the furthest reaching forward D-path in diagonal kf
            if kf == -D or (kf != D and vf[kf - 1] < vf[kf + 1]):
                xf = vf[kf + 1]
            else:
                xf = vf[kf - 1] + 1
            yf = xf - kf

            # Record snake start. Ref (u,v) in [1]
            x = xf
            y = yf
            while xf < N and yf < M and a[xf] == b[yf]:
                xf += 1
                yf += 1
            vf[kf] = xf
            # By Lemma 1 and 3 of [1], only need to check for overlap when extending
            # forwards if delta is odd.
            # Also, there needs to be an oposing path in the same diagonal. This is
            # true only if k ∈ [𝚫 - (D-1), 𝚫 + (D-1)]
            if check_forward and delta - (D - 1) <= kf <= delta + (D - 1):
                # kb is the diagonal index of the diagonal in the backwards
                # edit graph. Thus, kf in the forwards direction signifies the
                # same diagonal as kb in the backwards direction. An overlap happens
                # in the same diagonal.
                kb = delta - kf
                # xb is the column in the forward direction at which the backwards
                # path has found an end point.
                xb = N - vb[kb]
                if xb <= xf:
                    # Overlap found
                    # Record snake end. Ref. (x,y) in [1]
                    u = xf
                    v = yf
                    D_res = 2 * D - 1
                    return D_res, x, y, u, v
        # Do one step in backwards path
        for kb in range(kstart, kend, 2):
            if kb == -D or (kb != D and vb[kb - 1] < vb[kb + 1]):
                xb = vb[kb + 1]
            else:
                xb = vb[kb - 1] + 1
            yb = xb - kb

            u = N - xb
            v = M - yb
            while xb < N and yb < M and a[(N - 1) - xb] == b[(M - 1) - yb]:
                xb += 1
                yb += 1
            vb[kb] = xb

            if not check_forward and -D <= kb - delta <= D:
                kf = delta - kb
                xf = vf[kf]
                if xf >= N - xb:
                    # Overlap found
                    x = N - xb
                    y = M - yb
                    D_res = 2 * D
                    return D_res, x, y, u, v

    raise RuntimeError("Should not reach this code")


def _shortest_edit_script(
    a: PointSequence, b: PointSequence, cur_x: int, cur_y: int
) -> EditScript:
    """
    Calculate a diff between sequences 'a' and 'b'

    Another word for 'diff' is an edit script that transforms sequence _a_ to
    sequence _b_.

    Parameters
    ----------
    a, b :PointSequence of Hashable type
       PointSequences of hashable elements. Hashable because elements needs to
        be comparable.
    cur_x, cur_y : int
        Current x and y indexes of original a and b sequences. Lets us
        use dynamic programming.

    Returns
    -------
    Diffs
        The return value is an iterable object of insert/delete edit commands.

    Notes
    -----
    Some notes referencing [1]_.

    References
    ----------
    .. [1] Myers. "An O(ND) Difference Algorithm and Its Variations"
    """
    # Type guard
    if a is None or b is None:
        raise TypeError("None input")

    # Check equality
    if a == b:
        return []

    N = len(a)
    M = len(b)
    if N == 0:
        index = cur_x - 1  # insert in front of current index
        return [(index, "insert", l) for l in b]

    if M == 0:
        return [(i + cur_x, "delete") for i in range(0, N)]

    D, x, y, u, v = _find_middle_snake(a, b, N, M)
    if D > 1 or (x != u and y != v):
        diff1 = _shortest_edit_script(
            a[:x],
            b[:y],
            cur_x,
            cur_y,
        )
        diff2 = _shortest_edit_script(a[u:], b[v:], cur_x + u, cur_y + v)
        res = list(chain(diff1, diff2))
        return res
    elif M > N:
        return [((N - 1) + cur_x, "insert", l) for l in b[N:M]]
    else:
        return [(i + cur_x, "delete") for i in range(M, N)]


def diff(a: LineString, b: LineString) -> Patch:
    """Calculate a diff between sequences 'a' and 'b'

    Another word for 'diff' is an edit script that transforms sequence _a_ to
    sequence _b_.

    Parameters
    ----------
    a, b : Sequence of Hashable type
        Sequences of hashable elements. Hashable because elements needs to
        be comparable.

    Returns
    -------
    Diff
        The return value is an iterable object of insert/delete edit commands.

    """
    if not isinstance(a, LineString) or not isinstance(b, LineString):
        raise TypeError("Input must be LineString")
    seq1 = list(a.coords)
    seq2 = list(b.coords)
    if not _is_point_sequence(seq1):
        raise TypeError(f"Unexpected type {type(seq1)}. Expected PointSequence")
    if not _is_point_sequence(seq2):
        raise TypeError(f"Unexpected type {type(seq2)}. Expected PointSequence")
    return _shortest_edit_script(seq1,seq2, 0,0)
    edit_script = _shortest_edit_script(seq1, seq2, 0, 0)
    patch = _clean_up_edit_script(edit_script, seq1)
    return patch


# Make type guard to determine if PatchCommand is InsertCommand
def _is_insert_command(cmd) -> TypeGuard[InsertCommand]:
    if isinstance(cmd, tuple) and len(cmd) == 3:
        op = cmd[1]
        return op == "insert"
    return False


def _is_delete_command(cmd) -> TypeGuard[DeleteCommand]:
    if isinstance(cmd, tuple) and len(cmd) == 2:
        op = cmd[1]
        return op == "delete"
    return False


def _is_change_command(cmd: PatchCommand) -> TypeGuard[ChangeCommand]:
    op = cmd[1]
    if op == "change":
        return True
    return False


def _is_point_type(val: object) -> TypeGuard[Point]:
    return (
        isinstance(val, tuple)
        and len(val) == 2
        and all(isinstance(x, float) for x in val)
    )


def _is_point_sequence(seq: list) -> TypeGuard[PointSequence]:
    return all(_is_point_type(x) for x in seq)


def _clean_up_edit_script(
    edit_script: EditScript, old_state: PointSequence 
) -> Patch:
    """Clean up edit script

    Merge consecutive insert/delete commands into a single change command.
    Example:
        a = [(1,1)]
        b = [(3,3)]
        The edit script becomes:
        [(0, 'delete'), (0, 'insert', (3,3))]
        We want to return:
        [(0, 'change', (2,2))]
    """
    # TODO: implement change ranges
    # commands: list[EditCommand] = []  # to remember commands
    patch = []  # store processed commands
    for _, cmd in enumerate(edit_script):
        if len(patch) == 0:
            if _is_valid_edit_command(cmd):
                patch.append(cmd)
                continue
            else:
                raise UnexpectedEditCommandTypeError(cmd[1])
        prev_cmd = patch[-1]
        if _is_insert_command(prev_cmd):
            if _is_insert_command(cmd):
                # TODO: Chain insert commands
                patch.append(cmd)
                continue
            if _is_delete_command(cmd):
                if cmd[0] == prev_cmd[0] + 1:
                    # Merge insert/delete into change command
                    old_val = old_state[cmd[0]]
                    new_val = prev_cmd[2]
                    change_val = (new_val[0] - old_val[0], new_val[1] - old_val[1])
                    # Add change command to result. Replace previous insert command
                    patch[-1] = (cmd[0], "change", change_val)
                    continue
                patch.append(cmd)
        elif _is_delete_command(prev_cmd):
            if _is_delete_command(cmd):
                # TODO: Chain delete commands
                patch.append(cmd)
                continue
            if _is_insert_command(cmd):
                if cmd[0] == prev_cmd[0]:
                    # Merge insert/delete into change command
                    old_val = old_state[cmd[0]]
                    new_val = cmd[2]
                    change_val = (new_val[0] - old_val[0], new_val[1] - old_val[1])
                    # Add change command to result. Replace previous delete command
                    patch[-1] = (cmd[0], "change", change_val)
                    continue
                patch.append(cmd)
        elif _is_change_command(prev_cmd):
            patch.append(cmd)
        else:
            raise UnexpectedEditCommandTypeError(cmd[1])
    return list(patch)


def _is_valid_edit_command(cmd) -> TypeGuard[EditCommand]:
    if isinstance(cmd, tuple) and 2 <= len(cmd) <= 3:
        return _is_insert_command(cmd) or _is_delete_command(cmd)
    return False


class UnexpectedEditCommandTypeError(Exception):
    _op: str

    def __init__(self, op: str):
        self._op = op
        super().__init__(op)

    def __str__(self):
        return f"Unexpected command type '{self._op}'. Expected 'insert' or 'delete'"
