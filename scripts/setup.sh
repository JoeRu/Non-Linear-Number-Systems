#!/usr/bin/env bash
# setup.sh — One-shot environment setup for Non-Linear Number Systems
# Usage: bash scripts/setup.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Installing elan (Lean version manager) …"
if ! command -v elan &>/dev/null; then
  curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
    | sh -s -- -y --no-modify-path
  # Add to current shell session
  source "$HOME/.elan/env" 2>/dev/null || export PATH="$HOME/.elan/bin:$PATH"
else
  echo "    elan already installed ($(elan --version))"
fi

echo "==> Installing Lean 4 toolchain (from lean/lean-toolchain) …"
TOOLCHAIN="$(cat "$REPO_ROOT/lean/lean-toolchain")"
elan toolchain install "$TOOLCHAIN"
elan override set --path "$REPO_ROOT/lean" "$TOOLCHAIN"

echo "==> Installing Python dependencies (LeanDojo harness) …"
pip install --quiet -r "$REPO_ROOT/harnesses/lean_dojo/requirements.txt"

echo "==> Installing Python dependencies (MATH harness) …"
pip install --quiet -r "$REPO_ROOT/harnesses/math_harness/requirements.txt"

echo "==> Fetching Mathlib (this may take several minutes on first run) …"
cd "$REPO_ROOT/lean"
lake update

echo ""
echo "Setup complete!  Run 'bash scripts/run_lean.sh' to build the Lean project."
