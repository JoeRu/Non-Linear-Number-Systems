/-
  NonLinearNumberSystems.Completeness
  ===================================
  The system represents every integer in [0, F_n · F_{n+1}] without gaps.

  Two results live here:

  * `sum_sq_place` — the identity `∑_{k ≤ n} F_k² = F_n · F_{n+1}`, which fixes
    the range of values an `n`-place numeral can take. Mathlib has a good deal
    of Fibonacci theory (`Mathlib.Data.Nat.Fib.Basic`) but not this identity,
    so it is proved here. It holds only under the convention F 1 = F 2 = 1.

  * `exists_numeral_of_le` — completeness itself, by greedy descent on the
    number of places. At `n + 1` places the top digit `min (F_{n+1}) (N / F_{n+1})`
    takes as much of `N` as the top place's cap allows, and `greedy_residue_le`
    shows the residue always lies within the capacity of the remaining `n`
    places, so the induction hypothesis represents it. This is a direct
    induction, not an invocation of the classical Kempner–Fraenkel condition
    `u_k ≤ 1 + ∑_{j<k} m_j u_j` — that condition's usual statement assumes
    strictly increasing place values `u_1 < u_2 < …`, which `F_1 = F_2 = 1`
    does not satisfy. See theory/01-background.md §3 for the prose version of
    this argument.

  Reference (for the general completeness condition, not for this proof):
  Fraenkel, "Systems of Numeration", Amer. Math. Monthly 92 (1985).
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

/-- Positivity of the place values, in the form the greedy step needs.

    Same fact as `one_le_place` in `Redundancy.lean`, restated here so that
    `Completeness` keeps depending only on `Numeration`. -/
private lemma place_succ_pos (n : ℕ) : 0 < place (n + 1) :=
  Nat.fib_pos.2 (Nat.succ_pos n)

/-- **The greedy step.** Taking the top digit as large as the cap and the value
    allow leaves a residue that the remaining `n` places can still absorb.

    Two cases, on whether `N` reaches the top place's full contribution `F_{n+1}²`:

    * `N ≥ F_{n+1}²` — the digit saturates at the cap `F_{n+1}`, and the residue
      is `N - F_{n+1}² ≤ (C_n + F_{n+1}²) - F_{n+1}² = C_n`.
    * `N < F_{n+1}²` — the digit is `N / F_{n+1}`, below the cap, so the residue
      is exactly `N % F_{n+1} < F_{n+1}`. By `sum_sq_place` the remaining
      capacity is `C_n = F_n · F_{n+1}`, which is `≥ F_{n+1}` once `n ≥ 1`. For
      `n = 0` the divisor is `F_1 = 1`, so the residue is `0 = C_0`. -/
lemma greedy_residue_le (n N : ℕ)
    (h : N ≤ ∑ k ∈ range (n + 1), place (k + 1) * place (k + 1)) :
    N - min (place (n + 1)) (N / place (n + 1)) * place (n + 1)
      ≤ ∑ k ∈ range n, place (k + 1) * place (k + 1) := by
  have hpos : 0 < place (n + 1) := place_succ_pos n
  rw [Finset.sum_range_succ] at h
  rcases Nat.lt_or_ge N (place (n + 1) * place (n + 1)) with hlt | hge
  · -- The greedy digit `N / F_{n+1}` stays under the cap; the residue is `N % F_{n+1}`.
    have hdiv : N / place (n + 1) < place (n + 1) := (Nat.div_lt_iff_lt_mul hpos).2 hlt
    rw [min_eq_right hdiv.le]
    -- The residue fits in the remaining capacity `C_n = F_n · F_{n+1}`.
    have hmodle : N % place (n + 1) ≤ ∑ k ∈ range n, place (k + 1) * place (k + 1) := by
      rw [sum_sq_place]
      cases n with
      | zero => simp [place, Nat.mod_one]
      | succ m =>
        exact (Nat.mod_lt _ hpos).le.trans (Nat.le_mul_of_pos_left _ (place_succ_pos m))
    refine Nat.sub_le_iff_le_add.2 ?_
    calc N = N / place (n + 1) * place (n + 1) + N % place (n + 1) :=
          (Nat.div_add_mod' N (place (n + 1))).symm
      _ ≤ N / place (n + 1) * place (n + 1)
            + ∑ k ∈ range n, place (k + 1) * place (k + 1) := Nat.add_le_add_left hmodle _
      _ = (∑ k ∈ range n, place (k + 1) * place (k + 1))
            + N / place (n + 1) * place (n + 1) := Nat.add_comm _ _
  · -- The greedy digit saturates at the cap `F_{n+1}`.
    have hdiv : place (n + 1) ≤ N / place (n + 1) := (Nat.le_div_iff_mul_le hpos).2 hge
    rw [min_eq_left hdiv]
    exact Nat.sub_le_iff_le_add.2 h

/-- **Completeness.** Every integer up to `∑ F_k²` has a representation.

    Greedy descent on the number of places. At `n + 1` places the top digit is
    `min (F_{n+1}) (N / F_{n+1})` — as much of `N` as the top place can carry
    without exceeding its cap — and `greedy_residue_le` says the residue still
    lies within the capacity of the lower `n` places, so the induction
    hypothesis represents it. `Fin.snoc` glues the top digit on.

    The greedy algorithm succeeds because the Kempner–Fraenkel condition holds
    with slack; here that slack is what makes both cases of `greedy_residue_le`
    go through. -/
theorem exists_numeral_of_le (n N : ℕ)
    (h : N ≤ ∑ k ∈ range n, place (k + 1) * place (k + 1)) :
    ∃ d : Numeral n, d.value = N := by
  induction n generalizing N with
  | zero =>
    simp only [Finset.range_zero, Finset.sum_empty, Nat.le_zero] at h
    subst h
    exact ⟨⟨fun i => i.elim0, fun i => i.elim0⟩, by simp [Numeral.value]⟩
  | succ m ih =>
    obtain ⟨d', hd'⟩ := ih _ (greedy_residue_le m N h)
    -- The top digit takes as much of `N` as the cap `F_{m+1}` permits.
    have hle : min (place (m + 1)) (N / place (m + 1)) * place (m + 1) ≤ N :=
      (Nat.mul_le_mul_right _ (min_le_right _ _)).trans (Nat.div_mul_le_self _ _)
    refine ⟨⟨Fin.snoc d'.digit (min (place (m + 1)) (N / place (m + 1))), ?_⟩, ?_⟩
    · intro i
      refine Fin.lastCases ?_ ?_ i
      · -- top place: the digit is a `min` against the cap, so it is capped
        rw [Fin.snoc_last, Fin.val_last]
        exact min_le_left _ _
      · -- lower places: the digits are `d'`'s, already capped
        intro j
        rw [Fin.snoc_castSucc, Fin.coe_castSucc]
        exact d'.capped j
    · have hv : ∑ i : Fin m, d'.digit i * place (i.val + 1)
          = N - min (place (m + 1)) (N / place (m + 1)) * place (m + 1) := hd'
      simp only [Numeral.value, Fin.sum_univ_castSucc, Fin.snoc_castSucc, Fin.snoc_last,
        Fin.coe_castSucc, Fin.val_last, hv]
      exact Nat.sub_add_cancel hle

end NonLinearNumberSystems
