# Phase 0.5 — Constant Gate

**Question.** Which of the candidate leading constants does `log R_c(N)` follow?

**Method.** `log R_c(N) <= min_s [ s N + log F_c(e^-s) ]`, evaluated by ternary
search on `log s` with the generating function computed in pure log space. The
leading `(log N)^2` coefficient of the Legendre transform is the leading
coefficient of `log R_c(N)`; the correction is of lower order. The estimator is
the local slope `d(log R)/d((log N)^2)`, because the plain ratio converges too
slowly to separate the candidates.

**Result.** See `data/phase0_5_gate.csv` and `figures/phase0_5_gate.png`. The
local slope rises monotonically and approaches `1/(4 log phi) = 0.519522`,
decisively excluding `1/(2 log phi) = 1.039` and `1/(8 log phi) = 0.260`.

**Reading.** This supports the roadmap's Phase 3 conjecture
{claim:leading-constant}. The `1/(8 log phi)` figure obtainable from the §4
count of `theory/01-background.md` is a lower bound only — that count fixes the
numeral length at `n`, which undercounts `R_c(N)`.

**Status.** Numerical support for a conjecture. Not a proof. Phase 3 must still
derive the constant from the saddle-point heuristic, and Phase 5 must still
establish it rigorously.

**Consequence for the roadmap.** Phase 3 proceeds. Its job is now to explain a
measured number rather than to predict an unknown one.
