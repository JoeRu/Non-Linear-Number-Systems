# 03 — Invariants

Short proofs backing the `theorem`-status claims in `theory/claims.yaml` that
are not simply cited from the literature (`theory/01-background.md` covers
those). Kept separate from the numerical corroboration in the test suite:
tests check that code respects these facts, they do not establish them.

## sum-of-squares

**Claim.** `sum_{k<=n} F_k^2 = F_n * F_{n+1}` for `n >= 1`, under the
`F_1 = F_2 = 1` convention (`theory/00-definitions.md`).

**Proof.** By induction on `n`. Base case `n = 1`: `F_1^2 = 1 = F_1 F_2`.
Inductive step: assume `sum_{k<=n} F_k^2 = F_n F_{n+1}`. Then
`sum_{k<=n+1} F_k^2 = F_n F_{n+1} + F_{n+1}^2 = F_{n+1}(F_n + F_{n+1})
= F_{n+1} F_{n+2}`, using the Fibonacci recurrence `F_{n+2} = F_{n+1} + F_n`.
This is the classical identity; it is stated here only because the
`sum-of-squares` claim needs a checkable location, not because it is novel.

## gf-global-checksum

**Claim.** For the fixed-length system on places `F_1, ..., F_n`, the array
`counts` indexed by achievable value `N` satisfies
`sum_N counts[N] == prod_k (F_k + 1)`.

**Proof.** A digit tuple `(d_1, ..., d_n)` with `0 <= d_k <= F_k` is drawn
from a product of `n` finite ranges, so there are exactly
`prod_k (F_k + 1)` such tuples. The map `(d_1, ..., d_n) -> sum_k d_k F_k`
sends each tuple to the single value `N = counts` is built to enumerate, and
`counts[N]` is defined as the number of tuples landing on `N`. Since every
tuple lands on exactly one `N` (the sum is a function of the tuple, not a
relation), summing `counts[N]` over all `N` counts every tuple exactly
once — no tuple is omitted (every tuple has a well-defined sum) and none is
counted twice (a tuple has only one sum). Hence
`sum_N counts[N] = (number of tuples) = prod_k (F_k + 1)`. This is a
counting identity about the fixed-length array; it says nothing about
whether any individual `counts[N]` is correct, which is why it is a
sum-preserving-blind regression check (`tests/test_checksum.py`) rather than
a licence to report values (see the Phase 1 design spec, §3.2).

## sc-monotone

**Claim.** `S_c(N) = sum_{n <= N} R_c(n)` is non-decreasing in `N`.

**Proof.** `R_c(n)` is a cardinality — the number of digit tuples summing to
`n` — so `R_c(n) >= 0` for every `n >= 0`. Then
`S_c(N+1) - S_c(N) = R_c(N+1) >= 0`, so `S_c(N+1) >= S_c(N)` for all `N`.
Non-decreasing follows by definition of the partial sums of a non-negative
sequence; no bound on `N` is needed.
