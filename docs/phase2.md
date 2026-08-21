# Phase 2 — Result

**Status:** complete, 2026-08-21 · **Proved:** a two-sided bound on `log R_c(N)/(log N)^2`

Phase 2 proves the first theorem of the programme: `log R_c(N)` is trapped
between `(log N)^2/(8 log phi)` and `(log N)^2/(4 log phi)`. The two constants
differ by a factor of two, so the sandwich **does not close**, and the gap is
not an artefact of loose estimates — it is where the lower-bound construction
spends half its places.

The proofs are in [`docs/phases/phase2_bounds.md`](phases/phase2_bounds.md);
this page is the summary and quotes it. Every generated number below is read
from `data/phase2_figures.json` by key, and `tests/test_phase2_figures.py`
requires the literal in the prose to match the stored value exactly.

---

## What was proved

**T1 — the effective upper bound.** For every integer `N >= 1` and every real
`s > 0`, `log R_c(N) <= s N + log F_c(e^{-s})`. This is a Chernoff bound off the
non-negativity of the coefficients of `F_c`; it is an inequality at each `s`,
not an asymptotic statement, so a badly chosen `s` costs slack and never
soundness.

**T2 — the asymptotic upper bound.** `log F_c(e^{-s}) = T^2/(4 lambda) + O(T)`
as `s -> 0+`, with `T = log(1/s)` and `lambda = log phi`. Combined with T1 at
`s = t/(2 lambda N)`, `t = log N`, this gives the effective form
`log R_c(N) <= t^2/(4 lambda) - (t log t)/(2 lambda) + O(t)`, and in particular
`log R_c(N) <= (1 + o(1)) (log N)^2/(4 log phi)`.

The proof splits the places into three regimes — the cap binds, the budget
binds, the tail — and bounds the *sum* of the discarded terms in each, by
`8.473`, by `O(T)`, and by `1.167`. A shorter argument that discards terms
pointwise is recorded in §3.7 of the technical note as **not a proof**, with a
counterexample to its uniformity: at `s_n = 1/(F_n(F_n+1))` the discarded term
tends to `log(1 - e^{-1}) = -0.4587`, not to zero.

**T3 — the lower bound.** For `N >= 10000`,
`log R_c(N) >= (log N)^2/(8 log phi) - 2 (log N)(log log N)`. The pair
`(C, N_0) = (2, 10000)` is proved in §4.2 of the technical note by a
hand-checkable chain; it was chosen for that, not for sharpness. The
construction reserves a fixup block `[1, a]` with `sum_{k<=a} F_k^2 = F_a F_{a+1} >= N`
({claim:sum-of-squares}) and counts a rectangular free family on the remaining
places. The fixup step is the one statement the paper layer takes from the Lean
layer: `exists_numeral_of_le` in `lean/NonLinearNumberSystems/Completeness.lean`
({claim:completeness-no-gaps}) is **proved, with no `sorry`**, and gives that
every integer in `[0, F_a F_{a+1}]` is the value of some cap-respecting tuple on
places `1..a`.

**C4 — the sandwich.** {claim:sandwich-bounds}

```
1/(8 log phi) <= liminf log R_c(N)/(log N)^2 <= limsup log R_c(N)/(log N)^2 <= 1/(4 log phi)
```

numerically 0.2598 {fig:lower-constant} to 0.5195 {fig:upper-constant}.

**C4 does not assert that `C_c` exists.** It bounds the liminf and the limsup,
which is strictly weaker than convergence. Whether `log R_c(N)/(log N)^2`
converges at all is research question (A) of
[`theory/00-definitions.md`](../theory/00-definitions.md), and nothing in T1–T3
bears on it. The roadmap's parametrisation `C_c = 1/(C' log phi)` presupposes
existence; *if* `C_c` exists, C4 gives `C' in [4, 8]`.

**`C' in [4,8]` is not a strengthening of the roadmap's anticipated `[2,4]`.**
The roadmap expected an upper coefficient `1/(2 log phi)` cited from
Coons–Kristensen–Laursen and a lower coefficient `1/(4 log phi)` from its own
sketch. Phase 2 **strengthens the upper** coefficient to `1/(4 log phi)` and
**weakens the lower** to `1/(8 log phi)`. The two intervals are not nested: they
meet at `C' = 4` and are otherwise disjoint. The roadmap's lower sketch was in
any case unavailable as written — it bounded `R_c` below by `R_u`, and capping
only removes representations, so that inequality runs the other way.

