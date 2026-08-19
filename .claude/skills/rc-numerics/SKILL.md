---
name: rc-numerics
description: Use when computing, regenerating, or reporting any numerical result about R_c(N) — DP counts, generating-function evaluations, saddle-point estimates, fits, or figures.
---

# Running numerics for R_c(N)

## The gate comes first

Use the project venv created by `scripts/setup.sh`; `capfib` is installed only
there, so a bare `pytest` fails with an import error rather than a real gate
result. Before any numeric result is reported, run:

```bash
.venv/bin/pytest tests/test_brute.py tests/test_dp.py tests/test_gf.py -q
```

These verify the fast paths against the brute-force oracle to N=200 and against
each other to N=500. If they fail, the numbers are not trustworthy — fix the
failure, do not report around it.

## Rules

1. **Never hand-copy a number into a document.** Every figure and table is
   produced by a script under `scripts/` and recorded via `capfib.manifest.record`.
2. **Never construct Fibonacci numbers outside `capfib/fib.py`.** The convention
   F_1 = F_2 = 1 is defined once.
3. **Never fix the numeral length.** `R_c(N)` ranges over all places `F_k <= N`.
   A fixed length undercounts.
4. **Pass `log s`, not `s`,** to `capfib.product.log_F_c`. At the scales that
   matter, `s` underflows to zero.
5. **Check the bracket.** `capfib.saddle.log_R_bound` raises if the minimiser
   reaches an endpoint. Do not catch and ignore it — widen `half`.
6. After generating data, add or update the `theory/claims.yaml` entry and run
   `.venv/bin/python scripts/check_claims.py`.
