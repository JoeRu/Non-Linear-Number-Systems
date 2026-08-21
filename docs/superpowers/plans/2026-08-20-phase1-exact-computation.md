# Phase 1 — Exact Computation of R_c(N): Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce exact `R_c(N)` data to `N = 10^6` with the structural analyses Phase 1 exists for — monotonicity, fluctuation, extremal `N`, place-value jumps, and the summatory function — each licensed by a full-range cross-check between two independent algorithms.

**Architecture:** Pure, unit-tested analysis functions in `capfib/stats.py` operate on a counts array. `scripts/run_phase1.py` orchestrates: compute the array with both `gf` and `dp`, compare every coefficient as a precondition, run the analyses, and write artifacts atomically with provenance. No new numerics — the existing `capfib.gf.coefficients` is fast enough (~12 s at `10^6`).

**Tech Stack:** Python 3.11+, numpy, matplotlib, pytest. Exact Python integers throughout; no floating point in any counting path.

**Spec:** `docs/superpowers/specs/2026-08-20-phase1-exact-computation-design.md`

**Verification status:** Every Python module and test in Tasks 1-4 was extracted
from this plan and executed before it was committed — 21 tests, all passing, in
~2 s. Every expected value quoted here (the census figures, `S_c(0..20)`, the
place-jump ratios including the two awkward ones, the block-extrema table with
its ties) was computed and checked, not estimated.

## Global Constraints

- Python >= 3.11. System Python is externally managed — use `.venv/bin/python` and `.venv/bin/pytest`.
- **The Fibonacci convention is F_1 = 1, F_2 = 1, F_3 = 2, F_4 = 3, F_5 = 5, …** Place values are constructed in `capfib/fib.py` and **nowhere else**.
- `R_c(N)` counts digit tuples over **all** places `F_k <= N`, never a fixed length `n`.
- **The §4.2 gate:** no `capfib.dp`/`capfib.gf` output may appear in any report, figure, or claim until dp has matched brute for all N <= 200 and dp and gf have matched each other for all N <= 500.
- **New in this phase (spec §3.4):** reporting values *beyond* that pointwise-verified range additionally requires `dp` and `gf` to agree pointwise **over the whole reported range, in the same run that produces the data**. The global checksum is explicitly NOT sufficient.
- Every generated dataset writes an entry to `data/manifest.json`.
- Counting paths use exact Python ints. Floats appear only in derived ratios and logs.
- Commit at the end of every task.

## File Structure

| File | Responsibility |
|---|---|
| `capfib/stats.py` | Pure analysis functions over a counts array. No I/O, no plotting, no globals. |
| `capfib/gf.py` (modify) | Add `checksum_ok` — a regression invariant, not a licence. |
| `scripts/run_phase1.py` | Orchestration: cross-check precondition, analyses, atomic artifact writes, manifest. |
| `tests/test_stats.py` | Unit tests for every analysis function. |
| `tests/test_checksum.py` | The checksum's blind spot and the cross-check that covers it. |
| `docs/phases/phase1_report.md` | Prose deliverable. Hand-written. |

**Reference values used throughout this plan** (all verified before writing it, on commit `5659e4a`):

```
R_c(0..20) = [1, 2, 2, 3, 4, 5, 6, 6, 8, 10, 11, 13, 13, 15, 18, 18, 21, 23, 25, 29, 29]
S_c(0..20) = [1, 3, 5, 8, 12, 17, 23, 29, 37, 47, 58, 71, 84, 99, 117, 135, 156, 179, 204, 233, 262]
distinct places <= 20: [1, 2, 3, 5, 8, 13]
```

---

### Task 1: `monotonicity_census` and `summatory`

**Files:**
- Create: `capfib/stats.py`, `tests/test_stats.py`

**Interfaces:**
- Consumes: nothing from earlier tasks
- Produces: `stats.monotonicity_census(counts) -> dict[str, int]` with keys `increasing`, `flat`, `decreasing`, `steps`; `stats.summatory(counts) -> list[int]`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_stats.py
from capfib.gf import coefficients
from capfib.stats import monotonicity_census, summatory


def test_census_partitions_steps():
    """The three counts must exhaust the steps -- no step is uncounted."""
    for n_max in (5, 50, 500):
        c = coefficients(n_max)
        cen = monotonicity_census(c)
        assert cen["increasing"] + cen["flat"] + cen["decreasing"] == cen["steps"]
        assert cen["steps"] == n_max


def test_census_hand_checked_to_20():
    """R_c(0..20) is hand-verified in tests/test_brute.py. No step decreases yet."""
    assert monotonicity_census(coefficients(20)) == {
        "increasing": 15, "flat": 5, "decreasing": 0, "steps": 20,
    }


def test_census_finds_decreases_by_100():
    """The first decrease is at N=41, so a range to 100 must show some."""
    assert monotonicity_census(coefficients(100)) == {
        "increasing": 78, "flat": 11, "decreasing": 11, "steps": 100,
    }


def test_census_empty_and_single():
    assert monotonicity_census([1]) == {
        "increasing": 0, "flat": 0, "decreasing": 0, "steps": 0,
    }


def test_summatory_hand_checked():
    assert summatory(coefficients(20)) == [
        1, 3, 5, 8, 12, 17, 23, 29, 37, 47, 58, 71, 84, 99, 117, 135, 156,
        179, 204, 233, 262,
    ]


def test_summatory_is_exact_ints_and_monotone():
    s = summatory(coefficients(500))
    assert all(type(x) is int for x in s)
    assert s == sorted(s)  # non-decreasing, since R_c >= 0


