# Phase 2 — Elementary Sandwich Bounds for `log R_c(N)`

**Question.** How large is `R_c(N)`, to leading order in `(log N)^2`, and how much of
that can be settled by elementary means?

**Answer.** Between `(log N)^2/(8 log phi)` and `(log N)^2/(4 log phi)`, in the sense
of C4 below. The sandwich does not close: the two constants differ by a factor of two,
and the gap is not an artefact of loose estimates but of the lower-bound construction's
block structure (§4).

This note contains the statements and proofs. `docs/phase2.md` is the summary;
`docs/superpowers/specs/2026-08-21-phase2-elementary-bounds-design.md` is the design
spec these proofs are written from.

---

## 1. Setting and notation

Throughout, `phi = (1 + sqrt 5)/2` and `lambda = log phi = 0.4812118...`.

The Fibonacci convention is `F_1 = F_2 = 1`, `F_3 = 2`, `F_4 = 3`, `F_5 = 5`, …
({claim:convention-duplicated-place}). The duplicated 1-place is load-bearing in both
directions: it is what makes `sum_{k<=n} F_k^2 = F_n F_{n+1}` hold ({claim:sum-of-squares}),
and it is why the completeness argument of §4 cannot be quoted from the classical
Kempner–Fraenkel condition, whose usual statement assumes strictly increasing place
values (`theory/01-background.md` §3).

```
R_c(N)  = #{ (d_k)_{k>=1} : 0 <= d_k <= F_k, sum_k d_k F_k = N }
```

with `k` ranging over **all** places with `F_k <= N`, never a fixed length
({claim:place-range}). Since `F_1 = F_2 = 1` and `F_k` is strictly increasing from
`k = 2` on, that index set is exactly `{1, ..., c}` where `c = max{k : F_k <= N}`.

The generating function is

```
F_c(x) = prod_{k>=1} (1 - x^{F_k (F_k + 1)}) / (1 - x^{F_k})
```

because the `k`-th factor is `sum_{d=0}^{F_k} x^{d F_k}`. Places with `F_k > N`
contribute only monomials of degree `> N`, so `[x^N] F_c(x) = R_c(N)`: the infinite
product and the truncation to places `F_k <= N` agree in degree `N`.

Write `x = e^{-s}` for `s > 0` and set

```
T = log(1/s),   u_k = s F_k,   v_k = s F_k (F_k + 1),   h(x) = -log(1 - e^{-x}),
a_k(s) = h(u_k) - h(v_k),      log F_c(e^{-s}) = sum_{k>=1} a_k(s).
```

`h` is positive and strictly decreasing on `(0, infinity)`, and `u_k < v_k`, so every
`a_k(s) > 0`.

Two elementary Fibonacci facts are used repeatedly. Both are proved by induction under
this convention.

```
(F1)   phi^{k-2} <= F_k <= phi^{k-1}                for all k >= 1
(F2)   F_{k+1} / F_k >= 3/2                          for all k >= 2
```

`(F1)` at `k = 1` reads `phi^{-1} <= 1 <= 1`, and at `k = 2` reads `1 <= 1 <= phi`; the
induction step is `F_{k+1} = F_k + F_{k-1} >= phi^{k-2} + phi^{k-3} = phi^{k-3}(phi + 1)
= phi^{k-1}`, using `phi^2 = phi + 1`, and symmetrically for the upper bound. `(F2)` is
`F_3/F_2 = 2` and, for `k >= 3`, `F_{k+1}/F_k = 1 + F_{k-1}/F_k >= 3/2`, because
`2 F_{k-1} >= F_{k-1} + F_{k-2} = F_k` — the Fibonacci sequence being non-decreasing. Note that `(F2)` genuinely fails at `k = 1`
(`F_2/F_1 = 1`) — the duplicated place again.

Also `t = log N` and `L = t/lambda`, so `phi^L = N`.

---

## 2. T1 — the effective upper bound

> **T1.** For every integer `N >= 1` and every real `s > 0`,
> ```
> log R_c(N) <= s N + log F_c(e^{-s}).
> ```

**Proof.** Every coefficient of `F_c` is a non-negative integer, being a count of digit
tuples. Hence for `x = e^{-s}` in `(0,1)`,

```
R_c(N) x^N <= sum_{n>=0} R_c(n) x^n = F_c(x),
```

the middle sum converging for every `s > 0`: the product's logarithm is
`sum_k a_k(s)`, whose tail is bounded in §3.5 by `1.167` beyond the finitely many places
with `s F_k <= 1`. Taking logarithms and substituting `x = e^{-s}` gives the claim. ∎

