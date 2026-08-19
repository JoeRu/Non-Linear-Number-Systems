#!/usr/bin/env python3
"""Validate theory/claims.yaml and every {claim:id} reference in the docs.

The distinction between a heuristic and a theorem is the epistemic content of
this project, and Phase 3 is separated from Phase 5 by months -- long enough
for a conjecture to acquire the tone of a result. This makes that drift
mechanically detectable.
"""

import json
import re
import sys
from pathlib import Path

import yaml

VALID_STATUS = {"cited", "verified-numeric", "heuristic", "conjecture", "theorem", "open"}
REQUIRED_FIELDS = ("id", "statement", "status", "evidence", "source")
REFERENCE = re.compile(r"\{claim:([a-z0-9-]+)\}")
SEARCH_DIRS = ("theory", "docs/phases", "paper")
FILE_TOKEN = re.compile(r"[\w./-]+\.[A-Za-z0-9]+")
DATA_EXTENSIONS = {".csv", ".json", ".npy", ".npz", ".png", ".pdf", ".svg"}


def validate(root: Path) -> list[str]:
    """Return a list of problems; empty means the ledger is valid."""
    problems: list[str] = []
    ledger_path = root / "theory" / "claims.yaml"
    if not ledger_path.exists():
        return [f"missing ledger: {ledger_path}"]

    claims = yaml.safe_load(ledger_path.read_text()) or []
    ids: set[str] = set()
    for i, claim in enumerate(claims):
        for field in REQUIRED_FIELDS:
            if field not in claim:
                problems.append(f"claim #{i}: missing required field '{field}'")
        cid = claim.get("id", f"#{i}")
        if cid in ids:
            problems.append(f"claim '{cid}': duplicate id")
        ids.add(cid)
        status = claim.get("status")
        if status is not None and status not in VALID_STATUS:
            problems.append(
                f"claim '{cid}': invalid status '{status}'; "
                f"expected one of {sorted(VALID_STATUS)}"
            )

    manifest_path = root / "data" / "manifest.json"
    manifest_files = set()
    if manifest_path.exists():
        manifest_files = {e["file"] for e in json.loads(manifest_path.read_text())}
    for claim in claims:
        if claim.get("status") == "verified-numeric":
            evidence = claim.get("evidence", "")
            tokens = FILE_TOKEN.findall(evidence)
            data_tokens = [
                t for t in tokens if Path(t).suffix.lower() in DATA_EXTENSIONS
            ]
            if not data_tokens:
                problems.append(
                    f"claim '{claim.get('id')}': status verified-numeric but its "
                    f"evidence names no data artifact (.csv/.json/.npy/.npz/.png/.pdf/.svg)"
                )
            elif not all(Path(t).name in manifest_files for t in data_tokens):
                problems.append(
                    f"claim '{claim.get('id')}': status verified-numeric but its "
                    f"evidence names a data artifact not recorded in data/manifest.json"
                )

    for directory in SEARCH_DIRS:
        base = root / directory
        if not base.exists():
            continue
        for md in sorted(base.rglob("*.md")):
            for ref in REFERENCE.findall(md.read_text()):
                if ref not in ids:
                    problems.append(f"{md}: reference to unknown claim '{ref}'")

    return problems


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    problems = validate(root)
    for p in problems:
        print(f"FAIL {p}")
    if problems:
        print(f"\n{len(problems)} problem(s) found.")
        return 1
    print("claims.yaml OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
