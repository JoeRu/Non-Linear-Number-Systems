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


def git_rev(repo: str | Path | None = None) -> str:
    """Return the commit hash HEAD points at, or "unknown" outside git.

    Args:
        repo: the repository to ask. A runner passes its own repository root
            so the answer does not depend on where it was invoked from;
            `None` asks the current working directory.

    Returns:
        The full commit hash, or "unknown" if git is absent or `repo` is not
        inside a repository.
    """
    cmd = ["git", "rev-parse", "HEAD"]
    if repo is not None:
        cmd[1:1] = ["-C", str(repo)]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True)
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
    """Upsert a provenance entry for `path` and return it.

    If an entry with the same `file` and `script` already exists, it is
    replaced in place (preserving its position); otherwise the new entry is
    appended. This keeps re-running a generator from duplicating its entries.

    `path` must LOCATE the artifact, not merely name it: only `path.name` is
    stored, but `path` is what gets opened and hashed. Passing a repo-relative
    string resolves it against the current working directory instead, which
    hashes whatever happens to sit there -- silently correct when the script is
    run from the repository root and silently wrong everywhere else.
    `scripts/run_phase2.py` did exactly that, and it went unnoticed until a
    test ran a copy of the script from a scratch tree and watched it hash the
    real repository's files. Pass an absolute path, as every generator here now
    does.

    Args:
        path: the artifact to record. Absolute, or resolvable from the CWD.
        script: repo-relative path of the generating script.
        params: the parameters the generator ran with.
        manifest_path: where to upsert. Absolute, for the same reason.

    Returns:
        The entry that was written.
    """
    target = Path(path)
    entry = {
        "file": target.name,
        "script": script,
        "params": params,
        "git_rev": git_rev(),
        "sha256": _sha256(target),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    existing = entries(manifest_path)
    for i, e in enumerate(existing):
        if e.get("file") == entry["file"] and e.get("script") == entry["script"]:
            existing[i] = entry
            break
    else:
        existing.append(entry)
    mp = Path(manifest_path)
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(existing, indent=2) + "\n")
    return entry
