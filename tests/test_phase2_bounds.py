"""Tests for the certified Chernoff upper bound on log R_c(N).

The comparisons against exact values are marked `oracle_gate`: they are the
reason this file exists, and `tests/conftest.py` fails the whole session if one
of them skips instead of running. `data/phase1_data.csv` is tracked (see the
.gitignore note) precisely so that they always can run; a missing oracle is now
a failure with a regeneration command in the message, never a skip.
"""

import csv
import hashlib
import json
import math
from pathlib import Path

import pytest

from capfib.fib import places_up_to
from capfib.lower import t3_lower_bound
from capfib.product import log_F_c
from capfib.saddle import argmin_log_s, log_R_bound, log_R_bound_certified

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "phase1_data.csv"
MANIFEST = ROOT / "data" / "manifest.json"

# The N at which the exact oracle is consulted anywhere in this file. Pinned so
# that a truncated or silently re-scoped `phase1_data.csv` fails loudly rather
# than shrinking the gate to whatever rows happen to be present.
REQUIRED_EXACT_N = (100, 1_000, 1_597, 10_000, 100_000, 1_000_000)

LOG_PHI = math.log((1 + 5 ** 0.5) / 2)


def _exact():
    """Load the exact Phase 1 values.

    Raises:
        AssertionError: if the tracked oracle is absent or does not carry every
            N in `REQUIRED_EXACT_N`. This must fail rather than skip: while it
            skipped, a clean clone ran none of the twelve comparisons below and
            still reported green.
    """
    assert DATA.exists(), (
        f"{DATA.relative_to(ROOT)} absent -- it is tracked, so this means it was "
        f"deleted, not that it was never generated. Restore it from git, or "
        f"regenerate with: .venv/bin/python scripts/run_phase1.py"
    )
    with DATA.open() as handle:
        values = {int(r["N"]): float(r["log_R_c"]) for r in csv.DictReader(handle)}
    missing = [n for n in REQUIRED_EXACT_N if n not in values]
    assert not missing, (
        f"{DATA.relative_to(ROOT)} is missing exact values at N = {missing}; "
        f"regenerate with: .venv/bin/python scripts/run_phase1.py"
    )
    return values


@pytest.mark.oracle_gate
def test_the_tracked_oracle_matches_its_manifest_provenance():
    """The tracked exact-value ladder must be what run_phase1.py produced.

    Tracking a generated file buys a clean-clone gate at the price of a file
    that could be hand-edited into agreement with whatever it is meant to
    check. `data/manifest.json` records the SHA-256 the generator wrote, so
    comparing against it closes that hole: an edited CSV fails here before it
    can quietly license a bound.
    """
    entries = json.loads(MANIFEST.read_text())
    recorded = [
        e for e in entries
        if e["file"] == "phase1_data.csv" and e["script"] == "scripts/run_phase1.py"
    ]
    assert recorded, "data/manifest.json has no provenance entry for phase1_data.csv"
    digest = hashlib.sha256(DATA.read_bytes()).hexdigest()
    assert digest == recorded[-1]["sha256"], (
        "data/phase1_data.csv does not match the SHA-256 data/manifest.json "
        "records for it: the tracked oracle and its provenance have diverged. "
        "Regenerate both with: .venv/bin/python scripts/run_phase1.py"
    )


@pytest.mark.oracle_gate
@pytest.mark.parametrize("n", [100, 10_000, 1_000_000])
def test_certified_bound_holds_against_exact_values(n):
    """T1 must hold at every sampled N. Design-time slacks: 4.99, 9.20, 13.55."""
    exact = _exact()
    bound = log_R_bound_certified(n)
    assert bound >= exact[n], f"certified bound {bound} below exact {exact[n]} at N={n}"


@pytest.mark.oracle_gate
def test_certified_bound_is_not_vacuous():
    """A bound of +inf would satisfy the inequality and prove nothing."""
    exact = _exact()
    bound = log_R_bound_certified(1_000_000)
    assert math.isfinite(bound)
    assert bound - exact[1_000_000] < 20.0


