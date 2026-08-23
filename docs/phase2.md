# Phase 2 — Result

**Status:** complete, 2026-08-21 · **Proved:** `log R_c(N)/(log N)^2` converges,
to `1/(4 log phi)`

Phase 2 proves the programme's first asymptotic theorem about `log R_c(N)`, and
then closes it:

```
lim_{N->infinity} log R_c(N)/(log N)^2  =  1/(4 log phi)  =  0.5195217...
```

— C5 of the technical note ({claim:leading-constant}). It arrives in two stages
and both are kept. C4 first sandwiches the **liminf and limsup** between
`1/(8 log phi)` and `1/(4 log phi)`, a factor of two apart, the gap being where
T3's lower-bound construction spends half its places. §8 then closes that gap
from below with a second construction, and the limit follows.

**C5 is not a pointwise statement.** Nothing in Phase 2 traps `log R_c(N)`
between two expressions at a given `N`: C5 is a statement about the limit, and
the sampled ratios at `N = 2, 3, 5` sit above `1/(4 log phi)` (see "The ratio").
C4 is likewise a statement about the liminf and limsup and about nothing else.

The proofs are in [`docs/phases/phase2_bounds.md`](phases/phase2_bounds.md);
this page is the summary and quotes it. Every generated number below is read
from `data/phase2_figures.json` by key, and `tests/test_figure_tags.py`
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

**C4 does not assert that `C_c` exists — C5 does.** C4 bounds the liminf and the
limsup, which is strictly weaker than convergence, and nothing in T1–T3 bears on
whether `log R_c(N)/(log N)^2` converges: that is research question (A) of
[`theory/00-definitions.md`](../theory/00-definitions.md), and it is answered by
C5 below, not by C4. Keeping the two apart matters, because it is exactly what
T5 had to supply beyond a constant. The roadmap's parametrisation
`C_c = 1/(C' log phi)` presupposes existence; C4 alone gives `C' in [4, 8]`
*if* `C_c` exists, and C5 gives `C' = 4` unconditionally.

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

**This section is motivation, not a step.** Nothing in the proof of T3 uses the
identification with regime A: T3 is proved from `(F1)` and the completeness
lemma alone, and would stand unchanged if the identification were wrong
(technical note §4.4). It is offered only to explain *where* the missing factor
of two goes, and it is leading-order at that.

The factor is **structural to this construction as specified** — a rectangular
free family with one selected completion per residue — so re-estimating its sums
more tightly cannot recover it. It is **not** claimed structural to every
refinement. §4.4 of the technical note names two routes that attack the block
partition rather than the estimates (a sparse multi-scale fixup; counting all
completions rather than one), either of which alone would close the sandwich,
together with the failure mode of each. The second route closes; see "Closing
the sandwich" below.

That second route runs into Phase 1's finding directly: over the measured range
`N <= 1000000` the census records 49.6% decreasing steps
({claim:rc-not-monotone}), so an inner bound holding on average need not hold at
a given residue.

---

## Closing the sandwich

Route L2b closes, and §8 of the technical note carries the proof.

**Lemma F — a block is flat on its middle band.** Let `B(a, m)` count the
cap-respecting digit tuples on places `1..a` of value `m`, and let
`S_a = F_a F_{a+1}` be the block's capacity. For `a >= 8` and every integer `m`
of the band `[S_a/5, 3 S_a/4]`,

```
B(a, m)  >=  prod_{k=8}^{a} (F_{k-1}/5 - 1)  =  exp(lambda a^2/2 - 3.5057 a + 12.749).
```

The proof conditions on the top digit — `B(a, m) = sum_d B(a-1, m - d F_a)`, an
identity — keeps only the `d` whose residue stays inside the band one level
down, and counts them: a four-case interval argument resting on
`S_{a-1} = F_{a-1} F_a` and `S_a - S_{a-1} = F_a^2`, with completeness
({claim:completeness-no-gaps}) as the base at `a = 7`. Uniformity in the residue
was the obstacle §4.4 named; the reason it can be met is that the required
precision is far coarser than a local limit theorem. The block's total mass is
`exp(lambda a^2/2 + O(a))` spread over `S_a = exp(2 lambda a + O(1))` values, so
losing the whole range costs `exp(-O(a))`, which is invisible at the `a^2`
scale.