def test_summatory_last_is_total():
    c = coefficients(200)
    assert summatory(c)[-1] == sum(c)
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
.venv/bin/pytest tests/test_stats.py -q
```
Expected: FAIL — `ModuleNotFoundError: No module named 'capfib.stats'`.

- [ ] **Step 3: Write the implementation**

```python
# capfib/stats.py
"""Descriptive analyses of the counting function R_c.

Pure functions over a counts array -- no I/O, no plotting, no globals -- so
that every one is unit-testable against hand-checked values. This is where
off-by-one errors would otherwise hide: a miscounted "decreasing step" would
silently change which route Phase 5 takes.
"""

from collections.abc import Sequence


def monotonicity_census(counts: Sequence[int]) -> dict[str, int]:
    """Classify each step `counts[n-1] -> counts[n]` for n = 1 .. len-1.

    The three counts always sum to `steps`; the tests assert it.
    """
    increasing = flat = decreasing = 0
    for n in range(1, len(counts)):
        if counts[n] > counts[n - 1]:
            increasing += 1
        elif counts[n] == counts[n - 1]:
            flat += 1
        else:
            decreasing += 1
    return {
        "increasing": increasing,
        "flat": flat,
        "decreasing": decreasing,
        "steps": max(0, len(counts) - 1),
    }


def summatory(counts: Sequence[int]) -> list[int]:
    """S_c(N) = sum_{n <= N} R_c(n), exact.

    Phase 5 Route B needs this: R_c itself fluctuates too much for a direct
    Tauberian attack, while S_c is non-decreasing by construction.
    """
    out: list[int] = []
    running = 0
    for x in counts:
        running += x
        out.append(running)
    return out
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
.venv/bin/pytest tests/test_stats.py -q
```
Expected: PASS, 7 tests.

- [ ] **Step 5: Commit**

```bash
git add capfib/stats.py tests/test_stats.py
git commit -m "feat: add monotonicity census and summatory function"
```

---

### Task 2: `local_ratios` and `place_jumps`

**Files:**
- Modify: `capfib/stats.py`
- Modify: `tests/test_stats.py`

**Interfaces:**
- Consumes: `capfib.fib.places_up_to`
- Produces: `stats.local_ratios(counts) -> list[float]` of length `len(counts)-1`; `stats.place_jumps(counts) -> list[dict]` with keys `place`, `ratio`

- [ ] **Step 1: Write the failing test**

The place-jump values below were computed exhaustively during planning. **Two of them are deliberately awkward and must not be "cleaned up":** the ratio at `F = 2` is exactly `1.0`, and the sequence is *not* monotone — it rises at `F = 3` and again at `F = 8`. An earlier draft of the spec claimed decay at every place; that came from a sample starting at `F = 13`. These tests pin the real behaviour.

```python
# append to tests/test_stats.py
import math

import pytest

from capfib.stats import local_ratios, place_jumps


def test_local_ratios_length_and_indices():
    c = coefficients(50)
    r = local_ratios(c)
    assert len(r) == len(c) - 1 == 50
    assert r[0] == pytest.approx(c[1] / c[0])
    assert r[-1] == pytest.approx(c[50] / c[49])


def test_local_ratios_all_finite():
    """Guarded by min(counts) >= 1, asserted at runtime -- not by appealing to
    completeness, which is still a `sorry` in Lean."""
    r = local_ratios(coefficients(2000))
    assert all(math.isfinite(x) for x in r)


def test_local_ratios_rejects_zero_count():
    with pytest.raises(AssertionError):
        local_ratios([1, 0, 1])


def test_place_jumps_skips_F_equals_one_and_dedupes():
    """F_1 = F_2 = 1 is one distinct place, and F = 1 has no F-1 in range."""
    jumps = place_jumps(coefficients(20))
    assert [j["place"] for j in jumps] == [2, 3, 5, 8, 13]


def test_place_jumps_exact_values():
    c = coefficients(20)
    jumps = {j["place"]: j["ratio"] for j in place_jumps(c)}
    assert jumps[2] == pytest.approx(2 / 2)      # exactly 1.0 -- NOT > 1
    assert jumps[3] == pytest.approx(3 / 2)
    assert jumps[5] == pytest.approx(5 / 4)
    assert jumps[8] == pytest.approx(8 / 6)
    assert jumps[13] == pytest.approx(15 / 13)


def test_place_jumps_not_monotone_below_13():
    """Pins the two known exceptions so nobody 'fixes' them into a false law."""
    ratios = {j["place"]: j["ratio"] for j in place_jumps(coefficients(100_000))}
    assert ratios[2] == pytest.approx(1.0)
    assert ratios[3] > ratios[2]   # rises
    assert ratios[5] < ratios[3]
    assert ratios[8] > ratios[5]   # rises again
    # monotone decay only from F = 13 onward
    tail = [r for f, r in sorted(ratios.items()) if f >= 13]
    assert tail == sorted(tail, reverse=True)
    assert all(r > 1.0 for r in tail)
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
.venv/bin/pytest tests/test_stats.py -q
```
Expected: FAIL — `ImportError: cannot import name 'local_ratios' from 'capfib.stats'`.

- [ ] **Step 3: Write the implementation**

```python
# append to capfib/stats.py -- and add this import at the top of the file:
# from capfib.fib import places_up_to


