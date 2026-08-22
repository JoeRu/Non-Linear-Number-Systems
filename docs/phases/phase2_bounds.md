# Phase 2 — Elementary Sandwich Bounds for `log R_c(N)`

**Question.** How large is `R_c(N)`, to leading order in `(log N)^2`, and how much of
that can be settled by elementary means?

**Answer.** `log R_c(N) ~ (log N)^2/(4 log phi)`: the limit of
`log R_c(N)/(log N)^2` exists and equals `1/(4 log phi)` (C5, §8). The route there runs
through a weaker sandwich first — T2's upper constant `1/(4 log phi)` against T3's lower
constant `1/(8 log phi)`, a factor of two apart (C4, §5) — because the factor of two is
not an artefact of loose estimates but of T3's block structure (§4), and §8 closes it by
counting the reserved block instead of reserving it. §§1–7 are left as they were proved:
T5 is built on T3's machinery, and the factor of two is easier to follow with both halves
in view.

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

the middle sum converging for every `s > 0`. That needs no reference to the cutoffs of
§3.2, which are not even defined for large `s`: the product's logarithm is
`sum_k a_k(s)` with `0 < a_k(s) <= h(u_k)`, and by `(F2)` `F_k >= (3/2)^{k-2}` for
`k >= 2`, so `u_k = s F_k -> infinity` at a geometric rate. Hence `u_k >= 1` for all `k`
beyond some finite `K(s)`, where (H2) of §3.1 gives
`a_k <= e^{-u_k}/(1 - e^{-1})` and the tail is dominated by a convergent geometric-exponent
series; the finitely many earlier terms are each finite because `u_k > 0`. Taking
logarithms and substituting `x = e^{-s}` gives the claim. ∎

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
p = max({0} ∪ { k >= 1 : v_k <= 1 }),        q = max({0} ∪ { k >= 1 : u_k <= 1 }).
```

The `{0}` is not decoration: `{k : v_k <= 1}` is empty once `s > 1/2` and
`{k : u_k <= 1}` once `s > 1`, so without it the `max` has no argument there. Adjoining
`0` makes both well defined at every `s > 0`, and both sets are finite because
`u_k <= v_k` and `u_k -> infinity`, so both `p` and `q` are finite. `u_k <= v_k` gives
`p <= q`.

T2 is an `s -> 0+` statement, so assume from here on that `s <= 1/2`. Then
`v_1 = v_2 = 2s <= 1`, hence `p >= 2` and a fortiori `q >= 2`; both tend to infinity as
`s -> 0+`. Their location follows from `(F1)`, and — this is the point — only their
location is needed, never a pointwise approximation to `a_k`.

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
and `v_p <= 1` by the definition of `p`. Both facts are used in the display, so it is a
bound on the sum itself and not on a ratio:

```
sum_{k<=p} v_k <= v_p * 2 phi^2 * sum_{j>=0} phi^{-2j} = v_p * 2 phi^2/(1 - phi^{-2}) <= 8.473.
```

For the main term, `(F1)` and `F_k <= F_k + 1 <= 2 F_k` give
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

By `(F2)`, `u_{q+1+j} >= (3/2)^j u_{q+1} > (3/2)^j` for `j >= 0` — the ratio steps
involved run from index `q+1 >= 3`, and `(F2)` holds from index `2` on, so none of them is
the exceptional step `F_2/F_1 = 1`. Hence

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

(expanding `(t - log t + log 2 lambda)^2` also produces `(log t)^2`, `-2 log(2 lambda) log t`
and a constant, all of which are absorbed into the `O(t)`),

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

**(2) Free family.** The counting block is non-empty: §4.2's table gives
`a <= (L+5)/2` and `c > L`, so `M = c - a > (L-5)/2`, and `N >= 10000` gives
`L >= 19.13` and hence `M >= 8`. (That table is derived from `(F1)` and the definitions
of `a` and `c` alone — nothing in it uses this step, so the forward reference is not
circular.) On the counting block set `m_k = floor(N/(M F_k))` for `a < k <= c`, and let
the free family be all tuples `(d_k)_{a<k<=c}` with `0 <= d_k <= m_k`. Two things have to
be checked.

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
the construction directly at the decades `10^3` to `10^6` gives an implied `C` of about
`0.79`, `0.78`, `0.87`, `0.88` — smaller than `1.0390434...`, and **not** monotone in
between. That is a statement about a pre-asymptotic range with the `O(t)` term still
dominant, not a bound on `C`. The implied value is larger at the top of that range than
at the bottom; the proved coefficient governs.

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
- **L2b — count all completions, not one** (this is the one that closes; §8). L1 keeps one completion per residue and
  discards the rest. Keeping them replaces the product by
  `sum over free tuples of (number of representations of N - sigma on places [1, a])`,
  which is the same counting problem one scale down: the fixup block is itself a
  capacity-constrained Fibonacci system on `a = L/2 + O(1)` places. *Failure mode:* the
  inner bound would have to hold uniformly in `sigma`.

That second failure mode is the one Phase 1's data speaks to directly: over
`N <= 1000000` the census records 49.6% decreasing steps ({claim:rc-not-monotone}), so
an inner bound holding on average need not hold at a given residue.

*Outcome.* L2b closed; the uniform inner bound it needs is Lemma F of §8.2, which holds at
every residue of a middle band and is coarse enough that fluctuations of the measured size
pass under it. L2a did not, and §8.6 records where it stopped — not at the carry, which is
where this paragraph expected it, but a step earlier.

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
at all is research question (A) of `theory/00-definitions.md`; nothing in T1–T3 bears on
it, and C4 leaves it open. **That is a statement about C4's reach, not about the state of
the question:** research question (A) is answered later in this same note, by §8's T5,
which supplies a matching lower bound, and C5, which concludes that the limit exists and
equals `1/(4 lambda)`. The
distinction C4 draws is still the right one to keep in view — bounding a liminf and a
limsup is strictly weaker than asserting convergence — and it is what T5 had to supply in
addition to a constant. The roadmap's parametrisation `C_c = 1/(C' log phi)` presupposes
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

**Where this leaves the Phase 3 conjecture** — *as of T1–T3 alone; §8 goes further, and
this paragraph is left as written because it states correctly what T1–T3 by themselves
leave open.* The conjecture
`log R_c(N) ~ (log N)^2/(4 log phi)` ({claim:leading-constant}) sits at the *upper*
endpoint of the proved interval. T1–T3 therefore leave it to be settled entirely from
below: the upper bound is already at the conjectured value, and what T1–T3 do not supply
is a lower bound matching it — together with the existence statement the conjecture
asserts and C4 does not. (§8 supplies both; Phase 2 as a whole settled it.) Two formulations are deliberately avoided here. "The conjecture holds
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
The bound held at each of the 37 sampled `N`, with no violation, and unlike the lower
bound below it was strict at each of them — the smallest slack anywhere in the sample is
`1.94`, at `N = 2`. Each evaluation was gated in the same run on the float and certified
paths agreeing to `1e-12`.

**T3's construction, evaluated directly.** At the same `N` the construction of §4.1
gives 17.774 {fig:t3-lower-nmax}, with a fixup block ending at place 16
{fig:fixup-block-nmax} and 14 {fig:counting-places-nmax} counting places. It stayed
at or below the exact `log R_c(N)` at each of the 37 sampled `N` — it exceeded it at
none of them — and the cap and budget conditions of §4.1(2) held at each of them. At 36
of the 37 it is strictly below. At `N = 2` the two are **exactly equal**, both
`0.6931471805599453`.

That equality is expected, not alarming, and it is the one place in the sampled range
where L1 is lossless. At `N = 2` the blocks are `[1,2]` and `{3}`, so `M = 1` and
`m_3 = floor(2/2) = 1`: the free family is `d_3 in {0,1}` and the construction produces
exactly two numerals. §4.5 names L1's two sources of undercount, and at `N = 2` neither
is present. The fixup block `[1,2]` has capacity `F_2 F_3 = 2` and represents each of the
two residues it is asked for — `0` as `(0,0)` and `2` as `(1,1)` — in exactly one way, so
choosing "one completion per residue" discards nothing; and there are no cap-binding
places outside the reserved block to lose. Hence the construction enumerates all of
`R_c(2) = 2`. Note that `N = 2` is far below `N_0 = 10000`, so T3 as stated claims nothing
here in any case. This confronts the *construction*; the inequality stated as T3 is
vacuous at these `N` (§4.2).

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

## 8. T5 — closing the sandwich (route L2b)

Route **L2b** of §4.4 closes. Route L2a was attempted first, stopped, and is recorded in
§8.6 — the reason it stopped is what pointed at L2b.

> **T5.** For every integer `N >= 10000`, with `t = log N` and `lambda = log phi`,
> ```
> log R_c(N) >= t^2/(4 lambda) - (t log t)/(2 lambda) - 7.5 t.
> ```
> In particular `log R_c(N) >= (1 - o(1)) (log N)^2/(4 log phi)`.

> **C5.** With `lambda = log phi`,
> ```
> lim_{N->infinity} log R_c(N)/(log N)^2  =  1/(4 lambda)  =  0.5195217...
> ```
> — the limit exists, and equals the upper endpoint of C4's interval.

### 8.1 The one thing L1 was missing

L1 reserves the block `[1, a]` and takes **one** completion per residue, so the block
contributes a factor of `1` to the product and the whole cap-binding half of the count
is thrown away (§4.5). Keeping every completion replaces the product by

```
R_c(N)  >=  sum over free tuples of  B(a, N - sigma),
```

where `B(a, m)` is the number of cap-respecting digit tuples on places `1..a` of value
`m`. §4.4 named the obstacle: that inner count has to be bounded **uniformly in the
residue**, and the residue is not under the construction's control.

The obstacle dissolves once one notices how much room there is. `B(a, ·)` is supported on
`[0, S_a]` with `S_a = sum_{k<=a} F_k^2 = F_a F_{a+1}` ({claim:sum-of-squares}); its total
mass is `prod_{k<=a} (F_k + 1) = exp(lambda a^2/2 + O(a))`, spread over `S_a + 1` values,
and `S_a = exp(2 lambda a + O(1))`. So the mean of `B(a, ·)` is `exp(lambda a^2/2 + O(a))`
— the same as the maximum, to the precision that matters. A uniform lower bound on
`B(a, m)` only has to be within `exp(o(a^2))` of the mean, and dividing by the whole
range `S_a` costs `exp(-O(a))`, which is free at the `a^2` scale. What is needed is
therefore not a local limit theorem but a crude flatness statement, and that is Lemma F.

**This paragraph is motivation, not a step.** Nothing in §8.2 or §8.3 uses the mean of
`B(a, ·)`, or the value of its total mass; Lemma F is proved from `(F1)`, the two
identities `S_a = F_a F_{a+1}` and `S_a - S_{a-1} = F_a^2`, and completeness. The
paragraph is offered only to explain why a bound this coarse can be enough.

### 8.2 Lemma F — a block is flat on its middle band

Write `S_a = sum_{k<=a} F_k^2 = F_a F_{a+1}` (`{claim:sum-of-squares}`, `S_0 = 0`), and

```
B(a, m)  =  #{ (d_1, ..., d_a) : 0 <= d_k <= F_k,  sum_{k<=a} d_k F_k = m },
```

with `B(a, m) = 0` for `m < 0` and for `m > S_a`. Fix once and for all

```
theta_1 = 1/5,   theta_2 = 3/4,   rho = min(theta_2 - theta_1, theta_1, 1 - theta_2) = 1/5,
I_a = { m in Z : theta_1 S_a <= m <= theta_2 S_a }        (the band of the block [1, a]).
```

> **Lemma F.** For every `a >= 8` and every `m in I_a`,
> ```
> B(a, m)  >=  prod_{k=8}^{a} ( F_{k-1}/5 - 1 ),
> ```
> and consequently
> ```
> log B(a, m)  >=  lambda a^2/2  -  3.5057 a  +  12.749.
> ```

The constants `theta_1`, `theta_2` are not optimised. They are pinned by two unrelated
requirements — §8.3 needs `theta_1/theta_2 < 1/3`, and `rho` must be positive — and
every choice satisfying those gives the same leading term, because `rho` enters only
through an `O(a)` correction.

**Step 1 — conditioning on the top digit.** Splitting the count according to `d_a`,

```
B(a, m)  =  sum_{d=0}^{F_a} B(a-1, m - d F_a),                                    (8.1)
```

an identity, not an estimate: distinct `d` give disjoint sets of tuples, and every tuple
has exactly one value of `d_a`. Discarding all but a subset `D` of the admissible `d`
therefore leaves a lower bound.

**Step 2 — the admissible digits.** For `a >= 2` put

```
D_a(m) = { d in Z : 0 <= d <= F_a,  m - d F_a in I_{a-1} }.
```

Unwinding the membership condition, `d in D_a(m)` iff `d` is an integer of the closed
interval `[d_lo, d_hi] ∩ [0, F_a]`, where

```
d_lo = (m - theta_2 S_{a-1})/F_a,      d_hi = (m - theta_1 S_{a-1})/F_a.
```

(These are real bounds on the digit `d`, not integers, and they are unrelated to the
function `beta(t)` of §4.2 and §8.5, which is why they are not called `alpha` and `beta`.)

Three exact identities of this place set do all the work. `S_{a-1} = F_{a-1} F_a`
({claim:sum-of-squares}) gives

```
d_hi - d_lo = (theta_2 - theta_1) S_{a-1}/F_a = (11/20) F_{a-1};                   (F3)
```

`S_a - S_{a-1} = F_a^2`, which is the definition of `S`, together with `m >= theta_1 S_a`
gives

```
d_hi >= (theta_1 S_a - theta_1 S_{a-1})/F_a = theta_1 F_a;                          (F4)
```

and the same identity with `m <= theta_2 S_a` gives

```
d_lo <= (theta_2 S_a - theta_2 S_{a-1})/F_a = theta_2 F_a.                          (F5)
```

The intersection `[d_lo, d_hi] ∩ [0, F_a]` is a closed interval; its length is bounded
below in each of the four cases, using `F_a >= F_{a-1}` throughout (the place values are
non-decreasing):

| case | which endpoint is active | length | bounded below by |
|---|---|---|---|
| 1 | `d_lo >= 0`, `d_hi <= F_a` | `d_hi - d_lo` | `(11/20) F_{a-1}` by (F3) |
| 2 | `d_lo < 0`, `d_hi <= F_a` | `d_hi` | `theta_1 F_a >= (1/5) F_{a-1}` by (F4) |
| 3 | `d_lo >= 0`, `d_hi > F_a` | `F_a - d_lo` | `(1 - theta_2) F_a >= (1/4) F_{a-1}` by (F5) |
| 4 | `d_lo < 0`, `d_hi > F_a` | `F_a` | `F_{a-1}` |

In every case the length is at least `rho F_{a-1} = F_{a-1}/5`. A closed real interval
`[x, y]` contains `floor(y) - ceil(x) + 1 > (y - 1) - (x + 1) + 1 = y - x - 1` integers,
so

```
|D_a(m)|  >  F_{a-1}/5 - 1     for every a >= 2 and every m in I_a.                (8.2)
```

**The split is exhaustive by construction, and case 4 is unreachable.** The four rows are
the four sign patterns of `d_lo >= 0` and `d_hi <= F_a`, so they cover every `m` of the
band; case 4 is listed to make that manifest, not because it occurs. It cannot occur:
case 4 requires `d_lo < 0` and `d_hi > F_a`, hence `d_hi - d_lo > F_a`, while (F3) fixes
`d_hi - d_lo = (11/20) F_{a-1} <= F_a`. Covering an impossible case costs the proof
nothing — the bound in that row is the largest of the four — and the row is kept so the
case analysis can be checked for exhaustiveness without a further argument.

Cases 2 and 3 do occur; they are the residues nearest the two edges of the band. They are
why the table cannot be collapsed into the naive assumption `[d_lo, d_hi] ⊆ [0, F_a]`,
which is false there. Note also what (8.2) does **not** say: it is not a statement about
where `m` sits inside its band.

**Step 3 — the induction.** Let `a >= 8`. Then `F_{a-1} >= F_7 = 13`, so (8.2) gives
`|D_a(m)| > 13/5 - 1 = 1.6`, in particular `D_a(m)` is non-empty; and since an element
`d` of it exhibits the integer `m - d F_a` of `I_{a-1}`, the band `I_{a-1}` is non-empty
too, so `min_{m' in I_{a-1}} B(a-1, m')` is a minimum over a non-empty set. Keeping only
the terms of (8.1) with `d in D_a(m)`,

```
B(a, m)  >=  |D_a(m)| * min_{m' in I_{a-1}} B(a-1, m')  >=  (F_{a-1}/5 - 1) * min_{I_{a-1}} B(a-1, ·).
```

The right-hand side no longer depends on `m`, so the same bound holds for the minimum
over `I_a`. Iterating from `a` down to `8` leaves the factors
`prod_{k=8}^{a} (F_{k-1}/5 - 1)` multiplying `min_{m' in I_7} B(7, m')`, and that minimum
is at least `1`: `I_7 ⊆ [0, S_7]`, and by completeness ({claim:completeness-no-gaps}, the
Lean lemma `exists_numeral_of_le`) every integer of `[0, S_7]` is the value of at least
one cap-respecting tuple on seven places. This is the same lemma T3 uses, and it is the
only place in T5 where it is used.

**Step 4 — the closed form.** For `k >= 8` we have `F_{k-1} >= 13 >= 10`, hence
`F_{k-1}/5 - 1 >= F_{k-1}/10`, and `(F1)` gives `F_{k-1} >= phi^{k-3}`. So

```
log prod_{k=8}^{a} (F_{k-1}/5 - 1)  >=  sum_{k=8}^{a} ( (k-3) lambda - log 10 )
  =  lambda ( (a-3)(a-2)/2 - 10 )  -  (a - 7) log 10
  =  lambda a^2/2  -  (5 lambda/2 + log 10) a  +  ( 7 log 10 - 7 lambda ).
```

Numerically `5 lambda/2 + log 10 = 3.5056146...` and `7 log 10 - 7 lambda = 12.7496128...`.
Replacing the first by the larger `3.5057` and the second by the smaller `12.749` weakens
the bound in both places, which gives the stated closed form. ∎

**Sharpness of Lemma F is not claimed and is not needed.** Computing `B(a, ·)` exactly by
DP, the shortfall of the band minimum below `lambda a^2/2` grows with a least-squares slope
of 1.5230 {fig:flatness-slack-slope} per unit of `a`, measured over `a` from 8 to 16
{fig:flatness-slack-a-max} — against the proved coefficient `3.5057`, so Lemma F is loose
by roughly a factor of two in its linear term over that range. Nine points settle nothing
about the coefficient, and nothing below needs them to: both the proved and the measured
forms are `lambda a^2/2 + O(a)`, and only the quadratic term reaches §8.4. Like every other
generated number quoted in this note, the slope comes from `data/phase2_figures.json` and is
bound to the prose by `tests/test_phase2_figures.py`; `capfib.lower.block_band_min` is the
exact band minimum it is computed from.

### 8.3 The construction L2

Fix `N >= 10000` and let

```
c = max{ k : F_k <= N },                 a = min{ k >= 1 : S_k >= (4/3) N },
M = c - a,                               X = floor( N - S_a/5 ),
m_k = floor( X / (M F_k) )   for a < k <= c.
```

`a` is well defined because `S_k -> infinity`, and `a >= 2` because `S_1 = F_1 F_2 = 1`
is below `(4/3) N`. The condition defining `a` is `N <= theta_2 S_a`; the definition of
`X` is `X = floor(N - theta_1 S_a)`. That `M >= 1` is checked in §8.4.

**(1) The block absorbs the whole band, not just one residue.** By construction
`N <= theta_2 S_a`.

**(2) `X` is a constant fraction of `N`.** The place values satisfy `F_a/F_{a-1} <= 2` for
every `a >= 2` — at `a = 2` it reads `F_2/F_1 = 1`, at `a = 3` it reads `F_3/F_2 = 2`,
and for `a >= 4` it is `F_a = F_{a-1} + F_{a-2} <= 2 F_{a-1}` — so

```
S_a / S_{a-1} = F_{a+1}/F_{a-1} = 1 + F_a/F_{a-1} <= 3.
```

Minimality of `a` (available because `a >= 2`) gives `S_{a-1} < (4/3) N`, hence
`S_a < 4 N` and

```
X  >  N - (4/5) N - 1  =  N/5 - 1  >=  N/6      (the last step for N >= 30).
```

**(3) The caps are respected on the counting block.** For `a < k <= c`, using `M >= 1`
and `X <= N`,

```
m_k <= X/F_k <= N/F_k,     and    F_k^2 >= F_{a+1}^2 >= F_a F_{a+1} = S_a >= (4/3) N > N,
```

so `m_k <= N/F_k < F_k`.

**(4) The budget is respected.** For any tuple `(d_k)_{a<k<=c}` with `0 <= d_k <= m_k`,

```
sigma = sum_{a<k<=c} d_k F_k  <=  sum_{a<k<=c} (X/(M F_k)) F_k  =  X.
```

**(5) Every residue lands in the band.** For such a tuple, `m = N - sigma` satisfies
`m <= N <= theta_2 S_a` by (1), and, since `X = floor(N - theta_1 S_a) <= N - theta_1 S_a`,

```
m  =  N - sigma  >=  N - X  >=  theta_1 S_a.
```

So `m` is an integer of `I_a`, and Lemma F applies to it — provided `a >= 8`, which §8.4
checks.

**(6) Completion and injectivity.** By Lemma F there are at least
`G(a) := prod_{k=8}^{a} (F_{k-1}/5 - 1)` cap-respecting tuples on `[1, a]` of value
`m`. Gluing any of them to the free tuple, and setting `d_k = 0` for `k > c`, gives a
digit sequence with total `sigma + (N - sigma) = N`, respecting every cap, supported on
exactly the places `F_k <= N`; it is therefore counted by `R_c(N)`. Restricting a
produced numeral to `(a, c]` returns the free tuple and restricting it to `[1, a]`
returns the inner tuple, so distinct pairs give distinct numerals. Hence

```
R_c(N)  >=  ( prod_{k=a+1}^{c} (m_k + 1) )  *  G(a).                               (8.3)
```

The contrast with §4.1 is the second factor alone: L1's block contributes `1` there,
because it selects one completion per residue; here it contributes `G(a)`, and §8.4
shows that this factor is what supplies the missing `lambda L^2/8`.

### 8.4 Evaluation

Write `t = log N` and `L = t/lambda`, so `phi^L = N`; `N >= 10000` gives
`L >= 9.2103/0.4812119 >= 19.13`. From `(F1)`, `phi^{2k-3} <= S_k <= phi^{2k-1}`.

| quantity | bound | derivation |
|---|---|---|
| `c` | `L < c <= L + 2` | as in §4.2 |
| `a` | `(L+1)/2 <= a < (L + 5.5979)/2` | below |
| `M` | `(L - 5.5979)/2 < M <= (L+3)/2` | subtract |

For the lower bound on `a`: `phi^{2a-1} >= S_a >= (4/3) N >= phi^L`, so `2a - 1 >= L`.
For the upper: minimality gives `S_{a-1} < (4/3) N`, and `S_{a-1} >= phi^{2a-5}`, so
`2a - 5 < L + log(4/3)/lambda`; and `log(4/3)/lambda = 0.59782835... < 0.5979`.

At `L >= 19.13` this gives `M > 6.7` and `a >= 10.06`, so `M >= 1` and `a >= 8` as §8.3
and Lemma F require.

**The counting block.** Since `floor(x) + 1 > x`, each factor of (8.3) satisfies
`m_k + 1 > X/(M F_k)`, and the resulting inequality is valid term by term even where
`X/(M F_k) < 1` and the term is negative. With `log X >= t - log 6` from §8.3(2) and
`log F_k <= (k-1) lambda` from `(F1)`,

```
log prod_{k=a+1}^{c} (m_k + 1)  >=  M log X - M log M - sum_{k=a+1}^{c} log F_k
   >=  M (t - log 6) - M log M - lambda M (a + c - 1)/2
   >=  M lambda L - M log 6 - M log M - lambda M (3L + 7.5979)/4
    =  lambda M (L - 7.5979)/4 - M log M - M log 6,
```

using `a + c - 1 <= (L + 5.5979)/2 + (L + 2) - 1 = (3L + 7.5979)/2` from the table.
Since `L >= 19.13 > 7.5979` the first term increases with `M`, while `-M log M` and
`-M log 6` decrease with `M` on `M >= 1`; substituting `M > (L - 5.5979)/2` in the first
and `M <= (L+3)/2` in the other two,

```
log prod (m_k + 1)  >=  lambda (L - 5.5979)(L - 7.5979)/8
                        - ((L+3)/2) log((L+3)/2) - (log 6)(L+3)/2.
```

Expanding, and using the exact products `5.5979 + 7.5979 = 13.1958` and
`5.5979 * 7.5979 = 42.53228441`: `lambda * 13.1958/8 = 0.79374687... <= 0.79375`,
`lambda * 42.53228441/8 = 2.55837977... >= 2.5583` and
`(log 6)/2 = 0.89587973... <= 0.89588`, each rounding taken in the direction that lowers
the right-hand side:

```
log prod (m_k + 1)  >=  lambda L^2/8 - 1.68963 L - 0.12934 - ((L+3)/2) log((L+3)/2).  (8.4)
```

**The block.** By Lemma F, `log G(a) >= lambda a^2/2 - 3.5057 a + 12.749`. The two
terms are bounded using opposite ends of the table's range for `a`, which is legitimate
because both bounds hold at the actual `a`: `lambda a^2/2 >= lambda (L+1)^2/8` from
`a >= (L+1)/2`, and `-3.5057 a > -3.5057 (L + 5.5979)/2 = -1.75285 L - 9.81228` from
`a < (L + 5.5979)/2`. With `lambda/4 = 0.12030295... >= 0.120302` and
`lambda/8 = 0.06015147... >= 0.06015`,

```
log G(a)     >=  lambda L^2/8 + 0.120302 L + 0.06015 - 1.75285 L - 9.81228 + 12.749
             >=  lambda L^2/8 - 1.632548 L + 2.996.                                 (8.5)
```

**Together.** Adding (8.4) and (8.5) and discarding the positive constant
`2.996 - 0.12934`, which weakens the bound,

```
log R_c(N)  >=  lambda L^2/4 - ((L+3)/2) log((L+3)/2) - 3.322178 L
            >=  lambda L^2/4 - ((L+3)/2) log((L+3)/2) - 3.3222 L.                   (8.6)
```

`lambda L^2/4 = t^2/(4 lambda)`: the two halves have arrived at the same size, and their
sum is T2's upper constant.

### 8.5 From (8.6) to the stated form

`3.3222 L = 3.3222 t/lambda` and `3.3222/lambda = 6.9038203... <= 6.9039`, so that term
is at most `6.9039 t`. For the other, set `beta(t) = 1/(2 lambda) + 3/(2t)`, so that
`(L+3)/2 = beta(t) t` — the same `beta` as in §4.2, and unrelated to the block factor
`G(a)` above — and

```
((L+3)/2) log((L+3)/2)  =  (t/(2 lambda)) log t  +  (3/2) log t
                           +  (t/(2 lambda)) log beta(t)  +  (3/2) log beta(t).
```

Every rounding below is taken in the direction that weakens the conclusion, and the chain
is checkable at five decimals. `N >= 10000` means `t >= 9.2103`. Then
`3/(2t) <= 1.5/9.2103 <= 0.16288` and `1/(2 lambda) <= 1.03905`, so
`beta(t) <= 1.20193` and `log beta(t) <= log 1.20193 <= 0.18393`. Hence

- `(t/(2 lambda)) log beta(t)  <=  1.03905 * 0.18393 * t  <=  0.19112 t`;
- `(3/2) log t <= 0.36161 t`, because `log t/t` is decreasing for `t >= e` and equals
  `2.22033/9.2103 <= 0.24107` at `t = 9.2103`, and `1.5 * 0.24107 = 0.361605`;
- `(3/2) log beta(t) <= 1.5 * 0.18393 = 0.275895 <= 0.03 t`, since `0.03 * 9.2103 >= 0.2763`.

Adding, `((L+3)/2) log((L+3)/2) <= (t log t)/(2 lambda) + 0.58273 t`, and with (8.6)

```
log R_c(N)  >=  t^2/(4 lambda) - (t log t)/(2 lambda) - (0.58273 + 6.9039) t
            >=  t^2/(4 lambda) - (t log t)/(2 lambda) - 7.5 t,
```

which is T5. ∎

**Uniformity.** `a`, `c`, `M` and `X` are functions of `N` alone and every step is an
inequality valid at each `N >= 10000` — no subsequence, no averaging, no choice depending
on `N` beyond those four. So T5 holds at every integer `N >= 10000`, which is what C5
needs in order to bound the liminf.

**Proof of C5.** Dividing T5 by `t^2 = (log N)^2`, for `N >= 10000`

```
log R_c(N)/(log N)^2  >=  1/(4 lambda) - (log t)/(2 lambda t) - 7.5/t,
```

and both correction terms tend to `0`, so `liminf >= 1/(4 lambda)`. T2's consequence gives
`limsup <= 1/(4 lambda)`. A liminf at least as large as the limsup forces equality and the
existence of the limit. ∎

**The threshold is honest but the inequality is still vacuous at computable `N`.** The
right-hand side of T5 is negative until `t ≈ 20.475`, i.e. `N ≈ 7.8 * 10^8`. That is a
long way past the range where `R_c(N)` has been computed exactly, though nearer than T3's
`5.3 * 10^{10}`. As with T3, §8.7 confronts the *construction* with the exact values, not
this inequality.

### 8.6 Where route L2a stopped

L2a was attempted first and did not close. Its plan (§4.4) is to replace the contiguous
reserved block by a sparse reserved set and to correct residues hierarchically, coarsest
scale first, so that each reserved place absorbs only a residue of its own magnitude. The
statement it needs, and that could not be established, is:

> for a free family that is a **product** `prod_k {0, ..., m_k}` over the non-reserved
> places, the residue left after the free digits are chosen can be driven to zero by the
> reserved digits alone, without any digit exceeding its cap.

The obstruction is not the carry's termination, which is where §4.4 expected it to be. It
is upstream of that. In a product family the free digits are chosen independently of `N`,
so after they are chosen the residue is an arbitrary integer of `[0, N]` — the hierarchy
of scales never gets started, because there is no first scale at which the residue is
already small. Making the residue small at each scale requires choosing the free digits
greedily against `N`, and greedily-chosen digits are no longer a product: the number of
admissible choices at each place then depends on the choices already made, so the count is
no longer `prod (m_k + 1)` and has to be tracked through the adaptation.

Tracking the count through an adaptive choice at every place is precisely what Lemma F
does — its `D_a(m)` **is** the set of admissible top digits given the residue, and the
recursion (8.1) is the tracking. So the repair of L2a is not a sparse reserved set at all;
it is to stop reserving places and count the choices instead, at every place rather than
at a sparse subset. That is route L2b, and it is why L2a was not pursued further once
L2b closed. Whether a genuinely sparse variant also works is not settled here, and
nothing above shows that it cannot.

### 8.7 Numerical confrontation

The construction of §8.3, evaluated directly with the *proved* block factor `G(a)` of
Lemma F rather than with the true band minimum of `B(a, ·)`, is
`capfib.lower.t5_lower_bound`. At the
largest verified value, `N` = 1000000 {fig:n-max-verified}, it gives 39.802
{fig:t5-lower-nmax} against the exact `log R_c(N)` of 68.3632 {fig:log-rc-nmax}, with a
block boundary at place 16 {fig:t5-block-nmax}; of that total, 24.765
{fig:t5-log-block-nmax} is the block factor — the part L1 discards, and on its own already
larger than L1's whole bound of 17.774 {fig:t3-lower-nmax}. It stayed at or below the
exact value at each of the 37 sampled `N` and exceeded it at none of them; the run gate in
`scripts/run_phase2.py` refuses to write anything if it ever does.

Three further checks are in `tests/test_phase2_bounds.py`, all against exact enumeration
rather than against the formulas they are testing:

- Lemma F's closed form is checked against the exact band minimum of `B(a, ·)`, computed
  by DP by `capfib.lower.block_band_min`, for `a` = 8 to 16 — the same range the sharpness
  remark of §8.2 measures its slope over. That DP is itself pinned twice: against an
  independent direct-convolution implementation for `a` = 2 to 11, and against
  `capfib.brute`, the package's standard oracle, for `a` = 2 to 6.
- (8.2), the step everything rests on, is checked exhaustively — at every integer of the
  band, for `a` = 2 to 13, not at sampled residues.
- §8.3's cap, budget and band conditions are checked at four values of `N` up to `10^6`.

A fourth check enumerates the construction itself, element by element, at each `N` from 3
to 219 (at `N = 2` the counting block is empty and the construction is not defined):
`test_t5_construction_enumerates_to_valid_distinct_representations` in
`tests/test_phase2_bounds.py` builds every element — a fixup on the block together with a
free tuple on the counting block — and requires each to be a digit sequence respecting
every cap and evaluating to `N`, with its block residue inside the flat band; requires the
elements to be pairwise distinct; and requires their number to be at least the proved
bound `exp(t5_lower_bound(N).log_count)` and at most the brute-force `R_c(N)`. It is
marked `slow` (~45 s, nearly all of it the oracle) and runs with the rest of the suite.
This is a check over `N <= 219`, which is where exhaustive enumeration stops being cheap;
the validity of the construction for larger `N` is what §8.3 argues, not what this
measures.

### 8.8 What is not claimed

**C5 does not make T2 sharp in the secondary term.** T5 and T2's effective form of §3.6
sandwich `log R_c(N)` between `t^2/(4 lambda) - (t log t)/(2 lambda) - 7.5 t` and
`t^2/(4 lambda) - (t log t)/(2 lambda) + O(t)`, so the first two terms agree; but T2's
`O(t)` is not made explicit anywhere in this note, and no attempt is made here to pin the
`O(t)` term from either side.

**Lemma F is not a local limit theorem.** It bounds `B(a, m)` from below by
`exp(lambda a^2/2 - O(a))` on the band, which is `exp(-O(a))` times the total mass. It says
nothing about `B(a, m)` from above, nothing about the shape of `B(a, ·)`, and nothing at
all outside the band — in particular `B(a, 0) = 1`, so no bound of this kind can hold on
all of `[0, S_a]`.

**The fluctuation objection of §4.4 is answered, not refuted.** That paragraph observed
that `R_c` has 49.6% decreasing steps over N <= 1000000 ({claim:rc-not-monotone}), so an
inner bound holding on average need not hold at a given residue. Lemma F does not
contradict that measurement: it is a bound holding uniformly across the band rather than
on average over it, and it is coarse enough — `exp(-O(a))` below the mean — that
fluctuations of the measured size pass under it untouched.

**What the ledger now records, and what this note does not decide.** The promotion was
made after two independent reviews of §8, not as a side effect of writing it.
`{claim:leading-constant}` is now a `theorem`, its statement being C5 and its evidence
this section; `{claim:sandwich-bounds}` remains a `theorem`, stating C4, with a note that
C5 supersedes its lower half by a different construction while C4 itself stays true;
`{claim:saddle-tightness}` moved from `heuristic` to `theorem`, because T1, T2 and T5
together force the saddle-point correction to be `O(t)`, which is more than the
`o((log N)^2)` that claim asserts — the `t^2` and `t log t` terms cancel between T2's
effective form and T5. What this note still does not decide is the constant in front of
that `t`: T2's `O(t)` is nowhere made explicit, T5's is `-7.5 t`, and the two do not meet.
That gap is left open in the ledger as `{claim:saddle-correction-constant}`, and it is the
same gap as the `c_2` of research question (B).

Nothing in §§1–7 was weakened: T3 and C4 are left exactly as proved. T5 does not use T3 as
a step — the appendix table records that — but it reuses T3's machinery, the
block/counting split and the completeness lemma, and a reader tracking where the factor of
two went needs both halves in view.

**The weakest step, named.** It is Step 2 of Lemma F — the four-case table and the
integer count (8.2). Everything else in T5 is bookkeeping over inequalities of the kind
§4 already uses; that step is the only genuinely new inference, it is where an
off-by-one or a missed case would be invisible in the algebra, and cases 2 and 3 exist
only because the naive version (assuming `[d_lo, d_hi] ⊆ [0, F_a]`) is false near the
band edges. It is checked exhaustively rather than at samples for that reason.

---

## Appendix — proof dependencies

| Result | Depends on |
|---|---|
| T1 | non-negativity of `[x^n] F_c` only |
| T2 | (H1), (H2), `(F1)`, `(F2)`, and T1 for the consequence |
| T3 | `{claim:sum-of-squares}`, `{claim:completeness-no-gaps}` (Lean: `exists_numeral_of_le`), `(F1)` |
| C4 | T2, T3 |
| Lemma F (§8.2) | `{claim:sum-of-squares}`, `{claim:completeness-no-gaps}` (Lean: `exists_numeral_of_le`), `(F1)` |
| T5 | Lemma F, `(F1)`; not on T3 |
| C5 | T2, T5 |

Nothing in T1–T5 depends on the CKL citation, on `countReps_le_uncapped`, or on any
numerical result. §6 is confrontation, not evidence: no constant in §§2–5 was derived
from data.
