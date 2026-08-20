# Research Infrastructure for the R_c(N) Asymptotics Program

**Date:** 2026-08-19
**Status:** Approved design — implementation plan pending
**Scope:** Repository restructure, numerics core, claim discipline, revised phase sequence

---

## 1. Motivation

The repository was scaffolded for a different task than the one now planned.

The present tree — `benchmarks/miniF2F/`, `benchmarks/proofnet/`, `benchmarks/math_benchmark/`,
`harnesses/lean_dojo/`, `harnesses/math_harness/` — is infrastructure for *evaluating LLM
theorem provers* against formal benchmark suites. Roughly 650 lines of Python serve that goal.

`Roadmap_RC_Asymptotik.md` describes something else entirely: an analytic number theory
research program targeting an original publication. Its phases require exact computation of
`R_c(N)` to N ≈ 10^6–10^7, saddle-point heuristics, Mellin transform and Dirichlet series
analysis, oscillation detection by Fourier analysis, and a 25–40 page LaTeX writeup.

No phase of the roadmap consumes any part of the benchmark scaffolding. This document
specifies the restructure that closes that gap.

---

## 2. Decisions taken

Three decisions were settled before this design and are treated here as fixed:

**D1 — The benchmark scaffolding is deleted.** `benchmarks/` and `harnesses/` are removed
from the working tree. They remain recoverable from git history. The repository should
describe what it is.

**D2 — The canonical Fibonacci convention is F₁ = 1, F₂ = 1, F₃ = 2, F₄ = 3, F₅ = 5, …**
This is the convention of the source article and of `fibonacci-numeration-analysis.md`.
Roadmap Phase 0 currently proposes F₁ = 1, F₂ = 2, F₃ = 3; that proposal is rejected for
two reasons:

1. The duplicated 1-place is the origin of the phenomenon the project studies. Numerals
   `1000` and `0100` both evaluate to 1 — the article's "1 > 1". Merging the two 1-places
   deletes the object of study.
2. The identity `Σ_{k≤n} F_k² = F_n · F_{n+1}`, which fixes the completeness range in §3
   of the background analysis, holds only under F₁ = F₂ = 1. Under the rejected convention
   it fails already at n = 4 (39 vs 40).

**D3 — The conjectured leading constant is tested numerically before the heuristic is
developed.** A new Phase 0.5 is inserted (see §6).

---

## 3. Target repository structure

```
capfib/                  Python package — numerics core
  __init__.py
  fib.py                 place values; the single definition of the convention (D2)
  brute.py               exact enumeration of digit tuples — the test oracle
  dp.py                  fast DP; exact ints below threshold, log-domain above
  product.py             direct evaluation of log F_c(e^{-s})
  saddle.py              numerical Legendre transform s*(N)
  fit.py                 multiple regression for a·(log N)² + b·log N·loglog N + c·log N + d
  oscillation.py         residuals vs fractional part of log_φ N; Fourier analysis
tests/                   see §4
scripts/
  setup.sh               rewritten: Python env + elan, no benchmark dependencies
  run_lean.sh            retained
  run_phase0_gate.py
  run_phase1_dp.py
  make_figures.py
data/                    generated output; gitignored except manifest.json
figures/                 generated only; never hand-edited
theory/
  00-definitions.md      Phase 0 deliverable — canonical conventions and question statements
  01-background.md       ← fibonacci-numeration-analysis.md, moved unchanged
  claims.yaml            the claim ledger (§5)
docs/
  roadmap.md             ← Roadmap_RC_Asymptotik.md, moved; a living document
  lean_setup.md          retained
  phases/                phaseN_report.md deliverables
  superpowers/specs/     design documents including this one
paper/
  main.tex
  refs.bib
lean/NonLinearNumberSystems/
  Basic.lean
  Numeration.lean        digit tuples, the valuation map, the cap predicate
  Completeness.lean      Σ F_k² = F_n·F_{n+1}; surjectivity onto [0, Σ F_k²]
  Bounds.lean            sandwich bounds — statements, `sorry` until proved
  Zeckendorf.lean        existing stubs, retained (feeds open problems 3 and 4)
.claude/skills/          project skills (§5)
```

### 3.1 Migration order

1. Commit `Roadmap_RC_Asymptotik.md` and `fibonacci-numeration-analysis.md` **unchanged**,
   so their arrival is a clean point in history.
2. `git rm -r benchmarks/ harnesses/ tools/` — both modules in `tools/` exist only to
   serve the removed harnesses, leaving an empty package. Delete
   `docs/leandojo_setup.md`, `docs/math_benchmark_setup.md`, and
   `scripts/run_benchmarks.sh`. `docs/lean_setup.md` and `scripts/run_lean.sh` survive;
   `scripts/setup.sh` is rewritten.
