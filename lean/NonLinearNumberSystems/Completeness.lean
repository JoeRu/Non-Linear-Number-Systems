/-
  NonLinearNumberSystems.Completeness
  ===================================
  The system represents every integer in [0, F_n * F_{n+1}] without gaps.

  Reference: Fraenkel, "Systems of Numeration", Amer. Math. Monthly 92 (1985);
  theory/01-background.md §3.
-/

/- NOTE: This file has not been compiled. `elan`/`lake` were unavailable in the
   environment where it was written, so its syntax and Mathlib API usage are
   unverified. Run `lake build` before relying on it. -/

import NonLinearNumberSystems.Numeration

namespace NonLinearNumberSystems

open Finset

/-- `∑_{k ≤ n} F_k² = F_n · F_{n+1}`. Fixes the range of representable values. -/
theorem sum_sq_place (n : ℕ) :
    ∑ k ∈ range n, place (k + 1) * place (k + 1) = place n * place (n + 1) := by
  sorry  -- induction on n; Nat.fib_add_two

/-- **Completeness.** Every integer up to `∑ F_k²` has a representation.
    Follows from the Kempner–Fraenkel condition `F_k ≤ 1 + F_{k-1} · F_k`,
    which holds here with large slack. -/
theorem exists_numeral_of_le (n N : ℕ)
    (h : N ≤ ∑ k ∈ range n, place (k + 1) * place (k + 1)) :
    ∃ d : Numeral n, d.value = N := by
  sorry  -- greedy algorithm; induction on n using sum_sq_place

end NonLinearNumberSystems
