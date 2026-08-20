# Phase 1 — Exact Computation of R_c(N)

**Date:** 2026-08-20
**Status:** Approved design — implementation plan pending
**Roadmap phase:** 1 (`docs/roadmap.md`, "Exakte Berechnung und Sanity Checks")

---

## 1. What Phase 1 is actually for

The roadmap frames Phase 1 as the numerical benchmark for all later asymptotic
claims. Two measurements taken while designing this phase change that framing.

**The coefficients are small.** The plan deferred a log-domain computation path
on the assumption that exact counts would overflow or exhaust memory. They do
not: `R_c(10^6)` is **99 bits** — roughly `10^30` — and extrapolation puts
`R_c(10^7)` near 143 bits. Exact integer arithmetic is comfortable. The
bottleneck is Python allocation overhead, not number size, and the deferred
log-domain path is not needed for this phase.

| N | `gf` time | peak RSS | `R_c(N)` | `log R_c(N)` |
|---|---|---|---|---|
| 1,000,000 | 12.3 s | 179 MB | 99 bits | 68.4 |

Measured on commit `9074d3b` with `.venv/bin/python`, uninstrumented. An earlier
draft of this spec reported 178 s at `N = 10^6`; that figure was `tracemalloc`
overhead, not computation, and is corrected here. §9 requires the Phase 1 run to
re-derive these numbers and record them in the manifest, which holds here:
`scripts/run_phase1.py` records `gf_seconds` and `peak_rss_mb` at `n_max`. An
earlier draft of this table also carried a second, smaller-`N` row sourced
from an ad-hoc design-time probe; it has been dropped rather than merely
flagged, since no committed invocation re-derives it and this project's rule
is that a number in a document traces to a recorded artifact.

**Phase 1 is not where the constant gets measured.** Phase 0.5 already pinned
the leading coefficient at `N = 10^3200`. At `N = 10^6` the ratio
`log R_c(N) / (log N)^2` is 0.35 against a limit near 0.5195 — nowhere close to
asymptotic. Fitting the four-term expansion to data at this scale would measure
the pre-asymptotic regime, not the asymptotics.

So Phase 1's value is **structural, not asymptotic**: monotonicity, local
fluctuation, extremal `N`, the behaviour at place values, and the smoothness of
the summatory function. These need exactness far more than they need reach.

---

## 2. Decisions taken

**D1 — Exact integers to `N = 10^6`.** No log-domain path, no fast kernel. The
existing `capfib.gf.coefficients` is used as-is: ~12 s, 179 MB, exact.

**D2 — Roadmap deliverables plus the summatory function.** A measurement taken
during design settles a question the roadmap explicitly left open. Roadmap
Phase 0 says:

> Falls `R_c(N)` sehr fluktuiert → verwende summatorische Funktion `S_c(N)` für
> Taubersätze (Phase 5B). Falls `R_c(N)` glatt ist → direkter Attack auf
> `R_c(N)` selbst.

`R_c(N)` fluctuates heavily: of the first 100,000 steps, **48,446 strictly
decrease** and only 11 are flat. Phase 5 therefore needs `S_c(N)`, and since
`S_c` is a cumulative sum of the array Phase 1 already builds, computing it here
costs almost nothing.

**D3 — Tested analysis module, thin parameterised script, no cache.** The
descriptive analyses live in `capfib/stats.py` as pure functions with unit
tests; `scripts/run_phase1.py` orchestrates and takes `--n-max` so iteration
happens at `10^4` (0.07 s) and the full run happens once. An on-disk cache of
the counts array was considered and rejected: `--n-max` recovers most of the
iteration speed without introducing an artifact format or a staleness question.

**Explicitly not done:** optimising either path. `gf` takes ~12 s, so there is
nothing to optimise there. `dp` takes ~5 min at `n_max`, but that cost buys the
verification in §3.1 and is paid once per data run — speeding it up would remove
the one check that licenses the phase's numbers. A modular-arithmetic kernel
(counts mod several 31-bit primes, vectorised `cumsum` per residue class, CRT
reconstruction) was considered and rejected: it is a subsystem with its own
correctness burden, and it would make the fast path faster while leaving the
slow path — the one that matters — untouched.

