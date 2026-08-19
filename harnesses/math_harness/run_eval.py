#!/usr/bin/env python3
"""
MATH-Harness Evaluation Runner
================================
End-to-end harness that:
  1. Loads problems from benchmarks/math_benchmark/problems.json
  2. Optionally runs a model (or the reference solver) to generate answers
  3. Scores the answers and prints a report

Usage:
    # Verify reference solver answers
    python run_eval.py

    # Score model outputs stored in answers.json
    python run_eval.py --answers /path/to/answers.json

    # Compute reprCount for a single (n, c) pair
    python run_eval.py --compute 50 2

Prerequisites:
    pip install -r requirements.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Resolve paths relative to repository root
REPO_ROOT = Path(__file__).parents[2]
PROBLEMS_PATH = REPO_ROOT / "benchmarks" / "math_benchmark" / "problems.json"

# Add the benchmarks directory to sys.path so we can import evaluate.py
sys.path.insert(0, str(REPO_ROOT / "benchmarks" / "math_benchmark"))

from evaluate import compute_repr_count, evaluate  # noqa: E402  (after sys.path update)


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="MATH-Harness end-to-end evaluation runner"
    )
    parser.add_argument(
        "--problems", type=Path, default=PROBLEMS_PATH,
        help="Path to problems.json",
    )
    parser.add_argument(
        "--answers", type=Path, default=None,
        help="Path to answers.json produced by a model.  Omit for reference solver.",
    )
    parser.add_argument(
        "--compute", type=int, nargs=2, metavar=("N", "C"),
        help="Compute reprCount(N, C) and exit.",
    )
    args = parser.parse_args()

    if args.compute:
        n, c = args.compute
        result = compute_repr_count(n, c)
        print(f"reprCount({n}, {c}) = {result}")
        sys.exit(0)

    evaluate(args.problems, args.answers)


if __name__ == "__main__":
    main()
