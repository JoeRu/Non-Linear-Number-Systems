#!/usr/bin/env python3
"""PreToolUse hook: refuse hand edits to generated output under data/ and figures/.

Everything there is produced by a script and recorded in data/manifest.json
with its SHA-256; a hand edit breaks that provenance silently. Regenerate
with the script that produced the file instead.
"""
import json
import os
import sys
from pathlib import Path

GENERATED = ("data", "figures")

payload = json.load(sys.stdin)
target = payload.get("tool_input", {}).get("file_path") or payload.get(
    "tool_input", {}
).get("notebook_path")
if not target:
    sys.exit(0)

root = Path(os.environ.get("CLAUDE_PROJECT_DIR", payload.get("cwd", "."))).resolve()
try:
    rel = Path(target).resolve().relative_to(root)
except ValueError:
    sys.exit(0)

if rel.parts and rel.parts[0] in GENERATED and rel.name != ".gitkeep":
    print(
        f"{rel} is generated output and must not be edited by hand. "
        "Regenerate it with the script recorded for it in data/manifest.json "
        "(see the rc-numerics skill).",
        file=sys.stderr,
    )
    sys.exit(2)
