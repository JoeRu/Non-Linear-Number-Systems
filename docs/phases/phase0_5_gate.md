# Phase 0.5 — Constant Gate

**Question.** Which of the candidate leading constants does `log R_c(N)` follow?

**Method.** `log R_c(N) <= min_s [ s N + log F_c(e^-s) ]`, evaluated by ternary
search on `log s` with the generating function computed in pure log space. If the
saddle-point correction is of lower order than `(log N)^2` — expected, but not
established here {claim:saddle-tightness} — the leading coefficient of the Legendre
transform is also the leading coefficient of `log R_c(N)`. The estimator is the local
slope `d(log R)/d((log N)^2)`, because the plain ratio converges too slowly to
separate the candidates.

**Result.** See `data/phase0_5_gate.csv` and `figures/phase0_5_gate.png`. The local slope rises
monotonically to **0.518710** at `N = 10^3200`, against `1/(4 log phi) = 0.519522` — an absolute
error of 0.000812, still decreasing {claim:gate-local-slope}.

**What this establishes, and what it does not.** `log_R_bound` computes
`min_s [sN + log F_c(e^-s)]`, which is a Chernoff *upper* bound on `log R_c(N)`. Its leading
coefficient therefore bounds `C_c` from above. That excludes `1/(2 log phi) = 1.039` outright:
`C_c` cannot exceed a bound measured at 0.5187. It does **not**, by itself, exclude a smaller
true constant such as `1/(8 log phi) = 0.260`. Excluding that additionally requires the
saddle-point correction to be of lower order than `(log N)^2`, so that the bound is tight to
leading order {claim:saddle-tightness}. That is standard for generating functions of this type
and is expected here, but it is not established in Phase 0.5 — establishing it is part of
Phase 5's rigorisation. The bound's looseness at reachable `N` is visible directly: at `N = 500`
the exact `log R_c` is 12.53 against a bound of 18.98.

**Reading.** This supports the roadmap's Phase 3 conjecture
{claim:leading-constant}. The `1/(8 log phi)` figure obtainable from the §4
count of `theory/01-background.md` is a lower bound only — that count fixes the
numeral length at `n`, which undercounts `R_c(N)`.

**Status, as of Phase 0.5.** Numerical support for a conjecture. Not a proof.
Phase 3 must still derive the constant from the saddle-point heuristic, and
Phase 5 must still establish it rigorously.

**Superseded in part (Phase 2).** Three of this page's caveats have since been
discharged, none of them by this page's own method:

- `{claim:leading-constant}` is no longer a conjecture. C5 of
  `docs/phases/phase2_bounds.md` §8 proves that the limit exists and equals
  `1/(4 log phi)`, elementarily and without a saddle point.
- `{claim:saddle-tightness}` is no longer a heuristic; it is a `theorem`,
  forced by T1, T2 and T5 together. Where this page says it is "expected, but
  not established here", the second half is still an accurate statement about
  Phase 0.5 and the first is now an understatement.
- Excluding `1/(8 log phi)` no longer requires either. C5 excludes it
  unconditionally, so the conditional framing above — correct when written — is
  no longer the reason that value is out.

What is **not** superseded is the finer question the secondary term needs. The
correction's *order* is settled — Phase 2 gives `O(log N)` — but its coefficient
in `log N` is not, and that coefficient is what a secondary term needs
({claim:saddle-correction-constant}, open). Everything above is left as written,
because it records what Phase 0.5 itself established, which is unchanged — a
measurement is not a proof, and was not one then either. What Phase 2 removes is
the *outstanding* task, not the caveat: Phase 3's job is still to *explain* the
constant from the saddle point rather than to establish it.

**Consequence for the roadmap.** Phase 3 proceeds. Its job is now to explain a
measured number rather than to predict an unknown one.
