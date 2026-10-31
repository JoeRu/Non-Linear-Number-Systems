# Roadmap: Asymptotics of R_c(N)  
## Capacity-constrained Fibonacci partitions

**Status:** Research initiative  
**Current version:** 2026-08-15  
**Target audience:** Original mathematical publication

---

## Context

This project studies the asymptotics of $R_c(N)$ — the number of representations of a number $N$ as
$$\sum_{k \ge 1} d_k F_k = N$$
with digit bounds $0 \le d_k \le F_k$ for all positions $k$.

The problem sits exactly between two classical, solved cases:

1. **Binary partitions** (Mahler 1940, de Bruijn 1948):  
   Partitions into powers of two with unbounded multiplicity. Asymptotics known, including oscillating corrections periodic in $\log_2 N$.

2. **Fibonacci partitions without a cap** (Coons–Kristensen–Laursen 2023, arXiv:2312.07404):  
   Partitions into Fibonacci numbers, non-distinct, with unbounded multiplicity. Here, for the first time, the full asymptotics
   $$\log p_F(n) \sim \frac{(\log n)^2}{2\log\varphi}$$
   was rigorously established, with oscillations and error analysis. The method combines Hardy–Ramanujan ideas, Mahler–de Bruijn techniques and analytic continuation of the Fibonacci Dirichlet series $\zeta_F(z)=\sum_{k\ge1}F_k^{-z}$ (after Navas).

**The new challenge:** The position-dependent bound $d_k \le F_k$ breaks both simplifications. It is neither as uniform as with powers of two nor as simple as with unbounded multiplicity. This makes the problem an ideal test case for generalised asymptotic methods in additive combinatorics.

---

## Progress

**Open risks from unresolved review disputes:** [`docs/risks.md`](risks.md).

As of: 2026-08-21. Every completed subtask with the commit that covers it.
Open items are deliberately *not* checked off — not even when infrastructure
for them already exists.

### Infrastructure (cross-cutting, not a roadmap phase)

- [x] Benchmark scaffolding removed, repo rebuilt around the research programme — `6095170`
- [x] `capfib` package: place values, brute-force oracle, two independent fast paths — `425b503`, `0140c82`, `674058b`, `054f968`
- [x] Log-space evaluation of the generating function, Legendre transform, regression — `3aeffa6`, `78ccc80`, `de735dc`
- [x] Provenance manifest for all generated data (upsert instead of append) — `a688b99`, `9f3436d`
- [x] Claim ledger `theory/claims.yaml` + validator `scripts/check_claims.py` — `625ce82`, `1b4dca0`, `9f3436d`
- [x] Project skills `rc-numerics`, `claim-ledger` — `0d377c1`, `7e83f82`
- [x] Lean development compiles for the first time (elan, Mathlib v4.14.0, `lake-manifest.json` under version control) — `543c8b0`
- [x] Lean switched to the *right* object: position-dependent bound instead of constant capacity — `53f8030`

### Phase 0 — Specification ✅

- [x] Fibonacci convention fixed: $F_1=F_2=1$, $F_3=2$, $F_4=3$, $F_5=5$ — `425b503`, `860dd5b`
- [x] $R_c$, $R_u$, $b$ precisely defined; $R_c$ over **all** places $F_k \le N$ — `625ce82`
- [x] Research questions (A), (B), (C) formulated — `625ce82`
      ((A) "Does $C_c$ exist?" has been **answered** since Phase 2: yes, $C_c = 1/(4\log\varphi)$ — `43397a2`)
- [x] Deliverable `theory/00-definitions.md` — `625ce82`
- [x] Known / conjecture / open separated in the ledger — `625ce82`

### Phase 0.5 — Constant gate ✅

- [x] `scripts/run_phase0_gate.py`, `data/phase0_5_gate.csv`, `figures/phase0_5_gate.png` — `1d218a6`
- [x] Measurement: local slope **0.518710** at $N = 10^{3200}$ against $1/(4\log\varphi) = 0.519522$ {claim:gate-local-slope} — `1d218a6`
- [x] Result correctly stated as an *upper* bound; $1/(8\log\varphi)$ ruled out only under saddle-point tightness — `1b4dca0`, `3c97822`
      (**Addendum Phase 2:** The caveat no longer applies — C5 rules out $1/(8\log\varphi)$
      unconditionally, by a route that does not use this measurement at all; the measurement itself
      is unaffected by this — `30da98a`)
- [x] Deliverable `docs/phases/phase0_5/report.md` — `1d218a6`, `1b4dca0`, `3c97822`
- [x] Roadmap adapted to the revised phase sequence — `860dd5b`

### Phase 1 — Exact computation ✅

**Result:** [`docs/phases/phase1/summary.md`](phases/phase1/summary.md) — summary; details in
[`docs/phases/phase1/report.md`](phases/phase1/report.md).

Done:

- [x] DP recurrence (naive digit loop) — `674058b`
- [x] Independent second implementation via the closed product form — `054f968`
- [x] Brute-force oracle (deliberately slow, serves as the specification) — `0140c82`
- [x] **Correctness gate:** DP against the oracle for all $N \le 200$, both fast paths against each other for all $N \le 500$ — `054f968`
- [x] Table from `theory/01-background.md` §4 reproduced exactly for $n = 1..10$ — `674058b`
- [x] Completeness confirmed numerically (details: `docs/phases/phase1/summary.md` section "Completeness") — `674058b`
- [x] Run up to $N = 10^6$ (exact, not log-domain — the deferred path is not needed) — `9ce15e9`
- [x] `phase1_data.csv` — `9ce15e9`
- [x] `phase1_plot.png` → delivered as `phase1_growth.png` and `phase1_fluctuation.png` — `9ce15e9`
- [x] `docs/phases/phase1/report.md` — `8601426`
- [x] Descriptive statistics: monotonicity, local fluctuation — `9ce15e9`
- [x] Extremal $N$ (open problem 2) — `9ce15e9`
- [x] **Fluctuation finding:** `R_c(N)` fluctuates strongly (49.6
      {fig:decreasing-fraction}% decreasing steps, from
      `data/phase1_summary.json`) {claim:rc-not-monotone}; this
      settles the question left open in Phase 0: the finding
      **constrains Route B** (it is a boundary condition on it, not a choice
      against Route A) — it makes it advisable to conduct a Tauberian attack via the
      summatory function `S_c(N)` rather than directly via `R_c(N)`;
      Route A remains the primary route for the rigorous proof of the asymptotics
      (see Phase 5) — `8601426`

### Phase 2 — Elementary bounds ✅ Sandwich closed, limit proved

- [x] $\sum_{k \le n} F_k^2 = F_n F_{n+1}$ **proved in Lean** (not present in Mathlib) — `53f8030`
- [x] `countReps_le_uncapped` **proved in Lean**, without `sorry` — `53f8030`, `3a1b8c1`.
      What is proved is the **length-indexed** inequality `countReps n N ≤ countRepsUncapped n N`
      at fixed $n$, **not** the all-places $R_c(N) \le R_u(N)$ (Trap 1 in `CLAUDE.md`,
      distinction in `docs/phases/phase2/report.md` §7). The theorem is moreover **not load-bearing**:
      T1/T2 prove the upper bound directly and without citing CKL; the inequality supports
      only the qualitative CKL remark.
