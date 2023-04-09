from itertools import chain
from typing import Iterable, Literal, Sequence, Tuple

from shapely import LineString

EditCommand = (
    tuple[int, Literal["insert"], Tuple[float, float]] | tuple[int, Literal["delete"]]
)
Diff = Iterable[EditCommand]


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


def _find_middle_snake(
    a: Sequence, b: Sequence, N: int, M: int
) -> tuple[int, int, int, int, int]:
    max_D = (M + N + 1) // 2
    delta = N - M
    # row indexes for furthest reaching path in forward search
    vf = [-1] * (2 * max_D + 2)
    vf[1] = 0
    vb = vf[:]  # copy vf to initialize vector for reverse paths
    # By lemma 1 and 3 of [1] check for overlap only in forward direction
    # if delta is odd
    check_forward = delta % 2 != 0
    for D in range(0, max_D + 1):
        # Optimization: tighter bounds on diagonals that we search
        # A D-path will be off the bottom of the edit grid if k is lower
        # than kfstart, and off the right of the grid if k is higher than
        # kfend. Credit: Robert Elder
        kstart = -(D - 2 * max(0, D - M))
        kend = D - 2 * max(0, D - N)
        # Make a step in forward search path
        for kf in range(kstart, kend + 1, 2):
            # Find the end of the furthest reaching forward D-path in diagonal kf
            if kf == kstart or (kf != kend and vf[kf - 1] < vf[kf + 1]):
                xf = vf[kf + 1]
            else:
                xf = vf[kf - 1] + 1
            yf = xf - kf

            # Record snake start. Ref (u,v) in [1]
            u = xf
            v = yf
            while xf < N and yf < M and a[xf] == b[yf]:
                xf += 1
                yf += 1
            vf[kf] = xf
            # By Lemma 1 and 3 of [1], only need to check for overlap when extending
            # forwards if delta is odd.
            # Also, there needs to be an oposing path in the same diagonal. This is
            # true only if k ∈ [𝚫 - (D-1), 𝚫 + (D-1)]
            if check_forward and kf >= delta - (D - 1) and kf <= delta + (D - 1):
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
                    x = xf
                    y = yf
                    D_res = 2 * D - 1
                    return D_res, x, y, u, v
        # Do one step in backwards path
        for kb in range(kstart, kend + 1, 2):
            if kb == kstart or (kb != kend and vb[kb - 1] < vb[kb + 1]):
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

            if not check_forward and -D <= kb + delta <= D:
                kf = delta - kb
                xf = vf[kf]
                if xf >= N - xb:
                    # Overlap found
                    x = N - xb
                    y = M - yb
                    D_res = 2 * D
                    return D_res, x, y, u, v

    raise RuntimeError("Should not reach this code")


def _diff(a: Sequence, b: Sequence, cur_x: int, cur_y: int) -> Diff:
    """
    Calculate a diff between sequences 'a' and 'b'

    Another word for 'diff' is an edit script that transforms sequence _a_ to
    sequence _b_.

    Parameters
    ----------
    a, b : Sequence of Hashable type
        Sequences of hashable elements. Hashable because elements needs to
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
        return iter([])

    N = len(a)
    M = len(b)
    if N == 0:
        # Correct for 1-indexed edit graph
        index = cur_x - 1
        return iter((index, "insert", l) for l in b)

    if M == 0:
        return iter((i + cur_x, "delete") for i in range(0, N))

    D, x, y, u, v = _find_middle_snake(a, b, N, M)
    if D > 1 or (x != u and y != v):
        diff1 = _diff(
            a[:u],
            b[:v],
            cur_x,
            cur_y,
        )  # type : ignore
        diff2 = _diff(a[x:], b[y:], cur_x + x, cur_y + y)  # type : ignore
        return chain(diff1, diff2)
    elif M > N:
        return iter(((N - 1) + cur_x, "insert", l) for l in b[N:M])
    else:
        return iter((i + cur_x, "delete") for i in range(M, N))


def diff(a: LineString, b: LineString) -> Diff:
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
    return _diff(seq1, seq2, 0, 0)
