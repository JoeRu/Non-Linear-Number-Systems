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
SEARCH_FILES = ("docs/roadmap.md", "README.md", "CLAUDE.md", "docs/phase1.md")
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

# Unqualified universal quantifiers/modals. A `verified-numeric` claim is a
# measurement over a finite computed range; a paragraph citing one may report
# what was measured, but wording like "every"/"all"/"must" reads as a
# statement about all N, which the census this project runs never
# establishes. This is the recurring overclaim pattern (docs/risks.md R-005):
# it has recurred enough times, corrected by hand each time, that catching it
# needs to be mechanical rather than another manual pass.
UNIVERSAL_QUANTIFIER_WORDS = (
    "any", "every", "all", "never", "always", "must", "unavailable", "impossible",
    "jeder", "jede", "alle", "nie", "immer", "muss", "unmöglich",
)
_UNIVERSAL_QUANTIFIER_RE = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in UNIVERSAL_QUANTIFIER_WORDS) + r")\b",
    re.IGNORECASE,
)

# A paragraph carrying one of these is exempt: it has scoped its universal-
# sounding wording to the range that was actually measured.
RANGE_QUALIFIER_MARKERS = (
    "n <=", "n ≤", "over the measured range", "im gemessenen bereich",
    "in range", "observed", "gemessen",
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
    out the full namespace-qualified name at the declaration site.

    KNOWN LIMITATION, dormant: this is a text grep, not a Lean query. It does
    not exclude comments or string literals, so a commented-out
    `theorem foo`, a declaration under the wrong namespace, or a stale
    unbuilt file would all validate. No claim in theory/claims.yaml uses this
    route today (all current `theorem` claims cite a `theory/` path instead),
    so the gap is not blocking, but do not start relying on this path without
    fixing it first. Doing so properly means asking Lean itself (e.g. via
    `lake env lean --print-axioms` or an environment query), not grepping
    text -- that is its own design, not a quick patch here.
    """
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
        root_resolved = root.resolve()
        # A candidate allowed root only counts if it is itself contained in
        # the repo -- otherwise theory/, paper/, or lean/ being a symlink to
        # somewhere outside the repository would make that outside location
        # an "allowed root" and let an external file pass.
        allowed_roots = [
            r for r in ((root / d).resolve() for d in ("theory", "paper", "lean"))
            if r.is_relative_to(root_resolved)
        ]
        for tok in path_tokens:
            target = (root / tok).resolve()
            if not any(target.is_relative_to(a) for a in allowed_roots):
                return (
                    f"claim '{cid}': status theorem but its evidence references "
                    f"'{tok}', which resolves outside theory/, paper/ and lean/"
                )
            if not target.is_file():
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
        problems.extend(_check_universal_claims(md, text, status_by_id))

    return problems


def _check_universal_claims(md: Path, text: str, status_by_id: dict) -> list[str]:
    """Flag paragraphs that cite a `verified-numeric` claim with an
    unqualified universal quantifier/modal and no explicit range
    qualification.

    Hedging (`_check_hedging`) only fires for `conjecture`/`heuristic`
    claims, so a `verified-numeric` claim -- a measurement over a finite
    range -- can carry universal wording ("every", "must", ...) right past
    it. This catches that case. It cannot catch a paragraph with no
    `{claim:...}` token at all, which is why an untethered empirical
    statement should get a ledger entry and a citation in the first place.
    """
    problems: list[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        cited_verified = [
            ref for ref in REFERENCE.findall(paragraph)
            if status_by_id.get(ref) == "verified-numeric"
        ]
        if not cited_verified:
            continue
        # Collapse hard line-wraps to spaces before matching a multi-word
        # marker: a paragraph's prose is wrapped across source lines, so a
        # phrase like "over the measured range" can have a newline where the
        # rendered text has a space.
        lower = re.sub(r"\s+", " ", paragraph.lower())
        if any(marker in lower for marker in RANGE_QUALIFIER_MARKERS):
            continue
        match = _UNIVERSAL_QUANTIFIER_RE.search(paragraph)
        if not match:
            continue
        for ref in cited_verified:
            problems.append(
                f"{md}: paragraph cites claim '{ref}' (status verified-numeric) "
                f"with unqualified universal word '{match.group(0)}' and no "
                f"range qualification"
            )
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