- [x] Completeness **proved in Lean**, without `sorry` (`exists_numeral_of_le`, greedy descent) — `53f8030`, `613da4f`
- [x] Extra: "1 > 1" formally proved — two different numerals with the same value (`exists_two_numerals_same_value`) — `53f8030`
- [x] Upper bound **without** Coons–Kristensen–Laursen: T1 (effective Chernoff bound) and T2
      (asymptotic), coefficient $1/(4\log\varphi)$ — `9d282c1`
- [x] Lower bound: constructive proof T3 (two-block construction L1), coefficient
      $1/(8\log\varphi)$ for $N \ge 10000$, with $(C, N_0) = (2, 10000)$ — `9d282c1`
- [x] `docs/phases/phase2/report.md` with T1, T2, T3, C4 and explicit error terms — `9d282c1`, `4f93517`, `48cb082`
- [x] Certified numerical confrontation (interval arithmetic, gate 1e-12) at the
      37 sample values from `data/phase1_data.csv` — `2a5ee43`, `9ac2198`, `199d7dd`
- [x] Synthesis: C4 yields — **if** $C_c$ exists at all — $C' \in [4,8]$;
      C4 itself does not assert existence — `9d282c1`
- [x] Summary `docs/phases/phase2/summary.md`, ledger entries `sandwich-bounds`,
      `chernoff-effective-verified`, `product-residual-sampled` — `c4743bc`
- [x] **Sandwich closed** (Route L2b): flatness lemma F — the block $[1,a]$ is flat on
      its middle band, $B(a,m) \ge \exp(\lambda a^2/2 - O(a))$ uniformly in
      $m$ — and from it T5: $\log R_c(N) \ge t^2/(4\lambda) - t\log t/(2\lambda) - 7.5\,t$
      for $N \ge 10000$, $t = \log N$. Route L2a does **not** close; where it stalls
      is recorded in `docs/phases/phase2/report.md` §8.6 — `43397a2`
- [x] **Existence of $C_c$ proved** — research question (A) is thereby **answered**: C5 shows
      that $\lim_N \log R_c(N)/(\log N)^2$ exists and $= 1/(4\log\varphi)$. Hence
      $C' = 4$ holds **unconditionally**, no longer subject to an existence caveat. C4 remains as
      a weaker, still true statement (limit inferior / superior), as does T3
      — T5 does not replace them but improves on them — `43397a2`
- [x] Ledger: `leading-constant` promoted from `conjecture` to `theorem`, `sandwich-bounds`
      delimited from C5 — `43397a2`

### Phase 3 — Saddle-point heuristic ⬜ open

- [ ] Three-regime decomposition worked out cleanly
- [ ] Legendre transform to the constant derived
- [ ] `phase3_heuristic.md` with an explicit heuristic warning
- [ ] Secondary-term expansion ($C_1$, $C_2$)
      (**Addendum Phase 2:** The $\log N\log\log N$ term is already determined — T2's
      effective form and T5 carry the same coefficient, so
      $\log R_c(N) = t^2/(4\lambda) - t\log t/(2\lambda) + O(t)$ holds with $t=\log N$.
      **Mind the normalisation:** in the notation used further down in this section,
      which factors out $1/\log\varphi$, this means $C_1 = -1/2$; in the notation of
      research question (B) in `theory/00-definitions.md`, which factors out nothing,
      the same statement reads $c_1 = -1/(2\log\varphi)$. What remains open is $C_2$ resp. $c_2$ — ledger
      `secondary-term-constant`, not `saddle-correction-constant`; these are two
      different questions.)

Note: The constant has already been *measured* by Phase 0.5 and, since Phase 2, also
*proved* (C5, `docs/phases/phase2/report.md` §8). Phase 3 must now *explain* it, not
predict it and not establish it.

### Phase 4 — Numerical confrontation ⬜ open

- [x] Direct product evaluation $\log F_c(e^{-s})$ (tool in place, verified against the exact series to $10^{-16}$) — `3aeffa6`
- [x] Four-term regression available as a tool — `de735dc`
- [ ] Fit to Phase 1 data (requires Phase 1)
- [ ] Oscillation detection: residuals against $\{\log_\varphi N\}$, Fourier analysis
- [ ] `capfib/oscillation.py` (deliberately not created yet — no test material without Phase 1)
- [ ] `phase4_numerical_report.md`

### Phase 5 — Rigorisation ⬜ open

- [ ] Route A: Mellin transform and $\zeta_F^{(F+1)}$
- [ ] Route B: Tauberian theorems for $S_c(N)$
- [ ] Route C: functional equation (exploratory)
- [x] **Saddle-point tightness proved** — `saddle-tightness` has been a
      `theorem` since Phase 2, no longer a heuristic. With $t=\log N$ and
      $\Lambda(N) = \min_s\,[sN + \log F_c(e^{-s})]$: T1 places $\log R_c(N)$ below
      $\Lambda(N)$; T2, evaluated at $s = t/(2\lambda N)$, places $\Lambda(N)$ below
      $t^2/(4\lambda) - t\log t/(2\lambda) + O(t)$ — this $s$ is a candidate in the
      minimum; T5 places $\log R_c(N)$ above $t^2/(4\lambda) - t\log t/(2\lambda) - 7.5\,t$.
      The $t^2$ **and** the $t\log t$ terms cancel, so the saddle-point correction is
      $O(t) = O(\log N)$, in particular $o(t^2)$, and both share the
      leading coefficient. (The coarser reading $O(t\log t)$ is wrong — $\Lambda(N)$ is
      **not** $t^2/(4\lambda) + O(t)$; the term $-t\log t/(2\lambda)$ is not $O(t)$.)
      The original purpose of this item — ruling out $1/(8\log\varphi)$ — has
      lapsed anyway, because C5 rules out this value unconditionally — `43397a2`, `30da98a`
- [ ] **Two finer statements, both still open.** The *order* of the
      saddle-point correction is proved along with Phase 2 — it is $O(\log N)$, because
      the $t^2$ and $t\log t$ terms cancel between T2 and T5. What is open are two
      **different** constants, and they must not be equated:
      `saddle-correction-constant` (does $\Lambda(N) - \log R_c(N)$ have a definite
      leading coefficient in $\log N$?) and `secondary-term-constant` (does $c_2$ exist in
      the expansion of $\log R_c(N)$?). Both in the ledger with status `open`, neither of
      them part of `saddle-tightness`, which makes the coarser and now proved statement.
      They differ by the leading coefficient of
      $\Lambda(N) - [t^2/(4\lambda) - t\log t/(2\lambda)]$, which is itself unproved:
      T2's $O(t)$ is a bound, not an asymptotic.

### Phase 6 — Oscillations ⬜ open

- [ ] Pole spectrum from Phase 5
- [ ] Fourier coefficients of $\Psi(\log_\varphi N)$
- [ ] Explicit error bounds
- [ ] `phase6_oscillations.md`

### Phase 7 — Generalisation and write-up ⬜ open

