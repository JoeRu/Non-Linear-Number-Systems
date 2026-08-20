# Research Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the LLM-benchmark scaffolding with a verified numerics package, a claim ledger, and the Phase 0.5 constant gate, so the R_c(N) asymptotics program has infrastructure that matches it.

**Architecture:** A `capfib` Python package with a deliberately slow brute-force enumerator as the test oracle, two independent fast paths (naive digit DP and a closed-form generating-function recurrence) that must agree with it and each other, and a pure-log-space evaluation of the generating function that feeds a numerical Legendre transform. Every number that reaches a document passes through a provenance manifest and a claim ledger that distinguishes conjecture from theorem.

**Tech Stack:** Python 3.11+, numpy, matplotlib, pyyaml, pytest. Lean 4 (v4.14.0) with Mathlib for the elementary results only.

**Spec:** `docs/superpowers/specs/2026-08-19-research-infrastructure-design.md`

**Verification status:** Every Python module and test in this plan was extracted and executed
before the plan was committed. All 43 tests pass, the Phase 0.5 gate runs end to end, and the
ledger validator was confirmed to fail when its evidence is missing. The expected values quoted
throughout are measured, not estimated.

## Global Constraints

- Python >= 3.11.
- **The Fibonacci convention is F_1 = 1, F_2 = 1, F_3 = 2, F_4 = 3, F_5 = 5, …** (spec D2). Place values are constructed in `capfib/fib.py` and **nowhere else**. Every other module imports from there. The duplicated 1-place is load-bearing — it is the source of the "1 > 1" phenomenon, and dropping it also breaks the identity `sum_{k<=n} F_k^2 = F_n * F_{n+1}`.
- `R_c(N)` counts digit tuples over **all** places `F_k <= N`, never a fixed length `n`. Fixing the length undercounts (spec §4.3, Trap 1).
- **The §4.2 gate:** no output of `capfib.dp` or `capfib.gf` may appear in any report, figure, or claim until it has matched `capfib.brute` for all N <= 200 and the two fast paths have matched each other for all N <= 500.
- Never remove a Lean `sorry` without a real proof. A `sorry` is a statement; a wrong proof is worse than an open one.
- Every generated dataset writes an entry to `data/manifest.json`.
- Commit at the end of every task.

## File Structure

| File | Responsibility |
|---|---|
| `capfib/fib.py` | Place values. The single definition of the convention. |
| `capfib/brute.py` | Exact enumeration of digit tuples. The test oracle. Slow on purpose. |
| `capfib/dp.py` | Naive digit-loop DP. First fast path. |
| `capfib/gf.py` | Closed-form generating-function recurrence. Second, independent fast path. |
| `capfib/product.py` | `log F_c(e^-s)` in pure log space. |
| `capfib/saddle.py` | Numerical Legendre transform; the leading-constant estimator. |
| `capfib/fit.py` | Multiple regression for the four-term expansion. |
| `capfib/manifest.py` | Provenance records for generated data. |
| `scripts/check_claims.py` | Claim ledger validator. |
| `scripts/run_phase0_gate.py` | The Phase 0.5 deliverable. |
| `theory/claims.yaml` | The ledger. |

**Deferred by design.** The spec names five skills (§5.2); this plan builds only the two
that gate Phase 0.5 — `rc-numerics` and `claim-ledger`. `phase-report` and `lit-anchor` are
Phase 1 prerequisites and `walnut-transducer` is deferred further still; none is required by
the spec's §10 success criteria.

`capfib/oscillation.py` and the log-domain path in `dp.py` are **deliberately not created here**. They are Phase 1 and Phase 4 deliverables and have no tests to write yet; empty stubs would be placeholders.

---

### Task 1: Preserve the source documents

The two research documents are currently untracked. They must enter history unchanged before anything moves, so later diffs show edits rather than creation.

**Files:**
- Commit (no edits): `Roadmap_RC_Asymptotik.md`, `fibonacci-numeration-analysis.md`

- [ ] **Step 1: Confirm both files are untracked and unmodified**

```bash
git status --short
```
Expected: exactly two `??` lines for the two files.

- [ ] **Step 2: Commit them verbatim**

```bash
git add Roadmap_RC_Asymptotik.md fibonacci-numeration-analysis.md
git commit -m "docs: add roadmap and background analysis as received

Committed unchanged so that subsequent restructuring appears as edits."
```

- [ ] **Step 3: Verify the tree is clean**

```bash
git status --short
```
Expected: no output.

---

### Task 2: Remove the benchmark scaffolding and rewrite the entry docs

**Files:**
- Delete: `benchmarks/`, `harnesses/`, `tools/`, `docs/leandojo_setup.md`, `docs/math_benchmark_setup.md`, `scripts/run_benchmarks.sh`
- Move: `Roadmap_RC_Asymptotik.md` -> `docs/roadmap.md`, `fibonacci-numeration-analysis.md` -> `theory/01-background.md`
- Modify: `README.md`, `CLAUDE.md`, `scripts/setup.sh`

**Interfaces:**
- Produces: the directory layout every later task writes into.

- [ ] **Step 1: Delete the scaffolding**

`tools/` goes entirely — both `benchmark_utils.py` and `lean_utils.py` exist only to serve the removed harnesses, leaving an empty package.

```bash
git rm -r -q benchmarks/ harnesses/ tools/
git rm -q docs/leandojo_setup.md docs/math_benchmark_setup.md scripts/run_benchmarks.sh
```

- [ ] **Step 2: Move the research documents into place**

```bash
mkdir -p theory docs/phases data figures paper
git mv Roadmap_RC_Asymptotik.md docs/roadmap.md
git mv fibonacci-numeration-analysis.md theory/01-background.md
```

- [ ] **Step 3: Create the paper skeleton**

Spec §8 A1: the bib file exists from Phase 0 so citations accumulate in BibTeX from the
first day. Prose stays in Markdown phase reports until Phase 7.

`paper/refs.bib`:

```bibtex
@article{coons2023,
  author  = {Coons, Michael and Kristensen, Simon and Laursen, Mathias L.},
  title   = {Asymptotics for partitions over the Fibonacci numbers and related sequences},
  journal = {arXiv preprint arXiv:2312.07404},
  year    = {2023}
}

@article{fraenkel1985,
  author  = {Fraenkel, Aviezri S.},
  title   = {Systems of Numeration},
  journal = {American Mathematical Monthly},
  volume  = {92},
  pages   = {105--114},
  year    = {1985}
}

@article{debruijn1948,
  author  = {de Bruijn, N. G.},
  title   = {On {M}ahler's partition problem},
  journal = {Indagationes Mathematicae},
  volume  = {10},
  pages   = {210--220},
  year    = {1948}
}
```

`paper/main.tex`:

```latex
\documentclass[11pt]{amsart}
\usepackage{amsmath,amssymb,amsthm}

\newtheorem{theorem}{Theorem}
\newtheorem{conjecture}[theorem]{Conjecture}

\title{Capacity-constrained Fibonacci partitions}

\begin{document}
\maketitle

\section{Introduction}
Consolidated from the Markdown phase reports at Phase 7. Until then this file
exists so that citations accumulate in \texttt{refs.bib} from the outset.

\bibliographystyle{amsplain}
\bibliography{refs}
\end{document}
```

- [ ] **Step 4: Rewrite `README.md`**

```markdown
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
| `theory/` | Definitions, background analysis, the claim ledger |
| `docs/roadmap.md` | The phase plan |
| `docs/phases/` | Phase deliverables |
| `paper/` | LaTeX writeup and bibliography |
| `lean/` | Formal proofs of the elementary results |
| `data/`, `figures/` | Generated output; regenerate, never hand-edit |

## Quick start

```bash
bash scripts/setup.sh
pytest
python scripts/run_phase0_gate.py
```

## The convention

`F_1 = F_2 = 1`, `F_3 = 2`, `F_4 = 3`, `F_5 = 5`, … Defined once in `capfib/fib.py`.
See `theory/00-definitions.md`.
```

- [ ] **Step 5: Rewrite `CLAUDE.md`**

Replace the entire "Repository Layout", "Working with LeanDojo", "Working with MATH-Benchmark", and "Working with miniF2F / ProofNet" sections. The new file must contain the Global Constraints of this plan verbatim, plus the layout table from `README.md`. Delete every reference to `benchmarks/`, `harnesses/`, `tools/`, LeanDojo, MATH-Benchmark, miniF2F and ProofNet.

- [ ] **Step 6: Rewrite `scripts/setup.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "==> Python environment"
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"

echo "==> Lean toolchain (optional)"
if ! command -v elan >/dev/null 2>&1; then
  echo "elan not found. Install from https://github.com/leanprover/elan to build lean/."
else
  (cd lean && lake update && lake build)
fi

echo "==> Done. Run: .venv/bin/pytest"
```