def local_ratios(counts: Sequence[int]) -> list[float]:
    """r[n] = counts[n+1] / counts[n] for n = 0 .. len-2.

    The division is guarded by an explicit assertion rather than by appealing
    to completeness: completeness is still a `sorry` in the Lean development,
    so it is not something this code may lean on.
    """
    assert min(counts) >= 1, "counts must be positive; local_ratios would divide by zero"
    return [counts[n + 1] / counts[n] for n in range(len(counts) - 1)]


def place_jumps(counts: Sequence[int]) -> list[dict]:
    """R_c(F)/R_c(F-1) at each distinct place value F >= 2.

    Distinctness matters: F_1 = F_2 = 1 is a single place, and F = 1 has no
    predecessor in range.

    The result is NOT monotone. Measured: the ratio is exactly 1.0 at F = 2,
    rises at F = 3 and again at F = 8, and only decays monotonically from
    F = 13 onward. Reporting it as a clean decay law would be wrong.
    """
    n_max = len(counts) - 1
    out: list[dict] = []
    for place in sorted(set(places_up_to(n_max))):
        if place < 2:
            continue
        out.append({"place": place, "ratio": counts[place] / counts[place - 1]})
    return out
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
.venv/bin/pytest tests/test_stats.py -q
```
Expected: PASS, 13 tests (7 from Task 1 + 6 here).

- [ ] **Step 5: Commit**

```bash
git add capfib/stats.py tests/test_stats.py
git commit -m "feat: add local ratios and place jumps

place_jumps is deliberately tested as non-monotone: the ratio is exactly 1.0
at F=2 and rises at F=3 and F=8. Decay holds only from F=13 onward."
```

---

### Task 3: `block_extrema`

**Files:**
- Modify: `capfib/stats.py`
- Modify: `tests/test_stats.py`

**Interfaces:**
- Consumes: `capfib.fib.places_up_to`
- Produces: `stats.block_extrema(counts) -> list[dict]` with keys `lo`, `hi`, `argmax`, `max`, `argmin`, `min`

- [ ] **Step 1: Write the failing test**

Reference values computed exhaustively during planning for `n_max = 20`. Blocks `[5,8)` and `[8,13)` and `[13,21)` all contain ties, which is what exercises the tie rule.

```python
# append to tests/test_stats.py
from capfib.stats import block_extrema


def test_block_extrema_hand_checked_to_20():
    blocks = block_extrema(coefficients(20))
    got = [(b["lo"], b["hi"], b["argmax"], b["max"], b["argmin"], b["min"]) for b in blocks]
    assert got == [
        (1, 2, 1, 2, 1, 2),
        (2, 3, 2, 2, 2, 2),
        (3, 5, 4, 4, 3, 3),
        (5, 8, 6, 6, 5, 5),      # counts 5,6,6 -> max ties at 6 and 7, take 6
        (8, 13, 11, 13, 8, 8),   # counts 8,10,11,13,13 -> max ties at 11 and 12, take 11
        (13, 21, 19, 29, 13, 15),# counts ...,29,29 -> max ties at 19 and 20, take 19
    ]


def test_block_extrema_no_degenerate_first_block():
    """F_1 = F_2 = 1 must not produce two blocks starting at 1."""
    los = [b["lo"] for b in block_extrema(coefficients(20))]
    assert len(los) == len(set(los))
    assert los[0] == 1


def test_block_extrema_ties_go_to_smallest_n():
    counts = [1, 5, 5, 5, 5, 5, 5, 5, 5]  # n_max = 8, all equal within blocks
    for b in block_extrema(counts):
        assert b["argmax"] == b["lo"]
        assert b["argmin"] == b["lo"]


def test_block_extrema_exhaustive_against_direct_scan():
    """Independent re-derivation by brute scan, for n_max = 2000."""
    from capfib.fib import places_up_to
    c = coefficients(2000)
    places = sorted(set(places_up_to(2000)))
    expected = []
    for i, lo in enumerate(places):
        hi = min(places[i + 1] if i + 1 < len(places) else 2001, 2001)
        best_n = best_v = None
        worst_n = worst_v = None
        for n in range(lo, hi):
            if best_v is None or c[n] > best_v:
                best_n, best_v = n, c[n]
            if worst_v is None or c[n] < worst_v:
                worst_n, worst_v = n, c[n]
        expected.append((lo, hi, best_n, best_v, worst_n, worst_v))
    got = [(b["lo"], b["hi"], b["argmax"], b["max"], b["argmin"], b["min"])
           for b in block_extrema(c)]
    assert got == expected
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
.venv/bin/pytest tests/test_stats.py -q
```
Expected: FAIL — `ImportError: cannot import name 'block_extrema'`.

- [ ] **Step 3: Write the implementation**

```python
# append to capfib/stats.py


