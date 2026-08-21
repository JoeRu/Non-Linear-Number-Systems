import pytest
from capfib.fib import fibonacci, places_up_to


def test_convention_first_ten_places():
    """Spec D2: F_1 = F_2 = 1. The duplicated 1-place is deliberate."""
    assert fibonacci(10) == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]


def test_fibonacci_degenerate():
    assert fibonacci(0) == []
    assert fibonacci(1) == [1]
    assert fibonacci(2) == [1, 1]


@pytest.mark.parametrize("limit,expected", [
    (0, []),
    (1, [1, 1]),
    (2, [1, 1, 2]),
    (4, [1, 1, 2, 3]),
    (7, [1, 1, 2, 3, 5]),
    (8, [1, 1, 2, 3, 5, 8]),
])
def test_places_up_to(limit, expected):
    assert places_up_to(limit) == expected


# Hard-coded from the recurrence F_1 = F_2 = 1, F_k = F_{k-1} + F_{k-2},
# stopping at the last term <= 1_000_000 -- computed by hand, not by calling
# places_up_to, so this cannot pass by construction.
EXPECTED_PLACES_UP_TO_1_000_000 = [
    1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584,
    4181, 6765, 10946, 17711, 28657, 46368, 75025, 121393, 196418, 317811,
    514229, 832040,
]


def test_places_up_to_production_boundary():
    """Pins the place set the Phase 1 cross-check actually runs over at
    n_max = 10**6. The dp/gf comparison is only independent conditional on
    this place set being right (see the Phase 1 design spec, §3.1) -- a
    wrong or truncated place set is applied identically to both algorithms
    and would be invisible to that comparison. This test is the boundary
    check the spec points to instead.

    A weaker test that pins only the count, the last element, and the first
    excluded value would pass on a corrupted `places_up_to` that returns an
    interior value wrong (e.g. a stray 14 in the middle) -- both `dp` and
    `gf` would consume that wrong list identically, so the cross-check could
    not catch it either. Pinning the complete list closes that gap.
    """
    places = places_up_to(1_000_000)
    assert places == EXPECTED_PLACES_UP_TO_1_000_000
    assert places[-1] == 832040
    assert 1346269 not in places
    for k in range(2, len(EXPECTED_PLACES_UP_TO_1_000_000)):
        F = EXPECTED_PLACES_UP_TO_1_000_000
        assert F[k] == F[k - 1] + F[k - 2]


def test_sum_of_squares_identity():
    """sum_{k<=n} F_k^2 = F_n * F_{n+1} -- holds only under F_1 = F_2 = 1."""
    for n in range(1, 21):
        F = fibonacci(n + 1)
        assert sum(f * f for f in F[:n]) == F[n - 1] * F[n]
