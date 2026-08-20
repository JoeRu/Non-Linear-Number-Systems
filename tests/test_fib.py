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


def test_sum_of_squares_identity():
    """sum_{k<=n} F_k^2 = F_n * F_{n+1} -- holds only under F_1 = F_2 = 1."""
    for n in range(1, 21):
        F = fibonacci(n + 1)
        assert sum(f * f for f in F[:n]) == F[n - 1] * F[n]
