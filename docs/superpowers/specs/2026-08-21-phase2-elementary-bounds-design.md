# Phase 2 — Elementary Sandwich Bounds for log R_c(N)

**Date:** 2026-08-21
**Status:** design spec, awaiting review
**Roadmap phase:** 2 (`docs/roadmap.md` §"Phase 2 — Elementare Schranken: Das Sandwich")
**Predecessor:** Phase 1 (`docs/phase1.md`), Phase 0.5 (`docs/phases/phase0_5_gate.md`)

---

## 1. Objective

Prove, by elementary means, two-sided bounds on `log R_c(N)` of order `(log N)^2`,
with explicit constants; verify the effective form of the upper bound against the
exact Phase 1 values; and close the two remaining Lean `sorry`s.

### 1.1 Decisions taken during design

Labelled `PD1`–`PD6` ("Phase 2 decision") to avoid collision with the
infrastructure spec's `D1`, `D2`, … which this document also cites.

| # | Decision | Rationale |
|---|---|---|
| PD1 | Prove our own upper bound at `1/(4 log phi)` rather than cite Coons–Kristensen–Laursen at `1/(2 log phi)` | The Chernoff bound plus an elementary evaluation of `log F_c(e^-s)` reaches the conjectured constant. The citation route is a factor 2 weaker and makes the phase's headline result someone else's theorem. |
| PD2 | Lean scope is the two existing `sorry`s only | `exists_numeral_of_le` and `countReps_le_uncapped` are finite combinatorial statements. T1–T3 are analytic; `lean/NonLinearNumberSystems/Bounds.lean:15-18` already excludes that class from Lean. |
| PD3 | Two-layer theorems: effective **and** asymptotic | At `N = 10^6` the empirical ratio is only ≈0.358, so a bare `(1+o(1))` statement at 0.520 cannot be confronted with our data. The effective layer can be, and is what Phase 4 can plot. |
| PD4 | Lower bound: commit to L1, time-box the two L2 routes | L1 yields `1/(8 log phi)` and is near-certain to close. L2a and L2b attack L1's block structure rather than its estimates (§4.4); attempting them wastes no work. |
| PD5 | Certified numerics via interval arithmetic (`mpmath.iv`), at precision scaled to `log(1/s)` | The alternative — a hand-rolled float interval type — trades a pure-Python dependency for an unprovable assumption about libm ulp accuracy, which would need a `docs/risks.md` entry. Fixed precision is not an option (§5.3). |
| PD6 | `run_phase2.py` emits quotable figures to a tracked file | Closes the project's highest-rated open risk R-002 for this phase instead of re-incurring it. |

---

## 2. Notation

Fibonacci convention is `D2` of the infrastructure spec
(`docs/superpowers/specs/2026-08-19-research-infrastructure-design.md`), fixed in `capfib/fib.py`: `F_1 = F_2 = 1`, `F_3 = 2`, …
`phi = (1+sqrt 5)/2`, `log phi = 0.4812118…`.

```
R_c(N)  = #{ (d_k)_{k>=1} : 0 <= d_k <= F_k, sum_k d_k F_k = N }   (all places F_k <= N)
F_c(x)  = prod_{k>=1} (1 - x^{F_k (F_k+1)}) / (1 - x^{F_k})        (infinite product)
a_k(s)  = log( (1 - e^{-s F_k (F_k+1)}) / (1 - e^{-s F_k}) )       (so log F_c(e^-s) = sum_k a_k(s))
L       = log N / log phi                                          (number of places with F_k <= N, to O(1))
```

`[x^N] F_c(x) = R_c(N)`: places with `F_k > N` contribute only monomials of degree
`> N`, so the infinite product and the finite one agree in degree `N`.

---

## 3. Theorem inventory

**T1 — effective upper bound.** For every `N >= 1` and every `s > 0`,

```
log R_c(N) <= s N + log F_c(e^-s).
```

**T2 — asymptotic upper bound.** As `s -> 0+`,

```
log F_c(e^-s) = (log(1/s))^2 / (4 log phi) + O(log(1/s)),
```

and consequently `log R_c(N) <= (1 + o(1)) (log N)^2 / (4 log phi)`.

**T3 — lower bound (construction L1).** There are explicit `C > 0` and `N_0` such that
for all `N >= N_0`,

```
log R_c(N) >= (log N)^2 / (8 log phi) - C (log N)(log log N).
```

The construction of §4.3 gives the secondary coefficient explicitly as `1/(2 log phi) =
1.0391...`, so any admissible `C` is at least that. `C` and `N_0` are outputs of the write-up,
not inputs to it, and the value proved governs over any value suggested by finite data.

**C4 — sandwich.** Combining T2 and T3,

```
1/(8 log phi) <= liminf log R_c(N)/(log N)^2 <= limsup log R_c(N)/(log N)^2 <= 1/(4 log phi).
```

**C4 does not assert that `C_c` exists.** It bounds the liminf and the limsup. Existence is
research question (A) (`theory/00-definitions.md`), still open. Only *if* `C_c` exists does
the roadmap's parametrisation `C_c = 1/(C' log phi)` apply, and then `C' in [4, 8]`.