Three remarks.

**It holds at every `s`, which is why the minimiser needs no certification.** T1 is not
an asymptotic statement and carries no error term: whichever `s > 0` is supplied, the
inequality is true. The numerics of §6 choose `s` by an uncertified floating-point
minimisation of `s N + log F_c(e^{-s})` and then evaluate the right-hand side at that
`s` by certified interval arithmetic. A suboptimal `s` costs slack, never soundness.
This is the whole reason the certified pipeline has to enclose `log F_c(e^{-s})`
rigorously but may locate `s` however it likes (spec §5.4).

**Truncation is the wrong way round.** `F_c` is an infinite product of factors each
`>= 1`, so truncating it *lowers* the value and breaks T1's inequality in exactly the
direction that matters. The float path in `capfib/product.py` truncates; the certified
path in `capfib/interval.py` sums places exactly until `s F_k >= 40` and then adds a
rigorous upper bound for the remaining tail.

**This is a paper proof.** T1–T3 are analytic and are out of scope for the Lean layer
(spec PD2); the only statement crossing between the two layers is the fixup lemma of
§4.

---

## 3. T2 — the asymptotic upper bound

> **T2.** As `s -> 0+`, with `T = log(1/s)`,
> ```
> log F_c(e^{-s}) = T^2 / (4 lambda) + O(T).
> ```
> Consequently `log R_c(N) <= (1 + o(1)) (log N)^2 / (4 log phi)`.

### 3.1 Two uniform bounds on `h`

Everything in the proof rests on these, and on the fact that they are **uniform in `x`**
on the stated ranges.

> **(H1)** For every `x > 0`, `h(x) = -log x + r(x)` with `0 <= r(x) <= x`.
>
> **(H2)** For every `x >= 1`, `0 <= h(x) <= e^{-x} / (1 - e^{-1})`.

**Proof of (H1).** `r(x) = h(x) + log x = -log((1 - e^{-x})/x)`. From `1 - e^{-x} <= x`
we get `(1 - e^{-x})/x <= 1`, hence `r(x) >= 0`. From `x <= e^{x} - 1`, multiplying by
`e^{-x}`, we get `x e^{-x} <= 1 - e^{-x}`, hence `(1 - e^{-x})/x >= e^{-x}` and
`r(x) <= x`. ∎

**Proof of (H2).** Put `y = e^{-x} <= e^{-1}`. Then `h = -log(1 - y) <= y/(1 - y)`, and
`1 - y >= 1 - e^{-1}`. ∎

(H1) is stated for all `x > 0` but is only useful for `x <= 1`, where the bound `r <= x`
is small; (H2) is only useful for `x >= 1`, where `e^{-x}` is small.

### 3.2 Exact cutoffs

```
p = max{ k : v_k <= 1 },        q = max{ k : u_k <= 1 }.
```

Both are finite for each `s > 0` and both tend to infinity as `s -> 0+`; `u_k <= v_k`
gives `p <= q`. Their location follows from `(F1)`, and — this is the point — only
their location is needed, never a pointwise approximation to `a_k`.

For `q`: `F_q <= 1/s` with `(F1)` gives `phi^{q-2} <= e^{T}`, so `q <= T/lambda + 2`;
and `F_{q+1} > 1/s` with `(F1)` gives `phi^{q} >= F_{q+1} > e^{T}`, so `q > T/lambda`.

For `p`: `F_p(F_p + 1) <= 1/s` and `F_p(F_p+1) >= F_p^2 >= phi^{2p-4}` give
`p <= T/(2 lambda) + 2`; and `F_{p+1}(F_{p+1}+1) > 1/s` with
`F_{p+1}(F_{p+1}+1) <= 2 F_{p+1}^2 <= 2 phi^{2p}` gives
`p > T/(2 lambda) - log 2/(2 lambda)`.

So `p = T/(2 lambda) + O(1)` and `q = T/lambda + O(1)` with the `O(1)`s bounded by
absolute constants, uniformly in `s`.

### 3.3 Regime A: `k <= p` (the cap binds)

Here `u_k <= v_k <= 1`, so (H1) applies to both arguments and

```
a_k = log(v_k/u_k) + r(u_k) - r(v_k) = log(F_k + 1) + r(u_k) - r(v_k),
```

