#!/usr/bin/env python3
"""PostToolUse hook: elaborate an edited Lean file and report errors at once.

Runs `lake env lean <file>` from lean/. Errors go back to Claude (exit 2);
warnings, including `declaration uses 'sorry'`, are reported but do not block,
since a stated-but-open theorem is legitimate here. This is fast feedback,
not the gate: `lake build` and `#print axioms` still run before a commit.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

payload = json.load(sys.stdin)
target = payload.get("tool_input", {}).get("file_path", "")
if not target.endswith(".lean"):
    sys.exit(0)

root = Path(os.environ.get("CLAUDE_PROJECT_DIR", payload.get("cwd", "."))).resolve()
lean_dir = root / "lean"
path = Path(target).resolve()
if lean_dir not in path.parents or ".lake" in path.parts:
    sys.exit(0)

try:
    proc = subprocess.run(
        ["lake", "env", "lean", str(path.relative_to(lean_dir))],
        cwd=lean_dir, capture_output=True, text=True, timeout=600,
    )
except FileNotFoundError:
    print("lake not found on PATH; Lean file not checked.", file=sys.stderr)
    sys.exit(1)
except subprocess.TimeoutExpired:
    print("lake env lean timed out after 600 s; Lean file not checked.", file=sys.stderr)
    sys.exit(1)

out = (proc.stdout + proc.stderr).strip()
if proc.returncode != 0:
    print(f"Lean check failed for {path.name}:\n{out[-6000:]}", file=sys.stderr)
    sys.exit(2)
if out:
    print(f"Lean check passed with messages for {path.name}:\n{out[-3000:]}")
