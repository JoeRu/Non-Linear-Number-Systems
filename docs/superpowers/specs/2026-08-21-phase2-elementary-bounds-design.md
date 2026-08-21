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

| # | Decision | Rationale |
|---|---|---|
| D1 | Prove our own upper bound at `1/(4 log phi)` rather than cite Coons–Kristensen–Laursen at `1/(2 log phi)` | The Chernoff bound plus an elementary evaluation of `log F_c(e^-s)` reaches the conjectured constant. The citation route is a factor 2 weaker and makes the phase's headline result someone else's theorem. |
| D2 | Lean scope is the two existing `sorry`s only | `exists_numeral_of_le` and `countReps_le_uncapped` are finite combinatorial statements. T1–T3 are analytic; `lean/NonLinearNumberSystems/Bounds.lean:15-18` already excludes that class from Lean. |
| D3 | Two-layer theorems: effective **and** asymptotic | At `N = 10^6` the empirical ratio is only ≈0.358, so a bare `(1+o(1))` statement at 0.520 cannot be confronted with our data. The effective layer can be, and is what Phase 4 can plot. |
| D4 | Lower bound: commit to L1, time-box L2 | L1 yields `1/(8 log phi)` and is near-certain to close. L2 refines L1's own skeleton toward `1/(4 log phi)`; attempting it wastes no work. |
| D5 | Certified numerics via interval arithmetic (`mpmath.iv`) | The alternative — a hand-rolled float interval type — trades a pure-Python dependency for an unprovable assumption about libm ulp accuracy, which would need a `docs/risks.md` entry. |
| D6 | `run_phase2.py` emits quotable figures to a tracked file | Closes the project's highest-rated open risk R-002 for this phase instead of re-incurring it. |

---

## 2. Notation

Fibonacci convention is spec D2, fixed in `capfib/fib.py`: `F_1 = F_2 = 1`, `F_3 = 2`, …
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

**C4 — sandwich.** Combining T2 and T3,

```
1/(8 log phi) <= liminf log R_c(N)/(log N)^2 <= limsup log R_c(N)/(log N)^2 <= 1/(4 log phi).
```

In the roadmap's parametrisation `C_c = 1/(C' log phi)` this is `C' in [4, 8]`.
Note this **replaces** the roadmap's anticipated `C' in [2,4]` (`docs/roadmap.md:351`),
which assumed the upper bound came from CKL. The Phase 3 conjecture `C' = 4` now sits
**on the boundary** of the proved interval: Phase 2 establishes that the conjecture holds
if and only if the upper bound T2 is attained. The roadmap text must be updated accordingly.

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
valid at every `N`. This is a **paper proof**, not a Lean target (D2).

### 4.2 T2 — the three-regime evaluation

Each term `a_k(s)` depends on `k` through `u := s F_k` and `v := s F_k (F_k + 1)`:

| Regime | Condition | Behaviour of `a_k(s)` | Count of places |
|---|---|---|---|
| A — cap binds | `s F_k^2 << 1` | `= log(F_k + 1) + o(1) ≈ k log phi` | `≈ L/2` |
| B — budget binds | `s F_k^2 >> 1 >> s F_k` | `= log(1/(s F_k)) + o(1)` | `≈ L/2` |
| C — negligible | `s F_k >> 1` | exponentially small | `O(1)` before the tail bound takes over |

Both A and B contribute `(log(1/s))^2 / (8 log phi)`, summing to `(log(1/s))^2 / (4 log phi)`.
This equal split is the structural fact the lower bound has to contend with (§4.3).

Error control:
- By Binet, `log F_k = k log phi - log sqrt 5 + O(phi^{-2k})`, so each regime's sum is an
  arithmetic series with `O(1)` correction.
- Each regime boundary is crossed within `O(1)` places, because `F_k` grows geometrically.
- Hence the total error is `O(log(1/s))`, which is stronger than T2 requires.

Then T1 with `s` chosen so that `s N = log(1/s)/(2 log phi)` — i.e. `s ≈ log N/(2 N log phi)`,
giving `log(1/s) = log N - O(log log N)` — makes the `sN` term `O(log N)` and yields T2's
consequence.

### 4.3 T3 — the construction (L1)

Fix `N` and let `c` be the largest index with `F_c <= N`. Split the places into **two**
blocks — no third block is needed:

```
fixup block     [1, a]   where a is the smallest index with F_a F_{a+1} >= N
counting block  (a, c]   free digits; this is what produces the count
```

**(1) Fixup capacity.** By `sum_sq_place`, places `1..a` have total capacity
`sum_{k<=a} F_k^2 = F_a F_{a+1} >= N`. By completeness, every residue in `[0, N]` is
represented on that block **exactly**.

