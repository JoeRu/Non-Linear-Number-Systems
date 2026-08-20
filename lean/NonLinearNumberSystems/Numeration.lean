/-
  NonLinearNumberSystems.Numeration
  =================================
  The numeration system this project studies.

  Place values are the Fibonacci numbers and the digit permitted at place `k`
  is bounded by the place value itself:

      0 ≤ d_k ≤ F_k,      value = ∑ d_k · F_k

  The bound is *position-dependent* — it grows with the place. This is what
  distinguishes the system from a constant-capacity variant (`d_k ≤ c` for a
  fixed `c`) and it is what makes the system maximally redundant.

  Convention: F 1 = F 2 = 1, F 3 = 2, F 4 = 3, F 5 = 5, … Our `F k` is exactly
  Mathlib's `Nat.fib k` for `k ≥ 1`, with no index shift. The duplicated
  1-place is deliberate: it is the source of the "1 > 1" phenomenon
  (see `Redundancy.lean`).

  Reference: theory/00-definitions.md
-/

import Mathlib.Data.Nat.Fib.Basic
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Tactic

namespace NonLinearNumberSystems

/-- The place value at position `k` (one-indexed): `F 1 = F 2 = 1`. -/
def place (k : ℕ) : ℕ := Nat.fib k

@[simp] lemma place_one : place 1 = 1 := rfl
@[simp] lemma place_two : place 2 = 1 := rfl

lemma place_add_two (k : ℕ) : place (k + 2) = place k + place (k + 1) :=
  Nat.fib_add_two

/-- A numeral of length `n`: a digit at each place, bounded by that place value. -/
structure Numeral (n : ℕ) where
  digit : Fin n → ℕ
  capped : ∀ i : Fin n, digit i ≤ place (i.val + 1)

/-- The value of a numeral, `∑ d_k · F_k`. -/
def Numeral.value {n : ℕ} (d : Numeral n) : ℕ :=
  ∑ i : Fin n, d.digit i * place (i.val + 1)

/-- Two numerals are equal exactly when their digit functions are. -/
@[ext] lemma Numeral.ext {n : ℕ} {d e : Numeral n} (h : d.digit = e.digit) : d = e := by
  cases d; cases e; simp_all

end NonLinearNumberSystems
