---
name: explain
description: Use when explaining this project's mathematics in German to a reader with a strong mathematical background but no practice in formal proofs, Lean, or analytic number theory — e.g. a computer-science graduate reading the repository for the first time.
---

# Explaining this project's mathematics in German

Invoked as `/explain`. With no argument, give the arc from the problem to the
current result. With an argument — `/explain T5`, `/explain Lemma F`,
`/explain claims.yaml`, `/explain Completeness.lean` — explain that one piece
and only as much context as it needs.

## Who you are explaining to

A computer-science master's graduate. **Assume fluency in:** discrete
mathematics, induction, asymptotics and `O(·)`, dynamic programming, formal
power series as a computational device, floating-point behaviour and its
failure modes, reading code.

**Do not assume any practice in:** reading proof prose, Lean or any proof
assistant, analytic number theory, saddle-point or Mellin methods, or the
epistemic vocabulary this project runs on (`conjecture` vs `heuristic` vs
`verified-numeric` vs `theorem`).

The gap is *practice*, not capacity. Never simplify the mathematics. Do supply
the moves a working mathematician makes without noticing — why this estimate is
uniform, why that inequality points the way it does, what a limit superior buys
over a limit.

## Use the bridges this reader already has

| Explain… | …as |
|---|---|
| `R_c(N)` | a counting problem a DP solves — it literally is one, `capfib/dp.py` |
| the generating function | the algebra behind that DP; convolution of arrays is multiplication of series |
| the Chernoff bound (T1) | evaluate the series at one point, get a bound for free — no asymptotics needed |
| the three-regime split (T2) | a case analysis on which term dominates, like amortised analysis |
| the lower-bound construction (T3) | an explicit injection: build many distinct objects, count them |
| Lemma F | a robustness statement: the inner count is large *for every* residue, not on average |
| Lean | a type-checker for proofs; `sorry` is an unimplemented function that still type-checks |
| interval arithmetic | error bars the machine propagates for you, so a bound is certified rather than estimated |

## Order to build the ideas in

1. **The object.** `R_c(N)` counts digit sequences `(d_k)` with `0 <= d_k <= F_k`
   and `sum_k d_k F_k = N`, over *all* places `F_k <= N`. The cap grows with the
   place, so the system is maximally redundant — most integers have many
   representations. Contrast with Zeckendorf, where the digits are `{0,1}` with
   no two adjacent and every integer has exactly one representation.
2. **Why it is hard.** It sits between two solved problems (binary partitions;
   uncapped Fibonacci partitions) and breaks the simplification each relies on.
3. **What is being measured.** `log R_c(N)` against `(log N)^2` — so the answer
   is a *constant*, and the whole project is about pinning that constant.
4. **The upper bound**, T1 then T2: one line of algebra, then a real-analysis
   estimate of where the series' mass sits.
5. **The lower bound**, T3: an explicit construction, and why it loses a factor
   of two structurally rather than through slack in the estimates.
6. **Closing the gap**, Lemma F and T5, and finally C5: the limit exists.
7. **What is machine-checked and what is not.** Lean proves the elementary
   structural facts — the place recurrence, `sum_{k<=n} F_k^2 = F_n F_{n+1}`,
   the value bound, completeness, non-injectivity of the evaluation map, and
   `R_c(N) <= R_u(N)`; the index is the "What is proved" section of
   `lean/NonLinearNumberSystems/Theorems.lean`, and there are no `sorry`s.
   None of the asymptotics is in Lean: T1, T2, T3, Lemma F, T5, C4 and C5 are
   paper proofs in `docs/phases/phase2_bounds.md`.

Read from the sources rather than from memory — `docs/phase2.md` for the
summary, `docs/phases/phase2_bounds.md` for the proofs, `theory/claims.yaml`
for what is actually claimed and at what status. They are reviewed and current;
restating them here would go stale.

## Four things that must not slide

This reader will form a wrong picture if any of these is glossed. Each one has
already caused a real defect in this repository.

1. **`limsup`/`liminf` versus a limit.** C4 bounds the limit superior and limit
   inferior; C5 says the limit *exists*. To someone without practice this reads
   as pedantry, and it is the entire difference between "we know the constant is
   in a range" and "we know the constant". Explain the squeeze explicitly.
2. **The direction of a bound.** Truncating a sum of non-negative terms destroys
   an *upper* bound and preserves a *lower* one. This is why the certified
   evaluation needs a tail estimate. Getting it backwards is not a subtlety —
   it silently produces a number that is not a bound at all.
3. **`F_1 = F_2 = 1` is load-bearing**, not an off-by-one. The duplicated place
   is what makes `1 > 1` possible (two numerals, same value) and what makes
   `sum_{k<=n} F_k^2 = F_n F_{n+1}` hold. Dropping it breaks the completeness
   range.
4. **"Verified for `N <= 10^6`" is not "proved".** The claim ledger exists to
   keep those apart, and finite-to-universal drift is the defect this project
   has hit most often. When explaining a `verified-numeric` claim, say over what
   range and at how many points.

## Register and terminology

Mathematical German, `Sie`-neutral, no chattiness. The repository is in English
apart from `docs/roadmap.md`, so give the English original in parentheses at
first use: *die Schranke (bound)*, *die Behauptung (claim)*.

| English | German |
|---|---|
| statement / claim | Aussage / Behauptung |
| theorem, lemma, corollary | Satz, Lemma, Korollar |
| proof, proof sketch | Beweis, Beweisskizze |
| bound (upper/lower) | Schranke (obere/untere) |
| tight, sharp | scharf |
| conjecture | Vermutung |
| representation | Darstellung |
| place, place value | Stelle, Stellenwert |
| digit, digit cap | Ziffer, Ziffernschranke |
| completeness (no gaps) | Vollständigkeit (lückenlos) |
| redundancy | Redundanz |
| limit superior / inferior | Limes superior / inferior |
| generating function | erzeugende Funktion |
| saddle point | Sattelpunkt |
| uniform (in a parameter) | gleichmäßig (in …) |
| to hold (of a statement) | gelten |
| vacuous (of a bound) | gehaltlos |

Keep `R_c(N)`, `F_k`, `log`, `liminf` and identifiers in their code form; do not
Germanise names from the source.

## How to pitch it

Lead with the question, not the machinery: *"Wie viele Darstellungen hat `N`,
und wie schnell wächst diese Anzahl?"* Give the answer early, then earn it.

Prefer a worked small case to a general argument when both are available —
`R_c(2) = 2` with both numerals written out does more work than a paragraph. Say
which steps are routine and which are the real content, so the reader knows
where to slow down. When a proof has a step the authors themselves called the
weakest, say so and say why it survives.

Never present a heuristic as a proof, and never soften a proved statement into
a plausible one. If something is open, say it is open.
