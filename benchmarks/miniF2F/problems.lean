/-
  miniF2F-style Benchmark Problems
  ==================================
  Each theorem below is a *statement only* (proved with `sorry`).
  The goal is to replace each `sorry` with a valid Lean 4 proof.

  Problem IDs follow the convention: NLNS_mF2F_<number>.

  Source: Adapted from miniF2F (Zheng et al., 2021) and custom problems
          related to Non-Linear Number Systems.
-/

import NonLinearNumberSystems.Basic
import NonLinearNumberSystems.Fibonacci
import Mathlib.Tactic

namespace NonLinearNumberSystems.Benchmarks.MiniF2F

open NonLinearNumberSystems

/-- NLNS_mF2F_001
    The Fibonacci number at index 10 equals 55. -/
theorem fib_10_eq_55 : fib 10 = 55 := by decide

/-- NLNS_mF2F_002
    Every Fibonacci number with index ≥ 2 is the sum of the two preceding ones. -/
theorem fib_recurrence (n : ℕ) (hn : 2 ≤ n) :
    fib n = fib (n - 1) + fib (n - 2) := by
  cases n with
  | zero => omega
  | succ m =>
    cases m with
    | zero => omega
    | succ k =>
      simp [fib_add_two, Nat.add_sub_cancel]
      ring

/-- NLNS_mF2F_003
    Zeckendorf: every positive integer has a Zeckendorf representation. -/
theorem problem_003 (n : ℕ) (hn : 0 < n) :
    ∃ rep : Representation n 1, IsZeckendorf rep := by
  exact zeckendorf_exists n hn

/-- NLNS_mF2F_004
    With capacity 1, reprCount n 1 = 1 for all positive n. -/
theorem problem_004 (n : ℕ) (hn : 0 < n) : reprCount n 1 = 1 :=
  reprCount_one_eq_one n hn

/-- NLNS_mF2F_005
    reprCount is monotone in capacity. -/
theorem problem_005 (n c : ℕ) : reprCount n c ≤ reprCount n (c + 1) :=
  reprCount_mono n c (c + 1) (Nat.le_succ c)

/-- NLNS_mF2F_006
    The sum of the first n Fibonacci numbers equals fib(n+2) - 1. -/
theorem fib_sum (n : ℕ) :
    (∑ i ∈ Finset.range n, fib (i + 1)) = fib (n + 2) - 1 := by
  induction n with
  | zero => simp [fib]
  | succ k ih =>
    rw [Finset.sum_range_succ, ih]
    simp [fib_add_two]
    omega

/-- NLNS_mF2F_007
    fib is strictly monotone for indices ≥ 1. -/
theorem fib_strict_mono : StrictMono (fun n => fib (n + 1)) := by
  intro a b hab
  sorry

/-- NLNS_mF2F_008
    gcd(fib m, fib n) = fib(gcd m n)  (Fibonacci GCD identity). -/
theorem fib_gcd (m n : ℕ) : Nat.gcd (fib m) (fib n) = fib (Nat.gcd m n) := by
  sorry

end NonLinearNumberSystems.Benchmarks.MiniF2F
