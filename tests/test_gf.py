from capfib.brute import count
from capfib.dp import counts
from capfib.gf import coefficients
from capfib.fib import fibonacci


def test_gf_matches_dp_to_500():
    """Spec §4.2, second half of the gate: two independent algorithms agree."""
    assert coefficients(500) == counts(500)


def test_gf_matches_oracle_to_200():
    arr = coefficients(200)
    for n in range(201):
        assert arr[n] == count(n), f"mismatch at N={n}"


def test_gf_matches_dp_fixed_places():
    for n in range(1, 9):
        F = fibonacci(n)
        maxval = sum(f * f for f in F)
        assert coefficients(maxval, places=F) == counts(maxval, places=F)
