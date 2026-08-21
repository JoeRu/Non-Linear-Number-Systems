# Lean 4 Setup Guide

## Prerequisites

- A Unix-like OS (Linux, macOS) or Windows with WSL2
- `curl` installed
- Python ≥ 3.11 (for the `capfib` numerics package)

## Step 1: Install elan

[elan](https://github.com/leanprover/elan) is the Lean version manager (analogous to `rustup`).

```bash
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
  | sh -s -- -y
source ~/.elan/env
```

## Step 2: Install the pinned toolchain

The project pins a specific Lean 4 version in `lean/lean-toolchain`.

```bash
cd lean/
elan toolchain install "$(cat lean-toolchain)"
```

## Step 3: Fetch Mathlib

Mathlib is the main mathematical library for Lean 4.

```bash
cd lean/
lake update          # downloads Mathlib cache (~1 GB on first run)
```

## Step 4: Build

```bash
cd lean/
lake build
```

A successful build type-checks every theorem in the development. There are
currently no open statements: nothing is left standing on a `sorry`. If one is
ever added, it is intentional — it marks an open theorem that needs a proof —
and it is listed under "What is open" in `Theorems.lean`.

## Verified build state

The Lean development builds cleanly against the pinned toolchain. Verified with:

| | |
|---|---|
| elan | 4.2.3 |
| Lean | `leanprover/lean4:v4.14.0` (from `lean/lean-toolchain`) |
| Mathlib | `v4.14.0`, rev `4bbdccd9` (pinned in `lean/lake-manifest.json`) |

`lake build` succeeds with **no errors** and **zero `declaration uses 'sorry'`
warnings**. Phase 2 discharged the last two — `exists_numeral_of_le` in
`Completeness.lean` and `countReps_le_uncapped` in `Bounds.lean`.

Zero is the invariant to check against. It may rise again when a new statement
is written down before it is proved; what must never happen is a count dropping
without a corresponding proof, which would mean something was closed
dishonestly. `#print axioms` on the theorem is the check: `sorryAx` must not
appear among its axioms.

`lean/lake-manifest.json` is tracked on purpose so this build is reproducible.

## Useful Commands

| Command | Effect |
|---|---|
| `lake build` | Compile all files |
| `lake env lean File.lean` | Check a single file |
| `lake exe cache get` | Download pre-built Mathlib cache |
| `#check Nat.add_comm` | Look up a lemma interactively |
| `#eval fib 10` | Evaluate a definition |

## Editor Integration

- **VS Code**: install the [lean4](https://marketplace.visualstudio.com/items?itemName=leanprover.lean4) extension
- **Emacs**: use [lean4-mode](https://github.com/leanprover/lean4-mode)
- **Neovim**: use [lean.nvim](https://github.com/Julian/lean.nvim)