with `|r(u_k) - r(v_k)| <= max(r(u_k), r(v_k)) <= v_k`. The total error is bounded by
`sum_{k<=p} v_k`, and that sum is `O(1)` **uniformly in `s`**: by `(F1)`,
`v_k / v_p = F_k(F_k+1) / (F_p(F_p+1)) <= 2 phi^{2k-2} / phi^{2p-4} = 2 phi^{2(k-p)+2}`,
so

```
sum_{k<=p} v_k <= v_p * 2 phi^2 * sum_{j>=0} phi^{-2j} = v_p * 2 phi^2/(1 - phi^{-2}) <= 8.473,
```

using `v_p <= 1`. For the main term, `(F1)` and `F_k <= F_k + 1 <= 2 F_k` give
`(k-2) lambda <= log(F_k + 1) <= (k-1) lambda + log 2`, so

```
sum_{k<=p} log(F_k + 1) = lambda p^2/2 + O(p).
```

With `p = T/(2 lambda) + O(1)` from §3.2, `lambda p^2/2 = T^2/(8 lambda) + O(T)`, and the
regime contributes `T^2/(8 lambda) + O(T)`.

### 3.4 Regime B: `p < k <= q` (the budget binds)

Here `u_k <= 1 < v_k`, so (H1) applies at `u_k` and (H2) at `v_k`:

```
a_k = -log u_k + r(u_k) - h(v_k) = log(1/(s F_k)) + theta_k,
theta_k in [ -e^{-1}/(1 - e^{-1}), 1 ] = [-0.5820, 1],
```

since `0 <= r(u_k) <= u_k <= 1` and `0 <= h(v_k) <= e^{-v_k}/(1-e^{-1}) <= 0.5820`. The
total error over the regime is therefore `O(q - p) = O(T)`. For the main term, write
`log F_k = k lambda - mu_k` with `mu_k in [lambda, 2 lambda]` by `(F1)`; then

```
sum_{p<k<=q} log(1/(s F_k)) = sum_{p<k<=q} (T - k lambda) + sum_{p<k<=q} mu_k
                            = (q-p) T - lambda (q^2 - p^2)/2 + O(q-p).
```

Substituting `q = T/lambda + O(1)` and `p = T/(2 lambda) + O(1)` gives
`q - p = T/(2 lambda) + O(1)` and `(q^2 - p^2) = (q-p)(q+p) = 3T^2/(4 lambda^2) + O(T)`,
so the main term is `T^2/(2 lambda) - 3 T^2/(8 lambda) + O(T) = T^2/(8 lambda) + O(T)`.

### 3.5 Regime C: `k > q` (negligible in total)

There are infinitely many such places, and their total contribution is `O(1)`. For
`k > q` we have `u_k > 1`, so by positivity and (H2),

```
0 < a_k <= h(u_k) <= e^{-u_k}/(1 - e^{-1}).
```

By `(F2)`, `u_{q+1+j} >= (3/2)^j u_{q+1} > (3/2)^j` for `j >= 0` (the indices involved
are all `>= 2`, where `(F2)` holds), hence

```
sum_{k>q} a_k <= (1 - e^{-1})^{-1} sum_{j>=0} exp(-(3/2)^j) <= 1.167.
```

### 3.6 Conclusion of T2

Adding the three regimes,

```
log F_c(e^{-s}) = T^2/(8 lambda) + T^2/(8 lambda) + O(T) = T^2/(4 lambda) + O(T).
```

The equal split between A and B is the structural fact the lower bound has to contend
with: half the mass sits in the places where the digit cap `F_k` binds, half in the
places where the budget `N` binds.

Now apply T1 at `s = t/(2 lambda N)`, where `t = log N`. Then `sN = t/(2 lambda) = O(t)`
and

```
T = log(1/s) = t - log t + log(2 lambda),   T^2 = t^2 - 2 t log t + O(t),
```

so T1 and the display above give the **effective form**

```
log R_c(N) <= t^2/(4 lambda) - (t log t)/(2 lambda) + O(t),
```

and in particular `log R_c(N) <= (1 + o(1)) (log N)^2/(4 log phi)`. ∎

### 3.7 Remark — why the shorter argument fails

An earlier draft of the design spec replaced §3.3–§3.5 with: by Binet, `log F_k` is
`k lambda + O(1)`, each regime boundary is crossed within `O(1)` places, so
`a_k ≈ log(F_k + 1)` below the boundary and `a_k ≈ log(1/(s F_k))` above it. That is not
a proof, for two reasons, and it must not be reinstated.

