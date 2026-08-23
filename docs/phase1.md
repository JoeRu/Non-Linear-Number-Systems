# Phase 1 — Result

**Status:** complete, 2026-08-20 · **Range:** exact for `N ≤ 10^6`

Phase 1 computed `R_c(N)` — the number of representations of `N` as `∑ d_k F_k`
with `0 ≤ d_k ≤ F_k` — exactly, for every `N` up to one million, and measured
what the counting function actually looks like at computable scale.

Every figure below is read from `data/phase1_summary.json`, which is recorded in
`data/manifest.json` together with the git revision that produced it. The
detailed write-up is [`docs/phases/phase1_report.md`](phases/phase1_report.md);
this page is the summary.

> **On the numbers below.** Every figure produced by `scripts/run_phase1.py` is
> quoted with a `{fig:...}` tag and checked against `data/phase1_figures.json`
> by `tests/test_figure_tags.py`; a quoted value that drifts from the generated
> one fails the suite. Mathematical constants, section and equation numbers, and
> values quoted from the literature carry no tag and are not machine-checked.
> Wall-clock timings are excluded on purpose: they change on every run, so
> tagging them would force a prose edit at each regeneration.
>
> Two further categories are generated but not tagged with `{fig:...}` —
> checked a different way instead. The place-jump and block-extrema tables in
> `docs/phases/phase1_report.md` reproduce the `place_jumps` and
> `block_extrema` arrays from `data/phase1_summary.json` in full (28 and 29
> rows); `tests/test_phase1_tables.py` compares every cell of both tables
> against that file directly, rather than requiring one `{fig:...}` per cell.
> The `flat_step_positions` list here and the `dp==gf pointwise for all
> N <= 1000000` line below are reproduced verbatim and are not separately
> checked; only the specific values pulled out of the tables and lists into
> prose as headline figures — the block count, a handful of individual
> place-jump ratios, the flat-step extremes — carry a `{fig:...}`.

---

## What licenses these numbers

The project's standing correctness gate verifies `capfib.dp` against the
brute-force oracle to `N ≤ 200`, and `dp` against `capfib.gf` to `N ≤ 500`.
Phase 1 reports values three orders of magnitude beyond that, so it earns them a
different way: **`scripts/run_phase1.py` computes the whole array twice — once
with the closed-form generating-function recurrence, once with the naive digit
loop — and compares every single coefficient** before it will write anything.

```
dp==gf pointwise for all N <= 1000000
```

Two structurally different algorithms agreeing pointwise for every `N ≤ 10^6`
is the claim {claim:dp-gf-agree-to-nmax}. The comparison is not sampled and not
tolerance-based, and the script writes nothing if it fails.

**What it does not cover:** `dp`, `gf` and `brute` all take their place values
from `capfib.fib.places_up_to`, so a wrong *place set* would be invisible to the
cross-check. That shared dependency is pinned separately by boundary tests in
`tests/test_fib.py`, including the production boundary (30 places, ending at
832040, excluding 1346269).

---

## Result 1 — `R_c(N)` fluctuates

| steps | increasing | flat | decreasing |
|---|---|---|---|
| 1,000,000 {fig:census-steps} | 504,441 {fig:census-increasing} | 11 {fig:census-flat} | 495,548 {fig:census-decreasing} |

**49.6 {fig:decreasing-fraction}% of steps strictly decrease.** The counting function is not monotone and
not close to it — it is nearly a coin flip whether `R_c(N+1)` exceeds `R_c(N)`.

Roadmap Phase 0 left this question open and made the choice of attack depend on
it: a smooth `R_c` could be attacked directly; a fluctuation this pronounced
over the measured range `N ≤ 10^6` favors working with the summatory function
`S_c(N) = ∑_{n≤N} R_c(n)` instead. The measurement settles which
situation we are in and **motivates `S_c` as the object a Tauberian argument
should target** {claim:rc-not-monotone}. `S_c` is non-decreasing by
construction, since `R_c ≥ 0` ({claim:sc-monotone}, proved in
[`theory/03-invariants.md`](../theory/03-invariants.md)).

This is a numerical observation over `N ≤ 10^6`. It is not a theorem about all
`N`, and it does not prove any direct method impossible.