3. Move the two source documents to `docs/roadmap.md` and `theory/01-background.md`.
4. Create the `capfib` package skeleton and `tests/`.
5. Rewrite `README.md` and `CLAUDE.md` against the new tree.
6. Retarget `lean/`.

Steps 2 and 5 must land in the same commit: a tree whose `CLAUDE.md` documents deleted
directories is worse than either state alone.

---

## 4. Numerics core and correctness discipline

### 4.1 The oracle

`capfib.brute.count(N)` enumerates every digit tuple `(d_k)` with `0 ≤ d_k ≤ F_k` and
`Σ d_k F_k = N`. It is deliberately slow and obviously correct. It is not a debugging aid;
it is the specification against which the fast path is tested.

### 4.2 The gate

**No output of `capfib.dp` may be used in any report, figure, or claim until it has
matched `capfib.brute` on all N ≤ 200 and matched the truncated product
`∏_k (x^{F_k(F_k+1)} − 1)/(x^{F_k} − 1)` on all N ≤ 500.**

The roadmap requests both checks in prose. This design makes them a test-suite gate and
enforces them through the `rc-numerics` skill, because a check that is requested but not
enforced is a check that is skipped under time pressure in month four.

### 4.3 Two traps encoded in the code

**Trap 1 — place range.** The table in §4 of the background analysis counts numerals of
length *exactly* n, which **undercounts** `R_c(N)`: places beyond n with `F_k ≤ N` are also
usable. `dp.py` and `brute.py` both range over all k with `F_k ≤ N`.

Consequence for §2 D3: the §4 average `S(n)/V(n) = φ^{n²/2 − 2n}` with `N ≈ φ^{2n}` yields
`log R ≳ (log N)²/(8 log φ) ≈ 0.26 (log N)²`, but because the numerator undercounts this is
a *lower bound only*. It does not contradict the roadmap's conjectured
`(log N)²/(4 log φ) ≈ 0.52 (log N)²`. The two are consistent and unresolved, which is
precisely why Phase 0.5 exists.

**Trap 2 — convention leakage.** Place values are defined once, in `capfib.fib`. No other
module constructs a Fibonacci sequence. Every module imports from there.

### 4.4 Test suite

| Test | Content |
|---|---|
| `test_brute_vs_dp` | Agreement on all N ≤ 200 |
| `test_product_identity` | Truncated product vs DP on all N ≤ 500 |
| `test_sum_of_squares` | `Σ_{k≤n} F_k² = F_n · F_{n+1}` for n ≤ 40 |
| `test_completeness` | No zero entries in the count array up to `F_n·F_{n+1}` |
| `test_known_values` | The §2 worked examples: value 5 has 4 numerals at 4 places, value 6 has 4 |
| `test_table_section4` | Reproduces the n = 1..10 table of the background analysis |

### 4.5 Performance path

Python with numpy, gmpy2 and mpmath first. Exact integer counts below the point where
they exceed memory; log-domain convolution above it. A Rust or C kernel is considered
**only** if N = 10^7 proves unreachable in Python, and only after the Phase 0.5 gate has
justified the investment.

### 4.6 Provenance

Every generated dataset writes an entry to `data/manifest.json`: the generating script,
its parameters, the git revision, the output file hash, and a timestamp. `data/` is
otherwise gitignored. Figures are regenerated from data, never edited by hand.

---

## 5. Claim ledger and project skills

### 5.1 The ledger

`theory/claims.yaml` holds one entry per mathematical statement:

```yaml
- id: completeness-no-gaps
  statement: "Every integer in [0, F_n·F_{n+1}] has at least one representation."
  status: theorem
  evidence: "Kempner–Fraenkel condition; see theory/01-background.md §3"
  source: "Fraenkel 1985"
```

`status` is one of `cited`, `verified-numeric`, `heuristic`, `conjecture`, `theorem`, `open`.

Markdown documents reference claims by id. The distinction between a heuristic and a
theorem is the entire epistemic content of this project, and Phase 3 is separated from
Phase 5 by months — long enough for a conjecture to acquire the tone of a result. The
ledger makes that drift mechanically detectable.

### 5.2 Skills

Built in this order:

| Skill | When | Purpose |
|---|---|---|
| `rc-numerics` | Before Phase 0 | Runs numeric tasks with the §4.2 gate mandatory; stamps `data/manifest.json` |
| `claim-ledger` | Before Phase 0 | Validates claim ids resolve; fails if a doc asserts a `conjecture` or `heuristic` as established; fails if a `verified-numeric` entry has no manifest hash |
| `phase-report` | Before Phase 1 | Scaffolds a phase deliverable to the roadmap's own template: report, data, figures, risks |
| `lit-anchor` | Before Phase 1 | Verifies a citation exists before it enters a document; appends to `paper/refs.bib` |
| `walnut-transducer` | Deferred | Wraps the Walnut toolchain for open problems 3 and 4 |

