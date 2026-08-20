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