**T5 — the matching lower bound.** For every integer `N >= 10000`, with
`t = log N`,

```
log R_c(N)  >=  t^2/(4 log phi) - (t log t)/(2 log phi) - 7.5 t.
```

The construction is T3's, with the reserved block counted instead of reserved:
the boundary `a` is chosen so that `S_a >= (4/3) N`, which places every residue
`N - sigma` inside Lemma F's band, and the block then contributes a factor
`exp(lambda a^2/2 - O(a))` where T3's contributed `1`. With `L = log_phi N`, both
halves then weigh `lambda L^2/8`, and their sum `lambda L^2/4 = t^2/(4 lambda)`
is T2's constant.

**C5 — the limit exists.** Dividing T5 by `(log N)^2` bounds the liminf below by
`1/(4 log phi)`; T2 bounds the limsup above by the same value; so the limit
exists and equals it ({claim:leading-constant}).

**Route L2a did not close.** §8.6 records where it stopped, and the obstruction
is not the one §4.4 anticipated: it is not the carry's termination but a step
earlier. A product free family leaves an uncontrolled residue in `[0, N]`, so
the hierarchy of scales never starts; making the residue small at each scale
needs adaptively chosen digits, which are not a product. Tracking the count
through adaptive choices is what Lemma F does, so L2a's repair is L2b.

**T1–T3 and C4 are not superseded.** T5 does not use T3 as a step, but it reuses
T3's machinery and C4 remains true as proved; T3's `1/(8 log phi)` is the weaker
bound T5 improves on, and keeping both in view is what makes the factor of two
legible.

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
slack anywhere in the sample is `1.94`, at `N = 2`, read from
`data/phase2_bounds.csv`.

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
falls at every step from `N = 2` down to its sampled minimum `0.3245393` at
`N = 316`, wobbles across the next four samples (`N = 377, 610, 987, 1000`,
where it reads `0.3246032`, `0.3245443`, `0.3251635`, `0.3251464` — note
`N = 610` sits a hair *above* the minimum, not at it), and then rises at every
step from `N = 1000` to `0.3582` at `N = 1000000`. At the three smallest samples
(`N = 2, 3, 5`) it lies **above** the upper constant, at `1.4427`, `0.9102` and
`0.6213`; from `N = 8` upward, all 34 remaining sampled points lie strictly
inside `[0.2598, 0.5195]`.

**Small `N` above the interval is not evidence against C4, nor against C5.** C4
constrains the liminf and the limsup and C5 the limit; all three are unchanged by
any finite set of `N`. T2's consequence carries a `(1 + o(1))`, and T3 and T5 are
both stated only for `N >= 10000`, so none of these bounds claims anything at
`N = 2, 3, 5`. The ratio is inflated there by its denominator: `(log N)^2` is
tiny while `R_c(N) >= 1` forces `log R_c(N) >= 0`.

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

**It does not pin the secondary term.** T5 and T2's effective form agree to two
terms — `log R_c(N) = t^2/(4 log phi) - t log t/(2 log phi) + O(t)` with
`t = log N`, the lower `O(t)` explicit at `7.5 t` and the upper one not made
explicit — but no argument in Phase 2 fixes that `O(t)` from either side.

**It does not show T2 is sharp for `R_c(N)` at a given `N`.** C5 says the limit
of the ratio is `1/(4 log phi)`; it does not say `log R_c(N)` is close to
`(log N)^2/(4 log phi)` at any particular `N`, and the two proved inequalities
are both vacuous at every `N` where `R_c(N)` has been computed exactly.