**How this compares with the roadmap's `C' in [2,4]` — both endpoints move, in opposite
directions.** The roadmap anticipated an upper coefficient `1/(2 log phi)` cited from CKL
(`docs/roadmap.md:322-330`) and a lower coefficient `1/(4 log phi)` from its own construction
sketch (`docs/roadmap.md:332-347`). Phase 2 **strengthens the upper** coefficient to
`1/(4 log phi)` and **weakens the lower** to `1/(8 log phi)`. The two intervals are therefore
not nested — they merely meet at `C' = 4`. It would be wrong to present `[4,8]` as a
strengthening of `[2,4]`, and the phase documents must not do so.

What is true, and worth stating: the Phase 3 conjecture `C' = 4` sits at the *upper* endpoint
of the proved interval, so Phase 2 leaves the conjecture to be settled entirely from below.
Avoid the formulation "the conjecture holds iff T2 is attained" — matching the limsup to the
upper endpoint says nothing about the liminf, and under the reading "converges to the
endpoint" the statement is a tautology.

**T5 — stretch (construction L2).** If the multi-scale fixup closes,
`log R_c(N) >= (1 - o(1)) (log N)^2 / (4 log phi)`, the sandwich collapses, and research
question (A) of Phase 0 is answered. T5 is explicitly optional; the phase ships on T1–C4.

**Lean targets.**
- `exists_numeral_of_le` (`lean/NonLinearNumberSystems/Completeness.lean:53`)
- `countReps_le_uncapped` (`lean/NonLinearNumberSystems/Bounds.lean:40`)

---

## 4. Proof architecture

### 4.1 T1

All coefficients of `F_c` are non-negative, so for `x = e^-s` in `(0,1)`,
`R_c(N) x^N <= F_c(x)`, i.e. `log R_c(N) <= sN + log F_c(e^-s)`. One line, no asymptotics,
valid at every `N`. This is a **paper proof**, not a Lean target (PD2).

### 4.2 T2 — the three-regime evaluation

Throughout this subsection write `T = log(1/s)` and `lambda = log phi`. **`T`, not `L`** —
T2 is a statement about `s` alone, and place counts here are `T/(2 lambda) + O(1)`, not `L/2`.
(`L = log N / log phi` enters only at the very end, when `s` is tied to `N`.)

Set `u_k = s F_k`, `v_k = s F_k (F_k + 1)`, and `h(x) = -log(1 - e^{-x})`, so that
`a_k(s) = h(u_k) - h(v_k)`. Use **exact** cutoffs, not asymptotic ones:

```
p = max{ k : v_k <= 1 },      q = max{ k : u_k <= 1 },
p = T/(2 lambda) + O(1),      q = T/lambda + O(1)   (Binet).
```

| Regime | Index range | Contribution |
|---|---|---|
| A — cap binds | `k <= p` | `T^2/(8 lambda) + O(T)` |
| B — budget binds | `p < k <= q` | `T^2/(8 lambda) + O(T)` |
| C — negligible | `k > q` (infinitely many places) | `O(1)` **in total** |

Both A and B contribute `T^2/(8 lambda)`, summing to `T^2/(4 lambda)`. This equal split is
the structural fact the lower bound has to contend with (§4.3).

**Error control requires uniform bounds, not pointwise ones.** An earlier draft of this spec
argued from Binet plus "each regime boundary is crossed within `O(1)` places". That argument
is invalid and must not be reinstated: Binet controls `log F_k`, not the difference
`a_k - log(F_k + 1)`, and a pointwise `o(1)` cannot be summed over `Theta(T)` moving indices.
The approximation is provably **not** uniform at its own boundary — at `s_n = 1/(F_n(F_n+1))`,

```
a_n(s_n) - log(F_n + 1)  ->  log(1 - e^{-1}) = -0.458675...,  not 0
```

(verified numerically to six decimals for `n = 30, 38`).

The repair uses two uniform estimates of `h`, both elementary:

```
0 < x <= 1 :   h(x) = -log x + r(x)      with 0 <= r(x) <= x
x >= 1     :   0 <= h(x) <= e^{-x} / (1 - e^{-1})
```

(The first is `1 - e^{-x} <= x <= e^x - 1`; the second is `-log(1-y) <= y/(1-y)` at
`y = e^{-x}`.) With these:

- **`k <= p`** (both `u_k, v_k <= 1`): `a_k = log(v_k/u_k) + r(u_k) - r(v_k)
  = log(F_k + 1) + O(u_k + v_k)`, and `sum_k (u_k + v_k) = O(1)` because both are geometric
  and bounded by 1. Summing `log(F_k + 1)` over `k <= p` gives `lambda p^2/2 + O(p)
  = T^2/(8 lambda) + O(T)`.
- **`p < k <= q`** (`u_k <= 1 < v_k`): `a_k = log(1/u_k) + O(u_k) + O(e^{-v_k})`, and summing
  `log(1/(s F_k)) = T - k lambda + O(1)` over the range gives `lambda (q-p)^2/2 + O(q-p)
  = T^2/(8 lambda) + O(T)`.
- **`k > q`**: `0 <= a_k <= h(u_k) <= e^{-u_k}/(1 - e^{-1})` with `u_k` growing geometrically,
  so the total is `O(1)`.