First, Binet controls `log F_k`; it says nothing about the difference
`a_k(s) - log(F_k + 1)`, which is the quantity being discarded. Second — and this is
what kills the repair-by-more-care version — a *pointwise* `o(1)` cannot be summed over
`Theta(T)` indices that move with `s`.

The approximation is provably not uniform at its own boundary. Take
`s_n = 1/(F_n(F_n+1))`, so that `v_n = 1` exactly and `u_n = 1/(F_n + 1) -> 0`. By (H1),

```
a_n(s_n) = h(u_n) - h(1) = log(F_n + 1) + r(u_n) + log(1 - e^{-1}),
```

and `r(u_n) -> 0`, so

```
a_n(s_n) - log(F_n + 1)  ->  log(1 - e^{-1}) = -0.458675...,   not 0.
```

Numerically: `-0.4586745` at `n = 30` and `-0.4586751` at `n = 38`. A single boundary
place carrying an error of `0.46` is harmless, but the shorter argument gives no bound
at all on how many places sit in that state, and no reason the errors should not
accumulate. The uniform scheme above never needs to know: it bounds the *sum* of the
discarded terms, by `8.473` in regime A, by `O(T)` in regime B, and by `1.167` in
regime C.

---

## 4. T3 — the lower bound (construction L1)

> **T3.** For every `N >= 10000`,
> ```
> log R_c(N) >= (log N)^2/(8 log phi) - 2 (log N)(log log N).
> ```
> More precisely, the construction below yields
> `log R_c(N) >= t^2/(8 lambda) - t log t/(2 lambda) + O(t)` with `t = log N`, and the
> secondary coefficient `1/(2 lambda) = 1.0390434...` is explicit.

### 4.1 The two-block construction

Fix `N >= 10000`. Let

```
c = max{ k : F_k <= N },          a = min{ k : F_k F_{k+1} >= N },
fixup block   [1, a],             counting block   (a, c],      M = c - a.
```

Since `F_1 F_2 = 1 < N`, we have `a >= 2`. No third block is used; there is no
pigeonhole step and no steering step, because the fixup block's capacity already exceeds
`N` and therefore *every* free tuple completes.

**(1) Fixup capacity.** `sum_{k<=a} F_k^2 = F_a F_{a+1} >= N` ({claim:sum-of-squares}).
By completeness ({claim:completeness-no-gaps}), every integer in `[0, F_a F_{a+1}]` — in
particular every integer in `[0, N]` — is the value of at least one digit tuple on
places `1..a` respecting the caps `d_k <= F_k`. This is the one statement the paper
layer takes from the Lean layer: it is machine-checked as

```
exists_numeral_of_le (n N : ℕ) (h : N ≤ ∑ k ∈ range n, place (k+1) * place (k+1)) :
    ∃ d : Numeral n, d.value = N
```

in `lean/NonLinearNumberSystems/Completeness.lean`, with `sum_sq_place` converting the
hypothesis into `N <= F_a F_{a+1}`. `Numeral n` carries the cap `d_k <= F_k` in its
definition, so cap-respect is part of the conclusion, not an extra check. The Lean
statement is *length-indexed* — it fixes `n` places, whereas `R_c(N)` ranges over all
places `F_k <= N` — and that is exactly what is wanted here, because the fixup block
genuinely is a fixed finite block of length `a` (spec §4.5). Note that
"at least one" is all that is needed here; representations on the fixup block are
famously non-unique (`theory/01-background.md` §5) and L1 discards that multiplicity —
see §4.5.

**(2) Free family.** On the counting block set `m_k = floor(N/(M F_k))` for
`a < k <= c`, and let the free family be all tuples `(d_k)_{a<k<=c}` with
`0 <= d_k <= m_k`. Two things have to be checked.

*The caps are respected.* For `k > a`, using `a >= 2` so that `F_a < F_{a+1}`,

```
N <= F_a F_{a+1} < F_{a+1}^2 <= F_k^2,
```

hence `m_k <= N/F_k < F_k`, so `d_k <= m_k < F_k` is within the cap.

*The budget is respected.* For any free tuple with `sigma = sum_{a<k<=c} d_k F_k`,

```
sigma <= sum_{a<k<=c} m_k F_k <= sum_{a<k<=c} (N/(M F_k)) F_k = M * (N/M) = N.
```

