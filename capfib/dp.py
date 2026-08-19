"""Naive digit-loop dynamic programming for R_c.

This is the first of two independent fast paths. It mirrors the definition
directly -- one loop over digits per place -- so that agreement with
`capfib.gf`, which uses a different algorithm, is meaningful evidence.
"""

from capfib.fib import places_up_to


def counts(n_max: int, places: list[int] | None = None) -> list[int]:
    """Return exact R_c(0..n_max) as a list of Python ints.

    With `places` None the full range F_k <= n_max is used, which is the
    definition of R_c. Passing an explicit `places` computes the counting
    function of that fixed-length system instead.
    """
    if n_max < 0:
        return []
    if places is None:
        places = places_up_to(n_max)

    arr = [0] * (n_max + 1)
    arr[0] = 1
    for f in places:
        nxt = [0] * (n_max + 1)
        for v, c in enumerate(arr):
            if not c:
                continue
            for d in range(f + 1):
                t = v + d * f
                if t > n_max:
                    break
                nxt[t] += c
        arr = nxt
    return arr
