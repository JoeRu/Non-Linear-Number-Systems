#!/usr/bin/env bash
# run_benchmarks.sh — Run all benchmark harnesses.
# Usage: bash scripts/run_benchmarks.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Running MATH-Benchmark evaluation (reference solver) …"
python "$REPO_ROOT/harnesses/math_harness/run_eval.py"

echo ""
echo "==> Checking reprCount spot values …"
python "$REPO_ROOT/benchmarks/math_benchmark/evaluate.py" --compute 10 2
python "$REPO_ROOT/benchmarks/math_benchmark/evaluate.py" --compute 20 2
python "$REPO_ROOT/benchmarks/math_benchmark/evaluate.py" --compute 50 2

echo ""
echo "All benchmark harnesses completed."
