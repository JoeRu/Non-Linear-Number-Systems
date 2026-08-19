# MATH-Benchmark Setup Guide

The MATH-Benchmark harness evaluates answer-generation models on competition
mathematics problems, adapted here for the Non-Linear Number Systems domain.

## Problem Format

Problems are stored in `benchmarks/math_benchmark/problems.json`.  Each entry has:

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique problem identifier |
| `source` | string | Where the problem comes from |
| `level` | int 1–5 | Difficulty (1 = easiest, 5 = hardest) |
| `category` | string | Mathematical area |
| `problem` | string | The problem statement |
| `solution` | string | A human-readable solution |
| `answer` | string | The canonical answer for scoring |
| `verification_type` | string | `"exact_string"`, `"integer"`, or `"boolean"` |

## Running the Evaluation

```bash
# Score reference solver (integer problems only)
python harnesses/math_harness/run_eval.py

# Score model outputs
python harnesses/math_harness/run_eval.py --answers /path/to/model_answers.json
```

The `model_answers.json` file should be a JSON object mapping problem IDs to
answer strings:

```json
{
  "NLNS_MATH_001": "89 + 8 + 3",
  "NLNS_MATH_002": "7"
}
```

## Computing reprCount

```bash
# Compute reprCount(n=50, c=2)
python benchmarks/math_benchmark/evaluate.py --compute 50 2
```

## Adding New Problems

1. Append a new JSON object to `benchmarks/math_benchmark/problems.json`.
2. Assign a new unique `id` following the `NLNS_MATH_NNN` convention.
3. Verify the `answer` field using `evaluate.py --compute` if applicable.
4. **Do not modify or remove existing problem IDs** — this would invalidate
   historical evaluation results.

## Reference

- Hendrycks et al., "Measuring Mathematical Problem Solving With the MATH Dataset", NeurIPS 2021.