Hence `log F_c(e^-s) = T^2/(4 lambda) + O(T)`. **This scheme, not the Binet-only argument, is
what the implementer writes up.**

Then T1 with `s` chosen so that `s N = T/(2 lambda)` — i.e. `s ≈ log N/(2 N log phi)`, giving
`T = log N - log log N + O(1)` — makes the `sN` term `O(log N)` and yields T2's consequence
for `R_c(N)`.

### 4.3 T3 — the construction (L1)

Fix `N` and let `c` be the largest index with `F_c <= N`. Split the places into **two**
blocks — no third block is needed:

```
fixup block     [1, a]   where a is the smallest index with F_a F_{a+1} >= N
counting block  (a, c]   free digits; this is what produces the count
```

**(1) Fixup capacity.** By `sum_sq_place`, places `1..a` have total capacity
`sum_{k<=a} F_k^2 = F_a F_{a+1} >= N`. By completeness, every residue in `[0, N]` is
represented on that block by **at least one** digit tuple of exactly that value. Note
"exactly" qualifies the *value*, not the number of representations: representations here are
famously non-unique (`theory/01-background.md` §5), and L1 needs only existence.

**(2) Free family.** On the counting block set `m_k = floor(N / (M F_k))`, where `M = c - a`
is the number of counting places. Then `sum_k m_k F_k <= N`, so every free tuple has sum
`sigma <= N`. The caps are respected automatically: for `N` large enough that `a >= 2`, and
for `k > a`, we have `N <= F_a F_{a+1} < F_{a+1}^2 <= F_k^2`, hence `m_k <= N/F_k < F_k`.

**(3) Completion.** For each free tuple, `N - sigma` lies in `[0, N]` and is therefore
representable on the fixup block by (1). Fix one completion per residue — the
lexicographically least, say — so the map is well defined. The combined digit sequence is a
numeral of value `N` respecting every cap.

**(4) Injectivity.** Restricting a produced numeral to `(a, c]` recovers the free tuple it came
from, so the map from free tuples to representations of `N` is injective.

Hence `R_c(N) >= prod_{k=a+1}^{c} (m_k + 1)`, and since `m_k + 1 >= N/(M F_k)`, with
`t = log N`, `lambda = log phi`, `L = t/lambda`, `a = L/2 + O(1)`, `c = L + O(1)`,
`M = L/2 + O(1)`:

```
log R_c(N) >= sum_{k=a+1}^{c} log(m_k + 1)
           >= M t - M log M - sum_{k=a+1}^{c} log F_k
            = t^2/(8 lambda) - t log t / (2 lambda) + O(t).
```

**The secondary coefficient is explicit and it is not 1.** It is `1/(2 log phi) = 1.0391...`.
T3's `C` must therefore be at least that; `C = 1` is *not* justified by this estimate. The
`C ≈ 0.88` in Appendix A is finite-range evidence over `N <= 10^6` and is consistent with an
asymptotic coefficient above 1 — it must not be read as bounding `C`.

**No pigeonhole and no steering are required.** Because the fixup block's capacity already
exceeds `N`, *every* free tuple completes, so the count is the full product rather than the
contents of a fullest bucket. An earlier draft of this construction carried a third
"steering" block and a pigeonhole step; both are unnecessary and must not be reintroduced.

**Why the constant is `1/8` and not `1/4`.** The fixup block must absorb residues as large as
`N`, which forces `F_a F_{a+1} >= N`, i.e. `a = L/2 + O(1)`. To leading order those are the
cap-binding places of regime A in §4.2, which carry half the total; L1 spends that half on
fixup. (The identification with regime A is leading-order only: at the §4.2 saddle the regime-A
boundary sits at `(L - log_phi log N)/2 + O(1)`.)

The factor of two is structural **to L1 as specified** — a rectangular free family with one
selected completion per residue. Re-estimating L1's sums more tightly cannot recover it. But
the two-block partition alone does **not** prove that every refinement is futile, and this spec
does not claim it does: §4.4 lists two routes that attack the structure rather than the
estimates.

**Uniformity.** `a` and `c` are defined from `N` alone and every step is valid for all
sufficiently large `N`, so T3 holds for every `N >= N_0` — not along a convenient subsequence.

**`C` and `N_0` are outputs of the proof, not inputs to it.** The implementer derives them
from the evaluation above and then verifies them numerically per §8.4. A design-time run of
this exact construction (Appendix A) satisfies the budget, stays below the exact
`log R_c(N)` at every decade, and implies `C ≈ 0.88` — so `C = 1` is the expected order, but
the proved value governs.

### 4.4 T5 — the stretch: two routes past the factor of two

The binding constraint is §4.3(1): the fixup block must cover residues up to `N`, which costs
half the places. Two routes attack that, and they are independent — either alone would close
the sandwich.

**Route L2a — sparse, multi-scale fixup.** Replace the contiguous reserved block with a
**sparse** reserved set (roughly every `log L`-th place) and fix residues hierarchically,
coarsest scale first, so each scale absorbs only a residue of its own magnitude instead of the
full `N`. The reserved places then carry a vanishing fraction of the count and the yield tends
to `(1 - o(1)) (log N)^2 / (4 log phi)`.

