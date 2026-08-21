"""Certified evaluation of log F_c(e^-s) by interval arithmetic.

`capfib.product` evaluates the same quantity in floating point and is NOT
certified: it truncates the infinite product, which *lowers* the value and so
breaks the direction of the Chernoff bound T1 (spec 5.1). This module returns a
rigorous enclosure instead, and is the oracle the float path is checked against.

    log F_c(e^-s) = sum_{k>=1} a_k(s),
    a_k(s) = log(1 - e^{-s F_k (F_k+1)}) - log(1 - e^{-s F_k}),  all a_k >= 0.

Callers pass t = log(1/s), never s.
"""

import math

from mpmath import iv

TAIL_U_MIN = 40.0
"""Sum places exactly until s*F_k reaches this, then bound the remainder."""

SERIES_THRESHOLD_EXP = -12
"""Use the series enclosure only for z <= 1e-12; see _log1m_exp_neg."""

RELATIVE_TOL = 1e-12
"""Agreement tolerance for the spec 5.5 gate against the float path."""


def working_dps(t: float, guard: int = 40) -> int:
    """Return the decimal precision needed at t = log(1/s).

    The smallest argument is s = e^-t itself, so the working precision must
    exceed t in decimal digits or `1 - exp(-x)` cancels away entirely.

    Args:
        t: log(1/s), positive.
        guard: extra digits beyond the dynamic range.

    Returns:
        Decimal digits of precision, at least 30.
    """
    return max(30, math.ceil(t / math.log(10)) + guard)


def _log1m_exp_neg(z):
    """Enclose log(1 - exp(-z)) for an interval z with z.a > 0.

    For tiny z the alternating series 1 - e^-z = z - z^2/2! + z^3/3! - ... has
    strictly decreasing terms, so consecutive partial sums bracket it:

        z (1 - z/2)  <=  1 - e^-z  <=  z (1 - z/2 + z^2/6).

    Both sides are products, so no cancellation occurs. The bracket's own
    relative error is about z^2/6, which is why the threshold is 1e-12 and not
    1: at z = 1 that error is 0.17 and would dominate the whole result. Above
    the threshold, `working_dps` makes the direct computation exact enough.

    Args:
        z: an mpmath interval with positive lower endpoint.

    Returns:
        An mpmath interval enclosing log(1 - exp(-z)).
    """
    one = iv.mpf(1)
    if z.b <= iv.mpf(10) ** SERIES_THRESHOLD_EXP:
        lo = z * (one - z / 2)
        hi = z * (one - z / 2 + z * z / 6)
        return iv.mpf([iv.log(iv.mpf(lo.a)).a, iv.log(iv.mpf(hi.b)).b])
    return iv.log(one - iv.exp(-z))


def _tail_bound(u):
    """Bound sum_{k>K} a_k(s) above, given u = s*F_K with u.a >= 1 and K >= 3.

    Spec 5.2: for k > K >= 3, F_k >= (3/2)^{k-K} F_K, hence

        sum_{k>K} a_k(s) <= (1/0.632) e^-u e^{-u/2} / (1 - e^{-u/2}).

    Evaluated at the *lower* endpoint of u, which maximises the bound.

    Args:
        u: an mpmath interval for s*F_K, with lower endpoint at least 1.

    Returns:
        The upper endpoint of the bound, as an mpmath number.

    Raises:
        ValueError: if u.a < 1, since the geometric-decay precondition
            F_k >= (3/2)^(k-K) F_K underlying the bound is only established
            for u = s*F_K >= 1.
    """
    if u.a < 1:
        raise ValueError(f"_tail_bound requires u.a >= 1, got {float(u.a)}")
    ua = iv.mpf(u.a)
    numerator = iv.exp(-ua) * iv.exp(-ua / 2)
    denominator = iv.mpf(1) - iv.exp(-ua / 2)
    return (numerator / denominator / iv.mpf("0.632")).b


def log_F_c_interval(t: float, guard: int = 40) -> tuple[iv.mpf, iv.mpf, int]:
    """Return a certified enclosure of log F_c(e^-s) where s = e^-t.

    Args:
        t: log(1/s), must be positive.
        guard: extra decimal digits passed to `working_dps`.

    Returns:
        A tuple (lo, hi, terms): the enclosure's endpoints as mpmath numbers,
        and the number of places k = 1..terms summed exactly (the break index
        K = terms is included in the exact sum) before `_tail_bound` covers
        the remainder sum_{k>K} a_k(s).

    Raises:
        ValueError: if t is not positive.
    """
    if t <= 0:
        raise ValueError(f"t = log(1/s) must be positive, got {t}")
    iv.dps = working_dps(t, guard)
    s = iv.exp(iv.mpf(-t))
    total = iv.mpf(0)
    f_prev, f = 0, 1  # F_1 = 1
    k = 1
    while True:
        u = s * f
        total = total + (_log1m_exp_neg(u * (f + 1)) - _log1m_exp_neg(u))
        if k >= 3 and u.a >= TAIL_U_MIN:
            total = iv.mpf([total.a, total.b + _tail_bound(u)])
            break
        f_prev, f = f, (f_prev + f if k >= 2 else 1)  # F_2 = 1, then F_{k+1}
        k += 1
    return total.a, total.b, k


def certified_upper(t: float, guard: int = 40) -> float:
    """Return a certified upper bound on log F_c(e^-s), rounded upward.

    Args:
        t: log(1/s), must be positive.
        guard: extra decimal digits passed to `working_dps`.

    Returns:
        A float that is at least the true value; rounding is upward so the
        conversion cannot silently weaken the bound.
    """
    _, hi, _ = log_F_c_interval(t, guard)
    return math.nextafter(float(hi), math.inf)


def agrees_with_float(t: float, float_value: float, guard: int = 40) -> bool:
    """Return whether the float path agrees with the certified enclosure.

    This is the spec 5.5 gate. It is a relative tolerance on the midpoint, NOT
    containment: the certified interval is far tighter than double precision, so
    the float value falls outside it essentially always. Widening the certified
    interval until it contains the float value is the explicit anti-goal — it
    would make the gate pass while destroying the bound.

    Args:
        t: log(1/s), must be positive.
        float_value: the value returned by `capfib.product.log_F_c(-t)`.
        guard: extra decimal digits passed to `working_dps`.

    Returns:
        True if the two agree to within RELATIVE_TOL.
    """
    lo, hi, _ = log_F_c_interval(t, guard)
    midpoint = (iv.mpf(lo) + iv.mpf(hi)) / 2
    return abs(iv.mpf(float_value) - midpoint).b <= abs(midpoint).b * RELATIVE_TOL
