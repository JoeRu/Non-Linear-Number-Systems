"""Provenance records for generated data (spec §4.6).

`data/` is gitignored apart from the manifest, so the manifest is the only
record that a given figure or table came from a given script at a given commit.
"""

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MANIFEST = "data/manifest.json"


def _git_rev() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def entries(manifest_path: str | Path = DEFAULT_MANIFEST) -> list[dict]:
    """Return the recorded entries, or [] if the manifest does not exist."""
    p = Path(manifest_path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def record(
    path: str | Path,
    script: str,
    params: dict,
    manifest_path: str | Path = DEFAULT_MANIFEST,
) -> dict:
    """Append a provenance entry for `path` and return it."""
    target = Path(path)
    entry = {
        "file": target.name,
        "script": script,
        "params": params,
        "git_rev": _git_rev(),
        "sha256": _sha256(target),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    existing = entries(manifest_path)
    existing.append(entry)
    mp = Path(manifest_path)
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(existing, indent=2) + "\n")
    return entry