*Failure mode:* the hierarchical carry must terminate without pushing any digit past its cap
`F_k`.

**Route L2b — count all completions, not one.** L1 discards every completion but one. Keeping
them all replaces the product by

```
R_c(N) >= sum over free tuples of  ( # representations of N - sigma on places [1, a] ),
```

which is the same counting problem one scale down — the fixup block is itself a
capacity-constrained Fibonacci system on `a = L/2 + O(1)` places. A lower bound on the inner
count that is uniform over the relevant residues would recover regime A's missing half and give
the sharp constant, and the self-similarity suggests an induction on scale rather than a new
construction.

*Failure mode:* the inner bound must hold **uniformly** in `sigma`, and `R_c` is known to
fluctuate strongly ({claim:rc-not-monotone}: 49.6% of steps over `N <= 10^6` decrease), so a
bound that holds on average may not hold for every residue. This is exactly the difficulty
Phase 1's fluctuation finding predicts.

**Time-box.** T5 is attempted only after T1–C4, their proofs, artifacts, and the Lean work are
complete and committed. If neither route closes, the phase ships T1–C4 unchanged and the gap is
stated honestly. Whichever route is attempted, the outcome — including a negative one, with the
reason — is recorded in `docs/phases/phase2_bounds.md`.

### 4.5 The Lean interface

Exactly one statement crosses between the Lean layer and the paper layer:

```
exists_numeral_of_le a N (h : N <= sum_{k<a} F_{k+1}^2)  :  exists d : Numeral a, d.value = N
```

used at §4.3 step (3), with `sum_sq_place a : sum_{k<a} F_{k+1}^2 = F_a * F_{a+1}` (already
proved) converting the hypothesis into `N <= F_a F_{a+1}`. The paper consumes it as a black box.

Two facts the spec records rather than leaving to be rediscovered:

1. **`countReps_le_uncapped` is no longer load-bearing.** Under the roadmap's original plan
   `R_c <= R_u` *was* the upper bound. With T1/T2 proving `1/(4 log phi)` directly, this
   inequality supports nothing. It is still in scope — it clears the repo's last `sorry` and
   backs the comparison remark of §9 — but its justification has changed and the phase
   documents must not present it as a step of the upper bound.
2. **`countReps` is length-indexed; `R_c` is not.** `countReps n N` fixes `n` places, whereas
   `R_c(N)` ranges over all places with `F_k <= N` (`Bounds.lean:9-13`; Phase 1 spec §4.3
   Trap 1). The Lean statements are about the length-`n` restriction. This is sound for the
   §4.3 use, because the fixup block genuinely is a fixed finite block of length `a`.

---

## 5. Certified numerics

### 5.1 Why the existing float path cannot certify T1

`F_c` is an infinite product of terms each `>= 1`. Truncating it **lowers** the value, which
breaks T1's inequality in exactly the wrong direction. `capfib/product.py` truncates at
`cutoff_log = 3.9`. That is sound for Phase 0.5's exploratory slope but cannot certify a bound.

### 5.2 Tail lemma (to be proved and implemented)

For `k > K >= 3`, `F_k >= (3/2)^{k-K} F_K`. With `u := s F_K >= 1`:

```
0 <= a_k(s) <= e^{-s F_k} / (1 - e^{-s F_k})          [from -log(1-y) <= y/(1-y), y = e^{-s F_k}]
s F_k >= u (3/2)^{k-K} >= u (1 + (k-K)/2)
1 - e^{-s F_k} >= 1 - e^{-1} > 0.632

  =>   sum_{k > K} a_k(s)  <=  (1/0.632) * e^{-u} * e^{-u/2} / (1 - e^{-u/2}).
```

The certified evaluation returns `[lo, hi + tail]` where `tail` is this bound.

**Implementation obligations.** The lemma's hypotheses are `K >= 3` and `u = s F_K >= 1`. Both
must be *established*, not assumed: `u >= 1` is checked against the **lower** endpoint of the
interval for `s F_K`, and the tail itself is rounded **upward**. A tail added with the wrong
rounding direction silently invalidates the bound it is meant to certify.

### 5.3 Interval arithmetic and precision

**Fixed `dps = 30` is not sufficient, and a naive `1 - exp(-x)` is not acceptable.** Measured
on this repository at `log(1/s) = 80` — a value Appendix A already uses — with `x = s F_1 = e^{-80}`:

| precision | `1 - exp(-x)` | `log` of it |
|---|---|---|
| `dps = 30` | `[0, 9.86e-32]` — **lower endpoint exactly 0** | `[-inf, -71.39]` |
| `dps = 60` | width `4.3e-27` | `[-80.0000..., -79.9999...]` |

At `dps = 30` the enclosure is still *sound* but carries no information, and differencing two
such terms yields `[-inf, +inf]`. An earlier draft of this spec cited a `≈2e-29` width as
evidence that `dps = 30` suffices; that measurement was taken at `s = 0.1` and does not
transfer to the small-`s` regime the phase actually reports on. It has been withdrawn.