- [ ] **Step 7: Verify no dangling references remain**

```bash
grep -rn -E 'benchmarks/|harnesses/|lean_dojo|LeanDojo|miniF2F|ProofNet|math_benchmark|tools\.' \
  --include='*.md' --include='*.sh' --include='*.py' . | grep -v '^./docs/superpowers/'
```
Expected: no output. (Spec and plan documents under `docs/superpowers/` legitimately name the deleted paths as history.)

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "refactor: remove LLM-benchmark scaffolding, restructure for research program

Deletes benchmarks/, harnesses/ and tools/, which served theorem-prover
evaluation rather than the R_c(N) asymptotics program. Moves the roadmap and
background analysis into docs/ and theory/. Rewrites README and CLAUDE.md
against the new tree."
```

---

### Task 3: Package skeleton and the place values

**Files:**
- Create: `pyproject.toml`, `capfib/__init__.py`, `capfib/fib.py`, `tests/test_fib.py`

**Interfaces:**
- Produces: `fib.fibonacci(n: int) -> list[int]` — the first `n` place values, `F_1 .. F_n`.
- Produces: `fib.places_up_to(limit: int) -> list[int]` — every place value `F_k <= limit`.

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "capfib"
version = "0.1.0"
description = "Capacity-constrained Fibonacci numeration: counting and asymptotics"
requires-python = ">=3.11"
dependencies = ["numpy>=1.26", "matplotlib>=3.8", "pyyaml>=6.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[tool.setuptools]
packages = ["capfib"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_fib.py
import pytest
from capfib.fib import fibonacci, places_up_to


def test_convention_first_ten_places():
    """Spec D2: F_1 = F_2 = 1. The duplicated 1-place is deliberate."""
    assert fibonacci(10) == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]


def test_fibonacci_degenerate():
    assert fibonacci(0) == []
    assert fibonacci(1) == [1]
    assert fibonacci(2) == [1, 1]


@pytest.mark.parametrize("limit,expected", [
    (0, []),
    (1, [1, 1]),
    (2, [1, 1, 2]),
    (4, [1, 1, 2, 3]),
    (7, [1, 1, 2, 3, 5]),
    (8, [1, 1, 2, 3, 5, 8]),
])
def test_places_up_to(limit, expected):
    assert places_up_to(limit) == expected


def test_sum_of_squares_identity():
    """sum_{k<=n} F_k^2 = F_n * F_{n+1} -- holds only under F_1 = F_2 = 1."""
    for n in range(1, 21):
        F = fibonacci(n + 1)
        assert sum(f * f for f in F[:n]) == F[n - 1] * F[n]
```

- [ ] **Step 3: Run the test to verify it fails**

```bash
pip install -e ".[dev]" && pytest tests/test_fib.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'capfib'` or `ImportError`.

- [ ] **Step 4: Write the implementation**

```python
# capfib/__init__.py
"""Capacity-constrained Fibonacci numeration."""
```

```python
# capfib/fib.py
"""Place values for the capacity-constrained Fibonacci numeration system.

The convention F_1 = F_2 = 1, F_3 = 2, F_4 = 3, F_5 = 5, ... is fixed HERE AND
NOWHERE ELSE (spec D2). Every other module imports from this one.

Two properties depend on the duplicated 1-place:
  * numerals 1000 and 0100 both evaluate to 1 -- the "1 > 1" phenomenon;
  * sum_{k<=n} F_k^2 = F_n * F_{n+1}, which fixes the completeness range.
"""


def fibonacci(n: int) -> list[int]:
    """Return the first `n` place values F_1 .. F_n."""
    if n <= 0:
        return []
    F = [1, 1]
    while len(F) < n:
        F.append(F[-1] + F[-2])
    return F[:n]


def places_up_to(limit: int) -> list[int]:
    """Return every place value F_k with F_k <= limit.

    This is the correct place range for representing an integer N: passing a
    fixed length instead undercounts (spec §4.3, Trap 1).
    """
    if limit < 1:
        return []
    F = [1, 1]
    while F[-1] + F[-2] <= limit:
        F.append(F[-1] + F[-2])
    return F
```

- [ ] **Step 5: Run the test to verify it passes**

```bash
pytest tests/test_fib.py -v
```
Expected: PASS, 9 tests.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml capfib/ tests/
git commit -m "feat: add capfib package with the canonical place values

F_1 = F_2 = 1 is defined in capfib/fib.py and nowhere else."
```

---

### Task 4: The brute-force oracle

This module is deliberately slow. It is not a debugging aid — it is the specification the fast paths are tested against.

**Files:**
- Create: `capfib/brute.py`, `tests/test_brute.py`

**Interfaces:**
- Consumes: `fib.places_up_to`
- Produces: `brute.numerals(n: int, places: list[int] | None = None) -> Iterator[tuple[int, ...]]` — yields each digit tuple, least-significant place first, ordered as `places`.
- Produces: `brute.count(n: int, places: list[int] | None = None) -> int`

- [ ] **Step 1: Write the failing test**

The expected values below were computed independently and match §2 and §4 of `theory/01-background.md`.

```python
# tests/test_brute.py
from capfib.brute import count, numerals


def test_worked_example_value_one():
    """theory/01-background.md §2: numerals 1000 and 0100 both denote 1."""
    got = {"".join(map(str, t)) for t in numerals(1, places=[1, 1, 2, 3])}
    assert got == {"1000", "0100"}


def test_worked_example_value_five():
    got = {"".join(map(str, t)) for t in numerals(5, places=[1, 1, 2, 3])}
    assert got == {"1020", "0120", "1101", "0011"}


def test_worked_example_value_six():
    got = {"".join(map(str, t)) for t in numerals(6, places=[1, 1, 2, 3])}
    assert got == {"1120", "1011", "0111", "0002"}


def test_digit_caps_respected():
    for t in numerals(12):
        places = [1, 1, 2, 3, 5, 8]
        assert len(t) == len(places)
        assert all(0 <= d <= f for d, f in zip(t, places))


def test_counts_small():
    """R_c(N) for N = 0..20 over all places F_k <= N."""
    expected = [1, 2, 2, 3, 4, 5, 6, 6, 8, 10, 11, 13, 13, 15, 18, 18, 21, 23, 25, 29, 29]
    assert [count(n) for n in range(21)] == expected


def test_count_matches_enumeration():
    for n in range(0, 30):
        assert count(n) == sum(1 for _ in numerals(n))


def test_negative_is_zero():
    assert count(-1) == 0
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
pytest tests/test_brute.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'capfib.brute'`.

- [ ] **Step 3: Write the implementation**

```python
# capfib/brute.py
"""Exact enumeration of numerals -- the test oracle.

Deliberately slow and obviously correct. Every fast path in this package is
tested against this module; it is never used for production-scale counting.
"""

from collections.abc import Iterator

from capfib.fib import places_up_to


