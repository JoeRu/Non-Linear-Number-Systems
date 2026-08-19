# Lean 4 Setup Guide

## Prerequisites

- A Unix-like OS (Linux, macOS) or Windows with WSL2
- `curl` installed
- Python ≥ 3.10 (for the harnesses)

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

A successful build will type-check all theorems (with `sorry` placeholders for
open problems).  Any `sorry` is intentional — it marks an open theorem that
needs a proof.

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
