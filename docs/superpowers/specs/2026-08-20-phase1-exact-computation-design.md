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

| N | time | peak memory | `R_c(N)` | `log R_c(N)` |
|---|---|---|---|---|
| 200,000 | 1.3 s | 7 MB | 76 bits | 52.1 |
| 1,000,000 | 178 s | 145 MB | 99 bits | 68.4 |

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
existing `capfib.gf.coefficients` is used as-is: ~3 minutes, 145 MB, exact.

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

**Explicitly not done:** optimising the 178-second run. A modular-arithmetic
kernel (counts mod several 31-bit primes, vectorised `cumsum` per residue class,
CRT reconstruction) would cut it to seconds, but it is a subsystem with its own
correctness burden, and Phase 1 does not need it. Building it now would be
tooling mistaken for a result.

---

## 3. Verification: how a number at 10^6 becomes quotable

The project's §4.2 gate says no `dp`/`gf` output may appear in a report until
`dp` has matched `brute` for all `N ≤ 200` and `dp` and `gf` have matched each
other for all `N ≤ 500`. Phase 1 reports values at `10^6`, three orders of
magnitude past that. A previous review already caught a report quoting `gf` at
`N = 600` as a gate violation, so this must be resolved rather than waved past.

**The resolution is a global checksum.** In the *fixed-length* system on places
`F_1 … F_n`, every digit tuple has exactly one value, so

    Σ_N counts[N]  =  ∏_{k=1..n} (F_k + 1)

exactly. This is an independent, scale-free identity: it does not sample, and
any error in the recurrence would almost certainly break it. Verified during
design:

| n | max value | result |
|---|---|---|
| 10 | 4,895 | ✓ |
| 14 | 229,970 | ✓ (0.8 s) |
| 18 | 10,803,704 | ✓ (50 s) |
| 20 | **74,049,690** | ✓ (410 s) |

At `n = 20` an exact 39-digit identity holds across 7.4 × 10^7 coefficients —
two orders of magnitude beyond Phase 1's reporting range.

**Consequences for the gate.** `capfib.gf` gains `checksum_ok(n) -> bool`. The
test suite runs it to `n = 14`. `scripts/run_phase1.py` runs it at `n = 18` as a
**precondition** — if it fails, the script writes nothing. The gate clause in
`CLAUDE.md` and in the `rc-numerics` skill gains a third requirement: reporting
values beyond the pointwise-verified range additionally requires the global
checksum to pass at a scale exceeding the reporting range.

---

## 4. Components

### 4.1 `capfib/stats.py`

Pure functions over a counts array. No I/O, no plotting, no globals.

| Function | Returns |
|---|---|
| `monotonicity_census(counts)` | `{"increasing": int, "flat": int, "decreasing": int, "steps": int}` over `n = 1..N_max`, comparing `counts[n]` to `counts[n-1]`. The three counts must sum to `steps`. |
| `summatory(counts)` | `list[int]`, `S[N] = Σ_{n ≤ N} counts[n]`, exact. |
| `local_ratios(counts)` | `list[float]`, `r[n] = counts[n+1] / counts[n]`. Completeness guarantees `counts[n] ≥ 1` over the range, so no division by zero. |
| `block_extrema(counts)` | For each place value `F_k ≤ N_max`, the argmax/argmin of `R_c` over the block `[F_k, min(F_{k+1}, N_max+1))`, as a list of records. |
| `place_jumps(counts)` | For each **distinct** place value `F ≥ 2`, the ratio `counts[F] / counts[F-1]`. Distinctness matters: `F_1 = F_2 = 1`, and `F = 1` has no `F-1` in range. |

### 4.2 `capfib/gf.py` (addition)

`checksum_ok(n: int) -> bool` — computes the fixed-length counts on places
`F_1..F_n` and returns whether their sum equals `∏(F_k + 1)`.

### 4.3 `scripts/run_phase1.py`

Orchestration only. `--n-max` (default `1_000_000`), `--checksum-n` (default `18`, ~50 s — the
precondition is deliberately expensive because it is what licenses reporting
values at `10^6`). Order of operations:

1. Run `checksum_ok(checksum_n)`. **On failure: print the failure and exit
   non-zero, writing nothing.**