---

## Where the factor of two goes

The fixup block has to absorb residues as large as `N`, which forces
`F_a F_{a+1} >= N` and so `a = L/2 + O(1)` with `L = log N / log phi`. To
leading order those are the cap-binding places, which carry half of
`log F_c(e^{-s})`. The construction spends that half on landing on `N` at all
and counts only the other half.

The factor is **structural to this construction as specified** — a rectangular
free family with one selected completion per residue — so re-estimating its sums
more tightly cannot recover it. It is **not** claimed structural to every
refinement. §4.4 of the technical note names two routes that attack the block
partition rather than the estimates (a sparse multi-scale fixup; counting all
completions rather than one), either of which alone would close the sandwich,
together with the failure mode of each.

That second route runs into Phase 1's finding directly: over the measured range
`N <= 1000000` the census records 49.6% decreasing steps
({claim:rc-not-monotone}), so an inner bound holding on average need not hold at
a given residue.

---

## What was verified, and over what range

Phase 1 computed `R_c(N)` exactly for the whole range `N <= 1000000`. Phase 2's
verification is a **sample**: `data/phase1_data.csv` holds 37 sampled `N`
spanning 2 to 1000000 {fig:n-max-verified} — the Fibonacci numbers, the decades
and the half-decades — and no statement here reaches beyond those 37 points.
Each evaluation was gated in the same run on the float and certified paths
agreeing to `1e-12`; `scripts/run_phase2.py` writes nothing if a gate fails.

**T1, certified** {claim:chernoff-effective-verified}. At `N` = 1000000
{fig:n-max-verified} the exact `log R_c(N)` is 68.3632 {fig:log-rc-nmax} and the
certified Chernoff bound is 81.9137 {fig:chernoff-certified-nmax}, a slack of
13.5505 {fig:chernoff-slack-nmax}. Over the sampled `N <= 1000000` the bound was
violated at none of the 37 points and was strict at each of them; the smallest
slack anywhere in the sample is `1.94`, at `N = 2`, and the slack increases at
every one of the 36 steps between consecutive sampled points.

**T3's construction, evaluated directly.** At the same `N` the construction
gives 17.774 {fig:t3-lower-nmax}, with the fixup block ending at place 16
{fig:fixup-block-nmax} and 14 {fig:counting-places-nmax} counting places. Across
the 37 sampled `N <= 1000000` it exceeded the exact `log R_c(N)` nowhere: at 36
points it is strictly below, and at `N = 2` the two are exactly equal, both
`0.6931471805599453`. That equality is expected — at `N = 2` neither of the
construction's two sources of undercount is present, so it enumerates all of
`R_c(2) = 2` (technical note §6). Note that `N = 2` is far below `N_0 = 10000`:
the inequality stated as T3 is vacuous over this whole range, and it is the
*construction* that is being confronted, not that inequality.

**The ratio.** `log R_c(N)/(log N)^2` is 0.3582 {fig:ratio-nmax} at
`N` = 1000000 {fig:n-max-verified}, between the two proved constants. Its
behaviour over the sample is **not monotone**: reading the 37 rows in order, it
falls at every step from `N = 2` down to its sampled minimum `0.3245` at
`N = 316`, wobbles across the next four samples (`N = 377, 610, 987, 1000`,
where it reads `0.3246`, `0.3245`, `0.3252`, `0.3251`), and then rises at every
step from `N = 1000` to `0.3582` at `N = 1000000`. At the three smallest samples
(`N = 2, 3, 5`) it lies **above** the upper constant, at `1.4427`, `0.9102` and
`0.6213`; from `N = 8` upward, all 34 remaining sampled points lie strictly
inside `[0.2598, 0.5195]`.

**Small `N` above the interval is not evidence against C4.** C4 constrains the
liminf and the limsup, both unchanged by any finite set of `N`; T2's consequence
carries a `(1 + o(1))` and T3 is stated only for `N >= 10000`, so neither bound
claims anything at `N = 2, 3, 5`. The ratio is inflated there by its
denominator: `(log N)^2` is tiny while `R_c(N) >= 1` forces `log R_c(N) >= 0`.

