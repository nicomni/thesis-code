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