---

## 3. Verification: how a number at 10^6 becomes quotable

The project's §4.2 gate says no `dp`/`gf` output may appear in a report until
`dp` has matched `brute` for all `N ≤ 200` and `dp` and `gf` have matched each
other for all `N ≤ 500`. Phase 1 reports values at `10^6`, three orders of
magnitude past that. A previous review already caught a report quoting `gf` at
`N = 600` as a gate violation, so this must be resolved rather than waved past.

### 3.1 What licenses the numbers: a full-scale pointwise cross-check

`capfib.dp` (naive digit loop) and `capfib.gf` (closed-form
multiply-by-`(1-x^M)`, divide-by-`(1-x^f)` recurrence) are structurally
different algorithms, both obtaining their places from the same
`places_up_to` call. Running both at `n_max` and comparing every coefficient
is therefore an independent check **conditional on that shared place set**,
not an unconditional one: a wrong or truncated place set would be applied
identically to both algorithms and would be invisible to the comparison (see
`tests/test_fib.py` for the boundary tests that pin `places_up_to` instead).
It is not a sampled check, and it is affordable:

| N | `dp` | `gf` | pointwise agreement |
|---|---|---|---|
| 40,000\* | 2.3 s | 0.3 s | ✅ all coefficients |
| **1,000,000** | **298 s** | **9–12 s** | ✅ **all coefficients** |