- [x] `paper/main.tex` and `paper/refs.bib` created, so that citations accumulate in BibTeX from day 1 — `6095170`
- [ ] Generalisation to $d_k \le c F_k^\alpha$
- [ ] General linear recurrences (Pisot base)
- [ ] Paper
- [ ] arXiv preprint

---

## Phase 0 — Specification

**Time horizon:** 1–2 days  
**Criticality:** ESSENTIAL — all later phases rest on it

### Goals

- Fix all notational conventions  
- Turn the central research questions into precise mathematical statements  
- Scoping: which questions are posed, which are open?

### Substance

1. **Fibonacci convention:**  
   To fix: $F_1, F_2, F_3, \ldots$ with explicit values.  
   **Fixed:** $F_1=1, F_2=1, F_3=2, F_4=3, F_5=5, \ldots$ — see `theory/00-definitions.md`.
   The duplicated 1-place is intentional: it is the origin of the "1 > 1" phenomenon
   (numerals `1000` and `0100` both have value 1), and only under this convention
   does $\sum_{k\le n} F_k^2 = F_n F_{n+1}$ hold, which fixes the completeness bound.
   **Consequence:** $d_1, d_2 \in \{0,1\}$.

2. **Sharpen definitions:**  
   - $R_c(N):=$ number of sequences $(d_k)_{k\ge1}$ with $0\le d_k\le F_k$ and $\sum_k d_k F_k=N$.  
   - $R_u(N):=$ as above, but $d_k$ unbounded.  
   - $b(N):=$ binary partition function (partitions into powers of two, unbounded).

3. **Asymptotics target definition:**  
   Which of the following three questions are central to this roadmap?
   - **(A) Existence of the leading asymptotics:**  
     Does $C_c$ exist such that $\log R_c(N) \sim C_c (\log N)^2$?
   - **(B) Refined expansion:**  
     $\log R_c(N) = C_c(\log N)^2 + c_1 \log N \log\log N + c_2 \log N + (\text{oscillation}) + o(1)$?
   - **(C) Oscillation structure:**  
     If oscillations exist: periodic in $\log_\varphi N$? Which period(s)?

   **Focus of this roadmap:** Primarily (A) and (B); (C) downstream in Phase 6.

4. **Preliminary consideration on fluctuation:**  
   The classical partition function $p(n)$ is monotonically increasing.  
   $R_c(N)$ might fluctuate strongly locally (analogous to the distinct Fibonacci partition function A000119).  
   Decision: 
   - If $R_c(N)$ fluctuates a lot → use the summatory function $S_c(N):=\sum_{n\le N}R_c(n)$ for Tauberian theorems (Phase 5B).
   - If $R_c(N)$ is smooth → direct attack on $R_c(N)$ itself.  
   This question will be decided by data in Phase 1.

### Deliverable

**Document:** `theory/00-definitions.md` (1 page)  
Contains:
- Fibonacci convention with explicit values up to $F_{10}$  
- Precise definition of $R_c, R_u, b$, each in 2–3 lines  
- Central research questions (A), (B), (C) in mathematical form  
- Labelling: which asymptotics are *known* (with reference), which are *conjectures*, which are *open*?

---

## Phase 0.5 — Constant gate

**Time horizon:** 1 day
**Criticality:** HIGH — decision point before any months-long investment

### Goal

*Measure* the leading constant $C_c$ before the heuristic *derives* it.

### Substance

Direct evaluation of $\log F_c(e^{-s})$ in log space plus numerical
Legendre transform $\log R_c(N) \le \min_s [sN + \log F_c(e^{-s})]$.
The estimator is the local slope $d(\log R)/d((\log N)^2)$, which converges far faster
than the ratio $\log R/(\log N)^2$.

Candidates: $1/(2\log\varphi)=1.039$, $1/(4\log\varphi)=0.520$, $1/(8\log\varphi)=0.260$.

### Deliverables

`scripts/run_phase0_gate.py`, `data/phase0_5_gate.csv`, `figures/phase0_5_gate.png`,
`docs/phases/phase0_5/report.md`.

### Consequence

Phase 3 then explains a *measured* number instead of predicting an unknown one.

---

## Phase 1 — Exact computation and sanity checks

> **✅ Completed.** Result: [`docs/phases/phase1/summary.md`](phases/phase1/summary.md). Exact values for
> all `N ≤ 10^6`, secured by a pointwise comparison between two
> independent algorithms over the whole range. Central finding:
> `R_c(N)` fluctuates strongly (just under half of the steps decrease), which suggests `S_c(N)` as the
> target object of a Tauberian argument. The following section is the
> original plan and is retained as such.

**Time horizon:** 1–2 weeks  
**Criticality:** HIGH — benchmark for all theoretical claims

### Goals

- Reliable numerical data for $R_c(N)$ up to a practical limit (approx. $N \le 10^6$–$10^7$)  
- Verification of the generating function against brute force  
- First descriptive statistics: monotonicity, local fluctuation, symmetries

### Substance

1. **Algorithm: dynamic programming**  
   ```
   Recurrence: P_0(x) = 1
              P_k(x) = P_{k-1}(x) · G_k(x),
   where G_k(x) = 1 + x^{F_k} + x^{2F_k} + ... + x^{F_k^2}
                = (x^{F_k(F_k+1)} - 1) / (x^{F_k} - 1)  [closed form]
   
   Coefficient [x^N]P_k(x) = R_c^{(k)}(N)  [with only 1..k available]
   ```
   
   **Implementation:**  
   - For exact coefficients: array convolution with integer powers (memory ~GiB for $N_{\max}\sim 10^7$).  
   - For $\log R_c(N)$ (sufficient for asymptotics): logistic convolution via floating point, then conversion. Or bigint with periodic taking of logarithms.  
   - **Checksum:** verify the code against small cases $(N \le 200)$ via brute force (explicit enumeration of all $(d_k)$ sequences).

2. **Generating-function test**  
   Product form: $\prod_{k=1}^{K} \frac{1-x^{F_k(F_k+1)}}{1-x^{F_k}}$ for the truncated product.  
   Comparison against the DP recurrence up to $N=500$: should be identical.

3. **Descriptive statistics**  
   - Table: $N$, $R_c(N)$, $\log R_c(N)$, $(\log N)^2$, $\frac{\log R_c(N)}{(\log N)^2}$ for $N\in\{100,500,1000,5000,10000,\ldots\}$.
   - Monotonicity: is $R_c(N)$ increasing? Or are there drops (e.g. at $N=F_m-1$)?  
   - Local fluctuation: ratio $R_c(N+1)/R_c(N)$; are there spikes or systematic patterns?
   - **Completeness (done):** There are *no* gaps. The Kempner–Fraenkel condition
     $F_k \le 1 + F_{k-1}F_k$ is satisfied with a large margin, so every $N \in [0, \sum_k F_k^2]$
     is representable (`theory/01-background.md` §3, confirmed numerically in `tests/test_dp.py`)
     {claim:completeness-no-gaps}.
     The task is therefore the *proof* of completeness (Phase 2, Lean target), not the search for gaps.

### Deliverables