The certified evaluation must therefore do both of the following.

1. **Scale the precision to the dynamic range.** The smallest argument is `s F_1 = s`, so the
   working precision must exceed `log(1/s)` in decimal digits: `dps >= T/log(10) + guard`, with
   `guard >= 40`. This is cheap — `mpmath` is arbitrary-precision and the sum has `O(T)` terms.
2. **Avoid the cancellation directly.** Compute `log(1 - e^{-z})` through a small-`z` series
   enclosure with a proved remainder bound, mirroring what the float path already does in
   `capfib/product.py:_log1m_exp_log`, rather than forming `1 - exp(-z)` and taking a log.
   `mpmath.iv` has no interval `expm1`, so this must be written and tested.

**Acceptance test (§8):** across the whole reported range, the width of the certified interval
for `log F_c(e^-s)` must be below a stated threshold, and both endpoints finite. A test that
only checks soundness would pass on `[-inf, +inf]`.

### 5.4 The minimiser need not be certified

T1 holds for **every** `s > 0`. The fast float path picks a good `s`; interval arithmetic
certifies the bound at that single `s`. A suboptimal `s` costs a slightly weaker bound, never
a wrong one. Accordingly `capfib/saddle.py`'s existing "minimiser hit the bracket boundary"
`ValueError` stops being a correctness condition for the certified path and becomes a quality
signal only; the certified function must not inherit it as a hard failure.

### 5.5 The gate

Mirroring the §4.2 correctness gate that already governs `dp` versus `gf`:

> No certified bound may be reported unless the float path's value lies inside the certified
> interval **across the whole reported range, in the same run that produces the data.**

---

## 6. Code inventory

| File | Action | Responsibility |
|---|---|---|
| `capfib/interval.py` | create | Certified `log_F_c_interval(log_s) -> (lo, hi)` including the §5.2 tail bound |
| `capfib/saddle.py` | modify | Add `log_R_bound_certified(log_n)` returning a rigorous upper bound at a float-chosen `s`; existing float function unchanged |
| `capfib/product.py` | modify | Docstring only: state that this path is **not** certified and point at `capfib/interval.py` |
| `scripts/run_phase2.py` | create | Verification run, artifacts, manifest entry, quotable-figures file |
| `lean/NonLinearNumberSystems/Completeness.lean` | modify | Prove `exists_numeral_of_le` |
| `lean/NonLinearNumberSystems/Bounds.lean` | modify | Prove `countReps_le_uncapped` |
| `tests/test_interval.py` | create | §8.1, §8.2 — interval soundness and the tail bound |
| `tests/test_phase2_bounds.py` | create | §8.3, §8.4, §8.5 — Chernoff inequality, T3 validity, figures-file coverage |
| `pyproject.toml` | modify | Add `mpmath>=1.3` to dependencies |
| `.gitignore` | modify | Add the `!data/phase2_figures.json` exception (§7) |
| `theory/01-background.md` | modify | Repair the completeness argument to the overlapping-interval form (§9) |
| `theory/00-definitions.md` | modify | Restate the `R_u` / CKL identification as pending verification (§9) |
| `theory/claims.yaml` | modify | §12 entries; `completeness-no-gaps` evidence pointer updated |
| `docs/roadmap.md` | modify | Phase 2 checkboxes; the two corrections at line 351 and the one at 341-342 (§9) |

No change to `capfib/fib.py` (infrastructure spec `D2`: place values are constructed there and
nowhere else),
`capfib/dp.py`, `capfib/gf.py`, or `capfib/brute.py`.

---

## 7. Artifacts

| Path | Contents |
|---|---|
| `data/phase2_bounds.csv` | `N, log_R_c, lower_bound_T3, chernoff_certified_hi, asymptotic_upper` per sampled `N` |
| `data/phase2_figures.json` | **tracked** (gitignore exception) — every number quoted in the phase documents |
| `figures/phase2_sandwich.png` | exact `log R_c(N)` between the two bounds |

`data/manifest.json` gains an entry per generated dataset, per the global constraint.

**R-002 mitigation (PD6).** `data/*` is gitignored except the manifest, so numbers hand-copied
into narrative documents cannot be refreshed by regeneration — the project's highest-rated open
risk. `run_phase2.py` writes `data/phase2_figures.json`, added as a `.gitignore` exception so it
is tracked, and the phase documents quote figures from it.

**The check must be keyed, not a membership test.** An earlier draft proposed asserting that
every numeric literal in the prose appears somewhere in the JSON. That is too weak to deliver
what it promises: a drifted number can coincide with an unrelated field, stale entries survive,
and "every numeric literal" also sweeps up dates, section numbers, and mathematical constants.

Instead, each quoted figure carries its key inline, reusing the `{claim:...}` convention the
repository already has:

```
The certified bound exceeds the exact value by {fig:chernoff-slack-1e6} at N = 10^6.
```

The test resolves each `{fig:KEY}` against `data/phase2_figures.json`, formats the stored value
with the precision recorded alongside it, and requires an exact string match with the literal
that precedes the tag. Unknown keys fail; keys present in the JSON but unused anywhere are
reported. This gives correspondence, not mere co-occurrence.

---

## 8. Tests