\*The `40,000` row is an ad-hoc design-time probe run while scoping the
feasibility of a full-scale cross-check; `scripts/run_phase1.py` only ever
runs the comparison at `n_max`, so this row is not re-derived by any
committed invocation and is not a reproducible artifact — only the
`1,000,000` row (at the script's default `n_max`) is. An earlier draft of
this table also carried a second, intermediate-`N` row sourced from the same
kind of design-time probe; it has been dropped rather than merely flagged,
for the same reason.

`scripts/run_phase1.py` runs this comparison at `n_max` as its **precondition**.
Five minutes of `dp` is the price of quoting a million coefficients, and it is
worth paying. On mismatch the script reports the smallest disagreeing `N` and
writes nothing.

### 3.2 What the global checksum is, and what it is not

In the *fixed-length* system on places `F_1 … F_n`, every digit tuple has
exactly one value, so `Σ_N counts[N] = ∏_k (F_k + 1)` exactly. Verified during
design at n = 10, 14, 18 and 20 (the last spanning 7.4 × 10^7 coefficients).

**An earlier draft of this spec claimed this identity licensed reporting at
`10^6`. That was wrong, in two independent ways, and the claim is withdrawn.**

1. **It is one scalar.** A single sum constrains one number about an array of
   millions. Any sum-preserving corruption passes: add `e` to one coefficient
   and subtract `e` from another, permute the array, or place the right number
   of monomials at the wrong exponents — the total is identical. The earlier
   draft's "an error would almost certainly break it" was a hand-wave with no
   error model behind it.
2. **It does not exercise the production places.** `checksum_ok(18)` uses only
   `F_1 … F_18` (largest 2584). The production run uses `places_up_to(10^6)` —
   30 places, largest 832040. **Twelve of the thirty production places are never
   touched.** Worse, the n=18 fixed-length array stops equalling `R_c(N)` at
   `N = F_19 = 4181`. Coverage must be counted in *places exercised*, never in
   maximum coefficient index — and a covering checksum is impossible in
   principle: n = 30 would need an array of 1.12 × 10^12 entries.

So the checksum stays, demoted to what it honestly is: **a cheap regression
invariant** over the factor structure, run in the test suite to n = 14. It is
not a licence to report anything.

### 3.3 Considered and rejected

Random modular evaluation of the generating polynomial at points other than
`x = 1` would be far more sensitive than the checksum, being positional. It is
rejected because §3.1 is deterministic, covers every coefficient, and already
fits the budget; adding probabilistic evidence on top would be tooling for its
own sake.

### 3.4 Consequence for the gate

The gate clause in `CLAUDE.md` and in the `rc-numerics` skill gains a third
requirement: **reporting values beyond the pointwise-verified range requires
`dp` and `gf` to agree pointwise over the whole reported range**, in the same
run that produces the data. The global checksum is explicitly *not* sufficient.

## 4. Components

### 4.1 `capfib/stats.py`

Pure functions over a counts array. No I/O, no plotting, no globals.

| Function | Returns |
|---|---|
| `monotonicity_census(counts)` | `{"increasing": int, "flat": int, "decreasing": int, "steps": int}` over `n = 1..N_max`, comparing `counts[n]` to `counts[n-1]`. The three counts must sum to `steps`. |
| `summatory(counts)` | `list[int]`, `S[N] = Σ_{n ≤ N} counts[n]`, exact. |
| `local_ratios(counts)` | `list[float]` of length `n_max`; `r[n] = counts[n+1] / counts[n]` for `n = 0 … n_max-1`. Division by zero is guarded by an explicit runtime assertion `min(counts) >= 1` — **not** by appealing to completeness, which is still a `sorry` in Lean. Measured: `min(counts) == 1` at `n_max = 10^6`. |
| `block_extrema(counts)` | Over **distinct** place values only — `F_1 = F_2 = 1` would otherwise produce a degenerate duplicate first block. For consecutive distinct places `F < F'`, the block is `[F, min(F', n_max+1))`. Returns argmax/argmin per block; **ties broken by smallest `N`**, stated so results are reproducible. |
| `place_jumps(counts)` | For each **distinct** place value `F ≥ 2`, the ratio `counts[F] / counts[F-1]`. Distinctness matters: `F_1 = F_2 = 1`, and `F = 1` has no `F-1` in range. |

### 4.2 `capfib/gf.py` (addition)

`checksum_ok(n: int) -> bool` — computes the fixed-length counts on places
`F_1..F_n` and returns whether their sum equals `∏(F_k + 1)`. A regression
invariant only; see §3.2 for what it cannot detect.

### 4.3 `scripts/run_phase1.py`

Orchestration only. `--n-max` (default `1_000_000`). The `dp` precondition costs ~5 min at that
size; `--skip-crosscheck` exists **only** for development runs. It runs the
analyses but writes nothing at all — no data files, no figures, no manifest
entry — which is safer than stamping a `crosscheck: skipped` marker into an
artifact that could later be mistaken for validated data. Order of
operations:

1. Compute `gf.coefficients(n_max)` and `dp.counts(n_max)`.
2. **Precondition:** compare pointwise. On mismatch, report the smallest
   disagreeing `N` and exit non-zero, writing nothing.
3. Assert `min(counts) >= 1` (guards `local_ratios`).
4. Call each analysis in `capfib.stats`.
5. Write each artifact to a temporary path, then **atomically rename** it into
   place, so a failure mid-write cannot leave that one file half-written and
   later mistaken for validated data. This atomicity is **per file, not
   across the run**: the four artifacts (CSV, summary JSON, two figures) are
   written and renamed one at a time, so a failure between two of these
   renames can leave a mixed generation on disk -- e.g. a new CSV alongside
   an old summary. Stale artifacts from earlier runs are replaced, not
   merged.
6. Record each artifact in `data/manifest.json` via `capfib.manifest`, together
   with `n_max`, the git revision, and the cross-check result.

---

## 5. Artifacts

| Path | Contents |
|---|---|
| `data/phase1_data.csv` | `N, R_c, log_R_c, log_N_sq, ratio, S_c, log_S_c` at every `N = round(10^(j/2))` for `j = 4 … 2·log10(n_max)` (decades and half-decades from 100), plus every distinct place value `F_k ≤ n_max`. Sorted, deduplicated. |
| `data/phase1_summary.json` | Monotonicity census, block extrema, fluctuation quantiles, place jumps. No checksum result — the script does not call `checksum_ok`; §3.1's pointwise cross-check is what licenses the numbers. |
| `figures/phase1_growth.png` | `log R_c(N)` and `log S_c(N)` against `(log N)^2` |
| `figures/phase1_fluctuation.png` | Local ratio of `R_c` against the relative increment of `S_c` — the visual form of the Route B argument |
| `docs/phases/phase1_report.md` | The phase deliverable. **Written by hand, not by the script** — it is prose about the findings, and the script has no business generating it. Not recorded in the manifest. |

Figures must give each line a distinct colour and a legend entry that can be
matched to it. (The Phase 0.5 figure drew three reference lines in the same
default blue; that is a known defect not to repeat.)

---

## 6. Ledger claims

Added to `theory/claims.yaml`. Every `verified-numeric` entry names a file
recorded in `data/manifest.json`, and each states **exactly what was checked
over what range** — not a trend inferred from samples.

- `rc-not-monotone` — `verified-numeric`. `R_c(N)` is not monotone. The census
  gives exact counts of increasing, flat and decreasing steps over `N ≤ n_max`.
- `place-jump-decay` — `verified-numeric`. Computed **exhaustively over every
  distinct place value `F ≤ n_max`**, not sampled.

  **The exhaustive check was run during planning and the naive form of this
  claim is false.** `R_c(F)/R_c(F−1)` equals exactly `1.0` at `F = 2`, so it
  does not exceed 1 at *every* place; and monotone decay breaks twice, at
  `F = 3` (1.0 → 1.5) and `F = 8` (1.25 → 1.333). The behaviour is clean only
  from `F = 13` onward, where the ratio exceeds 1 and decays monotonically to
  1.0015 at `F = 75025`.

  An earlier draft asserted decay at every place. That came from a sample that
  happened to start at `F = 13` — the exact failure mode this bullet was
  rewritten to prevent, caught by actually running the exhaustive check. The
  claim states the measured behaviour with its two exceptions named, and the
  test asserts the exceptions so a future change cannot quietly "fix" them.
- `block-extremal-n` — `verified-numeric`. Argmax/argmin of `R_c` within each
  Fibonacci block, ties to smallest `N`. Progress on open problem 2 of
  `theory/01-background.md` §14.
- `dp-gf-agree-to-nmax` — `verified-numeric`. `dp` and `gf` agree on **every**
  coefficient to `n_max`. This is the claim that licenses the phase's numbers;
  §3.1 is its method.
- `gf-global-checksum` — `verified-numeric`. `Σ counts = ∏(F_k+1)` for the
  fixed-length system. The claim states the range that is **reproducible from
  the test suite** (`n ≤ 14`) and records the one-off n = 18 and n = 20 runs
  separately as manifest-backed evidence rather than folding them into a figure
  nothing re-derives. The claim text must state the limitation from §3.2: this
  identity is insensitive to sum-preserving corruption and does not exercise the
  production place set.
- `sc-monotone` — `theorem`. `S_c` is non-decreasing, immediately from
  `R_c ≥ 0`. Stated because Phase 5 Route B rests on it.

The report must state that the fluctuation finding **constrains** Phase 5
Route B — makes attacking `S_c(N)` the safer numerical target rather than
`R_c(N)` directly, without selecting Route B over Route A, which remains the
primary route for the rigorous asymptotic theorem — and equally that this is
a numerical observation over `N ≤ 10^6`, not a theorem about all `N`. No
numerical result is promoted to `theorem`.

## 7. Testing

| Test | Content |
|---|---|
| `test_census_partitions_steps` | increasing + flat + decreasing == steps, on random and hand-built sequences |
| `test_census_hand_checked` | Exact census of `R_c(0..20)`, whose values are hand-verified in `tests/test_brute.py` |
| `test_summatory_vs_brute` | `summatory` against cumulative `brute.count` for `N ≤ 60` |
| `test_block_extrema_small` | Exhaustive check against a direct scan for `N ≤ 2000`, including the tie-to-smallest-`N` rule and the absence of a degenerate `F_1`/`F_2` duplicate block |
| `test_local_ratios_length_and_bounds` | Length is exactly `n_max`; indices `0 … n_max-1`; every ratio finite |
| `test_place_jumps_distinct` | Distinct place values only; no entry for `F = 1`; matches direct computation |
| `test_checksum_ok` | True for `n ≤ 14`; a corrupted array that **changes the total** makes it false |
| `test_checksum_misses_sum_preserving_corruption` | **Asserts the known blind spot:** moving `e` from `counts[a]` to `counts[b]` leaves `checksum_ok` true. The test documents the limitation in executable form so no future reader over-trusts the invariant. |
| `test_crosscheck_catches_sum_preserving_corruption` | The *same* corruption that defeats the checksum is caught by pointwise `dp`/`gf` comparison. This pair is the point: it shows why §3.1 is the licence and §3.2 is not. |

The last two tests matter most. A checksum that cannot fail is not a check, and
a checksum whose blind spot is undocumented is worse than none.

## 8. Out of scope

- Any fast kernel (modular/CRT, Rust, C). See §2.
- `capfib/oscillation.py` and Fourier analysis — Phase 4, and it needs the
  four-term fit which needs asymptotic-range data this phase does not produce.
- Fitting the four-term expansion to Phase 1 data. See §1: the range is
  pre-asymptotic, and a fit here would report the wrong thing convincingly.
- Proving anything about monotonicity. The census is an observation over a
  finite range.

---

## 9. Success criteria

1. `dp` and `gf` agree pointwise over all of `0 … n_max`, verified in the same
   run that produces the data, and `scripts/run_phase1.py` refuses to emit
   anything if they do not.
2. `pytest` passes, including every test in §7 — in particular the pair showing
   that a sum-preserving corruption defeats the checksum but is caught by the
   cross-check.
3. `scripts/run_phase1.py --n-max 1000000` produces the four generated artifacts
   of §5 (CSV, JSON, two figures), written atomically, each recorded in
   `data/manifest.json` with `n_max`, git revision and cross-check result. The
   report is written separately.
4. The manifest records re-derived values for every measurement this spec quotes
   in §1 — runtime, peak RSS, `R_c(10^6)` bit length, `min(counts)` — so no
   figure in the design rests on an unrecorded ad-hoc run.
5. `theory/claims.yaml` carries the six §6 claims and
   `scripts/check_claims.py` reports `claims.yaml OK`.
6. `docs/phases/phase1_report.md` states the fluctuation finding, its
   consequence for Phase 5 Route B, and its limits.
7. `CLAUDE.md` and `.claude/skills/rc-numerics/SKILL.md` carry the §3.4 gate
   clause: reporting beyond the pointwise-verified range requires a full-range
   `dp`/`gf` agreement, and the global checksum does not substitute for it.
8. `docs/roadmap.md`'s Phase 1 checklist is updated: completed items checked
   with their commit, the phase marked ✅.

---

## Appendix — review history

This spec was reviewed by Codex (`gpt-5.4-codex`) on 2026-08-20. The review
rejected the original §3 argument, correctly, on two grounds: a single sum
cannot certify millions of coefficients, and `checksum_ok(18)` does not exercise
the production place set. Both were verified before rewriting — twelve of thirty
production places are untouched by the n=18 checksum, and a covering checksum
would need 1.12 × 10^12 entries.

The rewrite replaces the licence with the full-scale pointwise cross-check
(§3.1), demotes the checksum to a regression invariant with its blind spot
documented in executable form (§3.2, §7), and tightens boundary, tie-breaking,
provenance and atomicity semantics throughout.

Also corrected as a consequence of re-measuring: the original §1 reported 178 s
for `gf` at `N = 10^6`. The true figure is ~12 s; 178 s was `tracemalloc`
overhead.

One recommendation was declined: random modular evaluation at points other than
`x = 1`. It is sound and more sensitive than the checksum, but the deterministic
full-range cross-check subsumes it.
