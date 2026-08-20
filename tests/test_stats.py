from capfib.gf import coefficients
from capfib.stats import monotonicity_census, summatory


def test_census_partitions_steps():
    """The three counts must exhaust the steps -- no step is uncounted."""
    for n_max in (5, 50, 500):
        c = coefficients(n_max)
        cen = monotonicity_census(c)
        assert cen["increasing"] + cen["flat"] + cen["decreasing"] == cen["steps"]
        assert cen["steps"] == n_max


def test_census_hand_checked_to_20():
    """R_c(0..20) is hand-verified in tests/test_brute.py. No step decreases yet."""
    assert monotonicity_census(coefficients(20)) == {
        "increasing": 15, "flat": 5, "decreasing": 0, "steps": 20,
    }


def test_census_finds_decreases_by_100():
    """The first decrease is at N=41, so a range to 100 must show some."""
    assert monotonicity_census(coefficients(100)) == {
        "increasing": 78, "flat": 11, "decreasing": 11, "steps": 100,
    }


def test_census_empty_and_single():
    assert monotonicity_census([1]) == {
        "increasing": 0, "flat": 0, "decreasing": 0, "steps": 0,
    }


def test_summatory_hand_checked():
    assert summatory(coefficients(20)) == [
        1, 3, 5, 8, 12, 17, 23, 29, 37, 47, 58, 71, 84, 99, 117, 135, 156,
        179, 204, 233, 262,
    ]


def test_summatory_is_exact_ints_and_monotone():
    s = summatory(coefficients(500))
    assert all(type(x) is int for x in s)
    assert s == sorted(s)  # non-decreasing, since R_c >= 0


def test_summatory_last_is_total():
    c = coefficients(200)
    assert summatory(c)[-1] == sum(c)


import math

import pytest

from capfib.stats import local_ratios, place_jumps


def test_local_ratios_length_and_indices():
    c = coefficients(50)
    r = local_ratios(c)
    assert len(r) == len(c) - 1 == 50
    assert r[0] == pytest.approx(c[1] / c[0])
    assert r[-1] == pytest.approx(c[50] / c[49])


def test_local_ratios_all_finite():
    """Guarded by min(counts) >= 1, asserted at runtime -- not by appealing to
    completeness, which is still a `sorry` in Lean."""
    r = local_ratios(coefficients(2000))
    assert all(math.isfinite(x) for x in r)


def test_local_ratios_rejects_zero_count():
    with pytest.raises(AssertionError):
        local_ratios([1, 0, 1])


def test_place_jumps_skips_F_equals_one_and_dedupes():
    """F_1 = F_2 = 1 is one distinct place, and F = 1 has no F-1 in range."""
    jumps = place_jumps(coefficients(20))
    assert [j["place"] for j in jumps] == [2, 3, 5, 8, 13]


def test_place_jumps_exact_values():
    c = coefficients(20)
    jumps = {j["place"]: j["ratio"] for j in place_jumps(c)}
    assert jumps[2] == pytest.approx(2 / 2)      # exactly 1.0 -- NOT > 1
    assert jumps[3] == pytest.approx(3 / 2)
    assert jumps[5] == pytest.approx(5 / 4)
    assert jumps[8] == pytest.approx(8 / 6)
    assert jumps[13] == pytest.approx(15 / 13)


def test_place_jumps_not_monotone_below_13():
    """Pins the two known exceptions so nobody 'fixes' them into a false law."""
    ratios = {j["place"]: j["ratio"] for j in place_jumps(coefficients(100_000))}
    assert ratios[2] == pytest.approx(1.0)
    assert ratios[3] > ratios[2]   # rises
    assert ratios[5] < ratios[3]
    assert ratios[8] > ratios[5]   # rises again
    # monotone decay only from F = 13 onward
    tail = [r for f, r in sorted(ratios.items()) if f >= 13]
    assert tail == sorted(tail, reverse=True)
    assert all(r > 1.0 for r in tail)
