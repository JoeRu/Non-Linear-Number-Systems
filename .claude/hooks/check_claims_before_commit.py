#!/usr/bin/env python3
"""PreToolUse hook: run scripts/check_claims.py before any `git commit`.

The claim ledger is cheap to validate and CI would reject the push anyway;
catching it here keeps a broken ledger out of the commit history.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

payload = json.load(sys.stdin)
command = payload.get("tool_input", {}).get("command", "")
if not re.search(r"\bgit\b(\s+-\S+(\s+\S+)?)*\s+commit\b", command):
    sys.exit(0)

root = Path(os.environ.get("CLAUDE_PROJECT_DIR", payload.get("cwd", "."))).resolve()
venv_python = root / ".venv" / "bin" / "python"
python = str(venv_python) if venv_python.exists() else sys.executable
proc = subprocess.run(
    [python, "scripts/check_claims.py"], cwd=root, capture_output=True, text=True,
)
if proc.returncode != 0:
    print(
        "scripts/check_claims.py failed; fix the claim ledger before committing:\n"
        + (proc.stdout + proc.stderr)[-6000:],
        file=sys.stderr,
    )
    sys.exit(2)
