#!/usr/bin/env bash
set -euo pipefail

echo "==> Python environment"
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"

echo "==> Lean toolchain (optional)"
if ! command -v elan >/dev/null 2>&1; then
  echo "elan not found. Install from https://github.com/leanprover/elan to build lean/."
else
  (cd lean && lake update && lake build)
fi

echo "==> Done. Run: .venv/bin/pytest"
