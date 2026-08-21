/-
  NonLinearNumberSystems.Bounds
  =============================
  The counting function and its elementary bounds. Phase 2 targets.

  `countReps n N` is `R_c(N)` restricted to `n` places — the quantity the
  numerics package computes and whose asymptotics the project is after.

  Note the restriction: fixing the length at `n` *undercounts* `R_c(N)`, which
  ranges over every place with `F_k ≤ N`. For `N ≤ F_n · F_{n+1}` the two agree
  only once `n` is large enough to cover all such places. The numerics side
  handles this by defaulting to `places_up_to N` (see `capfib/fib.py`); here the
  length is explicit so the statements stay finite.

  The asymptotic theorems of Phases 5 and 6 are NOT Lean targets — Mellin
  transforms and analytic continuation of ζ_F are far outside what Mathlib
  makes practical. Those live in paper/.
-/

import NonLinearNumberSystems.Numeration

namespace NonLinearNumberSystems

/-- `R_c(N)` restricted to `n` places: the number of length-`n` numerals of
    value `N`. -/
noncomputable def countReps (n N : ℕ) : ℕ :=
  Nat.card {d : Numeral n // d.value = N}

/-- Digit functions with no cap at all — the `R_u(N)` of the roadmap. -/
noncomputable def countRepsUncapped (n N : ℕ) : ℕ :=
  Nat.card {f : Fin n → ℕ // ∑ i, f i * place (i.val + 1) = N}

/-- Every place value is at least 1. Proved locally rather than imported from
    `Redundancy` (as `one_le_place`), so that `Bounds` keeps depending on
    `Numeration` alone; `Completeness.place_succ_pos` makes the same choice. -/
private lemma one_le_place' (k : ℕ) : 1 ≤ place (k + 1) :=
  Nat.fib_pos.2 (Nat.succ_pos k)

/-- In an uncapped digit function of value `N`, every digit is at most `N`.

    Each summand `f i * place (i+1)` is at most the whole sum `N`, since all
    summands are natural numbers, and `place (i+1) ≥ 1` lets the place value be
    dropped from that summand. -/
private lemma digit_le_of_sum_eq {n N : ℕ} {f : Fin n → ℕ}
    (hf : ∑ i, f i * place (i.val + 1) = N) (i : Fin n) : f i ≤ N := by
  have hsummand : f i * place (i.val + 1) ≤ N := by
    rw [← hf]
    exact Finset.single_le_sum (f := fun j : Fin n => f j * place (j.val + 1))
      (fun j _ => Nat.zero_le _) (Finset.mem_univ i)
  calc f i = f i * 1 := (Nat.mul_one _).symm
    _ ≤ f i * place (i.val + 1) := Nat.mul_le_mul_left _ (one_le_place' i.val)
    _ ≤ N := hsummand

/-- The uncapped fibre over `N` is finite.

    Without this, the bound below would be vacuous rather than true: `Nat.card`
    of an infinite type is `0`, so `countRepsUncapped` would collapse to `0`.
    Finiteness holds because every digit is bounded by `N`
    (`digit_le_of_sum_eq`), which embeds the fibre into `Fin n → Fin (N + 1)`. -/
instance countRepsUncapped_finite (n N : ℕ) :
    Finite {f : Fin n → ℕ // ∑ i, f i * place (i.val + 1) = N} :=
  Finite.of_injective
    (fun f i => (⟨f.val i, Nat.lt_succ_of_le (digit_le_of_sum_eq f.property i)⟩ : Fin (N + 1)))
    (by
      intro f g h
      apply Subtype.ext
      funext i
      exact congrArg Fin.val (congrFun h i))

/-- **Trivial upper bound (Phase 2).** Capping digits cannot create
    representations, so `R_c(N) ≤ R_u(N)`.

    `fun d => d.digit` injects capped numerals of value `N` into unrestricted
    digit functions summing to `N`: the target value is unchanged because
    `Numeral.value` *is* that sum, and the map is injective because a `Numeral`
    is its digit function together with a proof (`Numeral.ext`). The uncapped
    fibre is finite by `countRepsUncapped_finite`, which is what makes the
    comparison of `Nat.card`s meaningful.

    Note this inequality is not load-bearing for the Phase 2 upper bound, which
    is proved directly and is sharper; it backs only the comparison against the
    uncapped counting function of Coons–Kristensen–Laursen. -/
theorem countReps_le_uncapped (n N : ℕ) :
    countReps n N ≤ countRepsUncapped n N := by
  refine Nat.card_le_card_of_injective
    (fun d : {d : Numeral n // d.value = N} =>
      (⟨d.val.digit, d.property⟩ :
        {f : Fin n → ℕ // ∑ i, f i * place (i.val + 1) = N})) ?_
  intro a b hab
  exact Subtype.ext (Numeral.ext (congrArg Subtype.val hab))

end NonLinearNumberSystems
