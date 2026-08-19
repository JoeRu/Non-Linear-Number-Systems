# Non-Linear Number Systems

**Mathematical Research Project on Non-Unique Number Systems /
Kapazitätsbeschränkte Fibonacci-Partitionen**

This project studies capacity-constrained Fibonacci partitions and related
non-linear number systems, with formal verification of theorems using Lean 4 /
Mathlib and automated evaluation via MATH-Benchmark and LeanDojo harnesses.

---

## Quick Start

```bash
# 1. Set up the environment (elan, Lean 4, Python deps)
bash scripts/setup.sh

# 2. Build the Lean project
bash scripts/run_lean.sh

# 3. Run benchmark harnesses
bash scripts/run_benchmarks.sh
```

## Repository Structure

```
lean/                  Lean 4 / Mathlib formal proofs
proofs/                Human-readable proof sketches
benchmarks/            Formal problem sets (miniF2F, ProofNet, MATH)
harnesses/             LeanDojo & MATH harness runners
tools/                 Shared Python utilities
scripts/               Shell convenience scripts
docs/                  Extended setup documentation
CLAUDE.md              AI-assistant guide
```

## Tooling

| Tool | Purpose |
|---|---|
| [Lean 4](https://leanprover.github.io) | Interactive theorem prover |
| [Mathlib](https://leanprover-community.github.io/mathlib4_docs/) | Mathematical library for Lean 4 |
| [LeanDojo](https://leandojo.org) | Programmatic proof interaction & search |
| [MATH-Benchmark](https://github.com/hendrycks/math) | Competition math evaluation harness |
| [miniF2F](https://github.com/openai/miniF2F) | Formal math benchmarks |
| [ProofNet](https://github.com/zhangir-azerbayev/ProofNet) | Graduate-level proof benchmarks |

## Documentation

- [`docs/lean_setup.md`](docs/lean_setup.md) — Lean 4 installation & usage
- [`docs/leandojo_setup.md`](docs/leandojo_setup.md) — LeanDojo integration
- [`docs/math_benchmark_setup.md`](docs/math_benchmark_setup.md) — MATH harness usage
- [`proofs/fibonacci_partitions.md`](proofs/fibonacci_partitions.md) — Proof sketches
- [`CLAUDE.md`](CLAUDE.md) — Guide for AI coding assistants
