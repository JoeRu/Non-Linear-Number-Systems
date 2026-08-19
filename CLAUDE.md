# CLAUDE.md — AI Assistant Guide for Non-Linear Number Systems

This file gives AI coding assistants (Claude, GitHub Copilot, etc.) the context they need
to contribute effectively to this project.

---

## Project Overview

**Non-Linear Number Systems** is a mathematical research project studying:

- Capacity-constrained Fibonacci partitions (Kapazitätsbeschränkte Fibonacci-Partitionen)
- Non-unique number representations and their combinatorial properties
- Formal verification of theorems about these systems using Lean 4 / Mathlib

The goal is to state, explore, and **formally prove** properties of non-linear number
systems using modern interactive theorem provers and automated benchmark harnesses.

---

## Repository Layout

```
.
├── CLAUDE.md                  ← You are here: AI-assistant guide
├── README.md                  ← Human-facing project overview
│
├── lean/                      ← Lean 4 / Mathlib formal proofs
│   ├── lean-toolchain         ← Pinned Lean 4 version
│   ├── lakefile.lean          ← Lake build system configuration
│   └── NonLinearNumberSystems/
│       ├── Basic.lean         ← Core definitions
│       ├── Fibonacci.lean     ← Fibonacci partition definitions & theorems
│       └── Theorems.lean      ← Top-level theorem statements
│
├── proofs/                    ← Human-readable proof sketches & LaTeX write-ups
│   └── fibonacci_partitions.md
│
├── benchmarks/                ← Formal benchmark problem sets
│   ├── miniF2F/               ← miniF2F-style problem stubs (Lean 4)
│   │   └── problems.lean
│   ├── proofnet/              ← ProofNet-style problem stubs (Lean 4)
│   │   └── problems.lean
│   └── math_benchmark/        ← MATH-Benchmark problems (JSON + Python driver)
│       ├── problems.json
│       └── evaluate.py
│
├── harnesses/                 ← Harness runners that interface with theorem provers
│   ├── lean_dojo/             ← LeanDojo integration
│   │   ├── requirements.txt
│   │   ├── trace_proofs.py    ← Trace & extract proof states via LeanDojo
│   │   └── search_proofs.py   ← BFS/MCTS proof search with LeanDojo
│   └── math_harness/          ← MATH dataset evaluation harness
│       ├── requirements.txt
│       └── run_eval.py
│
├── tools/                     ← Shared Python utilities
│   ├── __init__.py
│   ├── lean_utils.py          ← Helpers to invoke Lean / Lake
│   └── benchmark_utils.py     ← Benchmark scoring & reporting helpers
│
├── scripts/                   ← Shell convenience scripts
│   ├── setup.sh               ← One-shot environment setup
│   ├── run_lean.sh            ← Build & check all Lean files
│   └── run_benchmarks.sh      ← Run all benchmark harnesses
│
└── docs/                      ← Extended documentation
    ├── lean_setup.md
    ├── leandojo_setup.md
    └── math_benchmark_setup.md
```

---

## Key Concepts

### Fibonacci Partitions
A **Fibonacci partition** of a positive integer n is a representation
`n = F_{i₁} + F_{i₂} + … + F_{iₖ}` where each `F_j` is a Fibonacci number.
The **Zeckendorf representation** is the unique partition using non-consecutive
Fibonacci numbers.  This project studies *capacity-constrained* variants where
each Fibonacci number may be used at most `c` times.

### Non-Unique Representations
When the capacity constraint `c ≥ 2` is relaxed, multiple valid representations
exist.  We study:
- The count of representations for a given n and capacity c
- Patterns and recurrences in these counts
- Connections to other combinatorial objects (tilings, lattice paths, etc.)

---

## Working with Lean 4 / Mathlib

### Prerequisites
- Install `elan` (Lean version manager): https://github.com/leanprover/elan
- The toolchain version is pinned in `lean/lean-toolchain`

### Build
```bash
cd lean
lake update        # download Mathlib (first time, ~10 min)
lake build         # compile all files
```

### Check a Single File
```bash
cd lean
lake env lean NonLinearNumberSystems/Fibonacci.lean
```

### Common Lean 4 Patterns Used Here
- `def`, `theorem`, `lemma` for definitions and statements
- `simp`, `ring`, `omega`, `norm_num` for automated tactics
- `induction`, `rcases`, `obtain` for structural proofs
- `#check`, `#eval` for interactive exploration

---

## Working with LeanDojo

LeanDojo lets you programmatically interact with Lean proofs — extract proof states,
replay proofs, and run proof-search algorithms.

### Setup
```bash
pip install lean-dojo
# See docs/leandojo_setup.md for full instructions
```

### Trace Proofs
```bash
python harnesses/lean_dojo/trace_proofs.py
```

### Proof Search
```bash
python harnesses/lean_dojo/search_proofs.py --theorem fibonacci_unique_zeckendorf
```

---

## Working with MATH-Benchmark

The `benchmarks/math_benchmark/` directory contains problems in the format used by
the MATH dataset (Hendrycks et al., 2021) and the accompanying Python evaluation
harness.

### Run Evaluation
```bash
pip install -r harnesses/math_harness/requirements.txt
python harnesses/math_harness/run_eval.py --problems benchmarks/math_benchmark/problems.json
```

---

## Working with miniF2F / ProofNet

`benchmarks/miniF2F/problems.lean` and `benchmarks/proofnet/problems.lean` contain
formal theorem **statements** (without proofs) from the respective benchmarks,
adapted to the Non-Linear Number Systems domain.

To attempt a proof, copy the relevant `sorry`-filled theorem into the appropriate
`lean/NonLinearNumberSystems/` file and fill in the proof.

---

## Contribution Guidelines for AI Assistants

1. **Stay focused on the mathematics.** All code changes should serve the goal of
   formally verifying or computationally exploring theorems about non-linear number
   systems.

2. **Never remove `sorry` without a real proof.** A `sorry`-filled theorem is a
   *statement*; replacing it with a wrong proof is worse than leaving it open.

3. **Run `lake build` before committing** Lean changes to ensure the project compiles.

4. **Add docstrings** to all new Python functions using the Google style.

5. **Keep benchmark problem files stable.** Only add new problems; never modify
   existing problem IDs.

6. **Cite sources.** When adapting a theorem from Mathlib, miniF2F, or ProofNet,
   include the source reference in a comment.
