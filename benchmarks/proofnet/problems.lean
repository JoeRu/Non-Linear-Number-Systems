/-
  ProofNet-style Benchmark Problems
  ===================================
  Each theorem below mirrors the ProofNet benchmark format: a formal statement
  of a theorem from undergraduate/graduate mathematics, to be proved in Lean 4.

  Problem IDs follow the convention: NLNS_PN_<number>.

  Source: Adapted from ProofNet (Azerbayev et al., 2023) for the Non-Linear
          Number Systems domain.
-/

import NonLinearNumberSystems.Basic
import NonLinearNumberSystems.Fibonacci
import Mathlib.Tactic
import Mathlib.NumberTheory.Fibonacci

namespace NonLinearNumberSystems.Benchmarks.ProofNet

open NonLinearNumberSystems

/-- NLNS_PN_001  (Number Theory, undergraduate)
    Prove that every positive integer n can be written as a sum of distinct
    Fibonacci numbers (not necessarily in Zeckendorf form). -/
theorem sum_of_distinct_fibs (n : ℕ) (hn : 0 < n) :
    ∃ S : Finset ℕ, (∀ i ∈ S, 0 < i) ∧ S.sum fib = n := by
  sorry

/-- NLNS_PN_002  (Combinatorics, undergraduate)
    The number of ways to tile a 1×n strip with 1×1 and 1×2 tiles equals
    fib(n+1). -/
theorem tiling_count (n : ℕ) :
    True := by  -- placeholder; requires defining tiling count separately
  trivial

/-- NLNS_PN_003  (Number Theory, graduate)
    Cassini's identity: fib(n-1) * fib(n+1) - fib(n)^2 = (-1)^n  for n ≥ 1. -/
theorem cassini (n : ℕ) (hn : 1 ≤ n) :
    (fib (n + 1) * fib (n - 1) : ℤ) - (fib n : ℤ) ^ 2 = (-1) ^ n := by
  sorry

/-- NLNS_PN_004  (Number Theory, graduate)
    For capacity c ≥ 2, the representation count reprCount n c grows at least
    polynomially in n. -/
theorem reprCount_polynomial_growth (c : ℕ) (hc : 2 ≤ c) :
    ∀ k : ℕ, ∃ N : ℕ, ∀ n : ℕ, N ≤ n → n ^ k ≤ reprCount n c := by
  sorry

/-- NLNS_PN_005  (Linear Algebra, undergraduate)
    The Fibonacci sequence satisfies the matrix identity
    [[1,1],[1,0]]^n = [[fib(n+1), fib(n)], [fib(n), fib(n-1)]]. -/
theorem fib_matrix (n : ℕ) :
    True := by  -- placeholder; requires Matrix library setup
  trivial

end NonLinearNumberSystems.Benchmarks.ProofNet
