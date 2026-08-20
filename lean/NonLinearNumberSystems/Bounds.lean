/-
  NonLinearNumberSystems.Bounds
  =============================
  The counting function and its elementary bounds. Phase 2 targets.

  `countReps n N` is `R_c(N)` restricted to `n` places — the quantity the
  numerics package computes and whose asymptotics the project is after.

  Note the restriction: fixing the length at `n` *undercounts* `R_c(N)`, which
  ranges over every place with `F_k ≤ N`. For `N ≤ F_n · F_{n+1}` the two agree
  only once `n` is large enough to cover all such places. The numerics side
  handles this by defaulting to `places_up_to N` (see `capfib/fib.py`); here the
  length is explicit so the statements stay finite.

  The asymptotic theorems of Phases 5 and 6 are NOT Lean targets — Mellin
  transforms and analytic continuation of ζ_F are far outside what Mathlib
  makes practical. Those live in paper/.
-/

import NonLinearNumberSystems.Numeration

namespace NonLinearNumberSystems

/-- `R_c(N)` restricted to `n` places: the number of length-`n` numerals of
    value `N`. -/
noncomputable def countReps (n N : ℕ) : ℕ :=
  Nat.card {d : Numeral n // d.value = N}

/-- Digit functions with no cap at all — the `R_u(N)` of the roadmap. -/
noncomputable def countRepsUncapped (n N : ℕ) : ℕ :=
  Nat.card {f : Fin n → ℕ // ∑ i, f i * place (i.val + 1) = N}

/-- **Trivial upper bound (Phase 2).** Capping digits cannot create
    representations, so `R_c(N) ≤ R_u(N)`.

    Proof sketch: `fun d => d.digit` injects capped numerals into unrestricted
    digit functions of the same value. Formalising it needs the finiteness of
    the uncapped fibre, which holds because every place value is at least 1, so
    each digit is bounded by `N`. -/
theorem countReps_le_uncapped (n N : ℕ) :
    countReps n N ≤ countRepsUncapped n N := by
  sorry  -- injection `Numeral.digit`, plus finiteness of the uncapped fibre

end NonLinearNumberSystems
