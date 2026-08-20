/-
  NonLinearNumberSystems.Redundancy
  =================================
  Non-uniqueness: the evaluation map is not injective.

  This is the phenomenon the project is named for. The source article observed
  that its system writes some numbers more than once, and reported it as
  "1 > 1": the numerals `1000` and `0100` both denote 1, because the
  convention F 1 = F 2 = 1 gives two distinct places of value 1.

  `exists_two_numerals_same_value` below is that observation, formalised.

  ## Contrast: Zeckendorf

  Restricting digits to `{0,1}` *and* forbidding two consecutive nonzero digits
  recovers uniqueness — that is Zeckendorf's theorem. **Mathlib already proves
  it**, so nothing here re-derives it:

  * `List.IsZeckendorfRep` — increasing, non-consecutive index lists
  * `Nat.zeckendorf` — a natural number's Zeckendorf representation
  * `Nat.zeckendorfEquiv : ℕ ≃ {l // List.IsZeckendorfRep l}` — existence and
    uniqueness together, as a bijection

  in `Mathlib.Data.Nat.Fib.Zeckendorf` (Yaël Dillies, 2023).

  The two facts sit either side of the same coin: Zeckendorf's constraint buys
  a bijection, and dropping it — as this system does — buys redundancy instead.
-/

import NonLinearNumberSystems.Numeration
import Mathlib.Data.Nat.Fib.Zeckendorf

namespace NonLinearNumberSystems

open Finset

/-- Every place value is at least 1, so a digit of 1 is always permitted.
    (`1 ≤ x` is definitionally `0 < x` on `ℕ`.) -/
lemma one_le_place (k : ℕ) : 1 ≤ place (k + 1) :=
  Nat.fib_pos.2 (Nat.succ_pos k)

/-- The numeral carrying a single `1` at place `j` and zeros elsewhere. -/
def unitNumeral {n : ℕ} (j : Fin n) : Numeral n where
  digit := fun i => if i = j then 1 else 0
  capped := by
    intro i
    by_cases h : i = j
    · simpa [h] using one_le_place i.val
    · simp [h]

@[simp] lemma unitNumeral_digit {n : ℕ} (j i : Fin n) :
    (unitNumeral j).digit i = if i = j then 1 else 0 := rfl

lemma unitNumeral_value {n : ℕ} (j : Fin n) :
    (unitNumeral j).value = place (j.val + 1) := by
  classical
  simp [Numeral.value, unitNumeral]

/-- **"1 > 1".** With at least two places, two *distinct* numerals share a value.

    The witnesses are `1000…` and `0100…`: places 1 and 2 both have value
    `F 1 = F 2 = 1`, so each numeral evaluates to 1. This is exactly the source
    article's observation, and it is why the evaluation map is not injective. -/
theorem exists_two_numerals_same_value (n : ℕ) (hn : 2 ≤ n) :
    ∃ d e : Numeral n, d ≠ e ∧ d.value = e.value := by
  have h0 : (0 : ℕ) < n := lt_of_lt_of_le (by norm_num) hn
  have h1 : (1 : ℕ) < n := lt_of_lt_of_le (by norm_num) hn
  refine ⟨unitNumeral ⟨0, h0⟩, unitNumeral ⟨1, h1⟩, ?_, ?_⟩
  · -- the digit functions differ at place 1
    intro hde
    have := congrArg (fun d => Numeral.digit d ⟨0, h0⟩) hde
    simp [Fin.ext_iff] at this
  · -- both evaluate to 1, since F 1 = F 2 = 1
    rw [unitNumeral_value, unitNumeral_value]
    rfl

/-- The evaluation map is not injective once there are two places. -/
theorem value_not_injective (n : ℕ) (hn : 2 ≤ n) :
    ¬ Function.Injective (Numeral.value : Numeral n → ℕ) := by
  intro hinj
  obtain ⟨d, e, hne, hval⟩ := exists_two_numerals_same_value n hn
  exact hne (hinj hval)

end NonLinearNumberSystems
