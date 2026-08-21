# Phase 1 — Exact Computation of R_c(N)

**Question.** What does `R_c(N)` actually look like at computable scale, and
which of Phase 5's routes does its behaviour select?

**Method.** Exact integer computation for `N <= 10^6` via the closed-form
generating-function recurrence, with every coefficient in that range
cross-checked against an independently implemented digit-loop DP — two
independent counting algorithms
(`dp` and `gf`; `brute` too) run over a shared, separately-tested place set
(`places_up_to` in `capfib/fib.py`, pinned by boundary tests in
`tests/test_fib.py`). A wrong place set would be invisible to the cross-check
by construction. Reported values are licensed by that full-range agreement
{claim:dp-gf-agree-to-nmax} (`dp==gf pointwise for all N <= 1000000`), not by
a global checksum — see the design spec section 3 for why the checksum is
insufficient. The same run recorded `gf` at 8.7 s, `dp` at 286.9 s, and peak
RSS 273 MB (whole-process, i.e. covering `gf` and `dp` together, which is what
the script measures); these are environment-qualified observations from that
one recorded run — nothing pins the machine, OS, Python build, or dependency
versions (`pyproject.toml` states only lower bounds) — not reproducible
performance figures.

**What Phase 1 is not.** It does not measure the leading asymptotic constant.
Phase 0.5 already did that at `N = 10^3200`. At `N = 10^6`, `R_c(10^6) =
489526578056005407591009119276` (99 bits), so `log R_c(10^6) = 68.36` and the
ratio `log R_c(N)/(log N)^2` is `0.3582` against a limit near `0.5195` —
squarely pre-asymptotic. Fitting the four-term expansion here would report the
pre-asymptotic regime convincingly and wrongly.

**Result 1 — R_c fluctuates.** Over `N <= 1000000` the census records 504441
increasing steps, 11 flat steps and 495548 decreasing steps out of 1000000
steps — **49.6% of steps are decreasing** {claim:rc-not-monotone}. Roadmap
Phase 0 left this question open and made Phase 5's route depend on it: a
census this fluctuating over the observed range motivates working with the
summatory function `S_c` rather than `R_c` directly, and makes `S_c` the
safer numerical target for a Tauberian argument. **This constrains Route B,
it does not select it:** the fluctuation observed here makes a Tauberian
attack on the leading asymptotic safer to run through `S_c(N)` than through
`R_c(N)` directly; Route A remains the primary route for the rigorous
asymptotic theorem (see `docs/roadmap.md`, Phase 5). `S_c` is non-decreasing
{claim:sc-monotone}, and
the fluctuation figure (`figures/phase1_fluctuation.png`) shows the contrast
directly against the growth curve (`figures/phase1_growth.png`).

*Structural note.* Exactly 11 flat steps occur over `N <= 10^6`
(`data/phase1_summary.json`, `census` and `flat_step_positions` fields), at
`N = 2, 7, 12, 15, 20, 28, 33, 36, 57, 67, 78` -- the largest being `N = 78`
{claim:flat-steps-end-early}. This is recorded as the observation it is;
Phase 1 does not speculate about why.

*Quantiles of the step ratio.* `data/phase1_summary.json` records
`fluctuation_quantiles` for `R_c(N+1)/R_c(N)` over `N <= 10^6`: min `0.9853`,
p25 `0.9984`, median `1.0000`, p75 `1.0016`, max `2.0`. Each of these is the
order statistic recorded by the script — the sorted-ratio array indexed at
`len(srt)//4` etc., not a claim about the exact proportion of steps on either
side (ties and integer-index rounding can make an "exactly a quarter" reading
false). The median sitting at essentially 1 with a p25 order statistic below
1 is direct, distribution-level evidence for the fluctuation finding above —
it is not just the binary increasing/flat/decreasing count that shows
fluctuation: the 25th-percentile order statistic is 0.9984, and the extremes
reach as low as 0.9853 and as high as 2.0.

**Result 2 — structure at place values.** The ratio `R_c(F)/R_c(F-1)` at each
distinct Fibonacci place `F <= 1000000`:

