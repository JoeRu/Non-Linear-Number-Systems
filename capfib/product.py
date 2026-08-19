"""Evaluation of log F_c(e^-s) in pure log space.

    log F_c(e^-s) = sum_k [ log(1 - e^{-s F_k (F_k+1)}) - log(1 - e^{-s F_k}) ]

The caller passes log(s), not s. At the scales the Phase 0.5 gate reaches,
s underflows to 0.0, F_k outgrows float conversion, and exp(z) overflows.
Working from log(s) with log(F_k) tracked by its own recurrence avoids all
three.
"""

import math


def _log1m_exp_log(lz: float) -> float:
    """Return log(1 - exp(-z)) given lz = log z, for z > 0."""
    if lz < -30.0:
        # z < 1e-13: log(1 - e^-z) = log z - z/2 + O(z^2)
        return lz - math.exp(lz) / 2.0
    if lz > 6.0:
        # z > 400: 1 - e^-z is 1.0 in double precision
        return 0.0
    if lz > 3.6:
        return -math.exp(-math.exp(lz))
    return math.log(-math.expm1(-math.exp(lz)))


def log_F_c(log_s: float, cutoff_log: float = 3.9) -> float:
    """Return log F_c(e^-s) where log_s = log s.

    Terms with s * F_k > e^{cutoff_log} ~ 49 are negligible and end the sum.
    """
    total = 0.0
    log_prev: float | None = None
    log_f = 0.0  # k = 1, log F_1 = log 1 = 0
    while True:
        lz = log_s + log_f  # log(s F_k)
        if lz > cutoff_log:
            break
        log_f_plus_1 = log_f + math.log1p(math.exp(-log_f))  # log(F_k + 1)
        total += _log1m_exp_log(log_s + log_f + log_f_plus_1) - _log1m_exp_log(lz)
        if log_prev is None:
            log_prev, log_f = 0.0, 0.0  # k = 2, F_2 = 1 -- the duplicated place
        else:
            log_prev, log_f = log_f, log_f + math.log1p(math.exp(log_prev - log_f))
    return total
