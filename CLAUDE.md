# CLAUDE.md — AI Assistant Guide for Non-Linear Number Systems

This file gives AI coding assistants (Claude, GitHub Copilot, etc.) the context they need
to contribute effectively to this project.

---

## Project Overview

**Non-Linear Number Systems** is a research program on the asymptotics of `R_c(N)` — the
number of representations of `N` as `sum_k d_k F_k` with position-dependent digit bounds
`0 <= d_k <= F_k`.

The problem sits between two solved cases: binary partitions (Mahler 1940, de Bruijn 1948)
and uncapped Fibonacci partitions (Coons–Kristensen–Laursen 2023). The position-dependent
cap breaks the simplifications both rely on. The goal is to state, explore numerically, and
**formally prove** properties of this system, using Lean 4 / Mathlib for the elementary
results and a Python numerics package to generate and cross-check the underlying claims.

---

## Repository Layout

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

---

## Global Constraints

- Python >= 3.11.
- **The Fibonacci convention is F_1 = 1, F_2 = 1, F_3 = 2, F_4 = 3, F_5 = 5, …** (spec D2). Place values are constructed in `capfib/fib.py` and **nowhere else**. Every other module imports from there. The duplicated 1-place is load-bearing — it is the source of the "1 > 1" phenomenon, and dropping it also breaks the identity `sum_{k<=n} F_k^2 = F_n * F_{n+1}`.
- `R_c(N)` counts digit tuples over **all** places `F_k <= N`, never a fixed length `n`. Fixing the length undercounts (spec §4.3, Trap 1).
- **The §4.2 gate:** no output of `capfib.dp` or `capfib.gf` may appear in any report, figure, or claim until it has matched `capfib.brute` for all N <= 200 and the two fast paths have matched each other for all N <= 500.
- Never remove a Lean `sorry` without a real proof. A `sorry` is a statement; a wrong proof is worse than an open one.
- Every generated dataset writes an entry to `data/manifest.json`.
- Commit at the end of every task.

---

## Key Concepts

### Position-Dependent Digit Bounds
A **representation** of a positive integer `N` is a sequence of digits `(d_k)_{k>=1}`
with `0 <= d_k <= F_k` — the bound on each digit is the place value itself, so it
grows with position — satisfying `sum_k d_k F_k = N`, where the sum ranges over
**all** places `F_k <= N` (never a fixed length). Because the digit bound grows with
`k` rather than being fixed (as in a standard base-`b` system), this numeration is
**maximally redundant**: most integers have many representations, not one.

### Non-Unique Representations
`R_c(N)` denotes the number of such representations of `N`. We study:
- The growth of `R_c(N)` — in particular the leading coefficient of `log R_c(N)`
  as a function of `(log N)^2`
- Patterns and recurrences in these counts
- Connections to other combinatorial objects (tilings, lattice paths, etc.)

### Zeckendorf Representation (the unique-representation contrast)
The **Zeckendorf representation** constrains digits to `{0, 1}` and forbids two
consecutive nonzero digits (no `F_k` and `F_{k+1}` both used). Under that much
stricter constraint, every positive integer has a **unique** representation as a
sum of non-consecutive Fibonacci numbers. This project's position-dependent bound
`0 <= d_k <= F_k` sits at the opposite extreme from Zeckendorf's `{0,1}` bound —
maximal redundancy instead of uniqueness — which is why `R_c(N)` is interesting to
count in the first place.

---

## Working with Lean 4 / Mathlib

### Prerequisites
- Install `elan` (Lean version manager): https://github.com/leanprover/elan
- The toolchain version is pinned in `lean/lean-toolchain`

### Build
```bash
cd lean
lake update        # download Mathlib (first time, ~10 min)
lake build         # compile all files
```

### Check a Single File
```bash
cd lean
lake env lean NonLinearNumberSystems/Zeckendorf.lean
```

### Common Lean 4 Patterns Used Here
- `def`, `theorem`, `lemma` for definitions and statements
- `simp`, `ring`, `omega`, `norm_num` for automated tactics
- `induction`, `rcases`, `obtain` for structural proofs
- `#check`, `#eval` for interactive exploration

---

## Contribution Guidelines for AI Assistants

1. **Stay focused on the mathematics.** All code changes should serve the goal of
   formally verifying or computationally exploring theorems about non-linear number
   systems.

2. **Never remove `sorry` without a real proof.** A `sorry`-filled theorem is a
   *statement*; replacing it with a wrong proof is worse than leaving it open.

3. **Run `lake build` before committing** Lean changes to ensure the project compiles.

4. **Add docstrings** to all new Python functions using the Google style.

5. **Respect the correctness gate.** Never present `capfib.dp` or `capfib.gf` output as
   a fact until it has passed the cross-checks described in Global Constraints above.

6. **Cite sources.** When adapting a theorem or result from the literature (e.g. Mahler,
   de Bruijn, Coons–Kristensen–Laursen, Fraenkel) or from Mathlib, include the source
   reference in a comment.
