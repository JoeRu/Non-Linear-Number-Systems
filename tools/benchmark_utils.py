"""
benchmark_utils.py — Scoring and reporting helpers for MATH-Benchmark.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any


def _fibonacci_numbers(limit: int) -> list[int]:
    """Return all Fibonacci numbers (starting 1, 2, 3, 5, …) up to *limit*."""
    fibs: list[int] = []
    a, b = 1, 2
    while a <= limit:
        fibs.append(a)
        a, b = b, a + b
    return fibs


def compute_repr_count(n: int, capacity: int) -> int:
    """Count capacity-constrained Fibonacci representations of *n*.

    A representation is a multiset of Fibonacci numbers (from 1, 2, 3, 5, 8, …)
    where each element appears at most *capacity* times and the elements sum to *n*.

    Args:
        n: The non-negative integer to represent.
        capacity: Maximum multiplicity of each Fibonacci number (≥ 1).

    Returns:
        The total number of distinct representations.

    Example:
        >>> compute_repr_count(10, 2)
        7
    """
    if n == 0:
        return 1
    if capacity <= 0:
        raise ValueError("capacity must be at least 1")

    fibs = tuple(_fibonacci_numbers(n))

    @lru_cache(maxsize=None)
    def dp(remaining: int, idx: int) -> int:
        if remaining == 0:
            return 1
        if idx >= len(fibs) or remaining < 0:
            return 0
        f = fibs[idx]
        total = 0
        for times in range(min(capacity, remaining // f) + 1):
            total += dp(remaining - times * f, idx + 1)
        return total

    return dp(n, 0)


def score_answers(
    problems: list[dict[str, Any]],
    answers: dict[str, str],
) -> dict[str, Any]:
    """Score a set of model answers against ground-truth problems.

    Args:
        problems: List of problem dicts (from problems.json).
        answers: Mapping of problem ID → model answer string.

    Returns:
        A report dict with keys: ``correct``, ``total``, ``accuracy``, ``details``.
    """
    details: list[dict[str, Any]] = []
    correct = 0

    for prob in problems:
        pid = prob["id"]
        expected = prob["answer"]
        got = answers.get(pid, "")
        vtype = prob.get("verification_type", "exact_string")

        if vtype == "integer":
            try:
                ok = int(got.strip()) == int(expected.strip())
            except ValueError:
                ok = False
    elif vtype == "boolean":
        ok = got.strip().lower() in {expected.strip().lower(),
                                     expected.strip().lower()[0]}
        else:
            ok = got.strip() == expected.strip()

        if ok:
            correct += 1
        details.append({"id": pid, "correct": ok, "expected": expected, "got": got})

    total = len(problems)
    return {
        "correct": correct,
        "total": total,
        "accuracy": correct / total if total else 0.0,
        "details": details,
    }
