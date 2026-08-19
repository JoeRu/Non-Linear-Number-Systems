# Non-Linear Number Systems

Research program on the asymptotics of `R_c(N)` — the number of representations of `N` as
`sum_k d_k F_k` with position-dependent digit bounds `0 <= d_k <= F_k`.

The problem sits between two solved cases: binary partitions (Mahler 1940, de Bruijn 1948)
and uncapped Fibonacci partitions (Coons–Kristensen–Laursen 2023). The position-dependent
cap breaks the simplifications both rely on.

## Layout

| Path | Contents |
|---|---|
| `capfib/` | Numerics package: enumeration, DP, generating function, saddle point |
| `tests/` | Correctness gate — brute-force oracle and cross-checks |
| `theory/` | Definitions, background analysis, proof sketches, the claim ledger |
| `docs/roadmap.md` | The phase plan |
| `docs/phases/` | Phase deliverables |
| `paper/` | LaTeX writeup and bibliography |
| `lean/` | Formal proofs of the elementary results |
| `data/`, `figures/` | Generated output; regenerate, never hand-edit |

## Quick start

```bash
bash scripts/setup.sh
.venv/bin/pytest
.venv/bin/python scripts/run_phase0_gate.py
```

## The convention

`F_1 = F_2 = 1`, `F_3 = 2`, `F_4 = 3`, `F_5 = 5`, … Defined once in `capfib/fib.py`.
See `theory/00-definitions.md`.
