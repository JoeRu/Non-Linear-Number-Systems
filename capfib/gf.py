"""Generating-function coefficients via the closed form of each factor.

    prod_k ( 1 + x^{F_k} + ... + x^{F_k * F_k} )
      = prod_k ( x^{F_k(F_k+1)} - 1 ) / ( x^{F_k} - 1 )

Each factor is applied as a multiplication by (1 - x^M) followed by a division
by (1 - x^f), both O(n_max). This is the production path; `capfib.dp` is the
independent implementation it is checked against.
"""

from capfib.fib import places_up_to


def coefficients(n_max: int, places: list[int] | None = None) -> list[int]:
    """Return exact R_c(0..n_max) as a list of Python ints."""
    if n_max < 0:
        return []
    if places is None:
        places = places_up_to(n_max)

    p = [0] * (n_max + 1)
    p[0] = 1
    for f in places:
        m = f * (f + 1)
        # multiply by (1 - x^m)
        q = [p[n] - (p[n - m] if n >= m else 0) for n in range(n_max + 1)]
        # divide by (1 - x^f)
        nxt = [0] * (n_max + 1)
        for n in range(n_max + 1):
            nxt[n] = q[n] + (nxt[n - f] if n >= f else 0)
        p = nxt
    return p