2. Compute `coefficients(n_max)` once.
3. Call each analysis in `capfib.stats`.
4. Write artifacts; record each in `data/manifest.json` via `capfib.manifest`.

---

## 5. Artifacts

| Path | Contents |
|---|---|
| `data/phase1_data.csv` | `N, R_c, log_R_c, log_N_sq, ratio, S_c, log_S_c` at every `N = round(10^(j/2))` for `j = 4 … 2·log10(n_max)` (decades and half-decades from 100), plus every distinct place value `F_k ≤ n_max`. Sorted, deduplicated. |
| `data/phase1_summary.json` | Monotonicity census, block extrema, fluctuation quantiles, place jumps, checksum result |
| `figures/phase1_growth.png` | `log R_c(N)` and `log S_c(N)` against `(log N)^2` |
| `figures/phase1_fluctuation.png` | Local ratio of `R_c` against the relative increment of `S_c` — the visual form of the Route B argument |
| `docs/phases/phase1_report.md` | The phase deliverable. **Written by hand, not by the script** — it is prose about the findings, and the script has no business generating it. Not recorded in the manifest. |

Figures must give each line a distinct colour and a legend entry that can be
matched to it. (The Phase 0.5 figure drew three reference lines in the same
default blue; that is a known defect not to repeat.)

---

## 6. Ledger claims

Added to `theory/claims.yaml`, each `verified-numeric` entry naming a file
recorded in `data/manifest.json`:

- `rc-not-monotone` — `verified-numeric`. `R_c(N)` is not monotone; the census
  gives the exact counts of increasing, flat and decreasing steps to `N_max`.
- `place-jump-decay` — `verified-numeric`. `R_c(F_k)/R_c(F_k − 1) > 1` at every
  place value, decaying monotonically toward 1 (1.154 at `F = 13`, 1.0015 at
  `F = 75025`).
- `block-extremal-n` — `verified-numeric`. The argmax/argmin of `R_c` within
  each Fibonacci block. This is progress on open problem 2 of
  `theory/01-background.md` §14.
- `sc-monotone` — `theorem`. `S_c` is non-decreasing, immediately from
  `R_c ≥ 0`. Stated because Phase 5 Route B rests on it.
- `gf-global-checksum` — `verified-numeric`. `Σ counts = ∏(F_k+1)` verified to
  `n = 20`, i.e. across 7.4 × 10^7 coefficients.

The report must state that the fluctuation finding **selects** Phase 5 Route B,
and equally that this is a numerical observation over `N ≤ 10^6`, not a theorem
about all `N`. `rc-not-monotone` stays `verified-numeric`; no numerical result
is promoted to `theorem`.

---

## 7. Testing

| Test | Content |
|---|---|
| `test_census_partitions_steps` | increasing + flat + decreasing == steps, on random and hand-built sequences |
| `test_census_hand_checked` | Exact census of `R_c(0..20)`, whose values are hand-verified in `tests/test_brute.py` |
| `test_summatory_vs_brute` | `summatory` against cumulative `brute.count` for `N ≤ 60` |
| `test_block_extrema_small` | Exhaustive check against a direct scan for `N ≤ 2000` |
| `test_place_jumps_distinct` | Distinct place values only; no entry for `F = 1`; matches direct computation |
| `test_local_ratios_no_zero_division` | `counts[n] ≥ 1` across the range, so every ratio is finite |
| `test_checksum_ok` | `checksum_ok(n)` true for `n ≤ 14`; a deliberately corrupted array makes it false |

The last test matters most: a checksum that cannot fail is not a check.

---

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

1. `checksum_ok(18)` passes, and `scripts/run_phase1.py` refuses to emit data if
   it fails.
2. `pytest` passes, including every test in §7.
3. `scripts/run_phase1.py --n-max 1000000` produces the four generated artifacts
   of §5 (CSV, JSON, two figures), each recorded in `data/manifest.json`. The
   report is written separately.
4. `theory/claims.yaml` carries the five §6 claims and
   `scripts/check_claims.py` reports `claims.yaml OK`.
5. `docs/phases/phase1_report.md` states the fluctuation finding, its
   consequence for Phase 5 Route B, and its limits.
6. `docs/roadmap.md`'s Phase 1 checklist is updated: the completed items checked
   with their commit, the phase marked ✅.