def block_extrema(counts: Sequence[int]) -> list[dict]:
    """Argmax/argmin of R_c within each Fibonacci block.

    Blocks run between consecutive DISTINCT place values -- F_1 = F_2 = 1
    would otherwise yield a degenerate duplicate first block. Ties are broken
    toward the smallest N so results are reproducible.

    Progress on open problem 2 of theory/01-background.md section 14: which
    integers carry the most and fewest representations.
    """
    n_max = len(counts) - 1
    places = [p for p in sorted(set(places_up_to(n_max))) if p <= n_max]
    out: list[dict] = []
    for i, lo in enumerate(places):
        hi = min(places[i + 1] if i + 1 < len(places) else n_max + 1, n_max + 1)
        block = range(lo, hi)
        argmax = min(block, key=lambda n: (-counts[n], n))
        argmin = min(block, key=lambda n: (counts[n], n))
        out.append({
            "lo": lo, "hi": hi,
            "argmax": argmax, "max": counts[argmax],
            "argmin": argmin, "min": counts[argmin],
        })
    return out
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
.venv/bin/pytest tests/test_stats.py -q
```
Expected: PASS, 17 tests (13 + 4 here).

- [ ] **Step 5: Commit**

```bash
git add capfib/stats.py tests/test_stats.py
git commit -m "feat: add per-block extremal N with deterministic tie-breaking"
```

---

### Task 4: `checksum_ok` and its documented blind spot

**Files:**
- Modify: `capfib/gf.py`
- Create: `tests/test_checksum.py`

**Interfaces:**
- Consumes: `capfib.fib.fibonacci`, `capfib.gf.coefficients`, `capfib.dp.counts`
- Produces: `gf.checksum_ok(n: int) -> bool`

This task is where the lesson from the spec review gets encoded in executable form. The checksum is a **regression invariant, not a licence**. Two tests state that explicitly: one asserts the checksum *misses* a sum-preserving corruption, the next asserts the cross-check *catches* the same corruption.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_checksum.py
"""The global checksum, and the reason it is not a licence to report anything.

For the fixed-length system on places F_1..F_n every digit tuple has exactly
one value, so sum(counts) == prod(F_k + 1) exactly. That identity is a useful
regression invariant and nothing more:

  * it is one scalar constraining an array of millions, so any sum-preserving
    corruption passes it;
  * it does not exercise the production place set at all -- checksum_ok(18)
    uses places up to F_18 = 2584, while a run to 10^6 uses 30 places up to
    832040, leaving twelve untouched.

What licenses the numbers is the pointwise dp/gf cross-check. These tests hold
both facts in place.
"""

from capfib.dp import counts as dp_counts
from capfib.fib import fibonacci
from capfib.gf import checksum_ok, coefficients


def test_checksum_holds_for_small_n():
    for n in range(1, 15):
        assert checksum_ok(n), f"checksum failed at n={n}"


def test_checksum_detects_a_changed_total():
    F = fibonacci(10)
    max_value = sum(f * f for f in F)
    c = coefficients(max_value, places=F)
    product = 1
    for f in F:
        product *= f + 1
    assert sum(c) == product
    c[7] += 1
    assert sum(c) != product


def test_checksum_misses_sum_preserving_corruption():
    """The known blind spot, asserted so nobody over-trusts the invariant.

    Moving mass between two coefficients leaves the total identical. The
    checksum cannot see it.
    """
    F = fibonacci(10)
    max_value = sum(f * f for f in F)
    c = coefficients(max_value, places=F)
    product = 1
    for f in F:
        product *= f + 1

    c[7] += 1
    c[9] -= 1              # sum preserved
    assert sum(c) == product, "the checksum is blind to this corruption -- by design of the check, not of the code"


def test_crosscheck_catches_sum_preserving_corruption():
    """The same corruption the checksum misses, caught pointwise.

    This pair is the argument: the cross-check is the licence, the checksum
    is not.
    """
    n_max = 500
    good = coefficients(n_max)
    corrupted = list(good)
    corrupted[7] += 1
    corrupted[9] -= 1
    assert sum(corrupted) == sum(good)          # checksum-style test passes
    assert corrupted != dp_counts(n_max)        # pointwise comparison fails
    assert good == dp_counts(n_max)             # and the good array survives it
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
.venv/bin/pytest tests/test_checksum.py -q
```
Expected: FAIL — `ImportError: cannot import name 'checksum_ok' from 'capfib.gf'`.

- [ ] **Step 3: Write the implementation**

```python
# append to capfib/gf.py -- and add this import at the top of the file:
# from capfib.fib import fibonacci


def checksum_ok(n: int) -> bool:
    """Verify sum(counts) == prod(F_k + 1) for the fixed-length system on F_1..F_n.

    Every digit tuple has exactly one value, so the coefficients must sum to
    the number of tuples.

    This is a REGRESSION INVARIANT, not a correctness certificate. It is one
    scalar over an array of millions: any sum-preserving corruption passes, and
    it exercises only places F_1..F_n, not the place set a production run uses.
    See tests/test_checksum.py, which asserts both limitations. What licenses
    reported values is the pointwise dp/gf cross-check in scripts/run_phase1.py.
    """
    places = fibonacci(n)
    max_value = sum(f * f for f in places)
    total = sum(coefficients(max_value, places=places))
    product = 1
    for f in places:
        product *= f + 1
    return total == product
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
.venv/bin/pytest tests/test_checksum.py -q
```
Expected: PASS, 4 tests. All 21 tests added by Tasks 1-4 run in about 2 seconds.

- [ ] **Step 5: Commit**

```bash
git add capfib/gf.py tests/test_checksum.py
git commit -m "feat: add global checksum as a regression invariant

Two tests encode why it is not a licence: one asserts a sum-preserving
corruption passes the checksum, the next asserts the pointwise cross-check
catches the same corruption."
```

---

### Task 5: `scripts/run_phase1.py`

**Files:**
- Create: `scripts/run_phase1.py`

**Interfaces:**
- Consumes: `capfib.gf.coefficients`, `capfib.dp.counts`, everything in `capfib.stats`, `capfib.manifest.record`
- Produces: the four artifacts of spec §5

- [ ] **Step 1: Write the script**

> **Stale pre-execution draft.** The code block below is the plan's original
> proposal, written before implementation. It carries two defects that were
> found and fixed during execution: `ladder()` here has no `1 < p` filter,
> which divides by zero at the degenerate place `F_1 = F_2 = 1`; and the
> `fig.savefig(...)` calls are bare, non-atomic writes. Both were fixed in the
> committed source. `scripts/run_phase1.py` is authoritative — do not copy
> from here.

