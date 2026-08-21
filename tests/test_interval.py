"""Tests for the certified enclosure of log F_c(e^-s).

The certified path is the oracle; capfib.product is the fast path being checked.
Note what is NOT tested: that the float value lies inside the certified interval.
The certified interval is far tighter than double precision (3.9e-40 wide at
t = 10, against a float deviation of 2.8e-14), so containment fails always, and
widening the interval to obtain it is the spec's explicit anti-goal (spec 5.5).
"""

import math

import pytest
from mpmath import iv

from capfib.interval import (
    RELATIVE_TOL,
    agrees_with_float,
    certified_upper,
    log_F_c_interval,
    working_dps,
    _tail_bound,
)
from capfib.product import log_F_c


@pytest.mark.parametrize("t", [5.0, 10.0, 13.82, 80.0])
def test_interval_is_finite_and_sharp(t):
    """The enclosure must be informative, not merely sound: [-inf, +inf] is sound."""
    lo, hi, terms = log_F_c_interval(t)
    assert math.isfinite(float(lo)) and math.isfinite(float(hi))
    assert float(lo) <= float(hi)
    width = float((iv.mpf(hi) - iv.mpf(lo)).b)
    assert width < 1e-20, f"interval too wide at t={t}: {width}"
    assert terms > 0


@pytest.mark.parametrize("t", [5.0, 10.0, 13.82, 80.0])
def test_float_path_agrees_to_relative_tolerance(t):
    """The spec 5.5 gate. Largest deviation observed during design was 3.9e-14."""
    assert agrees_with_float(t, log_F_c(-t))


def test_disagreement_is_detected():
    """A perturbed float value must fail the gate, or the gate tests nothing."""
    good = log_F_c(-10.0)
    assert agrees_with_float(10.0, good)
    assert not agrees_with_float(10.0, good * (1 + 1e-9))


def test_working_dps_scales_with_t():
    """Precision must exceed log(1/s) in decimal digits, or 1 - exp(-x) cancels.

    At t = 80 and dps = 30, 1 - exp(-e^-80) returns an interval whose lower
    endpoint is exactly 0, so its log is -inf (spec 5.3).
    """
    assert working_dps(10.0) >= 30
    assert working_dps(1280.0) > working_dps(80.0) > working_dps(10.0)
    assert working_dps(1280.0) >= 1280.0 / math.log(10)


def test_tail_bound_exceeds_the_true_tail():
    """Checked at a deliberately small u, where the true tail is not negligible.

    With the production TAIL_U_MIN = 40 the true tail underflows to 0, which
    would make this test vacuous.
    """
    from capfib.fib import fibonacci

    F = fibonacci(200)
    t = 5.0
    s = math.exp(-t)
    u_min = 1.5
    K = max(3, next(k for k in range(1, 200) if s * F[k - 1] >= u_min))
    true_tail = 0.0
    for k in range(K + 1, 200):
        z = s * F[k - 1]
        if z > 700:
            break
        true_tail += math.log((1 - math.exp(-z * (F[k - 1] + 1))) / (1 - math.exp(-z)))
    assert true_tail > 0, "test setup failed: pick a smaller u_min"
    iv.dps = working_dps(t)
    bound = float(_tail_bound(iv.mpf(s) * iv.mpf(F[K - 1])))
    assert bound >= true_tail


def test_certified_upper_is_an_upper_bound():
    lo, hi, _ = log_F_c_interval(10.0)
    assert certified_upper(10.0) >= float(hi)


def test_non_positive_t_is_rejected():
    with pytest.raises(ValueError, match="must be positive"):
        log_F_c_interval(0.0)
