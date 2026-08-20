"""The global checksum, and the reason it is not a licence to report anything.

For the fixed-length system on places F_1..F_n every digit tuple has exactly
one value, so sum(counts) == prod(F_k + 1) exactly. That identity is a useful
regression invariant and nothing more:

  * it is one scalar constraining an array of millions, so any sum-preserving
    corruption passes it;
  * it does not exercise the production place set at all -- checksum_ok(18)
    uses places up to F_18 = 2584, while a run to 10^6 uses 30 places up to
    832040, leaving twelve untouched.

What licenses the numbers is the pointwise dp/gf cross-check. These tests hold
both facts in place.
"""

from capfib.dp import counts as dp_counts
from capfib.fib import fibonacci
from capfib.gf import checksum_ok, coefficients


def test_checksum_holds_for_small_n():
    for n in range(1, 15):
        assert checksum_ok(n), f"checksum failed at n={n}"


def test_checksum_detects_a_changed_total():
    F = fibonacci(10)
    max_value = sum(f * f for f in F)
    c = coefficients(max_value, places=F)
    product = 1
    for f in F:
        product *= f + 1
    assert sum(c) == product
    c[7] += 1
    assert sum(c) != product


def test_checksum_misses_sum_preserving_corruption():
    """The known blind spot, asserted so nobody over-trusts the invariant.

    Moving mass between two coefficients leaves the total identical. The
    checksum cannot see it.
    """
    F = fibonacci(10)
    max_value = sum(f * f for f in F)
    c = coefficients(max_value, places=F)
    product = 1
    for f in F:
        product *= f + 1

    c[7] += 1
    c[9] -= 1              # sum preserved
    assert sum(c) == product, "the checksum is blind to this corruption -- by design of the check, not of the code"


def test_crosscheck_catches_sum_preserving_corruption():
    """The same corruption the checksum misses, caught pointwise.

    This pair is the argument: the cross-check is the licence, the checksum
    is not.
    """
    n_max = 500
    good = coefficients(n_max)
    corrupted = list(good)
    corrupted[7] += 1
    corrupted[9] -= 1
    assert sum(corrupted) == sum(good)          # checksum-style test passes
    assert corrupted != dp_counts(n_max)        # pointwise comparison fails
    assert good == dp_counts(n_max)             # and the good array survives it
