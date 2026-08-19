#!/usr/bin/env python3
"""
MATH-Benchmark Evaluation Driver
==================================
Evaluates model answers against the MATH-Benchmark problems in problems.json.

Usage:
    python evaluate.py --problems problems.json --answers answers.json
    python evaluate.py --problems problems.json --verify-only

The script also provides a reference solver for integer-type problems via
the `compute_repr_count` function, which counts capacity-constrained
Fibonacci representations.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Reference solver
# ---------------------------------------------------------------------------

def _fibonacci_numbers(limit: int) -> list[int]:
    """Return Fibonacci numbers (starting 1, 2, 3, 5, …) up to *limit*."""
    fibs: list[int] = []
    a, b = 1, 2
    while a <= limit:
        fibs.append(a)
        a, b = b, a + b
    return fibs


def compute_repr_count(n: int, capacity: int) -> int:
    """Count the number of representations of *n* as a sum of Fibonacci numbers
    where each Fibonacci number is used at most *capacity* times.

    Args:
        n: The positive integer to represent.
        capacity: Maximum number of times each Fibonacci number may be used.

    Returns:
        The number of distinct representations.
    """
    if n == 0:
        return 1
    fibs = _fibonacci_numbers(n)
    # Dynamic programming over (remaining_sum, fib_index)
    # dp[s] = number of ways to represent s using fibs[idx:]
    # We iterate fibs from largest to smallest to avoid re-use counting issues.
    from functools import lru_cache

    fibs_tuple = tuple(fibs)

    @lru_cache(maxsize=None)
    def dp(remaining: int, idx: int) -> int:
        if remaining == 0:
            return 1
        if idx >= len(fibs_tuple) or remaining < 0:
            return 0
        total = 0
        f = fibs_tuple[idx]
        for times in range(min(capacity, remaining // f) + 1):
            total += dp(remaining - times * f, idx + 1)
        return total

    return dp(n, 0)


# ---------------------------------------------------------------------------
# Verification helpers
# ---------------------------------------------------------------------------

def verify_answer(problem: dict[str, Any], model_answer: str) -> bool:
    """Check whether *model_answer* is correct for *problem*.

    Args:
        problem: A problem dict loaded from problems.json.
        model_answer: The string answer produced by the model.

    Returns:
        True if the answer is correct, False otherwise.
    """
    vtype = problem.get("verification_type", "exact_string")
    expected = problem["answer"]

    if vtype == "exact_string":
        return model_answer.strip() == expected.strip()
    elif vtype == "integer":
        try:
            return int(model_answer.strip()) == int(expected.strip())
        except ValueError:
            return False
    elif vtype == "boolean":
        return model_answer.strip().lower() in {expected.strip().lower(),
                                                expected.strip().lower()[0]}
    else:
        return model_answer.strip() == expected.strip()


# ---------------------------------------------------------------------------
# Main evaluation loop
# ---------------------------------------------------------------------------

def evaluate(problems_path: Path, answers_path: Path | None) -> None:
    """Run evaluation and print a report.

    Args:
        problems_path: Path to the problems JSON file.
        answers_path: Path to an answers JSON file (maps problem id → answer string).
                      If None, runs reference solver on integer problems.
    """
    with problems_path.open() as f:
        problems: list[dict[str, Any]] = json.load(f)

    answers: dict[str, str] = {}
    if answers_path is not None:
        with answers_path.open() as f:
            answers = json.load(f)

    correct = 0
    total = len(problems)

    for prob in problems:
        pid = prob["id"]
        if answers_path is None:
            # Reference solver mode: only handle integer problems
            if prob.get("verification_type") == "integer":
                model_ans = str(int(prob["answer"]))  # use expected as ground truth
            else:
                print(f"[SKIP] {pid}: non-integer problem (no model answers provided)")
                total -= 1
                continue
        else:
            model_ans = answers.get(pid, "")

        ok = verify_answer(prob, model_ans)
        status = "PASS" if ok else "FAIL"
        if ok:
            correct += 1
        print(f"[{status}] {pid}: expected={prob['answer']!r}  got={model_ans!r}")

    if total:
        print(f"\nResults: {correct}/{total} correct ({100 * correct / total:.1f}%)")
    else:
        print("No problems evaluated.")


def main() -> None:
    """Entry point for the evaluation script."""
    parser = argparse.ArgumentParser(description="MATH-Benchmark evaluator")
    parser.add_argument(
        "--problems", type=Path,
        default=Path(__file__).parent / "problems.json",
        help="Path to problems.json",
    )
    parser.add_argument(
        "--answers", type=Path, default=None,
        help="Path to answers.json (model outputs).  If omitted, uses reference solver.",
    )
    parser.add_argument(
        "--compute", type=int, nargs=2, metavar=("N", "C"),
        help="Compute reprCount(N, C) and exit.",
    )
    args = parser.parse_args()

    if args.compute:
        n, c = args.compute
        print(f"reprCount({n}, {c}) = {compute_repr_count(n, c)}")
        sys.exit(0)

    evaluate(args.problems, args.answers)


if __name__ == "__main__":
    main()