1. **Interval soundness and sharpness** — for a range of `s` spanning the reported range, the
   float `log_F_c` value lies inside the certified interval, **and** the interval's width is
   below a stated threshold with both endpoints finite. Soundness alone is not enough: an
   interval of `[-inf, +inf]` is sound (§5.3).
2. **Tail bound** — the §5.2 bound exceeds the true tail, checked by evaluating the tail
   explicitly far past the cutoff at several `s`, including a case with `u` close to 1; and the
   hypotheses `K >= 3`, `u >= 1` are enforced rather than assumed.
3. **Chernoff inequality** — `log R_c(N) <= log_R_bound_certified(log N)` on a sampled subset
   of the exact Phase 1 values in the suite, and across the full range in `run_phase2.py`.
4. **Lower bound** — the T3 formula with the implemented `C`, `N_0` does not exceed the exact
   `log R_c(N)` anywhere in `[N_0, 10^6]`.
5. **Figures file** — every `{fig:KEY}` tag in `docs/phase2.md` and
   `docs/phases/phase2_bounds.md` resolves in `data/phase2_figures.json` and the literal
   preceding it matches the stored value at the recorded precision; unused keys are reported.
6. **Lean** — `lake build` succeeds and `#print axioms` shows no `sorryAx` for the two target
   theorems.

Test-suite runtime must stay proportionate: the exhaustive checks live in the script, the
sampled ones in `pytest`.

---

## 9. Documents

- `docs/phases/phase2_bounds.md` — the technical note: T1, T2, T3, C4 with full proofs,
  the L2 attempt and its outcome, the numerical confrontation, and the CKL comparison remark.
- `docs/phase2.md` — summary, cross-referenced from `docs/roadmap.md`, following the
  `docs/phase1.md` pattern.
- `docs/roadmap.md` — Phase 2 checkboxes with commit hashes; and two corrections at
  `docs/roadmap.md:351`:
  1. The formula there reads `C_c = (log N)^2 / (C' log phi)`, which cannot be right for a
     constant — the `(log N)^2` does not belong. Correct it to `C_c = 1/(C' log phi)`.
  2. The anticipated `C' in [2,4]` becomes `C' in [4,8]` **conditional on `C_c` existing**,
     with the honest account of §3: the upper coefficient strengthened, the lower weakened.
  Also correct `docs/roadmap.md:341-342`, whose lower-bound sketch bounds `R_c` below by `R_u`;
  capping only removes representations, so that direction is unavailable.

**CKL comparison remark, and an inconsistency to reconcile.** `theory/00-definitions.md`
currently defines `R_u` as "as above with `d_k` unbounded (Coons–Kristensen–Laursen 2023)" and
lists `log R_u(N) ~ (log N)^2/(2 log phi)` as "theorem, cited (CKL 2023)". That identifies our
duplicated-place `R_u` with CKL's object outright. We do not hold a copy of arXiv:2312.07404,
and their `p_F(n)` counts multisets of Fibonacci numbers whereas our `R_u` counts digit
sequences over places including **both** `F_1 = 1` and `F_2 = 1` — the two differ by a splitting
factor. That factor is very likely `o(exp((log N)^2))` and so harmless to leading order, but it
is not established here.

The two documents cannot both stand as written. Phase 2 reconciles them in the weaker direction,
which is cheap now that T2 does not depend on CKL at all: `theory/00-definitions.md` is amended
so the identification is stated as *pending verification against the paper*, and the comparison
remark in `phase2_bounds.md` is phrased qualitatively, asserting no numerical relationship
between our constants and theirs. Obtaining the paper and making the comparison precise stays
out of scope (§11).

**Completeness's supporting argument has a gap.** `theory/01-background.md:117-126` states the
Kempner–Fraenkel condition for strictly increasing place values `u_1 < u_2 < ...` and then
applies it with `u_k = F_k`, where `F_1 = F_2 = 1` is **not** strictly increasing. The
conclusion is true — an overlapping-interval induction needs only `F_n <= 1 + sum_{j<n} F_j^2`,
which the duplicated 1-place satisfies — but the justification as written does not cover the
convention this project uses, and `completeness-no-gaps` carries `theorem` status on the
strength of it. Since L1 depends on completeness and the Lean proof of `exists_numeral_of_le` is
already in scope, Phase 2 repairs the prose argument to the overlapping-interval form and keeps
the two in step.

---

## 10. Global constraints (inherited)

- Python >= 3.11; place values from `capfib/fib.py` only.
- `R_c(N)` over all places `F_k <= N`, never a fixed length.
- The §4.2 gate governs any `dp`/`gf` output; §5.5 above extends the same discipline to the
  certified bound.
- Never remove a Lean `sorry` without a real proof.
- Every generated dataset writes a `data/manifest.json` entry.
- Every claim added to `theory/claims.yaml` must pass `scripts/check_claims.py`, including the
  universal-quantifier guard. Finite observations are stated with their range.

---

## 11. Out of scope

- Any Lean formalisation of T1–T3 (PD2).
- Phase 3's heuristic derivation of the constant, Phase 4's regression and oscillation
  detection, Phase 5's rigorisation.
