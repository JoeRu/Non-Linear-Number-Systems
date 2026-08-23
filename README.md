# Non-Linear Number Systems

Research program on the asymptotics of `R_c(N)` — the number of representations of `N` as
`sum_k d_k F_k` with position-dependent digit bounds `0 <= d_k <= F_k`.

The problem sits between two solved cases: binary partitions (Mahler 1940, de Bruijn 1948)
and uncapped Fibonacci partitions (Coons–Kristensen–Laursen 2023). The position-dependent
cap breaks the simplifications both rely on.

## Where the programme stands

Phase 2 settles the leading constant: the limit of `log R_c(N)/(log N)^2` exists and equals
`1/(4 log phi) = 0.5195217...` ({claim:leading-constant}). It is a statement about the
limit and nothing more — it pins no individual value of `R_c(N)`, and the secondary term
is still open. The proof is a sandwich: a Chernoff upper bound against an explicit
lower-bound construction, written out in
[`docs/phases/phase2_bounds.md`](docs/phases/phase2_bounds.md) and summarised in
[`docs/phase2.md`](docs/phase2.md), which is the place to start.

The asymptotics are paper proofs. What is machine-checked is the elementary combinatorial
layer they rest on — the place recurrence, `sum_{k<=n} F_k^2 = F_n F_{n+1}`, completeness,
and non-uniqueness — formalised in Lean under `lean/` with no `sorry`. `theory/claims.yaml`
records which is which, and `scripts/check_claims.py` enforces it.

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
