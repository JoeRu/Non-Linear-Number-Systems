/-
  NonLinearNumberSystems.Completeness
  ===================================
  The system represents every integer in [0, F_n · F_{n+1}] without gaps.

  Two results live here:

  * `sum_sq_place` — the identity `∑_{k ≤ n} F_k² = F_n · F_{n+1}`, which fixes
    the range of values an `n`-place numeral can take. Mathlib has a good deal
    of Fibonacci theory (`Mathlib.Data.Nat.Fib.Basic`) but not this identity,
    so it is proved here. It holds only under the convention F 1 = F 2 = 1.

  * `exists_numeral_of_le` — completeness itself. Follows from the
    Kempner–Fraenkel condition `u_k ≤ 1 + ∑_{j<k} m_j u_j`, which here reads
    `F_k ≤ 1 + F_{k-1} · F_k` and holds with enormous slack. That slack is
    exactly the system's redundancy.

  Reference: Fraenkel, "Systems of Numeration", Amer. Math. Monthly 92 (1985);
  theory/01-background.md §3.
-/

import NonLinearNumberSystems.Numeration

namespace NonLinearNumberSystems

open Finset

/-- `∑_{k ≤ n} F_k² = F_n · F_{n+1}`. Fixes the range of representable values.

    Not in Mathlib; proved by induction using `Nat.fib_add_two`. -/
theorem sum_sq_place (n : ℕ) :
    ∑ k ∈ range n, place (k + 1) * place (k + 1) = place n * place (n + 1) := by
  induction n with
  | zero => simp [place]
  | succ m ih =>
    rw [Finset.sum_range_succ, ih, place_add_two]
    ring

/-- The largest value an `n`-place numeral can take. -/
lemma value_le_sum_sq {n : ℕ} (d : Numeral n) :
    d.value ≤ ∑ k ∈ range n, place (k + 1) * place (k + 1) := by
  classical
  have : d.value ≤ ∑ i : Fin n, place (i.val + 1) * place (i.val + 1) := by
    refine Finset.sum_le_sum ?_
    intro i _
    exact Nat.mul_le_mul_right _ (d.capped i)
  simpa [Finset.sum_range fun k => place (k + 1) * place (k + 1)] using this

/-- **Completeness.** Every integer up to `∑ F_k²` has a representation.

    The greedy algorithm succeeds because the Kempner–Fraenkel condition holds
    with slack; formalising the greedy descent is the remaining work. -/
theorem exists_numeral_of_le (n N : ℕ)
    (h : N ≤ ∑ k ∈ range n, place (k + 1) * place (k + 1)) :
    ∃ d : Numeral n, d.value = N := by
  sorry  -- greedy descent on n, using sum_sq_place for the induction bound

end NonLinearNumberSystems
