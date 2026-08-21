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


def _block_counts(a):
    """Exact B(a, .) as a list indexed by m in [0, S_a], by DP over the places.

    The inner loop is a sliding window of F_k + 1 terms along each residue
    class mod F_k, which is what makes a = 12 (S_a = 33552) cheap enough for
    the suite.
    """
    from capfib.fib import fibonacci

    F = fibonacci(a)
    current = [1]
    for k in range(1, a + 1):
        f = F[k - 1]
        previous_top = len(current) - 1
        top = previous_top + f * f
        nxt = [0] * (top + 1)
        for r in range(f):
            window, running, m = [], 0, r
            while m <= top:
                value = current[m] if m <= previous_top else 0
                window.append(value)
                running += value
                if len(window) > f + 1:
                    running -= window.pop(0)
                nxt[m] = running
                m += f
        current = nxt
    return current


@pytest.mark.parametrize("a", [8, 9, 10, 11, 12])
def test_flatness_bound_holds_against_exact_block_counts(a):
    """8.2. The proved product bound must not exceed the true band minimum."""
    from capfib.lower import THETA_HI, THETA_LO, flatness_log_bound

    counts = _block_counts(a)
    capacity = len(counts) - 1
    lo = math.ceil(THETA_LO * capacity)
    hi = math.floor(THETA_HI * capacity)
    band_min = min(counts[lo : hi + 1])
    assert band_min > 0
    assert flatness_log_bound(a) <= math.log(band_min) + 1e-9


@pytest.mark.parametrize("a", range(2, 14))
def test_flatness_choice_count_is_at_least_rho_fib(a):
    """8.2, cases 1-4: the number of admissible top digits, checked exhaustively.

    This is the step the whole of T5 rests on, so it is checked at every m in
    the band rather than at sampled ones.
    """
    from capfib.fib import fibonacci
    from capfib.lower import RHO, THETA_HI, THETA_LO

    F = fibonacci(a + 1)
    capacity = sum(f * f for f in F[:a])
    below = capacity - F[a - 1] * F[a - 1]
    for m in range(math.ceil(THETA_LO * capacity), math.floor(THETA_HI * capacity) + 1):
        lo = max(0, math.ceil((m - THETA_HI * below) / F[a - 1]))
        hi = min(F[a - 1], math.floor((m - THETA_LO * below) / F[a - 1]))
        assert max(0, hi - lo + 1) >= RHO * F[a - 2] - 1


@pytest.mark.parametrize("n", [1_000, 10_000, 100_000, 1_000_000])
def test_t5_never_exceeds_the_exact_value(n):
    """A lower bound above the true value would be a false theorem."""
    from capfib.lower import t5_lower_bound

    exact = _exact()
    assert t5_lower_bound(n).log_count <= exact[n]


@pytest.mark.parametrize("n", [1_597, 10_000, 100_000, 1_000_000])
def test_t5_improves_on_t3(n):
    """The point of T5: the block contributes a factor, not a 1."""
    from capfib.lower import t5_lower_bound

    assert t5_lower_bound(n).log_count > t3_lower_bound(n).log_count


@pytest.mark.parametrize("n", [1_000, 10_000, 100_000, 1_000_000])
def test_t5_residues_land_in_the_flat_band(n):
    """8.3. Every residue N - sigma must lie in [THETA_LO S_a, THETA_HI S_a]."""
    from capfib.fib import places_up_to
    from capfib.lower import THETA_HI, THETA_LO, t5_lower_bound

    result = t5_lower_bound(n)
    places = places_up_to(n)
    capacity = sum(f * f for f in places[: result.block])
    budget = n - (capacity + 4) // 5
    reached = sum(
        (budget // (result.counting_places * places[k - 1])) * places[k - 1]
        for k in range(result.block + 1, result.top_place + 1)
    )
    assert reached <= budget
    assert n <= THETA_HI * capacity
    assert n - reached >= THETA_LO * capacity


@pytest.mark.parametrize("n", [1_000, 10_000, 100_000, 1_000_000])
def test_t5_digits_respect_their_caps(n):
    """m_k <= F_k must hold automatically on the counting block (8.3)."""
    from capfib.fib import places_up_to
    from capfib.lower import t5_lower_bound

    result = t5_lower_bound(n)
    places = places_up_to(n)
    capacity = sum(f * f for f in places[: result.block])
    budget = n - (capacity + 4) // 5
    for k in range(result.block + 1, result.top_place + 1):
        assert budget // (result.counting_places * places[k - 1]) <= places[k - 1]