**(2) Free family.** On the counting block set `m_k = floor(N / (M F_k))`, where `M = c - a`
is the number of counting places. Then `sum_k m_k F_k <= N`, so every free tuple has sum
`sigma <= N`. The caps are respected automatically: for `k > a` we have `F_k^2 > N`, hence
`m_k <= N/F_k < F_k`.

**(3) Completion.** For each free tuple, `N - sigma` lies in `[0, N]` and is therefore
representable on the fixup block by (1). The combined digit sequence is a numeral of value `N`
respecting every cap.

**(4) Injectivity.** Distinct free tuples differ on the counting block, so the resulting
numerals differ.

Hence `R_c(N) >= prod_{k=a+1}^{c} (m_k + 1)`, and since `m_k + 1 >= N/(M F_k)`,

```
log R_c(N) >= sum_{k=a+1}^{c} log(m_k + 1)
           >= sum_{k=a+1}^{c} [ (L - k) log phi - log M ] + O(L)
            = (log N)^2 / (8 log phi) - O((log N)(log log N)),
```

using `a = L/2 + O(1)`, `c = L + O(1)`, `M = L/2 + O(1)`.

**No pigeonhole and no steering are required.** Because the fixup block's capacity already
exceeds `N`, *every* free tuple completes, so the count is the full product rather than the
contents of a fullest bucket. An earlier draft of this construction carried a third
"steering" block and a pigeonhole step; both are unnecessary and must not be reintroduced.

**Why the constant is `1/8` and not `1/4`.** The fixup block must absorb residues as large as
`N`, which forces `F_a F_{a+1} >= N`, i.e. `a = L/2 + O(1)`. Places `1..L/2` are exactly the
cap-binding regime A of §4.2, which carries half the total. L1 spends that half on fixup. The
factor of two is **structural to L1**, not slack in the estimates: sharpening L1's estimates
without changing its block structure is wasted effort, and the implementer should not try.

**Uniformity.** `a` and `c` are defined from `N` alone and every step is valid for all
sufficiently large `N`, so T3 holds for every `N >= N_0` — not along a convenient subsequence.

**`C` and `N_0` are outputs of the proof, not inputs to it.** The implementer derives them
from the evaluation above and then verifies them numerically per §8.4. A design-time run of
this exact construction (Appendix A) satisfies the budget, stays below the exact
`log R_c(N)` at every decade, and implies `C ≈ 0.88` — so `C = 1` is the expected order, but
the proved value governs.

### 4.4 T5 — the stretch (L2)

The binding constraint is §4.3(1): the fixup block must cover residues up to `N`. L2 attacks
exactly that. Replace the contiguous reserved block with a **sparse** reserved set — roughly
every `log L`-th place — and fix up residues hierarchically, coarsest scale first, so each
scale absorbs only a residue of its own magnitude instead of the full `N`. The reserved places
then carry a vanishing fraction of the count, and the yield tends to
`(1 - o(1)) (log N)^2 / (4 log phi)`.

**Failure mode, stated up front:** the hierarchical carry must terminate without pushing any
digit past its cap `F_k`. If that cannot be shown, T5 fails and the phase ships T1–C4
unchanged. Time-box: T5 is attempted only after T1–C4, their proofs, artifacts, and the Lean
work are complete and committed.

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

### 5.3 Interval arithmetic

`mpmath.iv` at `dps = 30`; verified during design to give interval widths `≈ 2e-29` on the
operations required (`log`, `exp`, `1 - exp(-x)`, quotient, sum). Cost is irrelevant: ~30
places times a few dozen values of `s`.

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

No change to `capfib/fib.py` (spec D2: place values are constructed there and nowhere else),
`capfib/dp.py`, `capfib/gf.py`, or `capfib/brute.py`.

---

## 7. Artifacts

| Path | Contents |
|---|---|
| `data/phase2_bounds.csv` | `N, log_R_c, lower_bound_T3, chernoff_certified_hi, asymptotic_upper` per sampled `N` |
| `data/phase2_figures.json` | **tracked** (gitignore exception) — every number quoted in the phase documents |
| `figures/phase2_sandwich.png` | exact `log R_c(N)` between the two bounds |

`data/manifest.json` gains an entry per generated dataset, per the global constraint.

**R-002 mitigation (D6).** `data/*` is gitignored except the manifest, so numbers hand-copied
into narrative documents cannot be refreshed by regeneration — the project's highest-rated open
risk. `run_phase2.py` writes `data/phase2_figures.json`, added as a `.gitignore` exception so it
is tracked, and `docs/phase2.md` and `docs/phases/phase2_bounds.md` cite figures from it. A test
asserts that every numeric literal quoted in those two documents appears in that file, so drift
between prose and data becomes a test failure rather than a silent error.

