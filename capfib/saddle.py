"""Numerical Legendre transform of log F_c.

    log R_c(N) <= min_{s>0} [ s N + log F_c(e^-s) ]

The minimiser sits near s = 1/N, so the search bracket is centred on
log s = -log N. The bracket is checked after the search: a minimiser pinned to
an endpoint is a silent failure that returns a plausible but meaningless
number, and was observed during design.
"""

import math

from capfib.product import log_F_c


def log_R_bound(log_n: float, half: float = 40.0, iters: int = 100) -> float:
    """Return min_s [ s N + log F_c(e^-s) ], given log_n = log N.

    Raises ValueError if the minimiser reaches a bracket endpoint.
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
    if not (log_s + log_n + half > 1e-6 and -log_n + half - log_s > 1e-6):
        raise ValueError(
            f"minimiser hit bracket boundary at log s = {log_s}; widen `half`"
        )
    return objective(log_s)


def log_R_bound_at(n: int, **kwargs: float) -> float:
    """Convenience wrapper taking N directly. Only for N within float range."""
    return log_R_bound(math.log(n), **kwargs)