`lit-anchor` is not bureaucracy: the roadmap's reference 4 currently reads
`Navas, L. (20XX) … [Referenz nachschlagen]`, and that reference is load-bearing for
Route A of Phase 5.

Existing skills used without modification: `superpowers:verification-before-completion`
for numeric claims, `superpowers:test-driven-development` (the brute-force enumerator is
the test oracle), `superpowers:writing-plans` for phase plans, `skill-creator` to build
the five above.

---

## 6. Revised phase sequence

| Phase | Change from roadmap |
|---|---|
| **0** Definitions | Pin D2; define `R_c` over all k with `F_k ≤ N`; seed `claims.yaml`. The convention paragraph of roadmap Phase 0 is rewritten. |
| **0.5** Constant gate | **New, ~1 day.** Direct evaluation of `log F_c(e^{−s})` plus numerical Legendre transform gives an empirical `C_c`, held against `1/(2 log φ) ≈ 1.04`, `1/(4 log φ) ≈ 0.52`, `1/(8 log φ) ≈ 0.26`. A decision point before any month-scale investment. |
| **1** Exact DP | Gap search removed — completeness is proved, not searched for (§6.1). Extremal-N tracking added, from open problem 2 of the background analysis. |
| **2** Sandwich bounds | Unchanged, plus completeness via the Kempner–Fraenkel condition as an explicit theorem; this is the primary Lean target. |
| **3** Heuristic | Content unchanged, but now explains a constant already measured rather than predicting one. |
| **4** Numerics | Full regression and oscillation Fourier analysis. Partly pre-empted by Phase 0.5. |
| **5** Rigorisation | Unchanged. Route A (Mellin + Dirichlet series) primary, Route B (Tauberian) fallback, Route C (functional equation) exploratory. |
| **6** Oscillations | Unchanged. |
| **7** Writeup | Unchanged. |

### 6.1 Why the gap search is removed

Roadmap Phase 1 asks: *"Lückenstruktur: An welchen N gilt R_c(N) = 0?"* Section 3 of the
background analysis answers this. The Kempner–Fraenkel completeness condition
`u_k ≤ 1 + Σ_{j<k} m_j u_j` reads here `F_k ≤ 1 + F_{k−1}F_k`, true for all k with large
slack, so there are no gaps anywhere in `[0, Σ F_k²]`. The appendix confirms it empirically
at every length up to 10. The task becomes "prove completeness rigorously and formalise it",
which is tractable in Lean, rather than "search numerically for gaps that cannot exist".

---

## 7. Lean scope

Lean is retained but narrowed to what is honestly formalisable within this project:

- numeral and valuation definitions (`Numeration.lean`)
- `Σ_{k≤n} F_k² = F_n · F_{n+1}` and completeness (`Completeness.lean`)
- sandwich bounds as statements, proved if the elementary arguments permit (`Bounds.lean`)
- existing Zeckendorf statements, retained for open problems 3 and 4 (`Zeckendorf.lean`)

The asymptotic theorems of Phases 5 and 6 are **not** Lean targets. Mellin transforms,
analytic continuation of `ζ_F^{(F+1)}`, and Tauberian arguments are far outside what
current Mathlib makes practical, and pretending otherwise would consume the project.
Those results live in `paper/`.

The existing prohibition stands and is restated here: a `sorry` is a statement; replacing
it with a wrong proof is worse than leaving it open.

---

## 8. Assumptions

Two questions were left open at design time and are resolved here by default. Either can
be revisited without disturbing the rest of the design.

**A1 — Paper format.** `paper/main.tex` and `paper/refs.bib` are created at Phase 0 so
that citations accumulate in BibTeX from the first day. Prose lives in Markdown phase
reports until Phase 7, when it is consolidated into LaTeX. Rationale: `lit-anchor` needs
a bib file to append to immediately; nothing else needs LaTeX early.

**A2 — Package installation.** `capfib` is installable via `pyproject.toml` and
`pip install -e .`, so scripts and tests import it without `sys.path` manipulation.

---

## 9. Out of scope

- Any implementation of Phase 5's Mellin analysis. This document specifies infrastructure.
- Walnut integration, until open problems 3 and 4 are actively worked.
- Rust or C numerics kernels, unless §4.5's condition is met.
- The four other open problems referenced in roadmap Phase 7.4, which remain unspecified
  in the source documents.

---

## 10. Success criteria

The restructure is complete when:

1. `benchmarks/` and `harnesses/` are gone; `README.md` and `CLAUDE.md` describe the tree
   that exists.
2. `pytest` passes all of §4.4 against `capfib`.
3. `scripts/run_phase0_gate.py` produces an empirical `C_c` with a figure and a manifest
   entry, and `theory/claims.yaml` records the result with status `verified-numeric`.
4. `theory/00-definitions.md` exists and fixes D2 with explicit values through F₁₀.
5. `rc-numerics` and `claim-ledger` exist under `.claude/skills/` and both run clean.
