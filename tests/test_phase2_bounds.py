"""Tests for the certified Chernoff upper bound on log R_c(N)."""

import csv
import math
from pathlib import Path

import pytest

from capfib.lower import t3_lower_bound
from capfib.saddle import argmin_log_s, log_R_bound, log_R_bound_certified

DATA = Path(__file__).resolve().parents[1] / "data" / "phase1_data.csv"


def _exact():
    """Load the exact Phase 1 values, or skip if they have not been generated."""
    if not DATA.exists():
        pytest.skip("data/phase1_data.csv absent; run scripts/run_phase1.py")
    with DATA.open() as handle:
        return {int(r["N"]): float(r["log_R_c"]) for r in csv.DictReader(handle)}


@pytest.mark.parametrize("n", [100, 10_000, 1_000_000])
def test_certified_bound_holds_against_exact_values(n):
    """T1 must hold at every sampled N. Design-time slacks: 4.99, 9.20, 13.55."""
    exact = _exact()
    bound = log_R_bound_certified(n)
    assert bound >= exact[n], f"certified bound {bound} below exact {exact[n]} at N={n}"


def test_certified_bound_is_not_vacuous():
    """A bound of +inf would satisfy the inequality and prove nothing."""
    exact = _exact()
    bound = log_R_bound_certified(1_000_000)
    assert math.isfinite(bound)
    assert bound - exact[1_000_000] < 20.0


def test_certified_bound_is_at_least_the_float_bound():
    """Certification may only weaken the bound, never sharpen it."""
    n = 10_000
    assert log_R_bound_certified(n) >= log_R_bound(math.log(n)) - 1e-9


def test_argmin_reports_boundary_instead_of_raising():
    """The certified path treats a pinned minimiser as a quality signal."""
    log_s, hit = argmin_log_s(math.log(1000), half=1e-3)
    assert hit is True
    assert math.isfinite(log_s)


def test_log_R_bound_still_raises_on_boundary():
    """The pre-existing float entry point keeps its failure behaviour."""
    with pytest.raises(ValueError, match="bracket boundary"):
        log_R_bound(math.log(1000), half=1e-3)


def test_non_positive_n_is_rejected():
    with pytest.raises(ValueError, match="must be at least 2"):
        log_R_bound_certified(1)


@pytest.mark.parametrize(
    "n, expected_a, expected_places",
    [(1_000, 9, 7), (10_000, 11, 9), (1_000_000, 16, 14)],
)
def test_t3_block_split(n, expected_a, expected_places):
    """The two-block split, measured during design."""
    result = t3_lower_bound(n)
    assert result.fixup_block == expected_a
    assert result.counting_places == expected_places


@pytest.mark.parametrize("n", [1_000, 10_000, 100_000, 1_000_000])
def test_t3_never_exceeds_the_exact_value(n):
    """Spec 8.4. A lower bound above the true value would be a false theorem."""
    exact = _exact()
    assert t3_lower_bound(n).log_count <= exact[n]


def test_t3_respects_the_budget():
    """Every free tuple must have sum at most N, or completion can fail."""
    from capfib.fib import places_up_to

    n = 1_000_000
    result = t3_lower_bound(n)
    places = places_up_to(n)
    budget = sum(
        (n // (result.counting_places * places[k - 1])) * places[k - 1]
        for k in range(result.fixup_block + 1, result.top_place + 1)
    )
    assert budget <= n


def test_t3_digits_respect_their_caps():
    """m_k < F_k must hold automatically on the counting block (spec 4.3 step 2)."""
    from capfib.fib import places_up_to

    n = 1_000_000
    result = t3_lower_bound(n)
    places = places_up_to(n)
    for k in range(result.fixup_block + 1, result.top_place + 1):
        assert n // (result.counting_places * places[k - 1]) < places[k - 1]
