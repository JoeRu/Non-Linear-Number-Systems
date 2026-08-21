/-
  NonLinearNumberSystems.Theorems
  ===============================
  Index of the formal development, and the open statements.

  Importing this file gives everything.

  ## What is proved

  * `place_add_two`          — the place values satisfy the Fibonacci recurrence
  * `sum_sq_place`           — `∑_{k ≤ n} F_k² = F_n · F_{n+1}` (not in Mathlib)
  * `value_le_sum_sq`        — an `n`-place numeral cannot exceed that bound
  * `exists_numeral_of_le`   — completeness: every `N` up to that bound is
                                represented, by greedy descent
  * `exists_two_numerals_same_value` — **"1 > 1"**: two distinct numerals share
                                a value, because F 1 = F 2 = 1
  * `value_not_injective`    — the evaluation map is not injective
  * `countReps_le_uncapped`  — `R_c(N) ≤ R_u(N)`: capping digits cannot create
                                representations, so the capped count is bounded
                                by the uncapped one. Not a step of the Phase 2
                                upper bound, which is proved directly and is
                                sharper; this supports only the comparison
                                against Coons–Kristensen–Laursen.

  ## What is open

  Nothing. The Lean development contains no `sorry`.

  Any statement added here without a proof carries a `sorry` and a proof
  sketch, and is listed in this section until it is discharged. A `sorry` is a
  statement; replacing one with a wrong proof is worse than leaving it open.

  ## What is deliberately NOT here

  Zeckendorf's theorem — Mathlib proves it (`Nat.zeckendorfEquiv` in
  `Mathlib.Data.Nat.Fib.Zeckendorf`). See `Redundancy.lean`, which cites it
  rather than re-deriving it.

  The asymptotics of `R_c(N)` — Mellin transforms and the analytic continuation
  of ζ_F are far outside what Mathlib makes practical. Those live in `paper/`
  and are tracked in `theory/claims.yaml`.
-/

import NonLinearNumberSystems.Numeration
import NonLinearNumberSystems.Completeness
import NonLinearNumberSystems.Redundancy
import NonLinearNumberSystems.Bounds

namespace NonLinearNumberSystems

/- Sanity checks on the convention: F 1 = F 2 = 1, F 3 = 2, F 4 = 3, F 5 = 5. -/
example : place 1 = 1 := rfl
example : place 2 = 1 := rfl
example : place 3 = 2 := rfl
example : place 4 = 3 := rfl
example : place 5 = 5 := rfl

/- The identity that fixes the completeness range, at n = 4:
   1 + 1 + 4 + 9 = 15 = F 4 · F 5 = 3 · 5. -/
example : ∑ k ∈ Finset.range 4, place (k + 1) * place (k + 1) = 15 := by decide

end NonLinearNumberSystems
