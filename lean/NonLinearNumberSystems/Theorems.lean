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

/-
  **Open Problem 2 (Bijection with tilings) -- not yet formalised.**
  Intended claim: there is a natural bijection between capacity-c Fibonacci
  representations of n and certain tilings of a 1×n board with tiles of sizes
  corresponding to Fibonacci numbers, where each tile size may appear at most
  c times.

  This is not stated as a Lean theorem here: without first formalising the
  tiling family (and without a working `lake build` to check any attempt), a
  real statement would be guesswork. A theorem whose body is `True` proved by
  `trivial` would assert nothing while looking like a result, which is worse
  than leaving the claim as a comment. The bijection remains open.
-/

/-
  **Trivial upper bound.**
  reprCount n c ≤ reprCount n (c + 1)  (already stated as `reprCount_mono`).
  This bound is tight only for specific (n, c).

  A `/-- … -/` doc comment must attach to a declaration; `#check` is a command,
  so this is a plain `/- … -/` comment.
-/
#check @reprCount_mono

end NonLinearNumberSystems
