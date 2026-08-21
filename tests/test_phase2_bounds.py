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


@pytest.mark.parametrize("a", range(8, 17))
def test_flatness_bound_holds_against_exact_block_counts(a):
    """8.2. The proved product bound must not exceed the true band minimum.

    The range matches FLATNESS_SLACK_A in scripts/run_phase2.py, so the sharpness
    remark quoted in 8.2 is supported over exactly the range checked here.
    """
    from capfib.lower import block_band_min, flatness_log_bound

    band_min = block_band_min(a)
    assert band_min > 0
    assert flatness_log_bound(a) <= math.log(band_min) + 1e-9


@pytest.mark.parametrize("a", range(2, 14))
def test_flatness_choice_count_is_at_least_rho_fib(a):
    """8.2, cases 1-3: the number of admissible top digits, checked exhaustively.

    This is the step the whole of T5 rests on, so it is checked at every m in the
    band rather than at sampled ones, in exact integer arithmetic rather than in
    floats: the band and the two endpoints d_lo, d_hi all have denominators
    dividing 20, so scaling by 20 clears them and no comparison is ever decided by
    a rounding. (8.2) claims the strict inequality |D_a(m)| > F_{a-1}/5 - 1, and
    that is what is asserted -- scaled to 20|D| > 4 F_{a-1} - 20.
    """
    from capfib.fib import fibonacci

    F = fibonacci(a + 1)
    capacity = sum(f * f for f in F[:a])
    below = capacity - F[a - 1] * F[a - 1]
    top = F[a - 1]
    # theta_1 S_a <= m <= theta_2 S_a, i.e. 4 S_a <= 20 m <= 15 S_a.
    for m in range(-((-capacity) // 5), (3 * capacity) // 4 + 1):
        # d >= (m - (3/4) below)/top  <=>  4 d top >= 4m - 3 below
        lo = max(0, -((-(4 * m - 3 * below)) // (4 * top)))
        # d <= (m - (1/5) below)/top  <=>  5 d top <= 5m - below
        hi = min(top, (5 * m - below) // (5 * top))
        count = max(0, hi - lo + 1)
        assert 20 * count > 4 * F[a - 2] - 20


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


def _naive_block_counts(a):
    """B(a, .) by direct convolution -- deliberately slow, obviously correct.

    Independent of `capfib.lower.block_band_min`, which reaches the same list by
    a sliding window over residue classes. Nothing is shared but the definition.
    """
    from capfib.fib import fibonacci

    F = fibonacci(a)
    counts = [1]
    for k in range(1, a + 1):
        f = F[k - 1]
        top = len(counts) - 1 + f * f
        nxt = []
        for m in range(top + 1):
            total = 0
            for d in range(f + 1):
                previous = m - d * f
                if 0 <= previous < len(counts):
                    total += counts[previous]
            nxt.append(total)
        counts = nxt
    return counts


@pytest.mark.parametrize("a", range(2, 12))
def test_block_band_min_matches_a_naive_convolution(a):
    """block_band_min is an oracle for the sharpness figure, so it needs one too.

    Without this, `flatness-slack-slope` and
    `test_flatness_bound_holds_against_exact_block_counts` share a single
    implementation of B(a, .), and a block_band_min that returned something too
    large would satisfy both.
    """
    from capfib.lower import THETA_HI, THETA_LO, block_band_min

    counts = _naive_block_counts(a)
    capacity = len(counts) - 1
    lo = math.ceil(THETA_LO * capacity)
    hi = math.floor(THETA_HI * capacity)
    assert block_band_min(a) == min(counts[lo : hi + 1])


@pytest.mark.parametrize("a", range(2, 7))
def test_block_band_min_matches_the_brute_force_oracle(a):
    """And against capfib.brute, the package's standard oracle, at small a."""
    from capfib.brute import count
    from capfib.fib import fibonacci
    from capfib.lower import THETA_HI, THETA_LO, block_band_min

    F = fibonacci(a)
    capacity = sum(f * f for f in F)
    lo = math.ceil(THETA_LO * capacity)
    hi = math.floor(THETA_HI * capacity)
    assert block_band_min(a) == min(count(m, list(F)) for m in range(lo, hi + 1))
