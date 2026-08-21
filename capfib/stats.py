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

    Phase 5 Route B needs this: the fluctuation observed in R_c over
    N <= 10^6 (docs/phases/phase1_report.md) motivates working with the
    summatory function instead of attacking R_c directly, and S_c is
    non-decreasing by construction, which R_c is not.
    """
    out: list[int] = []
    running = 0
    for x in counts:
        running += x
        out.append(running)
    return out


def local_ratios(counts: Sequence[int]) -> list[float]:
    """r[n] = counts[n+1] / counts[n] for n = 0 .. len-2.

    The division is guarded by an explicit check (raising `ValueError`) rather
    than by appealing to completeness: completeness is still a `sorry` in the
    Lean development, so it is not something this code may lean on.
    """
    if min(counts) < 1:
        raise ValueError("counts must be positive; local_ratios would divide by zero")
    return [counts[n + 1] / counts[n] for n in range(len(counts) - 1)]


def place_jumps(counts: Sequence[int]) -> list[dict]:
    """R_c(F)/R_c(F-1) at each distinct place value F >= 2.

    Distinctness matters: F_1 = F_2 = 1 is a single place, and F = 1 has no
    predecessor in range.

    The result is NOT monotone. Measured: the ratio is exactly 1.0 at F = 2,
    rises at F = 3 and again at F = 8, and only decays monotonically from
    F = 13 onward. Reporting it as a clean decay law would be wrong.
    """
    n_max = len(counts) - 1
    out: list[dict] = []
    for place in sorted(set(places_up_to(n_max))):
        if place < 2:
            continue
        out.append({"place": place, "ratio": counts[place] / counts[place - 1]})
    return out


def block_extrema(counts: Sequence[int]) -> list[dict]:
    """Argmax/argmin of R_c within each Fibonacci block.

    Blocks run between consecutive DISTINCT place values -- F_1 = F_2 = 1
    would otherwise yield a degenerate duplicate first block. Ties are broken
    toward the smallest N so results are reproducible.

    Progress on open problem 2 of theory/01-background.md section 14: which
    integers carry the most and fewest representations.
    """
    n_max = len(counts) - 1
    places = [p for p in sorted(set(places_up_to(n_max))) if p <= n_max]
    out: list[dict] = []
    for i, lo in enumerate(places):
        hi = min(places[i + 1] if i + 1 < len(places) else n_max + 1, n_max + 1)
        block = range(lo, hi)
        argmax = min(block, key=lambda n: (-counts[n], n))
        argmin = min(block, key=lambda n: (counts[n], n))
        out.append({
            "lo": lo, "hi": hi,
            "argmax": argmax, "max": counts[argmax],
            "argmin": argmin, "min": counts[argmin],
        })
    return out