1. **Code:** `phase1_DP.py` (or language of choice)  
   - Input: $N_{\max}$  
   - Output: array $[R_c(1), R_c(2), \ldots, R_c(N_{\max})]$ or $[\log R_c(1), \ldots]$  
   - Built-in checks against $N=\text{small}$ via brute force

2. **Data:** `phase1_data.csv`  
   Columns: `N, R_c(N), log(R_c(N)), (log N)^2, ratio_to_quad, log(R_c(N))/(log N)^2`  
   At least for $N \in \{10^i \cdot 10^j : i=2,\ldots,7; j=0,\ldots,9\}$.

3. **Figure:** `phase1_plot.png`  
   - Top: $\log R_c(N)$ vs. $(\log N)^2$ (should look proportional)  
   - Bottom: residuals after subtracting the $(\log N)^2$ term (visualise oscillatory structure)  
   - Marking of suspicious points (local minima etc.)

4. **Report:** `docs/phases/phase1/report.md` (2–3 pages)  
   - Summary of data quality  
   - Observed patterns with hypotheses  
   - Open numerical puzzles  

### Risks

- **Memory/compute time:** $10^7$ coefficients need efficient arithmetic. If too slow: reduce to $10^6$, or only approximate $\log R_c$.  
- **Numerical stability of $\log$:** beware of underflow; BigInt logarithms via mantissa+exponent.

---

## Phase 2 — Elementary bounds: the sandwich

**Time horizon:** 2–3 weeks  
**Criticality:** MEDIUM — first proved theorem, gives orientation

### Goals

- Rigorously prove upper and lower bounds $c_1(\log N)^2 \le \log R_c(N) \le c_2(\log N)^2$  
- State the constants $c_1, c_2$ with references  
- Thereby conclusively establish the *order of magnitude*, without claiming the full asymptotics

### Substance

1. **Upper bound:**  
   Trivial: $R_c(N) \le R_u(N)$ (caps only restrict).  
   From Coons–Kristensen–Laursen (arXiv:2312.07404):
   $$\log R_u(N) \sim \frac{(\log N)^2}{2\log\varphi}, \quad \log\varphi = \log\frac{1+\sqrt{5}}{2} \approx 0.481.$$
   
   Hence: **Theorem (upper bound):**  
   $$\log R_c(N) \le (1+o(1)) \cdot \frac{(\log N)^2}{2\log\varphi}.$$
   
   This is immediately citable and needs no proof.

   **Correction (Phase 2):** This route was not taken. T1 and T2 in
   [`docs/phases/phase2/report.md`](phases/phase2/report.md) prove the sharper
   coefficient $1/(4\log\varphi)$ directly from the generating function, without CKL and without
   $R_c \le R_u$. The identification of our $R_u$ with the $p_F$ of Coons–Kristensen–Laursen
   is still listed as *pending verification* in `theory/00-definitions.md`.

2. **Lower bound — constructive method:**  
   Partition the positions $k$ into two classes:
   - **Binding class $\mathcal{B}$:** $F_k \le N^{1/4}$ (here the cap can seriously restrict availability).  
   - **Nothing class $\mathcal{N}$:** $F_k > N^{1/4}$ (here each position on its own is far too large, the cap is irrelevant).  
   
   In class $\mathcal{N}$ we can use at most one position, namely one with $F_k \le N < F_{k+1}$.  
   Every representation of $N$ must therefore have a prefix from $\mathcal{B}$ and a single summand from $\mathcal{N}$ (or from $\mathcal{B}$ itself).
   
   Lower bound from an explicit injection:  
   For arbitrary $M \in \mathcal{B}$ count all $(d_k)_{k\in\mathcal{B}}$ with $\sum_{k\in\mathcal{B}}d_k F_k = N - M$.  

   **Correction (Phase 2):** The step that originally stood here — "this gives at least
   $R_u(N-M)$ possibilities" — runs in the wrong direction and is not available as stated.
   Capping removes representations, so it yields $R_c \le R_u$; $R_u$ therefore cannot bound $R_c$
   from below. The construction that does carry is the two-block construction L1 in
   [`docs/phases/phase2/report.md`](phases/phase2/report.md) §4: a fixup block $[1,a]$ with
   $F_a F_{a+1} \ge N$ plus a rectangular free family on the remaining places.
   
   Finer analysis: use the special structure of $\mathcal{N}$ (geometric growth of the Fibonacci numbers) to show:
   $$\log R_c(N) \ge \frac{(\log N)^2}{4\log\varphi}(1-o(1)) + O(\log N).$$
   
   **Detailed proof required**, but conceptually feasible with standard bijections.

   **Correction (Phase 2):** What was achieved is $1/(8\log\varphi)$, not $1/(4\log\varphi)$ — L1
   uses up the cap-binding places in the fixup block. The factor 2 is structural for L1 in the
   stated form; recovering it requires a different block split
   (L2a / L2b, `docs/phases/phase2/report.md` §4.4), not sharper estimates.

   **Addendum (Phase 2, stretch):** $1/(4\log\varphi)$ *is* attainable from below. Route L2b
   delivers it — not through a different reservation, but by counting the block instead of
   reserving it (Lemma F, T5 in `docs/phases/phase2/report.md` §8). The statement sketched here,
   $\log R_c(N) \ge \frac{(\log N)^2}{4\log\varphi}(1-o(1))$, is thereby proved; the path
   there, however, did not go through "standard bijections" but through a uniform
   lower bound for the block counting function.