```python
#!/usr/bin/env python3
"""Phase 1 -- exact computation of R_c(N) and its structural analyses.

The cross-check is the point. `dp` and `gf` are structurally different
algorithms over the same place set; comparing every coefficient to n_max is
what licenses reporting values three orders of magnitude past the range the
standing gate covers. It costs ~5 minutes at 10^6 and is not optional.
"""

import argparse
import csv
import io
import json
import math
import os
import resource
import subprocess
import tempfile
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from capfib.dp import counts as dp_counts  # noqa: E402
from capfib.fib import places_up_to  # noqa: E402
from capfib.gf import coefficients  # noqa: E402
from capfib.manifest import record  # noqa: E402
from capfib.stats import (  # noqa: E402
    block_extrema,
    local_ratios,
    monotonicity_census,
    place_jumps,
    summatory,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_CSV = REPO_ROOT / "data" / "phase1_data.csv"
SUMMARY_JSON = REPO_ROOT / "data" / "phase1_summary.json"
FIG_GROWTH = REPO_ROOT / "figures" / "phase1_growth.png"
FIG_FLUCT = REPO_ROOT / "figures" / "phase1_fluctuation.png"
MANIFEST = REPO_ROOT / "data" / "manifest.json"


def git_rev() -> str:
    try:
        out = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def atomic_write_text(path: Path, text: str) -> None:
    """Write via a temp file and rename, so a failure cannot leave a partial
    artifact that later looks validated."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline="") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def ladder(n_max: int) -> list[int]:
    """Decades and half-decades from 100, plus every distinct place value."""
    pts = set()
    j = 4
    while True:
        n = round(10 ** (j / 2))
        if n > n_max:
            break
        pts.add(n)
        j += 1
    pts.update(p for p in set(places_up_to(n_max)) if p <= n_max)
    pts.add(n_max)
    return sorted(pts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-max", type=int, default=1_000_000)
    ap.add_argument("--skip-crosscheck", action="store_true",
                    help="DEVELOPMENT ONLY: skips the precondition and refuses "
                         "to write to the real artifact paths.")
    args = ap.parse_args()
    n_max = args.n_max

    print(f"computing gf.coefficients({n_max}) ...")
    t0 = time.time()
    c = coefficients(n_max)
    gf_seconds = time.time() - t0
    print(f"  gf took {gf_seconds:.1f}s")

    if args.skip_crosscheck:
        print("WARNING: cross-check skipped; refusing to write real artifacts.")
        crosscheck = "skipped"
        dp_seconds = None
    else:
        print(f"computing dp.counts({n_max}) for the cross-check (slow) ...")
        t0 = time.time()
        d = dp_counts(n_max)
        dp_seconds = time.time() - t0
        print(f"  dp took {dp_seconds:.1f}s")
        if c != d:
            first = next(i for i in range(len(c)) if c[i] != d[i])
            print(f"CROSS-CHECK FAILED: first disagreement at N={first}: "
                  f"gf={c[first]} dp={d[first]}")
            print("Writing nothing.")
            return 1
        crosscheck = f"dp==gf pointwise for all N <= {n_max}"
        print(f"cross-check OK: {crosscheck}")

    assert min(c) >= 1, "a zero count would break local_ratios"

    census = monotonicity_census(c)
    sc = summatory(c)
    ratios = local_ratios(c)
    jumps = place_jumps(c)
    blocks = block_extrema(c)

    print(f"census: {census}")
    print(f"decreasing steps: {census['decreasing']} of {census['steps']} "
          f"({100 * census['decreasing'] / census['steps']:.1f}%)")

    if args.skip_crosscheck:
        print("skip-crosscheck set: analyses ran, nothing written.")
        return 0

    rows = []
    for n in ladder(n_max):
        log_n = math.log(n)
        rows.append({
            "N": n,
            "R_c": c[n],
            "log_R_c": math.log(c[n]),
            "log_N_sq": log_n * log_n,
            "ratio": math.log(c[n]) / (log_n * log_n),
            "S_c": sc[n],
            "log_S_c": math.log(sc[n]),
        })
    sio = io.StringIO()
    w = csv.DictWriter(sio, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
    atomic_write_text(DATA_CSV, sio.getvalue())

    srt = sorted(ratios)
    summary = {
        "n_max": n_max,
        "git_rev": git_rev(),
        "crosscheck": crosscheck,
        # spec section 9 criterion 4: every measurement the design quotes must be
        # re-derived here, so no figure in the spec rests on an unrecorded run.
        "gf_seconds": round(gf_seconds, 1),
        "dp_seconds": None if dp_seconds is None else round(dp_seconds, 1),
        "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024),
        "census": census,
        "min_count": min(c),
        "R_c_at_n_max": str(c[n_max]),
        "R_c_bit_length": c[n_max].bit_length(),
        "place_jumps": jumps,
        "block_extrema": [
            {**b, "max": str(b["max"]), "min": str(b["min"])} for b in blocks
        ],
        "fluctuation_quantiles": {
            "min": srt[0],
            "p25": srt[len(srt) // 4],
            "median": srt[len(srt) // 2],
            "p75": srt[3 * len(srt) // 4],
            "max": srt[-1],
        },
    }
    atomic_write_text(SUMMARY_JSON, json.dumps(summary, indent=2) + "\n")

    # --- figures: distinct colours, matchable legend entries ---
    xs = [r["log_N_sq"] for r in rows]
    FIG_GROWTH.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(xs, [r["log_R_c"] for r in rows], "o-", color="#1f77b4", label="log R_c(N)")
    ax.plot(xs, [r["log_S_c"] for r in rows], "s--", color="#d62728", label="log S_c(N)")
    ax.set_xlabel("(log N)^2")
    ax.set_ylabel("log")
    ax.set_title(f"Phase 1: growth of R_c and S_c (exact, N <= {n_max})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_GROWTH, dpi=150)
    plt.close(fig)

    step = max(1, n_max // 20_000)
    idx = list(range(1, n_max, step))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(idx, [ratios[i] for i in idx], ".", markersize=1,
            color="#1f77b4", label="R_c(N+1)/R_c(N)")
    ax.plot(idx, [1 + c[i + 1] / sc[i] for i in idx], "-",
            color="#d62728", label="1 + R_c(N+1)/S_c(N)  (S_c increment)")
    ax.axhline(1.0, ls=":", color="#555555", label="1")
    ax.set_xscale("log")
    ax.set_xlabel("N")
    ax.set_ylabel("relative increment")
    ax.set_title("Phase 1: R_c fluctuates, S_c does not")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_FLUCT, dpi=150)
    plt.close(fig)

    params = {"n_max": n_max, "crosscheck": crosscheck}
    for path in (DATA_CSV, SUMMARY_JSON, FIG_GROWTH, FIG_FLUCT):
        record(path, script="scripts/run_phase1.py", params=params,
               manifest_path=MANIFEST)

    print(f"wrote {DATA_CSV.name}, {SUMMARY_JSON.name}, "
          f"{FIG_GROWTH.name}, {FIG_FLUCT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Smoke-test at small n_max with the cross-check on**

```bash
.venv/bin/python scripts/run_phase1.py --n-max 5000
```
Expected: prints `cross-check OK: dp==gf pointwise for all N <= 5000`, a census line, and the four written filenames. Runs in a few seconds.

- [ ] **Step 3: Verify the artifacts and manifest**

```bash
head -3 data/phase1_data.csv
.venv/bin/python -c "import json;d=json.load(open('data/phase1_summary.json'));print(d['census'], d['crosscheck'])"
.venv/bin/python -c "import json;m=json.load(open('data/manifest.json'));print(len(m),'entries')"
ls -la figures/
```
Expected: CSV with the seven columns, summary carrying census and cross-check string, four new manifest entries, two PNGs.

- [ ] **Step 4: Verify the failure path actually writes nothing**

Induce a real mismatch by monkeypatching `dp.counts` to return a corrupted
array, then confirm the script exits non-zero and leaves the artifacts
untouched.

```bash
cp data/phase1_summary.json /tmp/p1_before.json
.venv/bin/python - <<'EOF'
import sys, runpy, filecmp
import capfib.dp as dp