@pytest.mark.oracle_gate
@pytest.mark.parametrize("n", [100, 1_000, 10_000, 100_000, 1_000_000])
def test_certified_bound_equals_an_independently_computed_transform(n):
    """T1's value, recomputed here rather than trusted.

    Mutation probe (Codex, pre-PR gate): replacing `log_R_bound_certified`
    with the constant 80.0 left the suite green, because every other check on
    it is an inequality against an exact value that is far below it. An
    inequality cannot pin a number; an identity can.

    `log_R_bound_certified(n)` is by construction `s N + log F_c(e^-s)`
    evaluated at the minimiser the float search returns, then rounded upward
    through interval arithmetic. This recomputes exactly that quantity from
    `argmin_log_s` and `log_F_c` -- two calls the certified path also makes,
    but composed here in the test rather than inside the function -- and
    requires the two to agree to 1e-6. Measured agreement is ~3e-14; the
    tolerance is the certification's upward rounding, not slack.
    """
    log_s, _ = argmin_log_s(math.log(n))
    independent = math.exp(log_s + math.log(n)) + log_F_c(log_s)
    certified = log_R_bound_certified(n)
    assert certified == pytest.approx(independent, abs=1e-6), (
        f"N={n}: certified bound {certified} is not the transform "
        f"{independent} it is defined to be"
    )
    assert certified >= independent - 1e-9, "certification may only round upward"


