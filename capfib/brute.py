"""Exact enumeration of numerals -- the test oracle.

Deliberately slow and obviously correct. Every fast path in this package is
tested against this module; it is never used for production-scale counting.
"""

from collections.abc import Iterator

from capfib.fib import places_up_to


def numerals(n: int, places: list[int] | None = None) -> Iterator[tuple[int, ...]]:
    """Yield every digit tuple (d_1, ..., d_K) with 0 <= d_k <= F_k summing to n.

    Digits are yielded least-significant place first, matching the order of
    `places`. When `places` is None the full range F_k <= n is used.
    """
    if n < 0:
        return
    if places is None:
        places = places_up_to(n)

    def rec(i: int, remaining: int, acc: list[int]) -> Iterator[tuple[int, ...]]:
        if i < 0:
            if remaining == 0:
                yield tuple(reversed(acc))
            return
        f = places[i]
        for d in range(min(f, remaining // f) + 1):
            yield from rec(i - 1, remaining - d * f, acc + [d])

    yield from rec(len(places) - 1, n, [])


def count(n: int, places: list[int] | None = None) -> int:
    """Number of numerals evaluating to n. The oracle for R_c(n)."""
    if n < 0:
        return 0
    return sum(1 for _ in numerals(n, places))