| place `F` | ratio `R_c(F)/R_c(F-1)` |
|---|---|
| 2 | 1.000000 |
| 3 | 1.500000 |
| 5 | 1.250000 |
| 8 | 1.333333 |
| 13 | 1.153846 |
| 21 | 1.137931 |
| 34 | 1.090909 |
| 55 | 1.070485 |
| 89 | 1.044832 |
| 144 | 1.034920 |
| 233 | 1.025770 |
| 377 | 1.020140 |
| 610 | 1.014472 |
| 987 | 1.010691 |
| 1597 | 1.008367 |
| 2584 | 1.006979 |
| 4181 | 1.005568 |
| 6765 | 1.004208 |
| 10946 | 1.003304 |
| 17711 | 1.002846 |
| 28657 | 1.002469 |
| 46368 | 1.001978 |
| 75025 | 1.001548 |
| 121393 | 1.001315 |
| 196418 | 1.001182 |
| 317811 | 1.001002 |
| 514229 | 1.000792 |
| 832040 | 1.000653 |

`R_c` jumps at each Fibonacci place, but the naive law is false: the ratio is
exactly 1.0 at `F = 2` and rises at `F = 3` and again at `F = 8`, decaying
monotonically only from `F = 13` onward, reaching 1.000653 at the largest
place in range {claim:place-jump-decay}. An earlier draft asserted decay
everywhere on the strength of a sample that began at `F = 13`.

**Result 3 — extremal N.** Argmax and argmin of `R_c` within each Fibonacci
block `[F, F')`, ties broken toward the smallest `N`:

| block `[lo, hi)` | argmax | max | argmin | min |
|---|---|---|---|---|
| [1, 2) | 1 | 2 | 1 | 2 |
| [2, 3) | 2 | 2 | 2 | 2 |
| [3, 5) | 4 | 4 | 3 | 3 |
| [5, 8) | 6 | 6 | 5 | 5 |
| [8, 13) | 11 | 13 | 8 | 8 |
| [13, 21) | 19 | 29 | 13 | 15 |
| [21, 34) | 32 | 77 | 21 | 33 |
| [34, 55) | 53 | 229 | 34 | 84 |
| [55, 89) | 87 | 808 | 55 | 243 |
| [89, 144) | 142 | 3270 | 89 | 839 |
| [144, 233) | 231 | 15898 | 144 | 3349 |
| [233, 377) | 375 | 90760 | 233 | 16121 |
| [377, 610) | 608 | 625773 | 377 | 91426 |
| [610, 987) | 985 | 5165815 | 610 | 627378 |
| [987, 1597) | 1595 | 51721824 | 987 | 5163510 |
| [1597, 2584) | 2582 | 629077676 | 1599 | 51538131 |
| [2584, 4181) | 4179 | 9315346376 | 2586 | 625735867 |
| [4181, 6765) | 6763 | 169156631839 | 4183 | 9258771395 |
| [6765, 10946) | 10944 | 3756243755226 | 6767 | 168107456426 |
| [10946, 17711) | 17709 | 102878431002127 | 10948 | 3733679244600 |
| [17711, 28657) | 28655 | 3462244951258511 | 17713 | 102305070921770 |
| [28657, 46368) | 46366 | 144183184789074435 | 28659 | 3444673128390741 |
| [46368, 75025) | 75023 | 7412554460121150564 | 46370 | 143531085567658909 |
| [75025, 121393) | 121391 | 472505449469124341719 | 75027 | 7382943442290721387 |
| [121393, 196418) | 196416 | 37336443834494397654386 | 121395 | 470856860021729586305 |
| [196418, 317811) | 317809 | 3663199405522131720967230 | 196420 | 37223323185940462824302 |
| [317811, 514229) | 514227 | 447011053723657655159723062 | 317813 | 3653612162743972195432946 |
| [514229, 832040) | 832038 | 67818682314307972010462530933 | 514231 | 446005217902628828758934222 |
| [832040, 1000001)\* | 999998 | 489947064206166830167042650942 | 832042 | 67687720957357242027785749964 |

\*Truncated by `n_max`: the next Fibonacci place is `1346269`, so this row
covers only `[832040, 1000000]`, not the full block `[832040, 1346269)`, and
should not be read as a complete block like the rows above it.

Progress on open problem 2 {claim:block-extremal-n}.

**Limits.** Every result is a numerical observation over `N <= 10^6`. None is a
theorem about all `N`, and none is recorded as one. The fluctuation finding
constrains Phase 5 Route B on the strength of what Phase 1 actually measured;
it is not itself a theorem about `R_c` at arbitrary `N`.
