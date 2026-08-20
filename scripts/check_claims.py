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
SEARCH_FILES = ("docs/roadmap.md", "README.md", "CLAUDE.md")
FILE_TOKEN = re.compile(r"[\w./-]+\.[A-Za-z0-9]+")
DATA_EXTENSIONS = {".csv", ".json", ".npy", ".npz", ".png", ".pdf", ".svg"}

# A `theorem` claim's evidence must point at something checkable: a path
# under one of these directories, or a Lean declaration name -- and the
# location has to actually exist, not merely look like one (shape alone lets
# a fabricated `theory/nonexistent.md` or an invented Lean name pass).
THEOREM_PATH_TOKEN_RE = re.compile(r"(?:theory|paper|lean)/[\w./-]+")
# A dotted, namespaced identifier such as `NonLinearNumberSystems.Fibonacci.foo`
# -- the shape of a Lean declaration name, as distinct from a file path (no
# slash) or an ordinary sentence (no dots between words).
LEAN_DECL_RE = re.compile(
    r"\b[A-Z][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*){1,}\b"
)
LEAN_DECL_KEYWORDS = ("theorem", "lemma", "def")

# Statuses that must not be asserted as established without a hedge.
UNSETTLED_STATUS = {"conjecture", "heuristic"}

# Hedge markers required in any paragraph that cites a conjecture/heuristic claim.
# English and German, because docs/roadmap.md is in German.
HEDGE_MARKERS = (
    "conjecture", "heuristic", "not established", "not proved", "unproven",
    "expected", "supported", "supports", "suggests", "numerical support",
    "assumption", "konjektur", "heuristik", "nicht bewiesen", "erwartet",
    "stütze", "vermutung",
)


def _extract_theorem_path_tokens(evidence: str) -> list[str]:
    """Extract theory/, paper/, lean/-prefixed path tokens from evidence text,
    stripping trailing sentence punctuation a regex match would otherwise
    swallow (e.g. "...theory/x.md." at the end of a sentence)."""
    tokens = []
    for m in THEOREM_PATH_TOKEN_RE.finditer(evidence):
        tok = m.group(0).rstrip(").,;:'\"")
        if tok:
            tokens.append(tok)
    return tokens


def _lean_project_files(root: Path) -> list[Path]:
    """`.lean` files under `lean/`, excluding `lean/.lake/` (vendored
    dependencies -- a declaration only "found" there is not this project's)."""
    lean_dir = root / "lean"
    if not lean_dir.exists():
        return []
    return [p for p in lean_dir.rglob("*.lean") if ".lake" not in p.parts]


def _lean_declaration_exists(root: Path, decl: str) -> bool:
    """Honest check for a Lean declaration reference: does some project
    `.lean` file actually declare a `theorem`/`lemma`/`def` with this name?
    Uses the last dotted segment, since the file text is unlikely to spell
    out the full namespace-qualified name at the declaration site."""
    last = decl.rsplit(".", 1)[-1]
    pattern = re.compile(
        r"\b(?:" + "|".join(LEAN_DECL_KEYWORDS) + r")\s+" + re.escape(last) + r"\b"
    )
    for f in _lean_project_files(root):
        try:
            text = f.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        if pattern.search(text):
            return True
    return False


def _theorem_evidence_problem(root: Path, cid: str, evidence: str) -> str | None:
    """Return a problem string for a `theorem` claim's evidence, or None if
    it checks out. A `theory/`, `paper/`, or `lean/` path must exist on disk;
    a bare Lean declaration name must be found declared in a project `.lean`
    file. Shape alone (matching the pattern) is not enough -- both the
    pattern and the referent must hold."""
    path_tokens = _extract_theorem_path_tokens(evidence)
    if path_tokens:
        for tok in path_tokens:
            if not (root / tok).is_file():
                return (
                    f"claim '{cid}': status theorem but its evidence references "
                    f"'{tok}', which does not exist under the repo root"
                )
        return None

    decls = LEAN_DECL_RE.findall(evidence)
    if decls:
        if any(_lean_declaration_exists(root, d) for d in decls):
            return None
        return (
            f"claim '{cid}': status theorem but its evidence names a Lean "
            f"declaration that no file under lean/ (excluding lean/.lake) "
            f"actually declares"
        )

    return (
        f"claim '{cid}': status theorem but its evidence does not reference "
        f"a checkable proof location (an existing path under theory/, paper/, "
        f"or lean/, or a Lean declaration name found in lean/) -- a test "
        f"file or prose alone is not enough"
    )


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
        if claim.get("status") == "theorem":
            problem = _theorem_evidence_problem(
                root, claim.get("id"), claim.get("evidence", "")
            )
            if problem:
                problems.append(problem)

    status_by_id = {claim.get("id"): claim.get("status") for claim in claims}

    md_paths = []
    for directory in SEARCH_DIRS:
        base = root / directory
        if base.exists():
            md_paths.extend(sorted(base.rglob("*.md")))
    for rel in SEARCH_FILES:
        candidate = root / rel
        if candidate.exists():
            md_paths.append(candidate)

    for md in md_paths:
        text = md.read_text()
        for ref in REFERENCE.findall(text):
            if ref not in ids:
                problems.append(f"{md}: reference to unknown claim '{ref}'")
        problems.extend(_check_hedging(md, text, status_by_id))

    return problems


def _check_hedging(md: Path, text: str, status_by_id: dict) -> list[str]:
    """Flag paragraphs that cite a conjecture/heuristic claim with no hedge marker."""
    problems: list[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        lower = paragraph.lower()
        for ref in REFERENCE.findall(paragraph):
            status = status_by_id.get(ref)
            if status not in UNSETTLED_STATUS:
                continue
            if not any(marker in lower for marker in HEDGE_MARKERS):
                problems.append(
                    f"{md}: paragraph cites claim '{ref}' (status {status}) as "
                    f"established, with no hedge marker"
                )
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