---

## 8. Tests

1. **Interval soundness** — for a range of `s`, the float `log_F_c` value lies inside the
   certified interval.
2. **Tail bound** — the §5.2 bound exceeds the true tail, checked by evaluating the tail
   explicitly far past the cutoff at several `s`.
3. **Chernoff inequality** — `log R_c(N) <= log_R_bound_certified(log N)` on a sampled subset
   of the exact Phase 1 values in the suite, and across the full range in `run_phase2.py`.
4. **Lower bound** — the T3 formula with the implemented `C`, `N_0` does not exceed the exact
   `log R_c(N)` anywhere in `[N_0, 10^6]`.
5. **Figures file** — every numeric literal in `docs/phase2.md` and
   `docs/phases/phase2_bounds.md` is present in `data/phase2_figures.json`.
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
- `docs/roadmap.md` — Phase 2 checkboxes with commit hashes; the `C' in [2,4]` text at line 351
  corrected to `C' in [4,8]` per §3.

**CKL comparison remark.** We do not hold a copy of arXiv:2312.07404, and their `p_F(n)` counts
multisets of Fibonacci numbers while our `R_u` counts digit sequences over places including both
`F_1 = 1` and `F_2 = 1` — the two differ by a splitting factor. That factor is very likely
`o(exp((log N)^2))` and so harmless to leading order, but it is **not** established here. The
remark must therefore be phrased qualitatively and must not assert a numerical relationship
between our constants and theirs. Obtaining the paper and making the comparison precise is
out of scope (§11).

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

- Any Lean formalisation of T1–T3 (D2).
- Phase 3's heuristic derivation of the constant, Phase 4's regression and oscillation
  detection, Phase 5's rigorisation.
- Obtaining arXiv:2312.07404 and making the CKL comparison numerically precise.
- Completing the incomplete Navas reference in `docs/roadmap.md:826`.

---

## 12. Claim ledger entries

| id | status | statement shape |
|---|---|---|
| `sandwich-bounds` | `theorem` | `1/(8 log phi) <= liminf <= limsup <= 1/(4 log phi)`; proof location `docs/phases/phase2_bounds.md` |
| `chernoff-effective-verified` | `verified-numeric` | The certified Chernoff bound holds at every `N <= 10^6`, range stated explicitly |
| `product-residual-constant` | `verified-numeric` | `log F_c(e^-s) - (log(1/s))^2/(4 log phi) ≈ 3.2274` over the **sampled** `log(1/s)` range, stated as a sampled observation and not as an `O(1)` error term |

If T5 succeeds, `leading-constant` moves from `conjecture` to `theorem` and `sandwich-bounds`
is restated. If T5 is not attempted or fails, both stay as above.

---

## 13. Acceptance criteria

1. T1, T2, T3, C4 stated and proved in `docs/phases/phase2_bounds.md`.
2. `lake build` clean; no `sorry` remains in `lean/NonLinearNumberSystems/`.
3. `run_phase2.py` regenerates every artifact, writes manifest entries, and reports the §5.5
   gate result; the certified bound holds at every exact `N <= 10^6`.
4. The full test suite passes, including the new tests of §8.
5. `scripts/check_claims.py` reports `claims.yaml OK` with the §12 entries added.
6. `docs/roadmap.md` Phase 2 checkboxes updated with commit hashes; the `C'` interval corrected.
7. Every number quoted in the phase documents is present in `data/phase2_figures.json`.

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

| `N` | `a` | `c` | counting places | T3 count | `(log N)^2/(8 log phi)` | exact `log R_c(N)` | implied `C` |
|---|---|---|---|---|---|---|---|
| 10^3 | 9 | 16 | 7 | 1.792 | 12.395 | 15.515 | 0.794 |
| 10^4 | 11 | 20 | 9 | 6.174 | 22.036 | 28.349 | 0.776 |
| 10^5 | 14 | 25 | 11 | 9.980 | 34.431 | 45.902 | 0.869 |
| 10^6 | 16 | 30 | 14 | 17.774 | 49.580 | 68.363 | 0.877 |

The implied `C` is still drifting upward over this range, so `C = 1` is an expected order of
magnitude and not a value this table establishes.

**Empirical ratio `log R_c(N)/(log N)^2`:** 0.3334 at `10^2`, 0.3342 at `10^4`, 0.3582 at `10^6`
— rising, and strictly inside the proved interval `[0.2599, 0.5195]` at every decade sampled.

---

## Appendix B — Review history

| Date | Reviewer | Outcome |
|---|---|---|
| 2026-08-21 | (pending) Codex `gpt-5.6-sol`, effort `ultra` | Spec review per CLAUDE.md rule 6 |
