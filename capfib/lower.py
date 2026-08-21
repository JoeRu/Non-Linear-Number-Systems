"""Direct evaluation of the Phase 2 lower-bound construction (spec 4.3).

The construction splits the places into a fixup block [1, a] whose capacity
F_a F_{a+1} already exceeds N, and a counting block (a, c] carrying free digits
bounded by m_k = floor(N / (M F_k)). Every free tuple has sum at most N and so
completes on the fixup block, which is why no pigeonhole or steering step is
needed and the count is the full product.
"""

import math
from typing import NamedTuple

from capfib.fib import fibonacci, places_up_to


class T3Result(NamedTuple):
    """The T3 construction evaluated at a single N."""

    log_count: float
    fixup_block: int
    top_place: int
    counting_places: int


def t3_lower_bound(n: int) -> T3Result:
    """Evaluate the T3 construction at N.

    Args:
        n: the integer N, at least 2.

    Returns:
        A T3Result whose `log_count` is a lower bound on log R_c(N).

    Raises:
        ValueError: if n is less than 2, or if no fixup block reaches capacity N.
    """
    if n < 2:
        raise ValueError(f"n must be at least 2, got {n}")
    places = places_up_to(n)
    fixup_block = None
    for i in range(1, len(places)):
        if places[i - 1] * places[i] >= n:
            fixup_block = i
            break
    if fixup_block is None:
        raise ValueError(f"no fixup block reaches capacity N at n={n}")
    counting = range(fixup_block + 1, len(places) + 1)
    counting_places = len(counting)
    if counting_places == 0:
        return T3Result(0.0, fixup_block, len(places), 0)
    log_count = sum(
        math.log(n // (counting_places * places[k - 1]) + 1) for k in counting
    )
    return T3Result(log_count, fixup_block, len(places), counting_places)


THETA_LO = 1 / 5
"""Lower edge of the flat band of a block, as a fraction of its capacity (T5)."""

THETA_HI = 3 / 4
"""Upper edge of the flat band of a block, as a fraction of its capacity (T5)."""

RHO = 1 / 5
"""min(THETA_HI - THETA_LO, THETA_LO, 1 - THETA_HI): the worst case of the four
cases in the flatness lemma of docs/phases/phase2_bounds.md 8.2."""

FLATNESS_BASE = 7
"""Largest block index handled by completeness alone. For k > this, the flatness
recursion contributes a factor rho * F_{k-1} - 1, which is above 1 exactly from
F_7 = 13 on."""


class T5Result(NamedTuple):
    """The T5 construction evaluated at a single N."""

    log_count: float
    log_free: float
    log_block: float
    block: int
    top_place: int
    counting_places: int


def flatness_log_bound(a: int) -> float:
    """Proved lower bound on log B(a, m), uniform over the band of block [1, a].

    `B(a, m)` counts cap-respecting digit tuples on places 1..a with value m.
    The bound is the product form of the flatness lemma
    (docs/phases/phase2_bounds.md 8.2): one factor `RHO * F_{k-1} - 1` per
    index k from FLATNESS_BASE + 1 to a, with `B(FLATNESS_BASE, m) >= 1`
    supplied by completeness.

    Args:
        a: block length, at least 1.

    Returns:
        A lower bound on log B(a, m) valid for every integer m in
        [THETA_LO * S_a, THETA_HI * S_a], where S_a = F_a F_{a+1}.
    """
    if a <= FLATNESS_BASE:
        return 0.0
    F = fibonacci(a)
    return sum(math.log(RHO * F[k - 2] - 1) for k in range(FLATNESS_BASE + 1, a + 1))


def t5_lower_bound(n: int) -> T5Result:
    """Evaluate the T5 construction at N.

    The block [1, a] is chosen so that its capacity S_a = F_a F_{a+1} is at
    least N / THETA_HI; the free family on (a, c] is bounded by
    m_k = floor(X / (M F_k)) with X = floor(N - THETA_LO * S_a), which keeps
    every residue N - sigma inside the band where the flatness lemma applies.
    Unlike T3 the block contributes a factor of `flatness_log_bound(a)` rather
    than 1, which is where the missing factor of two comes from.

    Args:
        n: the integer N, at least 2.

    Returns:
        A T5Result whose `log_count` is a lower bound on log R_c(N).

    Raises:
        ValueError: if n is less than 2, or if no block reaches capacity
            4N/3.
    """
    if n < 2:
        raise ValueError(f"n must be at least 2, got {n}")
    places = places_up_to(n)
    top_place = len(places)
    capacity = 0
    block = None
    for k in range(1, top_place + 1):
        capacity += places[k - 1] * places[k - 1]
        # THETA_HI = 3/4, compared exactly so the boundary carries no float edge.
        if 3 * capacity >= 4 * n:
            block = k
            break
    if block is None:
        raise ValueError(f"no block reaches capacity 4N/3 at n={n}")
    counting_places = top_place - block
    if counting_places == 0:
        return T5Result(0.0, 0.0, 0.0, block, top_place, 0)
    # X = floor(N - S_a / 5), in integers.
    budget = n - (capacity + 4) // 5
    log_free = sum(
        math.log(budget // (counting_places * places[k - 1]) + 1)
        for k in range(block + 1, top_place + 1)
    )
    log_block = flatness_log_bound(block)
    return T5Result(
        log_free + log_block,
        log_free,
        log_block,
        block,
        top_place,
        counting_places,
    )


def block_band_min(a: int) -> int:
    """Exact minimum of B(a, m) over the band of the block [1, a].

    `B(a, m)` counts cap-respecting digit tuples on places 1..a with value m,
    and the band is the integers of [THETA_LO * S_a, THETA_HI * S_a]. The DP
    runs a sliding window of F_k + 1 terms along each residue class mod F_k,
    which is what keeps a = 16 (S_a = 1576239) tractable.

    This is the exact quantity `flatness_log_bound` bounds from below; it is
    used to confront the proved bound with the truth, never to prove anything.

    Args:
        a: block length, at least 2.

    Returns:
        min over integers m in the band of B(a, m).

    Raises:
        ValueError: if a is less than 2.
    """
    if a < 2:
        raise ValueError(f"a must be at least 2, got {a}")
    F = fibonacci(a)
    current = [1]
    for k in range(1, a + 1):
        f = F[k - 1]
        previous_top = len(current) - 1
        top = previous_top + f * f
        nxt = [0] * (top + 1)
        for r in range(f):
            window: list[int] = []
            running = 0
            m = r
            while m <= top:
                value = current[m] if m <= previous_top else 0
                window.append(value)
                running += value
                if len(window) > f + 1:
                    running -= window.pop(0)
                nxt[m] = running
                m += f
        current = nxt
    capacity = len(current) - 1
    lo = math.ceil(THETA_LO * capacity)
    hi = math.floor(THETA_HI * capacity)
    return min(current[lo : hi + 1])
