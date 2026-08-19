"""Place values for the capacity-constrained Fibonacci numeration system.

The convention F_1 = F_2 = 1, F_3 = 2, F_4 = 3, F_5 = 5, ... is fixed HERE AND
NOWHERE ELSE (spec D2). Every other module imports from this one.

Two properties depend on the duplicated 1-place:
  * numerals 1000 and 0100 both evaluate to 1 -- the "1 > 1" phenomenon;
  * sum_{k<=n} F_k^2 = F_n * F_{n+1}, which fixes the completeness range.
"""


def fibonacci(n: int) -> list[int]:
    """Return the first `n` place values F_1 .. F_n."""
    if n <= 0:
        return []
    F = [1, 1]
    while len(F) < n:
        F.append(F[-1] + F[-2])
    return F[:n]


def places_up_to(limit: int) -> list[int]:
    """Return every place value F_k with F_k <= limit.

    This is the correct place range for representing an integer N: passing a
    fixed length instead undercounts (spec §4.3, Trap 1).
    """
    if limit < 1:
        return []
    F = [1, 1]
    while F[-1] + F[-2] <= limit:
        F.append(F[-1] + F[-2])
    return F
