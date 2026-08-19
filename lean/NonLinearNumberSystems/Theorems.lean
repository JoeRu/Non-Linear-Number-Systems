/-
  NonLinearNumberSystems.Theorems
  ================================
  Top-level collection of open and proved theorems for the project.
  Import this file to get everything.
-/

import NonLinearNumberSystems.Basic
import NonLinearNumberSystems.Zeckendorf

namespace NonLinearNumberSystems

/-! ## Summary of Open Problems -/

/--
  **Open Problem 1 (Counting formula).**
  Find a closed-form expression for `reprCount n c` in terms of n and c.

  Conjecture: for fixed c, reprCount n c satisfies a linear recurrence of order
  F(c) where F is the Fibonacci function, i.e. the generating function is rational.
-/
theorem reprCount_closed_form_conjecture :
    ∀ c : ℕ, ∃ (k : ℕ) (a : Fin k → ℤ),
      ∀ n : ℕ, (k : ℤ) * reprCount n c =
        ∑ i : Fin k, a i * reprCount (n - i.val) c := by
  sorry

/--
  **Open Problem 2 (Bijection with tilings).**
  There is a natural bijection between capacity-c Fibonacci representations of n
  and certain tilings of a 1×n board with tiles of sizes corresponding to
  Fibonacci numbers, where each tile size may appear at most c times.
-/
theorem reprCount_tiling_bijection (n c : ℕ) :
    True := by  -- placeholder; the actual statement requires defining tilings
  trivial

/--
  **Theorem (trivial upper bound).**
  reprCount n c ≤ reprCount n (c + 1)  (already stated as `reprCount_mono`).
  This bound is tight only for specific (n, c).
-/
#check @reprCount_mono

end NonLinearNumberSystems