real = dp.counts
def corrupted(n_max, places=None):
    c = list(real(n_max, places))
    c[7] += 1          # a single wrong coefficient
    c[9] -= 1          # sum-preserving, so a checksum would not notice
    return c
dp.counts = corrupted

sys.argv = ["run_phase1.py", "--n-max", "5000"]
try:
    runpy.run_path("scripts/run_phase1.py", run_name="__main__")
except SystemExit as e:
    print("exit code:", e.code)
    assert e.code == 1, "script should exit 1 on cross-check failure"
assert filecmp.cmp("data/phase1_summary.json", "/tmp/p1_before.json", shallow=False), \
    "artifacts were modified despite a failed cross-check"
print("PASS: cross-check failed, exit 1, artifacts untouched")
EOF
```
Expected: a `CROSS-CHECK FAILED: first disagreement at N=7` line, `exit code: 1`, then
`PASS: cross-check failed, exit 1, artifacts untouched`.

Note the corruption is deliberately sum-preserving — the exact kind
`gf.checksum_ok` cannot see. This step demonstrates on the real script what
`tests/test_checksum.py` asserts in the abstract.

- [ ] **Step 5: Restore the manifest and commit**

```bash
git checkout data/manifest.json
git add scripts/run_phase1.py
git commit -m "feat: add Phase 1 orchestration with cross-check precondition

