> **Note on provenance (added retroactively).** This document predates the current
> research program and was carried over unchanged from an earlier scaffolding. Its
> §2 describes the **constant-capacity** model `R(n, c)` — each Fibonacci number used
> at most `c` times — which is a **different object** from the position-dependent
> system `0 <= d_k <= F_k` (i.e. `R_c(N)`) that this project now studies; the two are
> not interchangeable and results below about `R(n, c)` do not transfer. The numerical
> table in §2.3 was produced by `evaluate.py`, a script that has since been removed
> from this repository; those numbers are therefore **unverified** and are not, and
> should not be, recorded in `data/manifest.json`. This document is retained only for
> its §1 Zeckendorf proof sketches, which remain correct and relevant.

# Fibonacci Partitions — Proof Sketches

## 1. Zeckendorf's Theorem

**Theorem.**  Every positive integer $n$ has a unique representation as a sum of
non-consecutive Fibonacci numbers.

### 1.1 Existence (by strong induction)

*Base cases:* $1 = F_2$, $2 = F_3$.

*Inductive step:* Let $n \geq 3$ and assume the result holds for all $k < n$.
Let $F_m$ be the largest Fibonacci number with $F_m \leq n$.  Then $n - F_m < F_{m-1}$
(otherwise $F_m$ would not be the largest such), so $n - F_m$ has a Zeckendorf
representation by the induction hypothesis.  Since $n - F_m < F_{m-1}$, the
representation of $n - F_m$ does not use $F_{m-1}$ or $F_m$, so appending $F_m$
gives a valid non-consecutive representation of $n$.

### 1.2 Uniqueness (by contradiction)

Suppose $n$ has two distinct non-consecutive representations.  Let $F_k$ be the
largest Fibonacci number appearing in one but not the other.  Analysing the sum
$\sum_{i \leq k} F_i = F_{k+2} - 1 < F_{k+1} \leq F_k$ leads to a contradiction.

---

## 2. Capacity-Constrained Representations

**Definition.**  For $c \geq 1$, let $R(n, c)$ denote the number of multisets of
Fibonacci numbers (from $\{F_1, F_2, \ldots\}$) with each element appearing at most
$c$ times, and with total sum $n$.

### 2.1 Basic Properties

- $R(0, c) = 1$ for all $c \geq 1$ (the empty multiset).
- $R(n, 1) = 1$ for all $n \geq 1$ by Zeckendorf's theorem.
- $R(n, c) \leq R(n, c+1)$ for all $n, c$ (every capacity-$c$ representation is
  also a valid capacity-$(c+1)$ representation).

### 2.2 Recurrence (conjectured)

For fixed $c$, the sequence $(R(n, c))_{n \geq 0}$ satisfies a linear recurrence
of order $O(F_c)$ with integer coefficients.  The generating function
$\sum_{n \geq 0} R(n,c) x^n$ is expected to be rational.

### 2.3 Small Values (computed via `evaluate.py --compute`)

| $n$ | $R(n,1)$ | $R(n,2)$ | $R(n,3)$ |
|-----|----------|----------|----------|
| 1   | 1        | 1        | 1        |
| 2   | 1        | 2        | 2        |
| 3   | 1        | 2        | 3        |
| 5   | 1        | 3        | 5        |
| 8   | 1        | 4        | 7        |
| 10  | 1        | 8        | ...      |
| 20  | 1        | 16       | ...      |

---

## 3. Open Problems

1. Find a closed-form formula for $R(n, c)$ as a function of both $n$ and $c$.
2. Determine whether the generating function of $(R(n,c))_n$ is always rational.
3. Establish a bijection between capacity-$c$ representations and lattice paths or tilings.
4. Generalise to arbitrary base sequences (not just Fibonacci).
