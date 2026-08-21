"""Direct evaluation of the Phase 2 lower-bound construction (spec 4.3).

The construction splits the places into a fixup block [1, a] whose capacity
F_a F_{a+1} already exceeds N, and a counting block (a, c] carrying free digits
bounded by m_k = floor(N / (M F_k)). Every free tuple has sum at most N and so
completes on the fixup block, which is why no pigeonhole or steering step is
needed and the count is the full product.
"""

import math
from typing import NamedTuple

from capfib.fib import places_up_to


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
