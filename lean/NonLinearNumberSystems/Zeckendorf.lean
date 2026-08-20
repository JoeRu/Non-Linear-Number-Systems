/-
  NonLinearNumberSystems.Zeckendorf
  ==================================
  Theorems about Fibonacci partitions and their capacity-constrained variants.

  References:
  · Zeckendorf (1972): every positive integer has a unique representation as a
    sum of non-consecutive Fibonacci numbers.
  · Klosinski (1977), Fraenkel–Klein–Fraenkel (1995): capacity-constrained
    variants and their counting functions.
-/

import NonLinearNumberSystems.Basic
import Mathlib.Tactic

namespace NonLinearNumberSystems

open Nat

/-! ## Zeckendorf's Theorem (Statement) -/

/-- A representation is *Zeckendorf* if its index list is strictly increasing
    and contains no two consecutive indices. -/
def IsZeckendorf (rep : Representation n 1) : Prop :=
  rep.indices.Sorted (· < ·) ∧
  ∀ i j, i ∈ rep.indices → j ∈ rep.indices → j = i + 1 → False

/-- **Zeckendorf's Theorem (existence):** every positive integer has at least one
    Zeckendorf representation. -/
theorem zeckendorf_exists (n : ℕ) (hn : 0 < n) :
    ∃ rep : Representation n 1, IsZeckendorf rep := by
  sorry  -- proof by strong induction on n; to be formalised

/-- **Zeckendorf's Theorem (uniqueness):** every positive integer has at most one
    Zeckendorf representation (up to reordering of the index list). -/
theorem zeckendorf_unique (n : ℕ) (r₁ r₂ : Representation n 1)
    (h₁ : IsZeckendorf r₁) (h₂ : IsZeckendorf r₂) :
    r₁.indices.toFinset = r₂.indices.toFinset := by
  sorry  -- classical uniqueness argument

/-! ## Capacity-Constrained Representations -/

/-! The *representation number* R(n, c) counts distinct multisets of Fibonacci
    indices (with capacity ≤ c) that sum to n.
    This satisfies recurrences analogous to the Fibonacci sequence itself.

    (A `/-- … -/` doc comment must attach to a declaration; this is prose about
    the section, so it is a `/-! … -/` section comment.) -/

/-- Base cases: R(0, c) = 1 for all c ≥ 1 (the empty representation). -/
theorem reprCount_zero (c : ℕ) (hc : 0 < c) : reprCount 0 c = 1 := by
  sorry

/-- Monotonicity: relaxing the capacity can only increase the count. -/
theorem reprCount_mono (n : ℕ) (c₁ c₂ : ℕ) (h : c₁ ≤ c₂) :
    reprCount n c₁ ≤ reprCount n c₂ := by
  sorry

/-- When capacity is 1, the count equals the number of Zeckendorf representations,
    which by Zeckendorf's theorem is exactly 1 for all positive n. -/
theorem reprCount_one_eq_one (n : ℕ) (hn : 0 < n) : reprCount n 1 = 1 := by
  sorry

/-! ## Growth Estimates -/

/-- **Fibonacci recurrence identity:** fib n = fib(n-1) + fib(n-2) for n ≥ 2.
    This is the defining recurrence, stated in subtraction form for natural numbers. -/
theorem fib_recurrence (n : ℕ) (hn : 2 ≤ n) :
    fib n = fib (n - 1) + fib (n - 2) := by
  cases n with
  | zero => omega
  | succ m =>
    cases m with
    | zero => omega
    | succ k =>
      -- `k+1+1-1` and `k+1+1-2` reduce definitionally to `k+1` and `k`
      show fib (k + 2) = fib (k + 1) + fib k
      -- the recurrence gives `fib k + fib (k+1)`; the goal wants the other order
      rw [fib_add_two]
      omega

end NonLinearNumberSystems
