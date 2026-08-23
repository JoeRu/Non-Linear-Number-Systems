#!/usr/bin/env bash
# run_lean.sh — Build and type-check all Lean files in the project.
# Usage: bash scripts/run_lean.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Building Lean project …"
cd "$REPO_ROOT/lean"
lake build

echo ""
echo "Build successful!  All declarations type-check."
echo "(lake build warns on any declaration that uses 'sorry'; read the output above.)"