- Obtaining arXiv:2312.07404 and making the CKL comparison numerically precise.
- Completing the incomplete Navas reference in `docs/roadmap.md:826`.

---

## 12. Claim ledger entries

| id | status | statement shape |
|---|---|---|
| `sandwich-bounds` | `theorem` | `1/(8 log phi) <= liminf <= limsup <= 1/(4 log phi)`, stated for liminf/limsup and **not** asserting that `C_c` exists; proof location `docs/phases/phase2_bounds.md` |
| `chernoff-effective-verified` | `verified-numeric` | The certified Chernoff bound holds at every `N <= 10^6`, range stated explicitly |
| `product-residual-constant` | `verified-numeric` | `log F_c(e^-s) - (log(1/s))^2/(4 log phi) ≈ 3.2274` over the **sampled** `log(1/s)` range, stated as a sampled observation and not as an `O(1)` error term |

If T5 succeeds via either route, `leading-constant` moves from `conjecture` to `theorem` and
`sandwich-bounds` is restated. If T5 is not attempted or fails, both stay as above.

Two existing ledger entries are also touched, both flagged by review rather than by the original
plan: `completeness-no-gaps` keeps `theorem` status but its evidence pointer moves to the
repaired overlapping-interval argument (§9), and the untagged CKL row in
`theory/00-definitions.md` is restated as pending verification (§9).

---

## 13. Acceptance criteria

1. T1, T2, T3, C4 stated and proved in `docs/phases/phase2_bounds.md`, with T2's error control
   written up via the uniform-bound scheme of §4.2 — not the withdrawn Binet-only argument —
   and C4 carrying its "if `C_c` exists" caveat.
2. `lake build` clean; no `sorry` remains in `lean/NonLinearNumberSystems/`.
3. `run_phase2.py` regenerates every artifact, writes manifest entries, and reports the §5.5
   gate result; the certified bound holds at every exact `N <= 10^6`.
4. The certified interval for `log F_c(e^-s)` has finite endpoints and width below the stated
   threshold across the whole reported range — soundness alone does not satisfy this.
5. The full test suite passes, including the new tests of §8.
6. `scripts/check_claims.py` reports `claims.yaml OK` with the §12 entries added.
7. `docs/roadmap.md` Phase 2 checkboxes updated with commit hashes; the malformed `C_c` formula
   and the `R_u`-as-lower-bound sketch corrected; the `C'` interval restated honestly per §3.
8. `theory/01-background.md`'s completeness argument covers the duplicated 1-place, and
   `theory/00-definitions.md`'s CKL identification is reconciled with §9.
9. Every `{fig:KEY}` tag in the phase documents resolves against `data/phase2_figures.json` and
   matches the literal beside it.

---

## Appendix A — Design-time numerical observations

Produced during this design session with `capfib.product` / `capfib.saddle` on the Phase 1
dataset. They motivated the decisions above and are **not** yet gate-verified under §5.5;
`run_phase2.py` regenerates all of them. Recorded here under the R-001 convention (measured
figures retained in a design spec, with provenance stated).

**Convergence of `log F_c(e^-s)` to `(log(1/s))^2/(4 log phi)`:**

| `log(1/s)` | `log F_c` | prediction | ratio |
|---|---|---|---|
| 10 | 55.1614 | 51.9522 | 1.06177 |
| 80 | 3328.1665 | 3324.9391 | 1.00097 |
| 1280 | 851187.6304 | 851184.4029 | 1.00000 |

Residual `≈ 3.2274`, varying by `< 2e-4` across one golden-ratio period at `log(1/s) ≈ 100`.
Stated as a sampled observation only.

**Certified-bound slack against exact Phase 1 values (float path, uncertified):**

| `N` | `log R_c(N)` | Chernoff bound | slack |
|---|---|---|---|
| 10^2 | 7.072 | 12.066 | +4.995 |
| 10^4 | 28.349 | 37.552 | +9.202 |
| 10^6 | 68.363 | 81.914 | +13.551 |

**T3 construction evaluated directly** (fixup block `[1,a]`, counting block `(a,c]`,
`m_k = floor(N/(M F_k))`). Budget respected at every row; the bound stays below the exact
value at every row:

| `N` | `a` | `c` | counting places | `log` of the T3 count | T3 count itself | `(log N)^2/(8 log phi)` | exact `log R_c(N)` | implied `C` |
|---|---|---|---|---|---|---|---|
| 10^3 | 9 | 16 | 7 | 1.792 | 6 | 12.395 | 15.515 | 0.794 |
| 10^4 | 11 | 20 | 9 | 6.174 | 480 | 22.036 | 28.349 | 0.776 |
| 10^5 | 14 | 25 | 11 | 9.980 | 21600 | 34.431 | 45.902 | 0.869 |
| 10^6 | 16 | 30 | 14 | 17.774 | 52390800 | 49.580 | 68.363 | 0.877 |

The `log`/count distinction matters for the artifact schema: `data/phase2_bounds.csv` stores
the logarithm, and a column named "count" holding `1.792` would be wrong.

The implied `C` is finite-range evidence only and **does not bound `C`**. The asymptotic
secondary coefficient derived in §4.3 is `1/(2 log phi) = 1.0391...`, above every entry in this
column, which is consistent: the implied values are still drifting upward across the range.

