import math

import pytest

from capfib.gf import coefficients
from capfib.product import log_F_c


@pytest.mark.parametrize("s", [0.9, 0.7, 0.5, 0.3, 0.2])
def test_product_matches_exact_series(s):
    """log F_c(e^-s) == log sum_n R_c(n) e^{-sn}, to machine precision.

    Truncation at n=600 is harmless: R_c grows subexponentially, so the tail
    is suppressed by e^{-600 s}.
    """
    counts = coefficients(600)
    series = math.log(sum(c * math.exp(-s * n) for n, c in enumerate(counts)))
    assert log_F_c(math.log(s)) == pytest.approx(series, abs=1e-10)


def test_survives_extreme_log_s():
    """s = e^-2000 underflows to 0.0 as a float; log space must still work."""
    v = log_F_c(-2000.0)
    assert math.isfinite(v)
    assert v > 0


def test_monotone_decreasing_in_s():
    ss = (0.1, 0.2, 0.3, 0.4, 0.5)
    values = [log_F_c(math.log(s)) for s in ss]
    assert values == sorted(values, reverse=True)