**It does not use Coons–Kristensen–Laursen.** The roadmap's upper bound went
through `R_c <= R_u` plus the cited CKL asymptotic, which would have given
`1/(2 log phi)`. T1 and T2 prove `1/(4 log phi)` directly, without the citation.
The Lean statement `countReps_le_uncapped` is proved with no `sorry` — but what
is proved is the *length-indexed* inequality
`countReps n N <= countRepsUncapped n N` at a fixed number of places `n`, not
the all-places `R_c(N) <= R_u(N)` of §1 (technical note §7) — and it is
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
| Does `C_c` exist at all? | **Answered.** Research question (A); C5 (§8) proves the limit exists and equals `1/(4 log phi)`. C4 alone does not address it |
| Closing the sandwich | **Done.** Route L2b of §4.4 closes it: §8's Lemma F and T5. Route L2a did not close; §8.6 records where it stopped |
| The size of the saddle correction | Phase 2 proves `0 <= Lambda(N) - log R_c(N) <= K log N`. Whether that correction divided by `log N` converges — and to what — is open {claim:saddle-correction-constant} |
| The secondary term `c_2` | Whether `c_2` in research question (B) exists is a **different** question: `c_2` is the limit of `(E - D)/t`, and T2 bounds `E` rather than evaluating it, so neither answer implies the other {claim:secondary-term-constant} |
| The CKL identification | Pending verification; out of scope for Phase 2 |

---

## Reproducing it

```bash
.venv/bin/python scripts/run_phase2.py --n-max 1000000
.venv/bin/python scripts/check_claims.py
.venv/bin/python -m pytest -q
cd lean && lake build
```

The recipe runs on a clean checkout as written, and that is checked rather than
assumed: `tests/test_run_phase2.py` runs the script to completion inside a
scratch tree with no `figures/` directory, and separately fails its very last
step to confirm nothing is left behind.

`data/` is gitignored except for the artifacts a clean clone has to have, each
tracked for a stated reason (`.gitignore` is the authoritative list and carries
the reason beside each entry):

- `data/manifest.json` — what was produced, by which script, at which revision,
  with what SHA-256.
- `data/phase2_figures.json` and `data/phase1_figures.json` — so prose and data
  cannot drift apart (risk R-002). The mechanism now covers both phases:
  `data/phase1_figures.json` was added when the Phase 1 documents were tagged,
  and R-002 records the mitigation as covering both, with the residuals it does
  *not* cover named there.
- the artifacts cited as evidence by `verified-numeric` claims —
  `data/phase1_summary.json`, `data/phase0_5_gate.csv`,
  `data/phase2_bounds.csv`, `data/phase2_residual.csv` — which
  `scripts/check_claims.py` requires to exist and to match their recorded hash.
- `data/phase1_data.csv` — the 37-row exact-value ladder. The Phase 2 bound
  tests compare T1, T3 and T5 against it, so while it was gitignored those
  twelve comparisons *skipped* on every clean clone and the suite was green
  without them. Its bytes are checked against the manifest's hash, so the
  tracked copy cannot drift from what `scripts/run_phase1.py` produced.

`figures/` is tracked as a directory (`figures/.gitkeep`) though its contents
are not: the script writes the PNG through an atomic rename, which needs the
parent directory to exist.

## Pointers

| | |
|---|---|
| Proofs (T1, T2, T3, C4, Lemma F, T5, C5) | [`docs/phases/phase2_bounds.md`](phases/phase2_bounds.md) |
| Design spec | [`docs/superpowers/specs/2026-08-21-phase2-elementary-bounds-design.md`](superpowers/specs/2026-08-21-phase2-elementary-bounds-design.md) |
| Claims | [`theory/claims.yaml`](../theory/claims.yaml), validated by `scripts/check_claims.py` |
| Lean | `lean/NonLinearNumberSystems/Completeness.lean`, `lean/NonLinearNumberSystems/Bounds.lean` |
| Verification run | `scripts/run_phase2.py` → `data/phase2_bounds.csv`, `data/phase2_residual.csv`, `data/phase2_figures.json`, `figures/phase2_sandwich.png` |
| Open review disputes | [`docs/risks.md`](risks.md) |
