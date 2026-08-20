"""Descriptive analyses of the counting function R_c.

Pure functions over a counts array -- no I/O, no plotting, no globals -- so
that every one is unit-testable against hand-checked values. This is where
off-by-one errors would otherwise hide: a miscounted "decreasing step" would
silently change which route Phase 5 takes.
"""

from collections.abc import Sequence

from capfib.fib import places_up_to


def monotonicity_census(counts: Sequence[int]) -> dict[str, int]:
    """Classify each step `counts[n-1] -> counts[n]` for n = 1 .. len-1.

    The three counts always sum to `steps`; the tests assert it.
    """
    increasing = flat = decreasing = 0
    for n in range(1, len(counts)):
        if counts[n] > counts[n - 1]:
            increasing += 1
        elif counts[n] == counts[n - 1]:
            flat += 1
        else:
            decreasing += 1
    return {
        "increasing": increasing,
        "flat": flat,
        "decreasing": decreasing,
        "steps": max(0, len(counts) - 1),
    }


def summatory(counts: Sequence[int]) -> list[int]:
    """S_c(N) = sum_{n <= N} R_c(n), exact.

    Phase 5 Route B needs this: R_c itself fluctuates too much for a direct
    Tauberian attack, while S_c is non-decreasing by construction.
    """
    out: list[int] = []
    running = 0
    for x in counts:
        running += x
        out.append(running)
    return out