**(3) Completion.** Given a free tuple, `N - sigma` lies in `[0, N]`, so by (1) it is
the value of some cap-respecting tuple on `[1, a]`. Fix one such tuple per residue —
the lexicographically least, say — so that the completion map is well defined. Gluing
the two blocks and setting `d_k = 0` for `k > c` gives a digit sequence with
`sum_k d_k F_k = sigma + (N - sigma) = N`, respecting every cap, supported on exactly
the places `F_k <= N`. It is therefore counted by `R_c(N)`.

**(4) Injectivity.** Restricting a produced numeral to the places `(a, c]` returns the
free tuple it was built from, so distinct free tuples give distinct representations.

Hence

```
R_c(N) >= prod_{k=a+1}^{c} (m_k + 1).
```

### 4.2 Evaluation

Since `floor(x) + 1 > x`, each factor satisfies `m_k + 1 > N/(M F_k)`, so

```
log R_c(N) >= sum_{k=a+1}^{c} log(N/(M F_k)) = M t - M log M - sum_{k=a+1}^{c} log F_k,
```

with `t = log N`. (Individual terms with `N/(M F_k) < 1` contribute negatively — this
does happen at the top few places, where `m_k = 0` — but the inequality is valid term
by term, so the sum is still a lower bound.)

Locate `a`, `c` and `M` by `(F1)`, with `L = t/lambda`:

| quantity | bound | derivation |
|---|---|---|
| `c` | `L < c <= L + 2` | `phi^{c-2} <= F_c <= N` and `N < F_{c+1} <= phi^{c}` |
| `a` | `(L+1)/2 <= a <= (L+5)/2` | `N <= F_a F_{a+1} <= phi^{2a-1}`; and minimality gives `phi^{2a-5} <= F_{a-1} F_a < N` |
| `M` | `(L-5)/2 < M <= (L+3)/2` | subtract |

For the Fibonacci sum, `log F_k <= (k-1) lambda` gives

```
sum_{k=a+1}^{c} log F_k <= lambda * sum_{j=a}^{c-1} j = lambda M (a + c - 1)/2
                        <= lambda M (3L + 7)/4,
```

using `a + c - 1 <= (L+5)/2 + (L+2) - 1 = (3L+7)/2`. Since `M t = M L lambda`,

```
log R_c(N) >= lambda M (L - 7)/4 - M log M.
```

For `N >= 10000` we have `L >= 19.13`, so `L - 7 > 0` and `M >= 1`; using `M > (L-5)/2` in
the positive first term and `M <= (L+3)/2` in the subtracted `M log M` (which is
increasing for `M >= 1`),

```
log R_c(N) >= lambda (L-5)(L-7)/8 - ((L+3)/2) log((L+3)/2)
            = t^2/(8 lambda) - (3/2) t + 35 lambda/8 - ((L+3)/2) log((L+3)/2).      (*)
```

Since `(L+3)/2 = t/(2 lambda) + 3/2`, the last term is
`t log t/(2 lambda) + O(t)`, so `(*)` is

```
log R_c(N) >= t^2/(8 lambda) - t log t/(2 lambda) + O(t).
```

**The constant `C` and the threshold `N_0`.** The stated form
`log R_c(N) >= t^2/(8 lambda) - C t log t` follows from `(*)` as soon as

```
(3/2) t + (t/(2 lambda) + 3/2) log(t/(2 lambda) + 3/2) - 35 lambda/8  <=  C t log t.
```

Divide by `t` and drop the term `-35 lambda/(8t)`, which is negative and so only makes
the requirement harder. Writing `beta(t) = 1/(2 lambda) + 3/(2t)`, so that
`t/(2 lambda) + 3/2 = beta(t) * t`, what remains to be shown is

```
3/2 + beta(t) * (log t + log beta(t))  <=  C log t.
```

`beta` is decreasing with limit `1/(2 lambda) = 1.0390434...`, and `beta(t) > 1/(2 lambda)`
for every `t`, so the left side exceeds `(1/(2 lambda)) log t` always: no
`C <= 1/(2 lambda)` can work, and every `C > 1/(2 lambda)` works once `t` is large enough.

Take `C = 2` and `t >= log 10000 = 9.21034...`, so `t >= 9.2103`. Every rounding below is taken in the
direction that weakens the conclusion, so the chain may be checked with a calculator at
five decimals and nothing depends on the digits beyond them. Since `3/(2t)` is largest
at the left endpoint, `3/(2t) <= 1.5/9.2103 <= 0.16287`, and `1/(2 lambda) <= 1.03905`,
so

```
beta(t) <= 1.03905 + 0.16287 = 1.20192,      log beta(t) <= log 1.20192 <= 0.18393.
```