**The product residual** {claim:product-residual-sampled}. A separate sweep
evaluates `log F_c(e^{-s}) - (log(1/s))^2/(4 lambda)` at eight values of
`T = log(1/s)` between 10 {fig:residual-t-min} and 1280 {fig:residual-t-max}.
Over the seven samples with T >= 20 {fig:residual-asymptotic-t-min} the residual
sits at 3.2274 {fig:residual-asymptotic-centre} with a spread of 0.000178
{fig:residual-asymptotic-spread}; including the `T = 10` point, which is
pre-asymptotic at `3.2092`, the spread over the full sweep is 0.018236
{fig:residual-full-spread}. This is a sampled observation at eight points, not a
proved `O(1)` error term — T2 establishes `O(T)` and nothing here upgrades that.
What it suggests is that T2's `O(T)` is not sharp on this range; eight points
cannot establish a bound, and the quantity was not evaluated between them.

---

## What Phase 2 is not

**It does not settle the constant.** The Phase 3 conjecture
`log R_c(N) ~ (log N)^2/(4 log phi)` ({claim:leading-constant}, still a
conjecture) sits at the *upper* endpoint of the proved interval. Phase 2
therefore leaves it to be settled entirely from below: what is missing is a
matching lower bound, together with the existence statement the conjecture makes
and C4 does not.

Two formulations are deliberately avoided. "The conjecture holds if and only if
T2 is attained" is wrong — matching the limsup to the upper endpoint says
nothing about the liminf. And "T2 is sharp" is not established: no argument in
Phase 2 shows the upper constant cannot be lowered.

**It does not use Coons–Kristensen–Laursen.** The roadmap's upper bound went
through `R_c <= R_u` plus the cited CKL asymptotic, which would have given
`1/(2 log phi)`. T1 and T2 prove `1/(4 log phi)` directly, without the citation.
The Lean statement `countReps_le_uncapped` is proved with no `sorry`, but it is
**not load-bearing**: it backs the qualitative comparison remark of §7 of the
technical note and nothing else. Nothing proved in Phase 2 depends on
identifying our `R_u` with CKL's `p_F`, an identification that remains recorded
as pending verification in [`theory/00-definitions.md`](../theory/00-definitions.md).

**It does not confirm a leading constant numerically.** At `N <= 1000000` the
ratio is far from either endpoint, and Phase 1 already recorded that this range
is pre-asymptotic.

---

## What remains open

| | |
|---|---|
| Does `C_c` exist at all? | Research question (A); C4 does not address it |
| Closing the sandwich | Needs a lower-bound construction that does not reserve half the places — L2a or L2b, §4.4 |
| The CKL identification | Pending verification; out of scope for Phase 2 |

---

## Reproducing it

```bash
.venv/bin/python scripts/run_phase2.py --n-max 1000000
.venv/bin/python scripts/check_claims.py
.venv/bin/python -m pytest -q
cd lean && lake build
```

`data/` is gitignored apart from `data/manifest.json` and
`data/phase2_figures.json`, which is tracked precisely so prose and data cannot
drift apart (risk R-002). `data/manifest.json` records what was produced, by
which script, at which revision, with what hashes.

## Pointers

| | |
|---|---|
| Proofs (T1, T2, T3, C4) | [`docs/phases/phase2_bounds.md`](phases/phase2_bounds.md) |
| Design spec | [`docs/superpowers/specs/2026-08-21-phase2-elementary-bounds-design.md`](superpowers/specs/2026-08-21-phase2-elementary-bounds-design.md) |
| Claims | [`theory/claims.yaml`](../theory/claims.yaml), validated by `scripts/check_claims.py` |
| Lean | `lean/NonLinearNumberSystems/Completeness.lean`, `lean/NonLinearNumberSystems/Bounds.lean` |
| Verification run | `scripts/run_phase2.py` → `data/phase2_bounds.csv`, `data/phase2_residual.csv`, `data/phase2_figures.json`, `figures/phase2_sandwich.png` |
| Open review disputes | [`docs/risks.md`](risks.md) |