The local ratio `R_c(N+1)/R_c(N)` has these recorded order statistics:

| min | p25 | median | p75 | max |
|---|---|---|---|---|
| 0.9853 {fig:fluctuation-min} | 0.9984 {fig:fluctuation-p25} | 1.0000 {fig:fluctuation-median} | 1.0016 {fig:fluctuation-p75} | 2.0 {fig:fluctuation-max} |

## Result 2 — structure at the place values

The ratio `R_c(F)/R_c(F−1)` was measured at every distinct place `F ≤ 10^6`:
it is exactly 1.0 {fig:place-jump-f2} at `F = 2` (not a rise, and not a fall),
above 1 and rising elsewhere below `F = 13` (1.5 {fig:place-jump-f3} at `F = 3`,
1.333 {fig:place-jump-f8} at `F = 8`), and monotonically decaying only from
`F = 13` onward, reaching 1.000653 {fig:place-jump-largest} at `F = 832040`,
the largest place in range. An earlier draft claimed decay everywhere, on the
strength of a sample that happened to begin at `F = 13`; the exhaustive check
above found the two exceptions, and `tests/test_stats.py` now pins them so
they cannot be quietly smoothed away {claim:place-jump-decay}.

## Result 3 — extremal `N`, and a plateau that stops early

Argmax and argmin of `R_c` within each Fibonacci block over `N ≤ 10^6` (29
{fig:block-count} blocks in that range) are recorded in the summary {claim:block-extremal-n} —
progress on open problem 2 of
[`theory/01-background.md`](../theory/01-background.md) §14. Note the final block
`[832040, 1000001)` is truncated by `n_max` rather than by the next place.

A structural observation with no explanation offered: there are **exactly 11
{fig:flat-step-count} flat steps** over the measured range `N ≤ 10^6`, at

```
N = 2, 7, 12, 15, 20, 28, 33, 36, 57, 67, 78
```

all of them at or below `N` = 78 {fig:flat-step-last} — nearly a million
further steps over `N ≤ 10^6` produce no plateau at all
{claim:flat-steps-end-early}.

## Completeness

`min(counts)` = 1 {fig:min-count} across the whole range — every `N ≤ 10^6` has at least one
representation, which is the Kempner–Fraenkel completeness condition holding in
practice {claim:completeness-empirical}. This is a measurement over the
computed range `N ≤ 10^6`, not the general statement. It was evidence toward the
Lean theorem `exists_numeral_of_le`, which Phase 2 has since **proved**, with no
`sorry` (`613da4f`); the measurement remains a check on the computation, not a
substitute for the proof.

---

## What Phase 1 is not

It does not measure the leading asymptotic constant. Phase 0.5 already did that
at `N = 10^3200`. At `N = 10^6` the ratio `log R_c(N)/(log N)^2` is far below its
limit — squarely pre-asymptotic — so fitting the four-term expansion to this data
would describe the pre-asymptotic regime convincingly and wrongly. `R_c(10^6)`
is a 99 {fig:rc-bit-length}-bit integer; the plan's assumption that exact
counts would overflow was wrong, and no log-domain path was needed.

## Reproducing it

```bash
.venv/bin/python scripts/run_phase1.py --n-max 1000000
```

Several minutes, nearly all of it the `dp` cross-check. `data/` and `figures/`
are gitignored; `data/manifest.json` records what was produced, by which script,
at which revision, with what hashes. Runtime and memory figures in the summary
are observations from one machine, not reproducible outputs.

## Pointers

| | |
|---|---|
| Detailed report | [`docs/phases/phase1_report.md`](phases/phase1_report.md) |
| Design spec | [`docs/superpowers/specs/2026-08-20-phase1-exact-computation-design.md`](superpowers/specs/2026-08-20-phase1-exact-computation-design.md) |
| Claims | [`theory/claims.yaml`](../theory/claims.yaml), validated by `scripts/check_claims.py` |
| Proofs of the invariants | [`theory/03-invariants.md`](../theory/03-invariants.md) |
| Analysis code | `capfib/stats.py` · orchestration `scripts/run_phase1.py` |