Using `log t > 0`, the left side is then at most
`3/2 + 1.20192 log t + 1.20192 * 0.18393 <= 1.72107 + 1.20192 log t`. So it is enough
that `1.72107 + 1.20192 log t <= 2 log t`, i.e. that

```
0.79808 log t >= 1.72107.
```

Since `1.72107/0.79808 <= 2.15652` and `e^{2.15652} <= 8.6411`, it is enough that
`t >= 8.6411` — and `t >= 9.2103`. Hence the pair `(C, N_0) = (2, 10000)`, proved. It
was chosen for a hand-checkable chain and a round `N_0`, not for sharpness: `C` may be
pushed toward `1/(2 lambda) = 1.0390434...` at the cost of a larger `N_0`.

**`C = 1` is not available, and finite-range data cannot supply it.** The secondary
coefficient of this construction is `1/(2 log phi) = 1.0390434...`, above `1`. Evaluating
the construction directly at the decades `10^3` to `10^6` gives an implied `C` rising
from about `0.79` to about `0.88` (design spec Appendix A), which is smaller — and that
is a statement about a pre-asymptotic range with the `O(t)` term still dominant, not a
bound on `C`. The implied value is larger at the top of that range than at the bottom;
the proved coefficient governs.

**The stated bound is vacuous at computable `N`.** `t^2/(8 lambda) - 2 t log t` is
negative until `t ≈ 24.69`, i.e. `N ≈ 5.3 * 10^{10}`, far beyond the range where
`R_c(N)` has been computed exactly. T3 is an asymptotic statement and §6 confronts the
*construction*, not this inequality, with the exact values.

### 4.3 Uniformity

`a` and `c` are functions of `N` alone, and every step above is an inequality valid for
each `N >= 10000` — no subsequence, no averaging, no choice depending on `N` beyond `a`
and `c` themselves. So T3 holds at every integer `N >= N_0`, which is what C4 needs in
order to bound the liminf rather than the limsup.

### 4.4 Why the constant is `1/8` and not `1/4`

The fixup block has to absorb residues as large as `N`, which forces
`F_a F_{a+1} >= N`, i.e. `a = L/2 + O(1)`. To leading order those are exactly the
cap-binding places of regime A in §3.3, which carry half of `log F_c(e^{-s})`. L1 spends
that half on making the construction land on `N` at all, and counts only the other half.

**This paragraph is motivation, not a step.** Nothing in §4.1 or §4.2 uses the
identification with regime A; T3 is proved from `(F1)` and the completeness lemma alone,
and would stand unchanged if the identification were wrong. It is offered only to explain
*where* the missing factor of two goes, and it is leading-order at that: at the `s` chosen
in §3.6 the regime-A boundary sits at `(L - log_phi log N)/2 + O(1)`, not at `a` exactly.

**The factor of two is structural to L1 as specified** — a rectangular free family
`prod (m_k + 1)` with one selected completion per residue. Re-estimating L1's sums more
tightly cannot recover it, because the loss is in the block partition and not in the
estimates: whatever is done with the counting block, the fixup block contributes a
factor of `1` to the product by construction.

**It is not structural to every refinement, and this note does not claim it is.** Two
routes attack the partition rather than the estimates, and either alone would close the
sandwich (spec §4.4):

- **L2a — sparse, multi-scale fixup.** Replace the contiguous reserved block by a sparse
  reserved set (roughly every `log L`-th place) and correct residues hierarchically,
  coarsest scale first, so each reserved place absorbs a residue of its own magnitude
  rather than the full `N`. The reserved places then carry a vanishing fraction of the
  count. *Failure mode:* the hierarchical carry has to terminate without pushing a digit
  past its cap `F_k`.
- **L2b — count all completions, not one.** L1 keeps one completion per residue and
  discards the rest. Keeping them replaces the product by
  `sum over free tuples of (number of representations of N - sigma on places [1, a])`,
  which is the same counting problem one scale down: the fixup block is itself a
  capacity-constrained Fibonacci system on `a = L/2 + O(1)` places. *Failure mode:* the
  inner bound would have to hold uniformly in `sigma`.

That second failure mode is the one Phase 1's data speaks to directly: over
`N <= 1000000` the census records 49.6% decreasing steps ({claim:rc-not-monotone}), so
an inner bound holding on average need not hold at a given residue.

### 4.5 What L1 throws away

