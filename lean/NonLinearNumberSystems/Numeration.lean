/-
  NonLinearNumberSystems.Numeration
  =================================
  The capacity-constrained Fibonacci numeration system.

  Convention: F 1 = 1, F 2 = 1, F 3 = 2, ...  (Mathlib's `Nat.fib` with the
  index shifted by one: our F k is `Nat.fib k` for k >= 1.)

  Reference: theory/00-definitions.md
-/

/- NOTE: This file has not been compiled. `elan`/`lake` were unavailable in the
   environment where it was written, so its syntax and Mathlib API usage are
   unverified. Run `lake build` before relying on it. -/

import Mathlib.Tactic
import Mathlib.Combinatorics.Enumerative.Partition

namespace NonLinearNumberSystems

/-- The place value at position `k` (one-indexed): `F 1 = F 2 = 1`. -/
def place (k : ℕ) : ℕ := Nat.fib k

/-- A numeral of length `n` is a digit function bounded by the place values. -/
structure Numeral (n : ℕ) where
  digit : Fin n → ℕ
  capped : ∀ i : Fin n, digit i ≤ place (i.val + 1)

/-- The value of a numeral. -/
def Numeral.value {n : ℕ} (d : Numeral n) : ℕ :=
  ∑ i : Fin n, d.digit i * place (i.val + 1)

end NonLinearNumberSystems
