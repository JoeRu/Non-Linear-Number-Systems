/-
  NonLinearNumberSystems.Bounds
  =============================
  Elementary bounds on the counting function. Phase 2 targets.

  The asymptotic theorems of Phases 5 and 6 are NOT Lean targets -- Mellin
  transforms and analytic continuation of ζ_F are far outside what Mathlib
  makes practical. Those live in paper/.
-/

/- NOTE: This file has not been compiled. `elan`/`lake` were unavailable in the
   environment where it was written, so its syntax and Mathlib API usage are
   unverified. Run `lake build` before relying on it. -/

import NonLinearNumberSystems.Numeration

namespace NonLinearNumberSystems

/-- `R_c n N` -- the number of length-`n` numerals with value `N`. -/
noncomputable def countReps (n N : ℕ) : ℕ :=
  Nat.card {d : Numeral n // d.value = N}

/-- Capping digits cannot increase the number of representations. -/
theorem countReps_le_uncapped (n N : ℕ) :
    countReps n N ≤ Nat.card {f : Fin n → ℕ // ∑ i, f i * place (i.val + 1) = N} := by
  sorry  -- the inclusion of capped into uncapped digit functions is injective

end NonLinearNumberSystems
