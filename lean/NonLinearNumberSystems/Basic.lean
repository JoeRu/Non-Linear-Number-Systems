/-
  NonLinearNumberSystems.Basic
  ============================
  Core definitions for non-linear (capacity-constrained) number systems.

  A *capacity-constrained Fibonacci representation* of a natural number n with
  capacity c ∈ ℕ⁺ is a multiset M of Fibonacci numbers such that
    · each element of M appears at most c times, and
    · the sum of M equals n.

  When c = 1 and we further require no two consecutive Fibonacci numbers appear,
  the unique such representation is the *Zeckendorf representation*.
-/

import Mathlib.Data.Nat.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Data.List.Basic

namespace NonLinearNumberSystems

/-! ## Fibonacci Numbers -/

/-- The Fibonacci sequence: fib 0 = 0, fib 1 = 1, fib (n+2) = fib n + fib (n+1) -/
def fib : ℕ → ℕ
  | 0     => 0
  | 1     => 1
  | n + 2 => fib n + fib (n + 1)

@[simp] lemma fib_zero : fib 0 = 0 := rfl
@[simp] lemma fib_one  : fib 1 = 1 := rfl
@[simp] lemma fib_two  : fib 2 = 1 := rfl

lemma fib_add_two (n : ℕ) : fib (n + 2) = fib n + fib (n + 1) := rfl

/-- fib is strictly positive for positive indices -/
lemma fib_pos : ∀ n : ℕ, 0 < n → 0 < fib n := by
  intro n hn
  induction n with
  | zero => exact absurd hn (lt_irrefl 0)
  | succ m ih =>
    cases m with
    | zero => simp [fib]
    | succ k =>
      simp [fib_add_two]
      have hk : 0 < k + 1 := Nat.succ_pos k
      exact Nat.add_pos_right _ (ih hk)

/-! ## Representations -/

/-- A *representation* of n with capacity c is a list of Fibonacci indices
    where each index i contributes fib i to the sum, each index i appears
    at most c times, and the total equals n. -/
structure Representation (n c : ℕ) where
  /-- The list of Fibonacci indices used (with repetition). -/
  indices : List ℕ
  /-- Every index is positive (we use 1-based Fibonacci indices). -/
  indices_pos : ∀ i ∈ indices, 0 < i
  /-- Each index appears at most c times. -/
  capacity_ok : ∀ i, indices.count i ≤ c
  /-- The sum of the corresponding Fibonacci numbers equals n. -/
  sum_eq : (indices.map fib).sum = n

/-- The number of distinct representations of n with capacity c. -/
noncomputable def reprCount (n c : ℕ) : ℕ :=
  -- Placeholder: a decidable enumeration would be finite; left as a definition
  -- for formal development.  See Fibonacci.lean for computable variants.
  sorry

end NonLinearNumberSystems