**Empirical ratio `log R_c(N)/(log N)^2`:** 0.3334 at `10^2`, 0.3342 at `10^4`, 0.3582 at `10^6`
— rising, and strictly inside the interval `[0.2598, 0.5195]` at every decade sampled
(`1/(8 log phi) = 0.2597608...`, `1/(4 log phi) = 0.5195217...`).

---

## Appendix B — Review history

### 2026-08-21 — Codex `gpt-5.6-sol`, effort `ultra` (spec review per CLAUDE.md rule 6)

Twelve findings, each verified against the repository before action. Nothing was accepted or
dismissed wholesale.

**Accepted and fixed — substantive:**

| Finding | Verification | Fix |
|---|---|---|
| §4.2's error control was a hand-wave: Binet controls `log F_k`, not `a_k - log(F_k+1)`, and a pointwise `o(1)` cannot be summed over `Theta(T)` indices | Reproduced the counterexample: at `s_n = 1/(F_n(F_n+1))`, `a_n - log(F_n+1) -> log(1-e^-1) = -0.458675`, confirmed to six decimals at `n = 30, 38` | §4.2 rewritten around two uniform bounds on `h(x) = -log(1-e^-x)` with exact cutoffs `p`, `q`. The theorem stands; the justification did not. |
| `dps = 30` is insufficient and naive `1 - exp(-x)` is cancellation-prone | Worse than reported: at `log(1/s) = 80`, `1 - exp(-x)` returns `[0, 9.86e-32]` — lower endpoint **exactly zero** — so `log` gives `[-inf, -71.39]` and the term difference is `[-inf, +inf]`. The original `≈2e-29` measurement was taken at `s = 0.1`, not in the reported regime | §5.3 rewritten: precision scaled as `dps >= T/log 10 + 40`, plus a series enclosure for small `z`; §8.1 now tests interval **width**, since soundness alone passes on `[-inf, +inf]` |
| `C' in [4,8]` is not a strengthening of `[2,4]`, and presumes `C_c` exists | Confirmed against `docs/roadmap.md:332-347`: the roadmap's anticipated lower coefficient is `1/(4 log phi)`, which Phase 2 **weakens** to `1/(8 log phi)` while strengthening the upper | §3 now states the existence caveat and that both endpoints move in opposite directions; the "iff attained" formulation is withdrawn as ambiguous |
| `C = 1` is not justified; the secondary coefficient is `1/(2 log phi) ≈ 1.039` | Re-derived independently; the finite-range `C ≈ 0.88` is consistent with an asymptotic coefficient above 1 | §3, §4.3 and Appendix A state the explicit coefficient and mark `C ≈ 0.88` as non-bounding |
| The figures-file membership test does not deliver the correspondence it claims | Correct — a drifted number can coincide with an unrelated field, and "numeric literal" sweeps up dates and section numbers | §7 replaced with keyed `{fig:KEY}` tags resolved against the JSON, mirroring the existing `{claim:...}` convention |
| Completeness's supporting argument states Kempner–Fraenkel for strictly increasing weights, then applies it to `F_1 = F_2 = 1` | Confirmed at `theory/01-background.md:117-126`. The conclusion is true; the justification does not cover this convention, and `completeness-no-gaps` holds `theorem` status on it | Repairing the prose to the overlapping-interval form brought into scope (§9) |
| `theory/00-definitions.md` identifies our duplicated-place `R_u` with CKL's object outright, contradicting this spec | Confirmed | Reconciled in the weaker direction (§9); cheap, since T2 no longer depends on CKL |
| `docs/roadmap.md:351` writes `C_c = (log N)^2/(C' log phi)` for a constant | Confirmed | Added to the roadmap corrections (§9) |

**Accepted and fixed — presentation:** `1/(8 log phi)` rounds to `0.2598`, not `0.2599`
(verified: `0.2597608651...`); Appendix A's "T3 count" column holds logarithms, now labelled and
accompanied by the integer counts; regime C has infinitely many places with `O(1)` total
contribution; `L` versus `T = log(1/s)` notation corrected in §4.2; the `D1`–`D6` labels
collided with the infrastructure spec's and are now `PD1`–`PD6`.

**Accepted with the scope widened:** the objection that L1's factor of two is structural only
to *this* family — one selected completion — rather than to any refinement. The "do not try"
wording is withdrawn, and following the objection produced a second stretch route, L2b
(§4.4): count all completions instead of one, which makes the sub-problem the same problem one
scale down.

**Pushed back:** Codex describes its derived lower bound `t^2/(8λ) - t log t/(2λ) + O(t)` as
"stronger than" the spec's `- O(log N log log N)`. It is not stronger — with `t = log N`,
`t log t` **is** `log N log log N`. It is the same order with an explicit constant, which is
the part that matters and which the spec now records.

**Confirmed correct, no change:** §4.3's L1 construction (distinct valid numerals, no
pigeonhole or steering needed, claimed yield right) and §5.2's tail lemma, including
`F_k >= (3/2)^{k-K} F_K` for `k > K >= 3` under this convention.