def numerals(n: int, places: list[int] | None = None) -> Iterator[tuple[int, ...]]:
    """Yield every digit tuple (d_1, ..., d_K) with 0 <= d_k <= F_k summing to n.

    Digits are yielded least-significant place first, matching the order of
    `places`. When `places` is None the full range F_k <= n is used.
    """
    if n < 0:
        return
    if places is None:
        places = places_up_to(n)

    def rec(i: int, remaining: int, acc: list[int]) -> Iterator[tuple[int, ...]]:
        if i < 0:
            if remaining == 0:
                yield tuple(reversed(acc))
            return
        f = places[i]
        for d in range(min(f, remaining // f) + 1):
            yield from rec(i - 1, remaining - d * f, acc + [d])

    yield from rec(len(places) - 1, n, [])


def count(n: int, places: list[int] | None = None) -> int:
    """Number of numerals evaluating to n. The oracle for R_c(n)."""
    if n < 0:
        return 0
    return sum(1 for _ in numerals(n, places))
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
pytest tests/test_brute.py -v
```
Expected: PASS, 7 tests.

- [ ] **Step 5: Commit**

```bash
git add capfib/brute.py tests/test_brute.py
git commit -m "feat: add brute-force enumerator as the correctness oracle"
```

---

### Task 5: The naive DP and the oracle gate

**Files:**
- Create: `capfib/dp.py`, `tests/test_dp.py`

**Interfaces:**
- Consumes: `fib.places_up_to`, `brute.count`
- Produces: `dp.counts(n_max: int, places: list[int] | None = None) -> list[int]` — index `i` holds `R_c(i)`, exact Python ints, for `i` in `0..n_max`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_dp.py
from capfib.brute import count
from capfib.dp import counts
from capfib.fib import fibonacci


def test_dp_matches_oracle_to_200():
    """Spec §4.2, first half of the gate."""
    arr = counts(200)
    for n in range(201):
        assert arr[n] == count(n), f"mismatch at N={n}"


def test_dp_zero():
    assert counts(0) == [1]


def test_section4_table():
    """Reproduces the n = 1..10 table of theory/01-background.md §4.

    Columns: max value, total numerals S(n), max representations, gap count.
    Note this table fixes the length at exactly n places, which UNDERCOUNTS
    R_c(N) -- it is a property of the length-n system, not of R_c.
    """
    expected = {
        1:  (1,    2,          1,      0),
        2:  (2,    4,          2,      0),
        3:  (6,    12,         2,      0),
        4:  (15,   48,         4,      0),
        5:  (40,   288,        10,     0),
        6:  (104,  2592,       37,     0),
        7:  (273,  36288,      202,    0),
        8:  (714,  798336,     1746,   0),
        9:  (1870, 27941760,   23638,  0),
        10: (4895, 1564738560, 510384, 0),
    }
    for n, (maxval, total, most, gaps) in expected.items():
        F = fibonacci(n)
        assert sum(f * f for f in F) == maxval
        arr = counts(maxval, places=F)
        s = 1
        for f in F:
            s *= f + 1
        assert s == total
        assert max(arr) == most
        assert arr.count(0) == gaps, "completeness: no gaps anywhere in range"
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
pytest tests/test_dp.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'capfib.dp'`.

- [ ] **Step 3: Write the implementation**

```python
# capfib/dp.py
"""Naive digit-loop dynamic programming for R_c.

This is the first of two independent fast paths. It mirrors the definition
directly -- one loop over digits per place -- so that agreement with
`capfib.gf`, which uses a different algorithm, is meaningful evidence.
"""

from capfib.fib import places_up_to


def counts(n_max: int, places: list[int] | None = None) -> list[int]:
    """Return exact R_c(0..n_max) as a list of Python ints.

    With `places` None the full range F_k <= n_max is used, which is the
    definition of R_c. Passing an explicit `places` computes the counting
    function of that fixed-length system instead.
    """
    if n_max < 0:
        return []
    if places is None:
        places = places_up_to(n_max)

    arr = [0] * (n_max + 1)
    arr[0] = 1
    for f in places:
        nxt = [0] * (n_max + 1)
        for v, c in enumerate(arr):
            if not c:
                continue
            for d in range(f + 1):
                t = v + d * f
                if t > n_max:
                    break
                nxt[t] += c
        arr = nxt
    return arr
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
pytest tests/test_dp.py -v
```
Expected: PASS, 3 tests. `test_dp_matches_oracle_to_200` is slow — the oracle is exponential by design. The full suite runs in about a minute, dominated by the oracle comparisons in this file and in `tests/test_gf.py`.

- [ ] **Step 5: Commit**

```bash
git add capfib/dp.py tests/test_dp.py
git commit -m "feat: add naive digit DP, verified against the oracle to N=200

Also reproduces the section 4 table of the background analysis, including
the zero-gap column that confirms completeness empirically."
```

---

### Task 6: The closed-form generating function and the cross-check

The second fast path uses the closed form of each factor,
`(x^{F_k(F_k+1)} - 1) / (x^{F_k} - 1)`, applied as multiply-then-divide:
with `M = f(f+1)`, `q[n] = p[n] - p[n-M]` then `new[n] = q[n] + new[n-f]`.
This is `O(n_max)` per place rather than `O(n_max * f)`, and shares no code
path with Task 5 — which is what makes their agreement evidence.

**Files:**
- Create: `capfib/gf.py`, `tests/test_gf.py`

**Interfaces:**
- Consumes: `fib.places_up_to`, `dp.counts`, `brute.count`
- Produces: `gf.coefficients(n_max: int, places: list[int] | None = None) -> list[int]` — same contract as `dp.counts`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_gf.py
from capfib.brute import count
from capfib.dp import counts
from capfib.gf import coefficients
from capfib.fib import fibonacci


def test_gf_matches_dp_to_500():
    """Spec §4.2, second half of the gate: two independent algorithms agree."""
    assert coefficients(500) == counts(500)


def test_gf_matches_oracle_to_200():
    arr = coefficients(200)
    for n in range(201):
        assert arr[n] == count(n), f"mismatch at N={n}"


def test_gf_matches_dp_fixed_places():
    for n in range(1, 9):
        F = fibonacci(n)
        maxval = sum(f * f for f in F)
        assert coefficients(maxval, places=F) == counts(maxval, places=F)
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
pytest tests/test_gf.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'capfib.gf'`.

- [ ] **Step 3: Write the implementation**

```python
# capfib/gf.py
"""Generating-function coefficients via the closed form of each factor.

    prod_k ( 1 + x^{F_k} + ... + x^{F_k * F_k} )
      = prod_k ( x^{F_k(F_k+1)} - 1 ) / ( x^{F_k} - 1 )

Each factor is applied as a multiplication by (1 - x^M) followed by a division
by (1 - x^f), both O(n_max). This is the production path; `capfib.dp` is the
independent implementation it is checked against.
"""

from capfib.fib import places_up_to


def coefficients(n_max: int, places: list[int] | None = None) -> list[int]:
    """Return exact R_c(0..n_max) as a list of Python ints."""
    if n_max < 0:
        return []
    if places is None:
        places = places_up_to(n_max)

    p = [0] * (n_max + 1)
    p[0] = 1
    for f in places:
        m = f * (f + 1)
        # multiply by (1 - x^m)
        q = [p[n] - (p[n - m] if n >= m else 0) for n in range(n_max + 1)]
        # divide by (1 - x^f)
        nxt = [0] * (n_max + 1)
        for n in range(n_max + 1):
            nxt[n] = q[n] + (nxt[n - f] if n >= f else 0)
        p = nxt
    return p
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
pytest tests/test_gf.py -v
```
Expected: PASS, 3 tests. The §4.2 gate is now fully satisfied.

- [ ] **Step 5: Commit**

```bash
git add capfib/gf.py tests/test_gf.py
git commit -m "feat: add closed-form GF recurrence; spec 4.2 gate now satisfied

Two independent algorithms agree with each other to N=500 and with the
brute-force oracle to N=200."
```

---

### Task 7: The generating function in log space

Everything here is computed from `log s`, never `s`. At the scales the gate reaches, `s` underflows to zero, `F_k` outgrows float conversion, and `exp(z)` overflows — each of which was observed during design. The function takes `log_s` for exactly this reason.

**Files:**
- Create: `capfib/product.py`, `tests/test_product.py`

**Interfaces:**
- Consumes: nothing from the package (self-contained on `math`)
- Produces: `product.log_F_c(log_s: float, cutoff_log: float = 3.9) -> float` — returns `log F_c(e^{-s})` where `log_s = log s`.

- [ ] **Step 1: Write the failing test**

The regression is against the exact power series built from Task 6, which is the strongest available independent check: `F_c(e^{-s}) = sum_n R_c(n) e^{-sn}`.

```python
# tests/test_product.py
import math

import pytest

from capfib.gf import coefficients
from capfib.product import log_F_c


@pytest.mark.parametrize("s", [0.9, 0.7, 0.5, 0.3, 0.2])
def test_product_matches_exact_series(s):
    """log F_c(e^-s) == log sum_n R_c(n) e^{-sn}, to machine precision.

    Truncation at n=600 is harmless: R_c grows subexponentially, so the tail
    is suppressed by e^{-600 s}.
    """
    counts = coefficients(600)
    series = math.log(sum(c * math.exp(-s * n) for n, c in enumerate(counts)))
    assert log_F_c(math.log(s)) == pytest.approx(series, abs=1e-10)


def test_survives_extreme_log_s():
    """s = e^-2000 underflows to 0.0 as a float; log space must still work."""
    v = log_F_c(-2000.0)
    assert math.isfinite(v)
    assert v > 0


def test_monotone_decreasing_in_s():
    values = [log_F_c(math.log(s)) for s in (0.5, 0.4, 0.3, 0.2, 0.1)]
    assert values == sorted(values)
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
pytest tests/test_product.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'capfib.product'`.

- [ ] **Step 3: Write the implementation**

```python
# capfib/product.py
"""Evaluation of log F_c(e^-s) in pure log space.

    log F_c(e^-s) = sum_k [ log(1 - e^{-s F_k (F_k+1)}) - log(1 - e^{-s F_k}) ]

The caller passes log(s), not s. At the scales the Phase 0.5 gate reaches,
s underflows to 0.0, F_k outgrows float conversion, and exp(z) overflows.
Working from log(s) with log(F_k) tracked by its own recurrence avoids all
three.
"""

import math


def _log1m_exp_log(lz: float) -> float:
    """Return log(1 - exp(-z)) given lz = log z, for z > 0."""
    if lz < -30.0:
        # z < 1e-13: log(1 - e^-z) = log z - z/2 + O(z^2)
        return lz - math.exp(lz) / 2.0
    if lz > 6.0:
        # z > 400: 1 - e^-z is 1.0 in double precision
        return 0.0
    if lz > 3.6:
        return -math.exp(-math.exp(lz))
    return math.log(-math.expm1(-math.exp(lz)))


def log_F_c(log_s: float, cutoff_log: float = 3.9) -> float:
    """Return log F_c(e^-s) where log_s = log s.

    Terms with s * F_k > e^{cutoff_log} ~ 49 are negligible and end the sum.
    """
    total = 0.0
    log_prev: float | None = None
    log_f = 0.0  # k = 1, log F_1 = log 1 = 0
    while True:
        lz = log_s + log_f  # log(s F_k)
        if lz > cutoff_log:
            break
        log_f_plus_1 = log_f + math.log1p(math.exp(-log_f))  # log(F_k + 1)
        total += _log1m_exp_log(log_s + log_f + log_f_plus_1) - _log1m_exp_log(lz)
        if log_prev is None:
            log_prev, log_f = 0.0, 0.0  # k = 2, F_2 = 1 -- the duplicated place
        else:
            log_prev, log_f = log_f, log_f + math.log1p(math.exp(log_prev - log_f))
    return total
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
pytest tests/test_product.py -v
```
Expected: PASS, 7 tests. The series comparison should agree to ~1e-16, not merely 1e-10; if it is off by about 0.34 at s=0.9, the loop has skipped `F_1` and is summing only one of the two 1-places.

- [ ] **Step 5: Commit**

```bash
git add capfib/product.py tests/test_product.py
git commit -m "feat: add log-space evaluation of the generating function

Takes log(s) rather than s so the Phase 0.5 gate can reach scales where s
underflows and F_k exceeds float range."
```

---

### Task 8: The saddle point / Legendre transform

`F_c(e^{-s}) = sum_n R_c(n) e^{-sn} >= R_c(N) e^{-sN}`, so
`log R_c(N) <= s N + log F_c(e^{-s})` for every `s > 0`. Minimising over `s`
gives the Legendre transform. Its leading `(log N)^2` coefficient is the
leading coefficient of `log R_c(N)` — the correction is of lower order, which
is why the bound is visibly loose at small `N` yet still measures `C_c`.

**Files:**
- Create: `capfib/saddle.py`, `tests/test_saddle.py`

**Interfaces:**
- Consumes: `product.log_F_c`
- Produces: `saddle.log_R_bound(log_n: float, half: float = 40.0, iters: int = 100) -> float`
- Produces: `saddle.log_R_bound_at(n: int, **kw) -> float` — convenience wrapper taking `N` directly.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_saddle.py
import math

import pytest

from capfib.gf import coefficients
from capfib.saddle import log_R_bound, log_R_bound_at

PHI = (1 + 5 ** 0.5) / 2
LOG_PHI = math.log(PHI)


def test_is_an_upper_bound():
    counts = coefficients(600)
    for n in (100, 200, 400, 600):
        assert log_R_bound_at(n) > math.log(counts[n])


def test_leading_constant_approaches_quarter_log_phi():
    """Local slope d(log R)/d((log N)^2) converges to 1/(4 log phi)."""
    target = 1.0 / (4 * LOG_PHI)
    pts = []
    for e in (100, 200, 400, 800):
        L = e * math.log(10)
        pts.append((L * L, log_R_bound(L)))
    slopes = [(pts[i + 1][1] - pts[i][1]) / (pts[i + 1][0] - pts[i][0])
              for i in range(len(pts) - 1)]
    assert slopes == sorted(slopes), "slope should rise monotonically"
    assert slopes[-1] == pytest.approx(target, abs=0.005)
    assert abs(slopes[-1] - 1.0 / (2 * LOG_PHI)) > 0.4, "rules out 1/(2 log phi)"
    assert abs(slopes[-1] - 1.0 / (8 * LOG_PHI)) > 0.2, "rules out 1/(8 log phi)"


def test_rejects_boundary_minimiser():
    """A bracket too narrow to contain the minimiser must raise, not return."""
    with pytest.raises(ValueError, match="bracket"):
        log_R_bound(math.log(10 ** 100), half=1e-9)
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
pytest tests/test_saddle.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'capfib.saddle'`.

- [ ] **Step 3: Write the implementation**

```python
# capfib/saddle.py
"""Numerical Legendre transform of log F_c.

    log R_c(N) <= min_{s>0} [ s N + log F_c(e^-s) ]

The minimiser sits near s = 1/N, so the search bracket is centred on
log s = -log N. The bracket is checked after the search: a minimiser pinned to
an endpoint is a silent failure that returns a plausible but meaningless
number, and was observed during design.
"""

import math

from capfib.product import log_F_c


def log_R_bound(log_n: float, half: float = 40.0, iters: int = 100) -> float:
    """Return min_s [ s N + log F_c(e^-s) ], given log_n = log N.

    Raises ValueError if the minimiser reaches a bracket endpoint.
    """
    lo, hi = -log_n - half, -log_n + half

    def objective(log_s: float) -> float:
        return math.exp(log_s + log_n) + log_F_c(log_s)

    for _ in range(iters):
        m1 = lo + (hi - lo) / 3
        m2 = hi - (hi - lo) / 3
        if objective(m1) < objective(m2):
            hi = m2
        else:
            lo = m1

    log_s = (lo + hi) / 2
    if not (log_s + log_n + half > 1e-6 and -log_n + half - log_s > 1e-6):
        raise ValueError(
            f"minimiser hit bracket boundary at log s = {log_s}; widen `half`"
        )
    return objective(log_s)


def log_R_bound_at(n: int, **kwargs: float) -> float:
    """Convenience wrapper taking N directly. Only for N within float range."""
    return log_R_bound(math.log(n), **kwargs)
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
pytest tests/test_saddle.py -v
```
Expected: PASS, 3 tests, in about 1 second.

- [ ] **Step 5: Commit**

```bash
git add capfib/saddle.py tests/test_saddle.py
git commit -m "feat: add numerical Legendre transform with bracket validation"
```

---

### Task 9: The four-term regression

**Files:**
- Create: `capfib/fit.py`, `tests/test_fit.py`

**Interfaces:**
- Consumes: numpy
- Produces: `fit.design_matrix(ns: Sequence[float]) -> np.ndarray` — columns `[L^2, L log L, L, 1]` with `L = log N`.
- Produces: `fit.fit_expansion(ns: Sequence[float], log_rs: Sequence[float]) -> dict[str, float]` — keys `a`, `b`, `c`, `d` for `log R = a L^2 + b L log L + c L + d`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_fit.py
import math

import numpy as np
import pytest

from capfib.fit import design_matrix, fit_expansion


def test_recovers_known_coefficients():
    ns = [10.0 ** k for k in range(5, 61)]
    truth = {"a": 0.519522, "b": 0.3, "c": 1.1, "d": 2.0}
    L = np.log(np.array(ns))
    log_rs = truth["a"] * L * L + truth["b"] * L * np.log(L) + truth["c"] * L + truth["d"]
    got = fit_expansion(ns, log_rs)
    for k, v in truth.items():
        assert got[k] == pytest.approx(v, rel=1e-6)


def test_design_matrix_shape_and_columns():
    ns = [100.0, 1000.0, 10000.0]
    m = design_matrix(ns)
    assert m.shape == (3, 4)
    L = math.log(100.0)
    assert m[0, 0] == pytest.approx(L * L)
    assert m[0, 1] == pytest.approx(L * math.log(L))
    assert m[0, 2] == pytest.approx(L)
    assert m[0, 3] == pytest.approx(1.0)
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
pytest tests/test_fit.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'capfib.fit'`.

- [ ] **Step 3: Write the implementation**

```python
# capfib/fit.py
"""Regression for the four-term expansion

    log R_c(N) = a (log N)^2 + b log N loglog N + c log N + d + o(1)

Convergence in the leading term is slow, so a plain ratio to (log N)^2 is a
poor estimator of `a`; this fit and the local slope in `capfib.saddle` are the
two usable ones.
"""

from collections.abc import Sequence

import numpy as np


def design_matrix(ns: Sequence[float]) -> np.ndarray:
    """Columns [L^2, L log L, L, 1] with L = log N."""
    L = np.log(np.asarray(ns, dtype=float))
    return np.column_stack([L * L, L * np.log(L), L, np.ones_like(L)])


def fit_expansion(ns: Sequence[float], log_rs: Sequence[float]) -> dict[str, float]:
    """Least-squares fit; returns the coefficients as {a, b, c, d}."""
    coef, *_ = np.linalg.lstsq(
        design_matrix(ns), np.asarray(log_rs, dtype=float), rcond=None
    )
    return {"a": float(coef[0]), "b": float(coef[1]),
            "c": float(coef[2]), "d": float(coef[3])}
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
pytest tests/test_fit.py -v
```
Expected: PASS, 2 tests.

- [ ] **Step 5: Commit**

```bash
git add capfib/fit.py tests/test_fit.py
git commit -m "feat: add four-term asymptotic regression"
```

---

### Task 10: Provenance manifest

Spec §4.6 requires every generated dataset to carry its provenance. The spec's file tree does not name a module for this; `capfib/manifest.py` is added as the smallest home for it.

**Files:**
- Create: `capfib/manifest.py`, `tests/test_manifest.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: nothing from the package
- Produces: `manifest.record(path: str | Path, script: str, params: dict, manifest_path: str | Path = "data/manifest.json") -> dict` — appends and returns the entry.
- Produces: `manifest.entries(manifest_path=...) -> list[dict]`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_manifest.py
import json

from capfib.manifest import entries, record


def test_record_captures_provenance(tmp_path):
    data = tmp_path / "out.csv"
    data.write_text("N,R\n1,2\n")
    mpath = tmp_path / "manifest.json"

    entry = record(data, script="scripts/demo.py", params={"n_max": 10},
                   manifest_path=mpath)

    assert entry["file"] == "out.csv"
    assert entry["script"] == "scripts/demo.py"
    assert entry["params"] == {"n_max": 10}
    assert len(entry["sha256"]) == 64
    assert entry["timestamp"].endswith("Z")
    assert "git_rev" in entry


def test_records_accumulate(tmp_path):
    mpath = tmp_path / "manifest.json"
    for i in range(3):
        f = tmp_path / f"f{i}.txt"
        f.write_text(str(i))
        record(f, script="s.py", params={"i": i}, manifest_path=mpath)
    assert len(entries(mpath)) == 3
    assert json.loads(mpath.read_text())[1]["params"] == {"i": 1}


def test_entries_missing_file(tmp_path):
    assert entries(tmp_path / "nope.json") == []
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
pytest tests/test_manifest.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'capfib.manifest'`.

- [ ] **Step 3: Write the implementation**

```python
# capfib/manifest.py
"""Provenance records for generated data (spec §4.6).

`data/` is gitignored apart from the manifest, so the manifest is the only
record that a given figure or table came from a given script at a given commit.
"""

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MANIFEST = "data/manifest.json"


def _git_rev() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def entries(manifest_path: str | Path = DEFAULT_MANIFEST) -> list[dict]:
    """Return the recorded entries, or [] if the manifest does not exist."""
    p = Path(manifest_path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def record(
    path: str | Path,
    script: str,
    params: dict,
    manifest_path: str | Path = DEFAULT_MANIFEST,
) -> dict:
    """Append a provenance entry for `path` and return it."""
    target = Path(path)
    entry = {
        "file": target.name,
        "script": script,
        "params": params,
        "git_rev": _git_rev(),
        "sha256": _sha256(target),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    existing = entries(manifest_path)
    existing.append(entry)
    mp = Path(manifest_path)
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(existing, indent=2) + "\n")
    return entry
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
pytest tests/test_manifest.py -v
```
Expected: PASS, 3 tests.

- [ ] **Step 5: Update `.gitignore`**

Append:

```
# Generated data -- everything except the provenance manifest
data/*
!data/manifest.json

# Generated figures
figures/*.png
figures/*.pdf
```

- [ ] **Step 6: Commit**

```bash
git add capfib/manifest.py tests/test_manifest.py .gitignore
git commit -m "feat: add provenance manifest for generated data"
```

---

### Task 11: Definitions, the claim ledger, and its validator

**Files:**
- Create: `theory/00-definitions.md`, `theory/claims.yaml`, `scripts/check_claims.py`, `tests/test_check_claims.py`

**Interfaces:**
- Consumes: pyyaml; reads `data/manifest.json` directly (not via `capfib.manifest`, so the
  validator runs without capfib installed)
- Produces: `check_claims.validate(root: Path) -> list[str]` — returns a list of human-readable problems; empty means valid.
- Claim reference syntax in Markdown: `{claim:some-id}`.

- [ ] **Step 1: Write `theory/00-definitions.md`**

```markdown
# 00 — Definitions and Conventions

The Phase 0 deliverable. Everything downstream depends on this file.

## Fibonacci convention

`F_1 = 1, F_2 = 1, F_3 = 2, F_4 = 3, F_5 = 5, F_6 = 8, F_7 = 13, F_8 = 21, F_9 = 34, F_10 = 55`

The duplicated 1-place is deliberate and load-bearing {claim:convention-duplicated-place}.
Defined in code exactly once, in `capfib/fib.py`.

## Counting functions

- `R_c(N)` — the number of sequences `(d_k)` with `0 <= d_k <= F_k` and `sum_k d_k F_k = N`.
  The index `k` ranges over **all** places with `F_k <= N` {claim:place-range}.
- `R_u(N)` — as above with `d_k` unbounded (Coons–Kristensen–Laursen 2023).
- `b(N)` — the binary partition function (Mahler 1940, de Bruijn 1948).

## Generating function

`sum_N R_c(N) x^N = prod_k ( 1 + x^{F_k} + ... + x^{F_k F_k} )
                  = prod_k ( x^{F_k(F_k+1)} - 1 ) / ( x^{F_k} - 1 )`

## Research questions

- **(A)** Does `C_c` exist with `log R_c(N) ~ C_c (log N)^2`?
- **(B)** `log R_c(N) = C_c (log N)^2 + c_1 log N loglog N + c_2 log N + osc + o(1)`?
- **(C)** If oscillations exist, are they periodic in `log_phi N`, and with what period?

Primary focus: (A) and (B). (C) is deferred to Phase 6.

## Status of the anchors

| Statement | Status |
|---|---|
| `log R_u(N) ~ (log N)^2 / (2 log phi)` | theorem, cited (CKL 2023) |
| Completeness: no gaps on `[0, sum F_k^2]` | theorem {claim:completeness-no-gaps} |
| `sum_{k<=n} F_k^2 = F_n F_{n+1}` | theorem {claim:sum-of-squares} |
| `C_c = 1 / (4 log phi)` | conjecture {claim:leading-constant} |
| Oscillation structure | open |
```

- [ ] **Step 2: Write `theory/claims.yaml`**

```yaml
- id: convention-duplicated-place
  statement: "The convention F_1 = F_2 = 1 retains two distinct places of value 1."
  status: cited
  evidence: "theory/01-background.md §1.1"
  source: "web-dreamer.de 2009; Lekkerkerker 1952"

- id: place-range
  statement: "R_c(N) ranges over all places F_k <= N, not a fixed length n."
  status: theorem
  evidence: "Direct from the definition; see spec §4.3 Trap 1"
  source: "spec 2026-08-19 §4.3"

- id: sum-of-squares
  statement: "sum_{k<=n} F_k^2 = F_n * F_{n+1}."
  status: theorem
  evidence: "tests/test_fib.py::test_sum_of_squares_identity, n <= 20"
  source: "classical Fibonacci identity"

- id: completeness-no-gaps
  statement: "Every integer in [0, sum_{k<=n} F_k^2] has at least one representation."
  status: theorem
  evidence: "Kempner-Fraenkel condition F_k <= 1 + F_{k-1} F_k; theory/01-background.md §3"
  source: "Fraenkel 1985, Systems of Numeration"

- id: leading-constant
  statement: "log R_c(N) ~ (log N)^2 / (4 log phi)."
  status: conjecture
  evidence: "docs/roadmap.md Phase 3 heuristic; Phase 0.5 numerical support"
  source: "this project"
```

- [ ] **Step 3: Write the failing test**

```python
# tests/test_check_claims.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from check_claims import validate  # noqa: E402

VALID = """- id: alpha
  statement: "A."
  status: theorem
  evidence: "e"
  source: "s"
"""


def _write(root, claims, docs=None):
    (root / "theory").mkdir(parents=True, exist_ok=True)
    (root / "theory" / "claims.yaml").write_text(claims)
    for name, text in (docs or {}).items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)


def test_valid_ledger_passes(tmp_path):
    _write(tmp_path, VALID, {"theory/x.md": "See {claim:alpha}."})
    assert validate(tmp_path) == []


def test_unknown_reference_is_reported(tmp_path):
    _write(tmp_path, VALID, {"theory/x.md": "See {claim:missing}."})
    problems = validate(tmp_path)
    assert any("missing" in p for p in problems)


def test_bad_status_is_reported(tmp_path):
    _write(tmp_path, VALID.replace("theorem", "probably-true"))
    assert any("probably-true" in p for p in validate(tmp_path))


def test_duplicate_id_is_reported(tmp_path):
    _write(tmp_path, VALID + VALID)
    assert any("duplicate" in p.lower() for p in validate(tmp_path))


def test_missing_field_is_reported(tmp_path):
    _write(tmp_path, '- id: alpha\n  statement: "A."\n  status: theorem\n')
    assert any("evidence" in p or "source" in p for p in validate(tmp_path))


def test_verified_numeric_needs_manifest(tmp_path):
    claims = (
        '- id: alpha\n  statement: "A."\n  status: verified-numeric\n'
        '  evidence: "data/results.csv"\n  source: "s"\n'
    )
    _write(tmp_path, claims)
    assert any("manifest" in p for p in validate(tmp_path))
```

- [ ] **Step 4: Run the test to verify it fails**

```bash
pytest tests/test_check_claims.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'check_claims'`.

- [ ] **Step 5: Write the validator**

```python
#!/usr/bin/env python3
"""Validate theory/claims.yaml and every {claim:id} reference in the docs.

The distinction between a heuristic and a theorem is the epistemic content of
this project, and Phase 3 is separated from Phase 5 by months -- long enough
for a conjecture to acquire the tone of a result. This makes that drift
mechanically detectable.
"""

import json
import re
import sys
from pathlib import Path

import yaml

VALID_STATUS = {"cited", "verified-numeric", "heuristic", "conjecture", "theorem", "open"}
REQUIRED_FIELDS = ("id", "statement", "status", "evidence", "source")
REFERENCE = re.compile(r"\{claim:([a-z0-9-]+)\}")
SEARCH_DIRS = ("theory", "docs/phases", "paper")


def validate(root: Path) -> list[str]:
    """Return a list of problems; empty means the ledger is valid."""
    problems: list[str] = []
    ledger_path = root / "theory" / "claims.yaml"
    if not ledger_path.exists():
        return [f"missing ledger: {ledger_path}"]

    claims = yaml.safe_load(ledger_path.read_text()) or []
    ids: set[str] = set()
    for i, claim in enumerate(claims):
        for field in REQUIRED_FIELDS:
            if field not in claim:
                problems.append(f"claim #{i}: missing required field '{field}'")
        cid = claim.get("id", f"#{i}")
        if cid in ids:
            problems.append(f"claim '{cid}': duplicate id")
        ids.add(cid)
        status = claim.get("status")
        if status is not None and status not in VALID_STATUS:
            problems.append(
                f"claim '{cid}': invalid status '{status}'; "
                f"expected one of {sorted(VALID_STATUS)}"
            )

    manifest_path = root / "data" / "manifest.json"
    manifest_files = set()
    if manifest_path.exists():
        manifest_files = {e["file"] for e in json.loads(manifest_path.read_text())}
    for claim in claims:
        if claim.get("status") == "verified-numeric":
            evidence = claim.get("evidence", "")
            if not any(name in evidence for name in manifest_files):
                problems.append(
                    f"claim '{claim.get('id')}': status verified-numeric but its "
                    f"evidence names no file in data/manifest.json"
                )

    for directory in SEARCH_DIRS:
        base = root / directory
        if not base.exists():
            continue
        for md in sorted(base.rglob("*.md")):
            for ref in REFERENCE.findall(md.read_text()):
                if ref not in ids:
                    problems.append(f"{md}: reference to unknown claim '{ref}'")

    return problems


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    problems = validate(root)
    for p in problems:
        print(f"FAIL {p}")
    if problems:
        print(f"\n{len(problems)} problem(s) found.")
        return 1
    print("claims.yaml OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Run the tests and the validator**

```bash
pytest tests/test_check_claims.py -v && python scripts/check_claims.py
```
Expected: 6 tests PASS, then `claims.yaml OK`.

- [ ] **Step 7: Commit**

```bash
git add theory/ scripts/check_claims.py tests/test_check_claims.py
git commit -m "feat: add Phase 0 definitions and the claim ledger with validator"
```

---

### Task 12: The Phase 0.5 constant gate

The deliverable that decides whether the roadmap's conjectured constant survives contact with numbers, before any month-scale investment.

**Files:**
- Create: `scripts/run_phase0_gate.py`, `docs/phases/phase0_5_gate.md`
- Modify: `theory/claims.yaml`

**Interfaces:**
- Consumes: `saddle.log_R_bound`, `manifest.record`
- Produces: `data/phase0_5_gate.csv`, `figures/phase0_5_gate.png`

- [ ] **Step 1: Write the gate script**

```python
#!/usr/bin/env python3
"""Phase 0.5 -- measure the leading constant before developing the heuristic.

Candidates:
    1 / (2 log phi) = 1.03904   (no cap effect; Coons-Kristensen-Laursen)
    1 / (4 log phi) = 0.51952   (roadmap Phase 3 conjecture)
    1 / (8 log phi) = 0.25976   (naive count; a lower bound only)

The estimator is the local slope d(log R)/d((log N)^2), which converges far
faster than the plain ratio log R / (log N)^2.
"""

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from capfib.manifest import record  # noqa: E402
from capfib.saddle import log_R_bound  # noqa: E402

PHI = (1 + 5 ** 0.5) / 2
LOG_PHI = math.log(PHI)
EXPONENTS = [50, 100, 200, 400, 800, 1600, 3200]
DATA = Path("data/phase0_5_gate.csv")
FIGURE = Path("figures/phase0_5_gate.png")


def main() -> None:
    rows = []
    prev = None
    for e in EXPONENTS:
        log_n = e * math.log(10)
        value = log_R_bound(log_n)
        sq = log_n * log_n
        slope = "" if prev is None else (value - prev[0]) / (sq - prev[1])
        rows.append({
            "log10_N": e,
            "log_R_bound": value,
            "ratio": value / sq,
            "local_slope": slope,
        })
        prev = (value, sq)
        print(f"1e{e:<6} log R = {value:16.2f}  ratio = {value / sq:.6f}  slope = {slope}")

    DATA.parent.mkdir(parents=True, exist_ok=True)
    with DATA.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    slopes = [(r["log10_N"], r["local_slope"]) for r in rows if r["local_slope"] != ""]
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot([x for x, _ in slopes], [y for _, y in slopes], "o-", label="local slope")
    for c, lab in ((2, "1/(2 log phi)"), (4, "1/(4 log phi)"), (8, "1/(8 log phi)")):
        ax.axhline(1 / (c * LOG_PHI), ls="--", lw=1, label=lab)
    ax.set_xscale("log")
    ax.set_xlabel("log10 N")
    ax.set_ylabel("d(log R) / d((log N)^2)")
    ax.set_title("Phase 0.5: leading constant of log R_c(N)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=150)

    final = slopes[-1][1]
    print(f"\nfinal local slope: {final:.6f}")
    print(f"1/(4 log phi):     {1 / (4 * LOG_PHI):.6f}")
    print(f"absolute error:    {abs(final - 1 / (4 * LOG_PHI)):.6f}")

    record(DATA, script="scripts/run_phase0_gate.py",
           params={"exponents": EXPONENTS})
    record(FIGURE, script="scripts/run_phase0_gate.py",
           params={"exponents": EXPONENTS})


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the gate**

```bash
python scripts/run_phase0_gate.py
```
Expected output, measured (runtime about 5 seconds):

```
1e50     log R =          6448.44  ratio = 0.486501  slope =
1e100    log R =         26492.02  ratio = 0.499671  slope = 0.5040604944327807
1e200    log R =        107726.88  ratio = 0.507964  slope = 0.5107281136887548
1e400    log R =        435128.26  ratio = 0.512939  slope = 0.5145977556107495
1e800    log R =       1750331.78  ratio = 0.515833  slope = 0.5167974332417503
1e1600   log R =       7023680.67  ratio = 0.517480  slope = 0.5180287928977025
1e3200   log R =      28144812.80  ratio = 0.518402  slope = 0.518709970676109

final local slope: 0.518710
1/(4 log phi):     0.519522
absolute error:    0.000812
```

Note how much better the local slope is than the plain ratio as an estimator: the ratio has
only reached 0.5184 while the slope is at 0.5187 and still climbing toward 0.519522.

If the slope instead sits near 0.26 or 1.04, stop and report — that overturns the roadmap's
conjecture and is exactly what this gate exists to catch.

- [ ] **Step 3: Write the phase report**

```markdown
# Phase 0.5 — Constant Gate

**Question.** Which of the candidate leading constants does `log R_c(N)` follow?

**Method.** `log R_c(N) <= min_s [ s N + log F_c(e^-s) ]`, evaluated by ternary
search on `log s` with the generating function computed in pure log space. The
leading `(log N)^2` coefficient of the Legendre transform is the leading
coefficient of `log R_c(N)`; the correction is of lower order. The estimator is
the local slope `d(log R)/d((log N)^2)`, because the plain ratio converges too
slowly to separate the candidates.

**Result.** See `data/phase0_5_gate.csv` and `figures/phase0_5_gate.png`. The
local slope rises monotonically to **0.518710** at `N = 10^3200`, against
`1/(4 log phi) = 0.519522`. Because `log_R_bound` is a Chernoff *upper* bound, this
excludes `1/(2 log phi) = 1.039` outright; excluding `1/(8 log phi) = 0.260`
additionally requires the saddle-point correction to be of lower order, which
Phase 5 must establish.

**Reading.** This supports the roadmap's Phase 3 conjecture
{claim:leading-constant}. The `1/(8 log phi)` figure obtainable from the §4
count of `theory/01-background.md` is a lower bound only — that count fixes the
numeral length at `n`, which undercounts `R_c(N)`.

**Status.** Numerical support for a conjecture. Not a proof. Phase 3 must still
derive the constant from the saddle-point heuristic, and Phase 5 must still
establish it rigorously.

**Consequence for the roadmap.** Phase 3 proceeds. Its job is now to explain a
measured number rather than to predict an unknown one.
```

- [ ] **Step 4: Add the ledger entry**

Change the `evidence` line of the existing `leading-constant` entry from

```yaml
  evidence: "docs/roadmap.md Phase 3 heuristic; Phase 0.5 numerical support"
```

to

```yaml
  evidence: "docs/roadmap.md Phase 3 heuristic; see claim gate-local-slope"
```

The status stays `conjecture` — numerical support never promotes a conjecture to a theorem.
Then append:

```yaml
- id: gate-local-slope
  statement: "The Legendre-transform local slope approaches 1/(4 log phi), excluding 1/(2 log phi) and 1/(8 log phi)."
  status: verified-numeric
  evidence: "data/phase0_5_gate.csv via scripts/run_phase0_gate.py"
  source: "docs/phases/phase0_5_gate.md"
```

- [ ] **Step 5: Verify the ledger still validates**

```bash
python scripts/check_claims.py
```
Expected: `claims.yaml OK`. The `verified-numeric` entry passes only because `data/manifest.json` now contains `phase0_5_gate.csv`.

- [ ] **Step 6: Commit**

```bash
git add scripts/run_phase0_gate.py docs/phases/phase0_5_gate.md theory/claims.yaml data/manifest.json
git commit -m "feat: add Phase 0.5 constant gate

Measures the leading constant of log R_c(N) by numerical Legendre transform.
The local slope approaches 1/(4 log phi), supporting the roadmap conjecture
and excluding both alternatives."
```

---

### Task 13: The two blocking skills

**Files:**
- Create: `.claude/skills/rc-numerics/SKILL.md`, `.claude/skills/claim-ledger/SKILL.md`

- [ ] **Step 1: Write `.claude/skills/rc-numerics/SKILL.md`**

```markdown
---
name: rc-numerics
description: Use when computing, regenerating, or reporting any numerical result about R_c(N) — DP counts, generating-function evaluations, saddle-point estimates, fits, or figures.
---

# Running numerics for R_c(N)

## The gate comes first

Before any numeric result is reported, run:

```bash
pytest tests/test_brute.py tests/test_dp.py tests/test_gf.py -q
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
   `python scripts/check_claims.py`.
```

- [ ] **Step 2: Write `.claude/skills/claim-ledger/SKILL.md`**

```markdown
---
name: claim-ledger
description: Use when adding, editing, or citing a mathematical statement in theory/, docs/phases/, or paper/ — keeps conjectures, heuristics and theorems distinguishable.
---

# The claim ledger

Every mathematical statement in this project lives in `theory/claims.yaml` with
an explicit epistemic status. Documents cite claims as `{claim:some-id}`.

## Statuses

| Status | Meaning |
|---|---|
| `cited` | Established elsewhere; `source` names the reference |
| `verified-numeric` | Supported by computation; `evidence` names a file in `data/manifest.json` |
| `heuristic` | Derived by a non-rigorous argument |
| `conjecture` | Believed, not derived |
| `theorem` | Proved, here or in a cited source |
| `open` | Stated, unresolved |

## Rules

1. **A new statement gets a ledger entry before it appears in prose.**
2. **Never promote a status without the corresponding work.** Numerical support
   makes a conjecture `verified-numeric` at most — never `theorem`.
3. **`verified-numeric` requires provenance.** The `evidence` field must name a
   file present in `data/manifest.json`, or the validator fails.
4. Run `python scripts/check_claims.py` after every edit to `theory/claims.yaml`
   or to any document citing a claim.

The distinction this enforces is the epistemic content of the project. Phase 3
produces a heuristic; Phase 5 produces the theorem. Months separate them —
long enough for the difference to blur without a mechanical check.
```

- [ ] **Step 3: Verify both skills load**

```bash
head -5 .claude/skills/rc-numerics/SKILL.md .claude/skills/claim-ledger/SKILL.md
python scripts/check_claims.py
```
Expected: both files show valid YAML frontmatter with `name` and `description`; validator prints `claims.yaml OK`.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/
git commit -m "feat: add rc-numerics and claim-ledger skills"
```

---

### Task 14: Retarget the Lean development

Lean narrows to what is honestly formalisable. The asymptotic theorems of Phases 5 and 6 are not Lean targets and must not be added as `sorry` stubs pretending otherwise.

**Files:**
- Create: `lean/NonLinearNumberSystems/Numeration.lean`, `lean/NonLinearNumberSystems/Completeness.lean`, `lean/NonLinearNumberSystems/Bounds.lean`
- Modify: `lean/NonLinearNumberSystems/Basic.lean`, `lean/NonLinearNumberSystems/Fibonacci.lean`

- [ ] **Step 1: Read the existing files**

```bash
cat lean/NonLinearNumberSystems/Basic.lean lean/NonLinearNumberSystems/Fibonacci.lean lean/NonLinearNumberSystems/Theorems.lean
```

- [ ] **Step 2: Rename `Fibonacci.lean` to `Zeckendorf.lean`**

The existing content is Zeckendorf statements, which are retained because they feed open problems 3 and 4 of `theory/01-background.md`.

```bash
git mv lean/NonLinearNumberSystems/Fibonacci.lean lean/NonLinearNumberSystems/Zeckendorf.lean
```

Update the module docstring and the `namespace` header to match, and fix the `import` line in `Theorems.lean`.

- [ ] **Step 3: Write `Numeration.lean`**

```lean
/-
  NonLinearNumberSystems.Numeration
  =================================
  The capacity-constrained Fibonacci numeration system.

  Convention: F 1 = 1, F 2 = 1, F 3 = 2, ...  (Mathlib's `Nat.fib` with the
  index shifted by one: our F k is `Nat.fib k` for k >= 1.)

  Reference: theory/00-definitions.md
-/

import Mathlib.Tactic
import Mathlib.Combinatorics.Enumerative.Partition

namespace NonLinearNumberSystems

/-- The place value at position `k` (one-indexed): `F 1 = F 2 = 1`. -/
def place (k : ℕ) : ℕ := Nat.fib k

/-- A numeral of length `n` is a digit function bounded by the place values. -/
structure Numeral (n : ℕ) where
  digit : Fin n → ℕ
  capped : ∀ i : Fin n, digit i ≤ place (i.val + 1)

/-- The value of a numeral. -/
def Numeral.value {n : ℕ} (d : Numeral n) : ℕ :=
  ∑ i : Fin n, d.digit i * place (i.val + 1)

end NonLinearNumberSystems
```

- [ ] **Step 4: Write `Completeness.lean`**

```lean
/-
  NonLinearNumberSystems.Completeness
  ===================================
  The system represents every integer in [0, F_n * F_{n+1}] without gaps.

  Reference: Fraenkel, "Systems of Numeration", Amer. Math. Monthly 92 (1985);
  theory/01-background.md §3.
-/

import NonLinearNumberSystems.Numeration

namespace NonLinearNumberSystems

open Finset

/-- `∑_{k ≤ n} F_k² = F_n · F_{n+1}`. Fixes the range of representable values. -/
theorem sum_sq_place (n : ℕ) :
    ∑ k ∈ range n, place (k + 1) * place (k + 1) = place n * place (n + 1) := by
  sorry  -- induction on n; Nat.fib_add_two

/-- **Completeness.** Every integer up to `∑ F_k²` has a representation.
    Follows from the Kempner–Fraenkel condition `F_k ≤ 1 + F_{k-1} · F_k`,
    which holds here with large slack. -/
theorem exists_numeral_of_le (n N : ℕ)
    (h : N ≤ ∑ k ∈ range n, place (k + 1) * place (k + 1)) :
    ∃ d : Numeral n, d.value = N := by
  sorry  -- greedy algorithm; induction on n using sum_sq_place
```

- [ ] **Step 5: Write `Bounds.lean`**

```lean
/-
  NonLinearNumberSystems.Bounds
  =============================
  Elementary bounds on the counting function. Phase 2 targets.

  The asymptotic theorems of Phases 5 and 6 are NOT Lean targets -- Mellin
  transforms and analytic continuation of ζ_F are far outside what Mathlib
  makes practical. Those live in paper/.
-/

import NonLinearNumberSystems.Numeration

namespace NonLinearNumberSystems

/-- `R_c n N` -- the number of length-`n` numerals with value `N`. -/
noncomputable def countReps (n N : ℕ) : ℕ :=
  Nat.card {d : Numeral n // d.value = N}

/-- Capping digits cannot increase the number of representations. -/
theorem countReps_le_uncapped (n N : ℕ) :
    countReps n N ≤ Nat.card {f : Fin n → ℕ // ∑ i, f i * place (i.val + 1) = N} := by
  sorry  -- the inclusion of capped into uncapped digit functions is injective

end NonLinearNumberSystems
```

- [ ] **Step 6: Build**

```bash
cd lean && lake build 2>&1 | tail -20
```
Expected: build succeeds with `declaration uses 'sorry'` warnings and no errors. If Mathlib is not yet fetched this takes roughly 10 minutes on first run.

- [ ] **Step 7: Commit**

```bash
git add lean/
git commit -m "refactor: retarget Lean to the elementary results

Numeration, completeness and elementary bounds. The asymptotic theorems are
explicitly not Lean targets. Existing Zeckendorf statements retained."
```

---

### Task 15: Update the roadmap to the revised sequence

Spec §6 revises the phase plan; `docs/roadmap.md` must reflect it or the two documents
disagree about what happens next.

**Files:**
- Modify: `docs/roadmap.md`

- [ ] **Step 1: Fix the convention in Phase 0**

Find the Phase 0 "Fibonacci-Konvention" item, which currently reads:

> Beispiel: $F_1=1, F_2=2, F_3=3, F_4=5, F_5=8, \ldots$ (Standard; aber Konsistenz über alle Phasen überprüfen).
> **Konsequenz:** $d_1 \in \{0,1\}$, da der Cap für Position 1 den Wert $F_1=1$ hat.

Replace with:

> **Festgelegt:** $F_1=1, F_2=1, F_3=2, F_4=3, F_5=5, \ldots$ — siehe `theory/00-definitions.md`.
> Die doppelte 1-Stelle ist beabsichtigt: sie ist der Ursprung des "1 > 1"-Phänomens
> (Numerale `1000` und `0100` haben beide den Wert 1), und nur unter dieser Konvention
> gilt $\sum_{k\le n} F_k^2 = F_n F_{n+1}$, das die Vollständigkeitsschranke fixiert.
> **Konsequenz:** $d_1, d_2 \in \{0,1\}$.

- [ ] **Step 2: Replace the gap hunt in Phase 1**

Find the Phase 1 bullet:

> - **Lückenstruktur:** An welchen $N$ gilt $R_c(N)=0$? (Erwartet: $N\ge\sum_k F_k(F_k+1)$ oder ähnliche Schwellen, wenn Cap *alle* Positionen bindet.)

Replace with:

> - **Vollständigkeit (erledigt):** Es gibt *keine* Lücken. Die Kempner–Fraenkel-Bedingung
>   $F_k \le 1 + F_{k-1}F_k$ ist mit großem Spielraum erfüllt, also ist jedes $N \in [0, \sum_k F_k^2]$
>   darstellbar (`theory/01-background.md` §3, numerisch bestätigt in `tests/test_dp.py`).
>   Aufgabe ist daher der *Beweis* der Vollständigkeit (Phase 2, Lean-Ziel), nicht die Suche nach Lücken.

- [ ] **Step 3: Insert Phase 0.5 before Phase 1**

Add a new section between Phase 0 and Phase 1:

```markdown
## Phase 0.5 — Konstanten-Gate

**Zeithorizont:** 1 Tag
**Kritikalität:** HOCH — Entscheidungspunkt vor jeder monatelangen Investition

### Ziel

Die führende Konstante $C_c$ *messen*, bevor die Heuristik sie *herleitet*.

### Substanz

Direkte Auswertung von $\log F_c(e^{-s})$ im Log-Raum plus numerische
Legendre-Transformation $\log R_c(N) \le \min_s [sN + \log F_c(e^{-s})]$.
Schätzer ist die lokale Steigung $d(\log R)/d((\log N)^2)$, die weit schneller
konvergiert als das Verhältnis $\log R/(\log N)^2$.

Kandidaten: $1/(2\log\varphi)=1.039$, $1/(4\log\varphi)=0.520$, $1/(8\log\varphi)=0.260$.

### Deliverables

`scripts/run_phase0_gate.py`, `data/phase0_5_gate.csv`, `figures/phase0_5_gate.png`,
`docs/phases/phase0_5_gate.md`.

### Konsequenz

Phase 3 erklärt danach eine *gemessene* Zahl statt eine unbekannte vorherzusagen.
```

- [ ] **Step 4: Update the critical-path diagram**

In the "Kritischer Pfad und Priorisierung" code block, insert `Phase 0.5 (1 Tag)` between
`Phase 0 (1–2 Tage)` and `Phase 1 (1–2 Wochen)`.

- [ ] **Step 5: Note the numerical support in Phase 3**

At the end of Phase 3's "Konjektur-Statement", append:

> **Numerische Stütze (Phase 0.5):** Die lokale Steigung der Legendre-Transformierten misst
> 0.518710 bei $N = 10^{3200}$ und steigt monoton gegen $1/(4\log\varphi) = 0.519522$.
> Da es sich um eine *obere* Schranke handelt, schließt dies $1/(2\log\varphi)$ unmittelbar aus;
> der Ausschluss von $1/(8\log\varphi)$ setzt zusätzlich voraus, dass die Sattelpunkt-Korrektur
> von niedrigerer Ordnung ist — erwartet, aber in Phase 0.5 nicht bewiesen.
> Siehe `docs/phases/phase0_5_gate.md`. Das bleibt eine Konjektur — Phase 5 muss sie beweisen.

- [ ] **Step 6: Verify the roadmap no longer contradicts the definitions**

```bash
grep -n 'F_2=2' docs/roadmap.md
grep -n 'Lückenstruktur' docs/roadmap.md
grep -n 'Phase 0.5' docs/roadmap.md
```
Expected: no output for the first two; at least two hits for the third.

- [ ] **Step 7: Commit**

```bash
git add docs/roadmap.md
git commit -m "docs: align roadmap with the revised phase sequence

Fixes the Fibonacci convention to F_1 = F_2 = 1, replaces the Phase 1 gap
search with the completeness proof target, and inserts Phase 0.5."
```

---

### Task 16: Final verification against the spec

**Files:**
- Modify: none expected. Fix whatever fails.

- [ ] **Step 1: Success criterion 1 — the tree matches the docs**

```bash
test ! -d benchmarks && test ! -d harnesses && test ! -d tools && echo "removed OK"
grep -rn -E 'benchmarks/|harnesses/|lean_dojo|miniF2F|ProofNet|math_benchmark' \
  README.md CLAUDE.md
```
Expected: `removed OK`, then no grep output.

- [ ] **Step 2: Success criterion 2 — the full suite passes**

```bash
pytest -q
```
Expected: all tests pass. `tests/test_saddle.py` is the slow one.

- [ ] **Step 3: Success criterion 3 — the gate reproduces**

```bash
python scripts/run_phase0_gate.py && test -f data/phase0_5_gate.csv && test -f figures/phase0_5_gate.png && echo "gate OK"
python -c "import json; print(len(json.load(open('data/manifest.json'))), 'manifest entries')"
```
Expected: the final local slope near 0.5187, `gate OK`, and at least 2 manifest entries.

- [ ] **Step 4: Success criterion 4 — definitions exist and fix the convention**

```bash
grep -c 'F_10 = 55' theory/00-definitions.md
```
Expected: `1`.

- [ ] **Step 5: Success criterion 5 — skills exist and the ledger validates**

```bash
test -f .claude/skills/rc-numerics/SKILL.md && test -f .claude/skills/claim-ledger/SKILL.md && echo "skills OK"
python scripts/check_claims.py
```
Expected: `skills OK`, then `claims.yaml OK`.

- [ ] **Step 6: Commit any fixes and report**

```bash
git status --short
```
Expected: clean, or a final commit of fixes.

Report which of the five spec §10 criteria pass, with the actual command output for each. Do not claim completion for a criterion whose command was not run.