3. **Convergence of the bounds:**  
   If the upper and lower bounds point to the same main term, you have:
   $$C_c = \frac{1}{C'\log\varphi} \quad \text{for explicit } C'.$$

   **Correction (Phase 2), two points.** First, this used to read
   $C_c = (\log N)^2/(C'\log\varphi)$ — a $(\log N)^2$ does not belong in a constant.
   Second, the expected interval $C' \in [2,4]$ is replaced by C4: **if** $C_c$
   exists, then $C' \in [4,8]$. The parametrisation presupposes existence; C4
   bounds only the limit inferior and limit superior and says nothing about existence.

   **Addendum (Phase 2, stretch):** The existence caveat no longer applies. C5
   (`docs/phases/phase2/report.md` §8) proves that the limit exists; hence
   $C' = 4$ holds **unconditionally**. The distinction nevertheless remains important and is not
   flattened: C4 bounds the limit inferior and limit superior, C5 asserts the existence
   of the limit — two different statements, and it is precisely the second that T5 had to deliver in addition
   to the constant.

   This is **not** a sharpening of $[2,4]$: the upper coefficient was sharpened from
   $1/(2\log\varphi)$ (cited from CKL) to $1/(4\log\varphi)$, the lower one weakened from
   $1/(4\log\varphi)$ (from the sketch above) to $1/(8\log\varphi)$. The
   two intervals are not contained in one another — they touch at $C' = 4$ and
   are otherwise disjoint.

   If $C'=4$: the upper endpoint of the proved interval is attained — exactly the
   Phase 3 conjecture $\log R_c(N) \sim (\log N)^2/(4\log\varphi)$.

   If $C'=8$: the lower endpoint is attained, so L1 would already be sharp.

   **Addendum (Phase 2, stretch):** $C' = 4$; the former Phase 3 conjecture is proved as
   C5 (ledger: `leading-constant`, status `theorem`). $C'=8$ is thereby
   ruled out — L1 is not sharp. The case distinction above is thereby
   settled: $C'\in(4,8)$ was one of the open possibilities and is ruled out.

### Deliverables

1. **Theorem: sandwich bounds**  
   Precise formulation, proof of upper and lower bounds, with error terms.

2. **Technical note:** `docs/phases/phase2/report.md` (4–5 pages)  
   - Theorem + proof of the upper bound (trivial, but explicit).  
   - Theorem + proof of the lower bound (core of the phase).  
   - Visualisation: plot numerical data from Phase 1 against both bounds.  
   - Conclusion: which value of $C'$ do the data suggest?

### Risks

- The lower-bound proof could become technically tricky (exact regime division, overlaps).  
- Pitfalls in passing from finite products (up to which position to sum?) to limits.

---

## Phase 3 — The saddle-point heuristic (core piece)

> **Addendum (Phase 2).** Where this section says "conjecture", the status before Phase 2
> is meant. $\log R_c(N) \sim (\log N)^2/(4\log\varphi)$ is proved (C5, ledger
> `leading-constant`, status `theorem`), and so is the tightness of the saddle-point bound
> (`saddle-tightness`). Phase 3 remains worthwhile and only changes its goal: to *explain*
> the constant instead of *guessing* it, and to attack the secondary term, where something
> is actually still open (`saddle-correction-constant`, `secondary-term-constant`).

**Time horizon:** 3–4 weeks  
**Criticality:** VERY HIGH — delivers the conjecture and intuition for Phase 5

### Goals

- Derive the conjectured constant $C_c$ from an **explicit, clean heuristic**  
- Expose the "three regimes" phenomenon and explain why the cap *halves* the asymptotics  
- **Clearly mark** everything **as conjecture and heuristic** (not as a theorem)

### Substance

The core idea: analyse the product side of the generating function
$$F_c(x) := \prod_{k\ge1}\frac{1-x^{F_k(F_k+1)}}{1-x^{F_k}}$$
via the transformation $x=e^{-s}$, $s\to0^+$. Then
$$\log F_c(e^{-s}) = \sum_{k\ge1}\left[\log(1-e^{-sF_k(F_k+1)})-\log(1-e^{-sF_k})\right].$$

1. **Three-regime decomposition:**  
   
   For each summand, parametrised by $z=sF_k$:
   - If $z\gg 1$: $\log(1-e^{-z})\approx -e^{-z}\approx 0$ (exponentially small contributions).  
   - If $z\approx 1$: critical range (transitions).  
   - If $z\ll 1$: $\log(1-e^{-z})\approx \log z$ (linear in $\log z$).  
   
   Since $F_k\approx \varphi^k/\sqrt{5}$ grows geometrically, for fixed $s$ there is a *unique* threshold $k^*(s)$ with $F_{k^*} \approx 1/s$.  
   
   This induces three regimes:

   | Regime | Condition | $k$ lies in | Contribution per term |
   |---|---|---|---|
   | **A (cap binds)** | $s F_k \gg F_k(F_k+1) \cdot s$ (impossible, contradiction — revision necessary) | — | — |
   
   **Correct regime division** (after reconsideration):  
   
   Use the fact that each term $k$ contributes the amount
   $$a_k(s):=\log\left(\frac{1-e^{-sF_k(F_k+1)}}{1-e^{-sF_k}}\right)$$
   For $F_k \gg 1/s$: numerator and denominator are both $\approx 1$, so $a_k\approx 0$.  
   For $F_k \ll 1/s$: 
   $$a_k \approx \log\left(\frac{sF_k(F_k+1)}{sF_k}\right) = \log(F_k+1)\approx\log F_k.$$
   
   The **three regimes** are, more precisely:

   | Regime | Condition on $k$ | Contribution to sum | Number of positions |
   |---|---|---|---|
   | **A** | $F_k \ll (sF_k)^{-1/2}$, i.e. $F_k^2 s\ll 1$ | $\approx \log F_k$ per term | $\approx \frac{1}{2}\frac{\log(1/s)}{\log\varphi}$ |
   | **B** | $(sF_k)^{-1/2} \ll F_k \ll s^{-1}$ | $\log F_k$-like (linear in sum) | $\approx \frac{1}{2}\frac{\log(1/s)}{\log\varphi}$ |
   | **C** | $F_k \gg s^{-1}$ | exponentially small | $\lesssim \text{const}$ |
   
   *(This division needs careful working out; first sketch here.)*

2. **Asymptotic evaluation of the sum:**  
   
   Regimes A + B together yield:
   $$\sum_{k \in A \cup B} \log F_k \approx \int_{k_{\min}}^{k_{\max}} \log(\varphi^k/\sqrt{5})\,dk$$
   where the limits are given by $F_k^2 s \sim 1$ and $F_k s\sim 1$.
   
   This gives:
   $$\int \log(\varphi^k)\,dk = \sum k \log\varphi = O((\log(1/s))^2 / \log\varphi).$$
   
   (The exact constant depends on the regime boundaries; the Legendre transform below supplies the main contribution.)

3. **Legendre transform to the asymptotic behaviour of $R_c(N)$:**  
   
   The relation $N \leftrightarrow s$ via the saddle point:
   $$\frac{d}{ds}\log F_c(e^{-s}) \Big|_{s=s^*} = N.$$
   
   This is an implicit-function-theorem argument: find $s^*(N)$ such that the derivative of the log generating function equals $N$.
   
   Known in the binary case (de Bruijn): $\frac{d}{ds}\log b(e^{-s})\approx \frac{\log(1/s)}{s}$, which leads to $s^* \sim \frac{1}{\log N}$ and hence to $\log b(N) \sim \frac{(\log N)^2}{2\log 2}$.
   
   In the Fibonacci cap case the structure should be similar, but **a further halving occurs** because of the symmetry of the cap rule: only *half* of the positions contribute to the main term (those whose cap *binds*). This leads to the conjecture:
   $$\log R_c(N) \sim \frac{(\log N)^2}{4\log\varphi}.$$

4. **Graphical visualisation:**  
   - Plot of $\log F_c(e^{-s})$ for $s$ from $0.1$ to $0.001$.  
   - Overlaid: the prediction $\frac{(\log(1/s))^2}{4\log\varphi}$ (should be visible as a curve).  
   - Residual: deviation from the asymptotic ansatz (reveals transition zones, secondary-term structures).

### Deliverables

1. **Heuristic chapter:** `phase3_heuristic.md` (8–10 pages)  
   - Careful explanation of the saddle-point approach.  
   - Three-regime decomposition with sketches and justification.  
   - Legendre transform to the constant.  
   - Figures (see above).  
   - **Huge warning:** "What follows is a heuristic. Rigorous proofs follow in Phase 5."

2. **Conjecture statement:**  
   $$\boxed{\ \log R_c(N) \sim \frac{(\log N)^2}{4\log\varphi} \quad \text{(CONJECTURE)}\ }$$
   With explicit numerical value: $\frac{1}{4\log\varphi} = \frac{1}{4 \cdot 0.481\ldots} \approx 0.520$.

   > **Numerical support (Phase 0.5):** The local slope of the Legendre transform measures
   > 0.518710 at $N = 10^{3200}$ and rises monotonically towards $1/(4\log\varphi) = 0.519522$
   > {claim:gate-local-slope}.
   > Since this is an *upper* bound, it immediately rules out $1/(2\log\varphi)$;
   > ruling out $1/(8\log\varphi)$ additionally presupposes that the saddle-point correction
   > is of lower order — expected, but not proved in Phase 0.5.
   > See `docs/phases/phase0_5/report.md`.
   >
   > **Addendum (Phase 2):** The boxed statement is **no longer** a conjecture statement —
   > it is proved as C5 (`docs/phases/phase2/report.md` §8, ledger `leading-constant`, status
   > `theorem`), and in fact elementarily and without the saddle point. For Phase 3 this changes the
   > task, not its value: the constant is now to be *explained*, no longer to be
   > *established*. The numerical support above remains what it was — a measurement, not a
   > proof.

3. **Secondary expansion (optional, but valuable):**  
   If the heuristic also hints at logarithmic terms of other orders, e.g.
   $$\log R_c(N) = \frac{(\log N)^2}{4\log\varphi} + C_1 \frac{\log N \log\log N}{\log\varphi} + C_2 \frac{\log N}{\log\varphi} + \text{oscillation} + o(1),$$
   then extract the constants $C_1, C_2$ from the heuristic.

### Risks

- The transition zones between regimes are mathematically delicate — small errors in the asymptotic analysis can lead to wrong constants.  
- The Legendre transform presupposes partial analyticity of the saddle point; this has to be made plausible (or is this the point at which Phase 5A needs rigorisation?).

---

## Phase 4 — Numerical confrontation (in parallel with Phase 3)

> **Addendum (Phase 2).** "The conjecture" here consistently means the statement that was one before
> Phase 2; it is proved as C5. The numerical work of this phase loses
> nothing by this: it turns from a conjecture test into a *confrontation* of a theorem
> with data, and the secondary term together with the oscillation, which is what it actually targets, is
> still open.

**Time horizon:** 2–3 weeks  
**Criticality:** HIGH — quantitative feedback on the conjecture

### Goals

- Test the conjecture $\log R_c(N)\sim\frac{(\log N)^2}{4\log\varphi}$ numerically against Phase 1 data  
- Detect and quantify oscillations  
- Clarify the order of magnitude and possibly the secondary-term structure

### Substance

1. **Direct product evaluation (fastest test):**  
   
   Compute $\log F_c(e^{-s})$ directly from the product for small $s$ (e.g. $s=0.01, 0.003, 0.001$):
   $$\log F_c(e^{-s}) = \sum_{k=1}^{K} \log\left(\frac{1-e^{-sF_k(F_k+1)}}{1-e^{-sF_k}}\right),$$
   where $K$ is chosen large enough that further terms are exponentially small.
   
   Compare against $\frac{(\log(1/s))^2}{4\log\varphi}$:
   
   | $s$ | $\log F_c(e^{-s})$ (numerical) | $\frac{(\log(1/s))^2}{4\log\varphi}$ | Ratio |
   |---|---|---|---|
   | $0.01$ | ? | $\approx 1.35$ | ? |
   | $0.001$ | ? | $\approx 5.40$ | ? |
   | $0.0001$ | ? | $\approx 12.1$ | ? |
   
   If the ratio converges to 1: ✓ conjecture consistent.  
   If not: conjecture needs revision or additional terms (secondary terms still dominate).

2. **Fitting to Phase 1 data:**  
   
   Convergence in $(log N)^2$ regressions is infamously slow (errors like $O(1/\log N)$). Instead, a parametric fit:
   $$\log R_c(N) = a(\log N)^2 + b\log N \log\log N + c\log N + d + o(1).$$
   
   Use multiple regression with data from Phase 1 (at least 20–30 data points) and extract $a, b, c, d$ together with error bars.
   
   Expected: $a \approx \frac{1}{4\log\varphi} \approx 0.520$.  
   Test of the conjecture: is $a$ consistent with $0.520$ within the uncertainty?

3. **Oscillation detection:**  
   
   Compute residuals:
   $$R(N) := \log R_c(N) - a(\log N)^2 - b\log N\log\log N - c\log N - d.$$
   
   Plot $R(N)$ against $\{\log_\varphi N\}$ (fractional part of $\log_\varphi N$), i.e. the "*fractional phase*".
   
   If there are periodic patterns: Fourier analysis of the period(s). Expected from theory: main period 1 (since the poles of the Dirichlet series lie at $z=\frac{2\pi i k}{\log\varphi}$).

4. **Reliability check:**  
   
   Split the data into two halves: fit with half A, test the coefficients against half B. The deviation should be small.

### Deliverables

1. **Numerics script:** `phase4_numerical.py`  
   - Function `evaluate_product_FC(s, K_max)`: computes $\log F_c(e^{-s})$ directly.  
   - Function `fit_logRC(data_file)`: multiple regression on Phase 1 data.  
   - Visualisations: plots (product vs. hypothesis; residuals vs. phase; etc.).

2. **Numerics report:** `phase4_numerical_report.md` (5–7 pages)  
   - Tables with the product evaluations.  
   - Fitting results with confidence intervals.  
   - Oscillation plots.  
   - **Conclusion:** How well does the conjecture hold up? Which corrections are visible?

3. **Updated conjecture statement (if necessary):**  
   If the numerical data show systematic deviations (e.g. secondary-term coefficients), incorporate them into the conjecture.

### Risks

- **Slow convergence:** With $N$ only up to $10^7$, secondary-term effects could still dominate; genuine $(log N)^2$ asymptotics only shows at $10^{10}$ or so.  
- **Numerical accuracy:** Floating point in summations over $\sim 30$ Fibonacci terms can accumulate rounding errors. Work in double precision and check later with extended precision.

---

## Phase 5 — Rigorisation: three lines of attack

> **Addendum (Phase 2).** The leading coefficient no longer needs this phase — C5 proves
> it elementarily. What remains to be gained here is everything below it: the secondary term
> (`saddle-correction-constant`, `secondary-term-constant`) and the oscillation structure.

**Time horizon:** months (3–6, depending on the route)  
**Criticality:** CRITICAL — the difference between conjecture and theorem

This phase splits into three possible, partly parallel routes:

### Route A — Mellin transform and Dirichlet series (favourite)

**Time horizon:** 4–6 months  
**Analogous to:** Coons–Kristensen–Laursen, Navas on $\zeta_F$.

**Strategy:**

1. **Setting up the Mellin transform:**  
   Write
   $$\log F_c(e^{-s}) = \int_1^\infty \left(\log F_c(e^{-x/t})\right) \frac{dx}{x} \quad (\text{integration by parts/Mellin pair}).$$
   
   This transforms the product into a sum over poles and residues of a meromorphic function.

2. **Dirichlet-series approach:**  
   Define
   $$\zeta_F^{(C)}(z) := \sum_{k\ge1} F_k^{-z}, \quad \zeta_F^{(F+1)}(z):=\sum_{k\ge1} (F_k(F_k+1))^{-z}.$$
   
   Then
   $$\prod_k (1-x^{F_k}) = x^{\zeta_F^{(C)}(0)} \cdot (\text{Regge structure in } z)$$
   and similarly for the numerator. The quotient generating function becomes a difference or ratio of these Dirichlet series.
   
   **Critical new territory:** $\zeta_F^{(F+1)}(z)$ is new in the literature (not reducible to earlier work). The analytic continuation of this series is the core problem.
   
   **Expected result:** $\zeta_F^{(F+1)}(z)$ has poles and residues similar to $\zeta_F(z)$ (Navas), but possibly with altered residue structures (e.g. double poles at $z=0$? New imaginary poles?). A careful analysis by means of Borel summation or Mellin asymptotics could rigorously establish the constant $\frac{1}{4\log\varphi}$.

3. **Mellin inversion:**  
   With the analytic properties of $\zeta_F$ and $\zeta_F^{(F+1)}$, back to the asymptotics of $R_c(N)$ via the inverse Mellin transform and Tauberian theorems.

**Prospects:** This route parallels historically proven techniques with a new Dirichlet series — high potential for success at moderate technical effort (if $\zeta_F^{(F+1)}$ behaves similarly to known cases).

**Pitfalls:** The new series could have pathologically awkward convergence properties (e.g. a smaller radius of convergence); then Navas' techniques might not help directly.

**Main deliverable:** Theorem (with full proof or detailed sketch):
$$\log R_c(N) = \frac{(\log N)^2}{4\log\varphi} + O\left(\frac{\log N \log\log N}{\log\varphi}\right).$$

---

### Route B — Tauberian theorems (for the summatory function)

**Time horizon:** 2–3 months  
**Analogous to:** Ingham 1941 (binary partitions); Hardy–Littlewood Tauberian classics.

**Strategy:**

1. If $R_c(N)$ is too fluctuating (known from Phase 1), work with the summatory function:
   $$S_c(N) := \sum_{n\le N} R_c(n).$$
   
   This is monotonically increasing and smoother.

2. **Tauberian theorem (Ingham type):** If
   $$\sum_{n\ge1} S_c(n) x^n \sim (1-x)^{-\alpha} L(1/(1-x)) \quad (x\to 1^-)$$
   for a certain $\alpha$ and a (possibly iterated) logarithm $L$, then it follows that
   $$S_c(N) \sim \frac{N^{\alpha+1}}{(\alpha+1)!} \exp(\sqrt{\beta \log N})$$
   or a similar form, depending on the structure.

3. **From $S_c$ back to $R_c$:**  
   Differences $R_c(N) = S_c(N) - S_c(N-1)$ are not directly asymptotic unless $S_c$ is very smooth. This is the crux: if $S_c(N)\sim A N^{\alpha} \exp(B(\log N)^\beta)$, then $R_c(N)$ is asymptotic only if $\beta\ne 1$ or further smoothness is present.

**Prospects:** If $S_c$ behaves like $\exp(c(\log N)^2/\log\varphi)$, modern Tauberian theorems (e.g. Delange, Karamata, etc.) are probably applicable.

**Pitfalls:** The passage from $S_c$ back to $R_c$ is often subtle and requires additional regularity assumptions.

**Main deliverable:** Theorem for $S_c(N)$ with asymptotics; corollary for $R_c(N)$ under regularity conditions.

---

### Route C — Functional equation (exploratory strand)

**Time horizon:** 1–2 months (exploratory; high risk)  
**Analogous to:** de Bruijn's functional equation for binary partitions; Mahler operators.

**Strategy:**

1. **Is there a functional equation?**  
   In the binary case: $b(x) = b(x^2)/(1-x)$ (taking into account duplicates and Zeckendorf-like symmetries).  
   
   A similar structure for $R_c$? Presumably *not exactly*, but possibly approximately under the Zeckendorf substitution $x\to x^{\varphi^k}$ for certain sequences?
   
   This is very speculative and needs exploration.

2. **Exploit self-similarity:** If (partial) self-similarity is present, set up and solve recursion equations for asymptotic constants.

**Prospects:** Could lead to unexpectedly elegant arguments that underlie the problem.

**Pitfalls:** Very high risk; could cost a lot of time without a result.

**Main deliverable (if successful):** Functional equation (or an asymptotic version); from it an asymptotics theorem.

---

### Choice and prioritisation

**Recommendation:** 
- **Primary:** Route A (Mellin + Dirichlet series), since it parallels Coons–Kristensen–Laursen.  
- **Secondary:** Route B (Tauberian theorems) as a fallback or verification.  
- **Tertiary:** Route C (functional equation) only if time/energy is available and exploratory ideas arise.

**Clarification after Phase 1:** Route A and Route B are not a choice
between two alternatives for the same goal — they answer different
questions. Route A remains the primary route for the rigorous
asymptotics theorem about $\log R_c(N)$. The fluctuation finding from Phase 1
(`docs/phases/phase1/report.md`) shows, however, that $R_c(N)$ itself over
$N \le 10^6$ is so irregular (49.6 {fig:decreasing-fraction}% decreasing
steps) {claim:rc-not-monotone}
that a direct
Tauberian attack on $R_c(N)$ is made harder by it — the summatory
function $S_c(N)$ is therefore the numerically safer target for a
Tauberian attack (Route B), once it is pursued, rather than $R_c(N)$ itself.
This is not a weakening of Route A but a boundary condition on Route B,
once it is pursued.

---

## Phase 6 — Oscillations and error terms

**Time horizon:** 6–8 weeks (started after Phase 5)  
**Criticality:** MEDIUM — refines the theorem from Phase 5

### Goals

- Explicitly identify and characterise oscillatory corrections to $\log R_c(N)$  
- Prove/refute periodicity in $\log_\varphi N$  
- Obtain error bounds that take effect at computable $N$

### Substance

1. **Poles of the Dirichlet series (follows from Phase 5A):**  
   The imaginary poles of $\zeta_F$ lie at $z=\frac{2\pi i k}{\log\varphi}$, $k\in\mathbb{Z}\setminus\{0\}$.  
   
   These generate oscillations periodic in $\log_\varphi N$ with period 1.  
   
   In $\zeta_F^{(F+1)}$ *additional* poles could appear (or old ones disappear), which could lead to a richer spectrum.

2. **Fourier analysis of the residues:**  
   The residue at a pole $z=z_j$ contributes a term like $N^{\text{Re}(z_j)} \exp(2\pi i (\text{Im}(z_j)/\log\varphi) \log N)$ to the asymptotic expansion.
   
   Collect terms by *imaginary* parts (frequencies) and write
   $$\log R_c(N) = \frac{(\log N)^2}{4\log\varphi} + \text{(main secondary terms)} + \Psi(\log_\varphi N),$$
   where $\Psi$ is a (usually small) periodic function.

3. **Explicit Fourier coefficients:**  
   If $\Psi(\phi) = \sum_{k\ne 0} a_k e^{2\pi i k \phi}$, extract the coefficients $|a_k|$ from theoretical residue computations and compare against numerical data from Phase 4.

4. **Error bounds:**  
   With the full asymptotic expansion (up to degree $d$ in logarithmic terms) known, obtain explicit numerical error bounds of the form
   $$\left|\log R_c(N) - \left(\frac{(\log N)^2}{4\log\varphi}+\text{(corrections)}\right)\right| \le C\frac{(\log N)^d}{(\log\varphi)^d}$$
   for an effective constant $C$ and exponent $d < 2$ (better than the main order).

### Deliverables

1. **Theorem: asymptotic expansion with oscillations**  
   Precise formulation with Fourier coefficients.

2. **Technical note:** `phase6_oscillations.md` (6–8 pages)  
   - Pole spectrum from Phase 5.  
   - Fourier analysis.  
   - Residue computations.  
   - Error bounds.

3. **Figures:** Comparison of numerical residuals (Phase 4) against the theoretical prediction of the oscillations.

---

## Phase 7 — Generalisation and write-up

**Time horizon:** 2–3 months  
**Criticality:** MEDIUM — context and publication

### Goals

- Generalise the results to general caps and linear recurrences  
- Establish the connection to the other four open problems in your system  
- Write the publication

### Substance

1. **Generalisation: arbitrary caps $d_k \le c F_k^\alpha$**  
   
   The heuristic from Phase 3 suggests that the constant $C_c(\alpha)$ interpolates between:
   - $\alpha=0$: $d_k\le c$ (all positions capped equally) → different asymptotics?  
   - $\alpha=1$: $d_k\le c F_k$ (our case) → $\frac{1}{4\log\varphi}$ (**proved**, C5, Phase 2)
   - $\alpha\to\infty$: $d_k\le c F_k^\infty$ (practically uncapped) → $\frac{1}{2\log\varphi}$ (Coons–Kristensen–Laursen).
   
   Formulate a *parametric theorem* with $C_c(\alpha)$ as a function of $\alpha$ and verify/prove it for limiting cases.

2. **General linear recurrences (Pisot base)**  
   
   Coons–Kristensen–Laursen show that the uncapped case works for arbitrary linearly recurrent sequences (under the Pisot condition).  
   
   Extend this to caps: how must $d_k$ be adapted on base $\alpha$ (instead of Fibonacci)? What analogous constant $C_c(\text{base})$ results?

3. **Paper structure**  
   - **Introduction:** Your number system; motivation (representation counting); placement in the context of the literature (Mahler, de Bruijn, CKL, Navas).  
   - **Known anchors:** define, confirm the statement of results for Fibonacci-uncapped and binary.  
   - **Main result:** Sandwich theorem and main theorem with proof (both Phase 2: C4 and C5, elementary, without saddle point); heuristic as an *explanation* of the constant (Phase 3); secondary term (Phase 5, open).
   - **Numerics:** Phase 4 experiments.  
   - **Oscillations:** Phase 6 refines the theorem.  
   - **Generalisation:** $\alpha$-interpolation; general recurrences (sketched).  
   - **Open problems:** The five problems from your system; which are now partially solved? Which remain open?  
   - **Appendix:** Complete proofs of difficult lemmas; numerical procedures.

4. **Connection to other open problems in your system**  
   
   (Based on your research so far — please specify the four other problems; then this section can be made concrete.)

### Deliverables

1. **Research paper:** `CappedFibonacciPartitions.pdf`  
   - Typically 25–40 pages for a good mathematics journal (e.g. J. Number Theory, Ramanujan J., etc.).  
   - All theorems rigorous; all numerics disclosed.

2. **Preprint on arXiv:** preparation and submission.

3. **Presentation (optional):** Short summary (1–2 pages) for possible discussion with co-authors or mentors.

---

## Critical path and prioritisation

```
Phase 0 (1–2 days)
    ↓
Phase 0.5 (1 day)
    ↓
Phase 1 (1–2 weeks) ← in parallel with Phase 3
    ↓
Phase 2 (2–3 weeks) — quick theorem
    ↓
Phase 3 (3–4 weeks) ← critical core piece
Phase 4 (2–3 weeks) — numerics feedback
    ↓
**Decision point:** conjecture robust enough for Phase 5?
        (moot for the leading coefficient — Phase 2 has proved it;
         still applies to the secondary term)
    ↓ Yes
Phase 5A (4–6 months) — Mellin + Dirichlet series
    ↓
Phase 6 (6–8 weeks) — oscillations
    ↓
Phase 7 (2–3 months) — write-up and generalisation
```

**Time horizon summary:**  
- **Short term (4–6 weeks):** Phases 0–2 deliver the sandwich theorem + proof of the order of magnitude.  
- **Medium term (3–4 additional months):** Phases 3–4 establish a robust numerical conjecture.
  (Phase 2 has already proved the leading coefficient; from now on this refers to the secondary term.)
- **Long term (6–12 months):** Phases 5–7 achieve a complete proof and a publishable paper.

---

## Literature anchors (references for all phases)

1. **Mahler, K.** (1940). "An application of Jensen's formula to polynomials." *Mathematica*, 7(2).  
   → Origin of the idea for binary partitions.

2. **de Bruijn, N. G.** (1948). "On the number of uncancelled elements in the sieve of Eratosthenes." *Proc. Ned. Akad.*  
   → Oscillation theory for binary partitions.

3. **Coons, M., Kristensen, S., Laursen, M. L.** (2023). "Asymptotics for partitions over the Fibonacci numbers and related sequences." arXiv:2312.07404.  
   → *Central to our project:* uncapped Fibonacci partitions, Mellin/Dirichlet-series method, Navas' $\zeta_F$.

4. **Navas, L.** (20XX). "Analytic continuation of the Fibonacci zeta function." [Reference to be looked up; cited in Coons–Kristensen–Laursen].  
   → $\zeta_F(z)$ analytic continuation; poles and residues.

5. **Hardy, G. H., Ramanujan, S.** (1918). "Asymptotic formulae in combinatory analysis." *Proc. London Math. Soc.*  
   → Classical partition asymptotics; starting point for all modern methods.

6. **Meinardus, G.** (1954). "Asymptotische Formeln für Partitionsfunktionen." *Mathematische Annalen*.  
   → Generalises Hardy–Ramanujan to partitions with restricted summands; fails for lacunary sequences (such as Fibonacci!).

7. **Stockmeyer, P., Chow, S., Slattery, T.** (2019–2020). "On the Fibonacci partition function" (OEIS A000119 and related work).  
   → Distinct Fibonacci partitions; automata literature.

---

## Appendix: open questions for exploration

1. **Beyond $\alpha=1$:** How does $C_c(\alpha)$ change for $\alpha \ne 1$?  
2. **Oscillations:** Which frequencies arise in $\Psi(\log_\varphi N)$?  
3. **General recurrences:** Which Pisot sequences behave similarly?  
4. **Zeckendorf connection:** How does your Zeckendorf representation refine under the cap?  
5. **Generic question:** Is the halving by the cap a universal phenomenon in filtered partition problems?

---

**Version 1.0 — August 2026**  
Ready for feedback, iterations and concrete implementation.