@pytest.mark.oracle_gate
@pytest.mark.parametrize("n", [1_000, 10_000, 100_000, 1_000_000])
def test_t3_log_count_is_the_product_over_the_counting_block(n):
    """T3's value is a product identity, and is checked as one.

    Mutation probe (Codex, pre-PR gate): zeroing every T3 `log_count` left
    the suite green, because `t3 <= exact` and `t5 > t3` both get *easier* as
    T3 falls. Zero is a perfectly valid lower bound and a perfectly useless
    one. This recomputes the product of `spec 4.3`'s factors
    `floor(N / (M F_k)) + 1` over the counting block, from `places_up_to` and
    the block split the result itself reports, and requires equality -- so a
    zero, a constant, or a dropped factor all fail.
    """
    result = t3_lower_bound(n)
    places = places_up_to(n)
    expected = sum(
        math.log(n // (result.counting_places * places[k - 1]) + 1)
        for k in range(result.fixup_block + 1, result.top_place + 1)
    )
    assert result.log_count == pytest.approx(expected, rel=1e-12)
    assert result.log_count > 0.0, (
        f"N={n}: T3 counts a single representation, which is no bound at all"
    )


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


@pytest.mark.oracle_gate
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


@pytest.mark.oracle_gate
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


@pytest.mark.oracle_gate
@pytest.mark.parametrize("n", [10_000, 100_000, 1_000_000])
def test_t5_carries_its_block_factor_at_large_n(n):
    """T5's content at large N, where the enumeration cannot reach.

    Mutation probe (Codex, pre-PR gate): weakening T5 to `T3 + 0.01` for
    N >= 1000 left the suite green. Nothing caught it because the element-by-
    element enumeration of the construction stops at N = 219 -- below the
    mutation's own threshold -- and every other T5 check was either an
    inequality against the exact value (which a weaker bound satisfies more
    easily) or the strict-improvement check above, which `T3 + 0.01` also
    passes.

    Three things are pinned here, none of which `T3 + 0.01` satisfies:

    1. The decomposition. `log_count` is `log_free + log_block` exactly --
       T5's whole claim is that the block contributes a factor, so the block
       factor has to be *in* the total.
    2. The block factor is the proved flatness bound, recomputed here.
    3. The margin over T3 is the size the construction predicts, not an
       epsilon: at these N it is 3.7, 12.3 and 22.0 nats.
    """
    from capfib.lower import flatness_log_bound, t5_lower_bound

    t5 = t5_lower_bound(n)
    t3 = t3_lower_bound(n)

    assert t5.log_count == pytest.approx(t5.log_free + t5.log_block, rel=1e-12)
    assert t5.log_block == pytest.approx(flatness_log_bound(t5.block), rel=1e-12)
    assert t5.log_block > 0.0, "the block must contribute a factor, not a 1"
    assert t5.log_count - t3.log_count > 3.0, (
        f"N={n}: T5 beats T3 by only {t5.log_count - t3.log_count:.4f} nats; "
        f"the construction predicts several"
    )
    # T5's leading coefficient heads for 1/(4 log phi) while T3's stalls at
    # 1/(8 log phi), so at the top of the verified range T5's normalised value
    # must be well clear of T3's. Measured at N = 10^6: 0.2085 against 0.0931.
    log_n_sq = math.log(n) ** 2
    assert t5.log_count / log_n_sq > 1.5 * (t3.log_count / log_n_sq), (
        f"N={n}: T5/(log N)^2 = {t5.log_count / log_n_sq:.4f} is not clear of "
        f"T3/(log N)^2 = {t3.log_count / log_n_sq:.4f}"
    )
    assert t5.log_count / log_n_sq < 1.0 / (4 * LOG_PHI), (
        "T5 is a lower bound on a quantity whose leading coefficient is "
        "1/(4 log phi); exceeding it at finite N would be a contradiction"
    )


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


def _t5_family(n):
    """Enumerate the T5 construction of §8.3 element by element at N.

    Each element is a full digit tuple over *all* places `F_k <= N`, least
    significant first: a fixup on the block [1, a] together with one free
    tuple on the counting block (a, c]. The free digits are bounded by
    `m_k = floor(X / (M F_k))` and the fixup ranges over every cap-respecting
    representation of the residue `N - sigma` on the block, which is the
    quantity `B(a, N - sigma)` that Lemma F bounds below.

    Args:
        n: the integer N, at least 3.

    Returns:
        tuple: (`T5Result`, place values, list of digit tuples).
    """
    import itertools

    from capfib.brute import numerals
    from capfib.fib import places_up_to
    from capfib.lower import t5_lower_bound

    result = t5_lower_bound(n)
    places = places_up_to(n)
    a, c, m_count = result.block, result.top_place, result.counting_places
    capacity = sum(f * f for f in places[:a])
    budget = n - (capacity + 4) // 5
    caps = [budget // (m_count * places[k - 1]) for k in range(a + 1, c + 1)]
    family = []
    for free in itertools.product(*(range(m + 1) for m in caps)):
        sigma = sum(d * places[a + i] for i, d in enumerate(free))
        for block in numerals(n - sigma, places[:a]):
            family.append(tuple(block) + free)
    return result, places, family


@pytest.mark.slow
def test_t5_construction_enumerates_to_valid_distinct_representations():
    """8.7. The construction, enumerated element by element for N = 3 .. 219.

    This is the property the whole lower bound rests on, and it is checked
    against `capfib.brute` rather than against the formulas being tested. At
    each N the enumerated family must consist of valid capped representations
    of N, all distinct, at least as numerous as the proved bound
    `exp(t5_lower_bound(N).log_count)`, and no more numerous than the exact
    `R_c(N)`.

    N starts at 3: at N = 2 the counting block is empty and the construction
    is not defined. The upper end 219 is where the exhaustive brute-force
    oracle stops being cheap -- this is a check over that finite range, not a
    proof of the construction's validity for all N, which is what §8.3 is for.

    Marked `slow` (~45 s, most of it the brute-force oracle) so it can be
    deselected with `-m "not slow"`; it runs by default.
    """
    from capfib.brute import count
    from capfib.lower import THETA_HI, THETA_LO

    for n in range(3, 220):
        result, places, family = _t5_family(n)
        capacity = sum(f * f for f in places[: result.block])

        for sequence in family:
            assert len(sequence) == len(places), f"N={n}: wrong number of places"
            assert all(0 <= d <= f for d, f in zip(sequence, places)), \
                f"N={n}: a digit exceeds its cap"
            assert sum(d * f for d, f in zip(sequence, places)) == n, \
                f"N={n}: a sequence does not evaluate to N"
            residue = sum(
                d * f for d, f in zip(sequence[: result.block], places[: result.block])
            )
            assert THETA_LO * capacity <= residue <= THETA_HI * capacity, \
                f"N={n}: residue {residue} outside the flat band"

        assert len(set(family)) == len(family), f"N={n}: the family repeats an element"
        exact = count(n)
        assert len(family) <= exact, \
            f"N={n}: construction gives {len(family)} > R_c(N) = {exact}"
        assert len(family) >= math.exp(result.log_count) - 1e-9, \
            f"N={n}: proved bound exp({result.log_count}) exceeds the {len(family)} " \
            f"elements the construction actually produces"


@pytest.mark.slow
def test_t5_enumeration_would_notice_a_broken_construction():
    """The enumeration above passes trivially if the family is empty.

    Without this, deleting the body of `_t5_family` would leave the checks
    above green at every N.
    """
    for n in (3, 89, 219):
        _, _, family = _t5_family(n)
        assert family, f"N={n}: the construction produced no elements at all"
