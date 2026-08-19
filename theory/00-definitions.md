# 00 — Definitions and Conventions

The Phase 0 deliverable. Everything downstream depends on this file.

## Fibonacci convention

`F_1 = 1, F_2 = 1, F_3 = 2, F_4 = 3, F_5 = 5, F_6 = 8, F_7 = 13, F_8 = 21, F_9 = 34, F_10 = 55`

The duplicated 1-place is deliberate and load-bearing {claim:convention-duplicated-place}.
Defined in code exactly once, in `capfib/fib.py`.

## Counting functions

- `R_c(N)` — the number of sequences `(d_k)` with `0 <= d_k <= F_k` and `sum_k d_k F_k = N`.
  The index `k` ranges over **all** places with `F_k <= N` {claim:place-range}.
- `R_u(N)` — as above with `d_k` unbounded (Coons–Kristensen–Laursen 2023).
- `b(N)` — the binary partition function (Mahler 1940, de Bruijn 1948).

## Generating function

`sum_N R_c(N) x^N = prod_k ( 1 + x^{F_k} + ... + x^{F_k F_k} )
                  = prod_k ( x^{F_k(F_k+1)} - 1 ) / ( x^{F_k} - 1 )`

## Research questions

- **(A)** Does `C_c` exist with `log R_c(N) ~ C_c (log N)^2`?
- **(B)** `log R_c(N) = C_c (log N)^2 + c_1 log N loglog N + c_2 log N + osc + o(1)`?
- **(C)** If oscillations exist, are they periodic in `log_phi N`, and with what period?

Primary focus: (A) and (B). (C) is deferred to Phase 6.

## Status of the anchors

| Statement | Status |
|---|---|
| `log R_u(N) ~ (log N)^2 / (2 log phi)` | theorem, cited (CKL 2023) |
| Completeness: no gaps on `[0, sum F_k^2]` | theorem {claim:completeness-no-gaps} |
| `sum_{k<=n} F_k^2 = F_n F_{n+1}` | theorem {claim:sum-of-squares} |
| `C_c = 1 / (4 log phi)` | conjecture {claim:leading-constant} |
| Oscillation structure | open |