dp/gf pointwise agreement over the whole range is required before any artifact
is written, and artifacts are written atomically."
```

---

### Task 6: The production run

**Files:**
- Modify (generated): `data/manifest.json`

- [ ] **Step 1: Run at full scale**

```bash
time .venv/bin/python scripts/run_phase1.py --n-max 1000000
```
Expected: ~12 s for `gf`, ~5 min for the `dp` cross-check, then the analyses. It must print `cross-check OK: dp==gf pointwise for all N <= 1000000`. Total ~6 minutes.

If the cross-check fails, **stop and report**. That is the check doing its job, and it means one of the two algorithms is wrong — not something to work around.

- [ ] **Step 2: Record the headline numbers**

These also satisfy spec §9 criterion 4: the summary JSON re-derives every
measurement the design document quotes, so no figure in the spec rests on an
unrecorded ad-hoc run.

```bash
.venv/bin/python -c "
import json
d = json.load(open('data/phase1_summary.json'))
c = d['census']
print('n_max      ', d['n_max'])
print('crosscheck ', d['crosscheck'])
print('census     ', c)
print('decreasing ', f\"{100*c['decreasing']/c['steps']:.1f}%\")
print('R_c bits   ', d['R_c_bit_length'])
print('min count  ', d['min_count'])
print('gf seconds ', d['gf_seconds'])
print('dp seconds ', d['dp_seconds'])
print('peak RSS MB', d['peak_rss_mb'])
"
```
Expected: `min count 1` (completeness holding empirically), `R_c bits 99`, and a decreasing-step share near 48%.

- [ ] **Step 3: Look at both figures**

Open `figures/phase1_growth.png` and `figures/phase1_fluctuation.png`. Each line must be a distinct colour with a legend entry that can be matched to it. If two lines share a colour, fix the script — the Phase 0.5 figure had that defect and it is not to be repeated.

- [ ] **Step 4: Commit the manifest**

```bash
git add data/manifest.json
git commit -m "data: Phase 1 production run at n_max=1e6

dp and gf agree pointwise on all 10^6 coefficients."
```

---

### Task 7: Ledger claims and the phase report

**Files:**
- Modify: `theory/claims.yaml`
- Create: `docs/phases/phase1_report.md`

- [ ] **Step 1: Add the claims**

Append to `theory/claims.yaml`, substituting the real numbers from `data/phase1_summary.json`:

```yaml
- id: dp-gf-agree-to-nmax
  statement: "capfib.dp and capfib.gf agree on every coefficient of R_c(N) for N <= 1000000."
  status: verified-numeric
  evidence: "data/phase1_summary.json (crosscheck field), produced by scripts/run_phase1.py"
  source: "this project, Phase 1"

- id: rc-not-monotone
  statement: "R_c(N) is not monotone: over N <= 1000000 the census records the exact counts of increasing, flat and decreasing steps, and the decreasing count is large."
  status: verified-numeric
  evidence: "data/phase1_summary.json (census field)"
  source: "this project, Phase 1"

- id: place-jump-decay
  statement: "R_c(F)/R_c(F-1) at distinct place values equals exactly 1.0 at F=2, rises at F=3 and F=8, and decays monotonically toward 1 only from F=13 onward. It does NOT exceed 1 at every place, and is NOT monotone overall."
  status: verified-numeric
  evidence: "data/phase1_summary.json (place_jumps field), checked exhaustively over every distinct place F <= 1000000"
  source: "this project, Phase 1"

- id: block-extremal-n
  statement: "Argmax and argmin of R_c within each Fibonacci block [F, F') over N <= 1000000, ties broken toward the smallest N."
  status: verified-numeric
  evidence: "data/phase1_summary.json (block_extrema field)"
  source: "open problem 2, theory/01-background.md section 14"

- id: gf-global-checksum
  statement: "For the fixed-length system on F_1..F_n, sum(counts) equals prod(F_k+1). Reproducible from the test suite for n <= 14. This invariant is insensitive to sum-preserving corruption and does not exercise the production place set; it is not a licence to report values."
  # status: theorem, not verified-numeric -- the identity is derived (each
  # digit tuple has exactly one value, so summing counts over all values
  # counts every tuple exactly once), not measured. The test suite
  # corroborates it for n <= 14; it does not establish it.
  status: theorem
  evidence: "Proved in theory/03-invariants.md (gf-global-checksum): each digit tuple has exactly one value, so summing counts over all values counts every tuple exactly once. Corroborated in tests/test_checksum.py for n <= 14, which also asserts the sum-preserving blind spot (test_checksum_misses_sum_preserving_corruption)."
  source: "this project, Phase 1"

- id: sc-monotone
  statement: "S_c(N) = sum_{n<=N} R_c(n) is non-decreasing."
  status: theorem
  evidence: "Immediate from R_c(n) >= 0. Corroborated in tests/test_stats.py::test_summatory_is_exact_ints_and_monotone."
  source: "this project"
```

- [ ] **Step 2: Validate the ledger**

```bash
.venv/bin/python scripts/check_claims.py
```
Expected: `claims.yaml OK`. If a `verified-numeric` claim fails, its evidence does not name a file in the manifest — fix the evidence, not the validator.

- [ ] **Step 3: Write `docs/phases/phase1_report.md`**

Prose, written by hand. It must contain, with real numbers substituted from the summary JSON:

> **Stale pre-execution draft.** The template below is the plan's original
> proposal, including phrasing that treated the census as if it had chosen a
> proof strategy outright. Review after execution found that overstates a
> finite observation; the committed `docs/phases/phase1_report.md` instead
> says the finding *constrains* the route without selecting it over the
> alternative (see spec §6 and `docs/roadmap.md` Phase 5). The committed
> report is authoritative — do not copy this wording from here.

```markdown
# Phase 1 — Exact Computation of R_c(N)

**Question.** What does `R_c(N)` actually look like at computable scale, and
which of Phase 5's routes does its behaviour select?

**Method.** Exact integer computation to `N = 10^6` via the closed-form
generating-function recurrence, with every coefficient cross-checked against an
independently implemented digit-loop DP. Reported values are licensed by that
full-range agreement {claim:dp-gf-agree-to-nmax}, not by a global checksum —
see the design spec section 3 for why the checksum is insufficient.

**What Phase 1 is not.** It does not measure the leading asymptotic constant.
Phase 0.5 already did that at `N = 10^3200`. At `N = 10^6` the ratio
`log R_c(N)/(log N)^2` is around 0.35 against a limit near 0.5195 — squarely
pre-asymptotic. Fitting the four-term expansion here would report the
pre-asymptotic regime convincingly and wrongly.

**Result 1 — R_c fluctuates.** Quote the `census` object from
`data/phase1_summary.json` verbatim (its four fields: increasing, flat,
decreasing, steps) and state the decreasing share as a percentage
{claim:rc-not-monotone}. Roadmap Phase 0 left this question open and
made Phase 5's route depend on it: a census this fluctuating over the
observed range motivates working with the summatory function `S_c` rather
than `R_c` directly, and makes `S_c` the safer numerical target. **This
constrains Route B, it does not select it** (Route A remains primary; see
spec §6). `S_c` is non-decreasing
{claim:sc-monotone}, and the fluctuation figure shows the contrast directly.

**Result 2 — structure at place values.** Reproduce the `place_jumps` table
from `data/phase1_summary.json` as a two-column list (place, ratio). `R_c`
jumps at each Fibonacci place, but the naive law is false: the ratio is exactly 1.0 at
`F = 2` and rises at `F = 3` and `F = 8`, decaying monotonically only from
`F = 13` onward {claim:place-jump-decay}. An earlier draft asserted decay
everywhere on the strength of a sample that began at `F = 13`.

**Result 3 — extremal N.** Reproduce the `block_extrema` table from
`data/phase1_summary.json`, one row per Fibonacci block: the block range, the
argmax with its count, and the argmin with its count. Progress on open
problem 2 {claim:block-extremal-n}.

**Limits.** Every result is a numerical observation over `N <= 10^6`. None is a
theorem about all `N`, and none is recorded as one.
```

- [ ] **Step 4: Re-validate and commit**

```bash
.venv/bin/python scripts/check_claims.py && .venv/bin/pytest -q
git add theory/claims.yaml docs/phases/phase1_report.md
git commit -m "docs: Phase 1 claims and report

The fluctuation result selects Phase 5 Route B. Recorded as a numerical
observation over N <= 1e6, not as a theorem."
```

---

### Task 8: Propagate the gate clause

**Files:**
- Modify: `CLAUDE.md`
- Modify: `.claude/skills/rc-numerics/SKILL.md`

The spec's §3.4 extends the standing correctness gate. Both places that state the gate must say so, or the next person reports a number at scale without the cross-check.

- [ ] **Step 1: Extend the gate in `CLAUDE.md`**

In the Global Constraints section, immediately after the existing `§4.2 gate` bullet, add:

```markdown
- **Beyond the verified range:** reporting any `capfib.dp`/`capfib.gf` value
  outside the pointwise-verified range additionally requires `dp` and `gf` to
  agree pointwise **over the whole reported range, in the same run that
  produces the data** (`scripts/run_phase1.py` does this). The global checksum
  `gf.checksum_ok` is a regression invariant and is explicitly **not**
  sufficient: it is one scalar over millions of coefficients, so any
  sum-preserving corruption passes, and it does not exercise the production
  place set.
```

- [ ] **Step 2: Extend the `rc-numerics` skill**

In `.claude/skills/rc-numerics/SKILL.md`, under "The gate comes first", add:

```markdown
Reporting a value beyond the range those tests cover needs more: `dp` and `gf`
must agree pointwise across the whole range you are reporting, computed in the
same run. `scripts/run_phase1.py` enforces this as a precondition and writes
nothing if it fails. Do not substitute `gf.checksum_ok` — it cannot see a
sum-preserving corruption and does not touch the production places.
```

- [ ] **Step 3: Verify both files state it**

```bash
grep -c "sum-preserving" CLAUDE.md .claude/skills/rc-numerics/SKILL.md
```
Expected: `1` for each.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md .claude/skills/rc-numerics/SKILL.md
git commit -m "docs: extend the correctness gate for out-of-range reporting"
```

---

### Task 9: Roadmap checklist and final verification

**Files:**
- Modify: `docs/roadmap.md`

- [ ] **Step 1: Update the Phase 1 checklist**

In the `## Fortschritt` section, change the Phase 1 heading from
`### Phase 1 — Exakte Berechnung 🟡 teilweise` to
`### Phase 1 — Exakte Berechnung ✅`, check the previously open items, and
append their commits. The items to check off, with the commit that covers each:

- Lauf bis `N = 10^6` (exakt, nicht Log-Domain — der zurückgestellte Pfad wird nicht gebraucht)
- `phase1_data.csv`
- `phase1_plot.png` → delivered as `phase1_growth.png` and `phase1_fluctuation.png`
- `phase1_report.md`
- Deskriptive Statistik: Monotonie, lokale Fluktuation
- Extremale `N` (offenes Problem 2)

Add one new checked line recording the finding that decides Phase 5:

> **Stale pre-execution draft.** The line below originally phrased the
> census as if it had chosen a proof route outright, which overstates a
> finite observation. The committed `docs/roadmap.md` says the finding
> constrains that route without choosing it over the alternative. Do not
> copy this wording from here.

```markdown
- [x] **Fluktuations-Befund:** `R_c(N)` ist stark fluktuierend (Anteil fallender
      Schritte aus `data/phase1_summary.json` einsetzen), damit ist die in Phase 0
      offengelassene Frage entschieden: der Befund **schränkt Route B ein**
      (keine Auswahl gegen Route A) über die summatorische Funktion `S_c(N)`
      — Commit aus Task 7 einsetzen
```

- [ ] **Step 2: Full verification**

```bash
.venv/bin/pytest -q
.venv/bin/python scripts/check_claims.py
grep -c '^- \[x\]' docs/roadmap.md
git status --short
```
Expected: all tests pass, `claims.yaml OK`, an increased checked-item count, clean tree after commit.

- [ ] **Step 3: Commit**

```bash
git add docs/roadmap.md
git commit -m "docs: mark Phase 1 complete in the roadmap"
```

- [ ] **Step 4: Report against the spec's success criteria**

Report which of the eight criteria in spec §9 pass, quoting the actual command output for each. Do not claim a criterion passes without having run its command.