Two distinct sources of undercount, worth separating because they point at different
repairs. The multiplicity of fixup-block representations is discarded by the choice of a
single completion — that is L2b's target. The cap-binding places are discarded wholesale
by reserving `[1, a]` — that is L2a's target. L1's `1/8` is what survives both.

---

## 5. C4 — the sandwich

> **C4.** With `lambda = log phi`,
> ```
> 1/(8 lambda) <= liminf_{N->inf} log R_c(N)/(log N)^2
>              <= limsup_{N->inf} log R_c(N)/(log N)^2 <= 1/(4 lambda),
> ```
> numerically `0.2597608... <= liminf <= limsup <= 0.5195217...`.

**Proof.** Divide T3 by `t^2 = (log N)^2`: for `N >= N_0`,
`log R_c(N)/t^2 >= 1/(8 lambda) - 2 (log t)/t`, and `(log t)/t -> 0`, so the liminf is
at least `1/(8 lambda)`. Divide T2's consequence by `t^2` to get the limsup bound.
`liminf <= limsup` always. ∎

**C4 does not assert that `C_c` exists.** It bounds the liminf and the limsup, which is
a strictly weaker statement than convergence. Whether `log R_c(N)/(log N)^2` converges
at all is research question (A) of `theory/00-definitions.md`, still open, and nothing
in T1–T3 bears on it. The roadmap's parametrisation `C_c = 1/(C' log phi)` presupposes
existence; *if* `C_c` exists, C4 gives `C' in [4, 8]`.

**How `C' in [4,8]` relates to the roadmap's anticipated `[2,4]`.** It is not a
strengthening of it, and must not be presented as one. The roadmap anticipated an upper
coefficient `1/(2 log phi)` cited from Coons–Kristensen–Laursen and a lower coefficient
`1/(4 log phi)` from its own construction sketch. Phase 2 **strengthens the upper**
coefficient to `1/(4 log phi)` and **weakens the lower** to `1/(8 log phi)`. The two
intervals are therefore not nested — they meet at `C' = 4` and are otherwise disjoint.
The roadmap's lower sketch was in any case unavailable as written: it bounded `R_c`
below by `R_u`, and capping only removes representations, so the inequality runs the
other way.

**Where this leaves the Phase 3 conjecture.** The conjecture
`log R_c(N) ~ (log N)^2/(4 log phi)` ({claim:leading-constant}) sits at the *upper*
endpoint of the proved interval. Phase 2 therefore leaves it to be settled entirely from
below: the upper bound is already at the conjectured value, and what is missing is a
lower bound matching it — together with the existence statement the conjecture asserts
and C4 does not. Two formulations are deliberately avoided here. "The conjecture holds
if and only if T2 is attained" is wrong, because matching the limsup to the upper
endpoint says nothing about the liminf. And "T2 is sharp" is not established: no
argument in this note shows the upper constant cannot be lowered.

---

## 6. Numerical confrontation

All numbers in this section are quoted from `data/phase2_figures.json`, generated by
`scripts/run_phase2.py`, and are checked against this prose by
`tests/test_phase2_figures.py`. The verification ran against the exact `R_c` values in
`data/phase1_data.csv`, which holds **37 sampled `N`** spanning 2 to 1000000
{fig:n-max-verified} — the Fibonacci numbers, the decades, and the half-decades. Phase 1 computed `R_c(N)` exactly for the whole range up to `10^6`; the Phase 2
checks ran at those 37 points, and no statement below reaches beyond them.

**T1, certified.** At the largest verified value, `N` = 1000000 {fig:n-max-verified},
the exact `log R_c(N)` is 68.3632 {fig:log-rc-nmax} and the certified Chernoff bound is
81.9137 {fig:chernoff-certified-nmax}, a slack of 13.5505 {fig:chernoff-slack-nmax}.
The bound held at each of the 37 sampled `N`, with no violation. Each evaluation was
gated in the same run on the float and certified paths agreeing to `1e-12`.

**T3's construction, evaluated directly.** At the same `N` the construction of §4.1
gives 17.774 {fig:t3-lower-nmax}, with a fixup block ending at place 16
{fig:fixup-block-nmax} and 14 {fig:counting-places-nmax} counting places. It stayed
below the exact `log R_c(N)` at each of the 37 sampled `N`, and the cap and budget
conditions of §4.1(2) held at each of them. This confronts the *construction*; the
inequality stated as T3 is vacuous here (§4.2).

