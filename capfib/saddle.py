"""Numerical Legendre transform of log F_c.

    log R_c(N) <= min_{s>0} [ s N + log F_c(e^-s) ]

The minimiser sits near s = 1/N, so the search bracket is centred on
log s = -log N. The bracket is checked after the search: a minimiser pinned to
an endpoint is a silent failure that returns a plausible but meaningless
number, and was observed during design.
"""

import math

from capfib.interval import log_F_c_interval, working_dps
from capfib.product import log_F_c
from mpmath import iv


def argmin_log_s(
    log_n: float, half: float = 40.0, iters: int = 100
) -> tuple[float, bool]:
    """Locate the minimising log s for the Chernoff bound, in floating point.

    T1 holds for every s > 0, so this search only affects how sharp the bound
    is, never whether it is valid. The certified path therefore treats a
    minimiser pinned to a bracket endpoint as a quality signal, while
    `log_R_bound` keeps treating it as an error.

    Args:
        log_n: log N.
        half: half-width of the search bracket around log s = -log N.
        iters: ternary-search iterations.

    Returns:
        A tuple (log_s, hit_boundary).
    """
    lo, hi = -log_n - half, -log_n + half

    def objective(log_s: float) -> float:
        return math.exp(log_s + log_n) + log_F_c(log_s)

    for _ in range(iters):
        m1 = lo + (hi - lo) / 3
        m2 = hi - (hi - lo) / 3
        if objective(m1) < objective(m2):
            hi = m2
        else:
            lo = m1

    log_s = (lo + hi) / 2
    hit_boundary = not (
        log_s + log_n + half > 1e-6 and -log_n + half - log_s > 1e-6
    )
    return log_s, hit_boundary


def log_R_bound(log_n: float, half: float = 40.0, iters: int = 100) -> float:
    """Return min_s [ s N + log F_c(e^-s) ], given log_n = log N.

    Floating point throughout, and therefore NOT certified; see
    `log_R_bound_certified`.

    Raises ValueError if the minimiser reaches a bracket endpoint.
    """
    log_s, hit_boundary = argmin_log_s(log_n, half, iters)
    if hit_boundary:
        raise ValueError(
            f"minimiser hit bracket boundary at log s = {log_s}; widen `half`"
        )
    return math.exp(log_s + log_n) + log_F_c(log_s)


def log_R_bound_at(n: int, **kwargs: float) -> float:
    """Convenience wrapper taking N directly. Only for N within float range."""
    return log_R_bound(math.log(n), **kwargs)


def log_R_bound_certified(n: int, half: float = 40.0, iters: int = 100) -> float:
    """Return a rigorous upper bound on log R_c(N).

    T1 (spec 4.1) states log R_c(N) <= s N + log F_c(e^-s) for every s > 0, so
    only the evaluation needs certifying, not the choice of s: the float search
    picks s, interval arithmetic bounds the value there, and the result is
    rounded upward.

    Args:
        n: the integer N, at least 2.
        half: half-width of the float search bracket.
        iters: ternary-search iterations.

    Returns:
        A float that is at least log R_c(N).

    Raises:
        ValueError: if n is less than 2.
    """
    if n < 2:
        raise ValueError(f"n must be at least 2, got {n}")
    log_s, _ = argmin_log_s(math.log(n), half, iters)
    t = -log_s
    _, hi, _ = log_F_c_interval(t)
    iv.dps = working_dps(t)
    total = iv.exp(iv.mpf(log_s)) * iv.mpf(n) + iv.mpf([hi, hi])
    return math.nextafter(float(total.b), math.inf)