**The ratio.** The observed `log R_c(N)/(log N)^2` is 0.3582 {fig:ratio-nmax} at that
`N` — between the proved constants 0.2598 {fig:lower-constant} and 0.5195
{fig:upper-constant}. Leading-order constants cannot be confirmed at
N <= 1000000 {fig:n-max-verified}; the ratio is far from either endpoint and is not
monotone, falling to about `0.3245` near `N = 316` before rising to its value at the top
of the sampled range. At the three smallest sampled points (`N = 2, 3, 5`) it exceeds
the upper constant outright. **This does not contradict C4, and a reader should not read
it as data against the theorem.** C4 is a statement about the tail: it constrains the
liminf and limsup of `log R_c(N)/(log N)^2`, both of which are unchanged by the values at
any finite set of `N`. T2's consequence carries a `(1 + o(1))`, and T3 is stated only for
`N >= 10000`, so neither bound claims anything whatsoever at `N = 2, 3, 5`. Small `N` sit
above the interval for the obvious reason: `(log N)^2` is tiny there while `R_c(N) >= 1`
forces `log R_c(N) >= 0`, so the ratio is inflated by the denominator. From `N = 8`
upward it lies strictly inside `[0.2598, 0.5195]` at each of the sampled points in that
range.

**The product residual.** A separate sweep evaluates
`log F_c(e^{-s}) - (log(1/s))^2/(4 lambda)` at eight values of `T = log(1/s)` between 10
{fig:residual-t-min} and 1280 {fig:residual-t-max}. Over the seven samples with
T >= 20 {fig:residual-asymptotic-t-min} the residual sits at 3.2274
{fig:residual-asymptotic-centre} with a spread of 0.000178
{fig:residual-asymptotic-spread}; including the `T = 10` point, which is
pre-asymptotic, the spread over the full sweep is 0.018236
{fig:residual-full-spread}. This is a **sampled observation at eight points**, not a
proved `O(1)` error term: T2 establishes `O(T)`, and nothing here upgrades that. What it
does suggest is that T2's `O(T)` is not sharp on this range — but eight points cannot
establish a bound, and the quantity was not evaluated between them.

---

## 7. Comparison with Coons–Kristensen–Laursen — qualitative only

The uncapped analogue `R_u(N)` — same places, digits unbounded — is related to the
Fibonacci partition function `p_F(n)` studied by Coons, Kristensen and Laursen (2023,
arXiv:2312.07404), for which `log p_F(n) ~ (log n)^2/(2 log phi)` is cited.

**No numerical relationship between our constants and theirs is asserted here.** Their
`p_F(n)` counts multisets of Fibonacci numbers; our `R_u(N)` counts digit sequences over
a place set containing *both* `F_1 = 1` and `F_2 = 1`. The two objects differ by a
splitting factor arising from that duplicated 1-place: a multiset with `j` copies of the
value `1` corresponds to `j + 1` digit sequences. That factor is very plausibly
`o(exp((log N)^2))` and so harmless to leading order, but this project does not hold the
paper, and the identification is recorded as **pending verification** in
`theory/00-definitions.md`. Making it precise is out of scope (spec §11).

**`countReps_le_uncapped` is proved but not load-bearing.** The Lean statement
`R_c <= R_u` is proved with no `sorry` in `lean/NonLinearNumberSystems/Bounds.lean`. It
is the length-indexed inequality — `countReps n N <= countRepsUncapped n N` for a fixed
number of places `n`, not the all-places `R_c(N)` of §1. Under the roadmap's original
plan it *was* the upper bound: `R_c <= R_u` plus the cited CKL asymptotic would have
given `1/(2 log phi)`. T1 and T2
prove `1/(4 log phi)` directly and without reference to CKL, so that route is not taken
and the inequality is not a step in any bound in this note. It backs this remark, and
that is all it is claimed to do. This is also what makes the reconciliation above cheap:
nothing proved here depends on the identification being correct.

---

## 8. The L2 attempt

Attempted after the main results; see the section added by the stretch task.

---

## Appendix — proof dependencies

| Result | Depends on |
|---|---|
| T1 | non-negativity of `[x^n] F_c` only |
| T2 | (H1), (H2), `(F1)`, `(F2)`, and T1 for the consequence |
| T3 | `{claim:sum-of-squares}`, `{claim:completeness-no-gaps}` (Lean: `exists_numeral_of_le`), `(F1)` |
| C4 | T2, T3 |

Nothing in T1–T3 depends on the CKL citation, on `countReps_le_uncapped`, or on any
numerical result. §6 is confrontation, not evidence: no constant in §§2–5 was derived
from data.
