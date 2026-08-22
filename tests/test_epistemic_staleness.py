"""Catch stale statements about this repository's own proof state in code.

`scripts/check_claims.py` reads Markdown only, and only under `theory/`,
`docs/phases/`, `paper/` and five named files. Four separate stale epistemic
statements have now been found *outside* that reach -- in a `.py` docstring,
in a `.sh` echo, and in a skill file -- each one surviving because nothing
mechanical looks there. This is the cheap complement: a phrase grep over the
source trees the claim checker does not read *as files*.

This file's own scope -- `capfib/`, `scripts/` and `.claude/skills/` --
deliberately stops short of also scanning `docs/`, `theory/` and `paper/`,
even though those are exactly the trees `check_claims.py` reads. That is
not because `check_claims.py` already screens that Markdown for stale
proof-state language: it has no `sorry`-related pattern at all, only
claim-ledger and universal-quantifier checks, so a "still a `sorry`"
sentence written into e.g. `docs/phases/phase2_bounds.md` would be caught by
neither guard today. The trees are left out of this file only to avoid a
second copy of the same patterns; that Markdown blind spot is real and
unmitigated, not covered elsewhere.

It is deliberately narrow. It matches assertions *about the current state of
this project's proofs* ("still a `sorry`", "modulo sorry", "not yet proved",
"remains a conjecture"), because those are the sentences that go stale the
moment a proof lands. It does NOT match the bare words `conjecture`,
`heuristic`, `unproven` or `not proved`: those are this project's own status
vocabulary (`theory/claims.yaml` statuses, `check_claims.py`'s
`HEDGE_MARKERS`, the `claim-ledger` skill's reference table), they occur 21
times legitimately in the scanned trees, and a check that fires on all of
them would be turned off rather than obeyed.

So: a docstring that says "C5 is a conjecture" in plain words is still not
caught here, and a reviewer is still the backstop for that. What is caught is
the recurring, mechanical shape -- a sentence asserting something is *not yet*
proved, or *still* carries a `sorry`, after it has been.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Trees `scripts/check_claims.py` never reads. `tests/` is excluded because
# this file necessarily contains every pattern it searches for.
SCAN_GLOBS = (
    "capfib/**/*.py",
    "scripts/**/*.py",
    "scripts/**/*.sh",
    ".claude/skills/**/*.md",
    ".claude/skills/**/*.sh",
    ".claude/skills/**/*.py",
)

# Each entry is (compiled pattern, what a hit means). Matching is
# case-insensitive and line-by-line, so the report can name a line number.
STALE_PROOF_STATE_PATTERNS = (
    (
        re.compile(r"still\b[^.\n]{0,40}\bsorr(?:y|ies)\b", re.IGNORECASE),
        "asserts something is still a `sorry`",
    ),
    (
        re.compile(r"\bmodulo\s+`?sorr(?:y|ies)\b", re.IGNORECASE),
        "qualifies a build or a proof as holding only 'modulo sorry'",
    ),
    (
        re.compile(
            r"\b(?:is|are|remains?|contains?|has|have|carr(?:y|ies))\b"
            r"[^.\n]{0,25}\ba\s+`?sorr(?:y|ies)\b",
            re.IGNORECASE,
        ),
        "asserts a declaration is/contains/carries a `sorry`",
    ),
    (
        re.compile(r"\bsorry-filled\b", re.IGNORECASE),
        "describes the development as sorry-filled",
    ),
    (
        re.compile(
            r"\bnot\s+yet\s+(?:been\s+)?(?:proved|proven|formali[sz]ed|discharged)\b",
            re.IGNORECASE,
        ),
        "asserts something is not yet proved",
    ),
    (
        re.compile(
            r"\b(?:still|remains?)\s+(?:a|an)\s+(?:conjecture|heuristic)\b",
            re.IGNORECASE,
        ),
        "asserts a result is still a conjecture or heuristic",
    ),
    (
        re.compile(r"\b(?:only|merely|just)\s+(?:a|an)\s+conjecture\b", re.IGNORECASE),
        "downgrades a result to 'only a conjecture'",
    ),
    (
        re.compile(r"\b(?:still|remains?)\s+(?:open|unproved|unproven)\b", re.IGNORECASE),
        "asserts a question is still/remains open or unproved",
    ),
)


def _scanned_files():
    files = []
    for pattern in SCAN_GLOBS:
        files.extend(sorted(ROOT.glob(pattern)))
    return [f for f in files if "__pycache__" not in f.parts]


def test_the_scan_actually_reaches_files():
    """A silent glob failure would make every assertion below vacuous."""
    files = _scanned_files()
    names = {f.relative_to(ROOT).as_posix() for f in files}
    assert "capfib/stats.py" in names
    assert "scripts/check_claims.py" in names
    assert "scripts/run_lean.sh" in names
    assert any(n.startswith(".claude/skills/") for n in names)


def test_no_stale_proof_state_statements_in_source_trees():
    """The Lean development has no `sorry`; no file may say otherwise."""
    problems = []
    for path in _scanned_files():
        try:
            text = path.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for pattern, meaning in STALE_PROOF_STATE_PATTERNS:
                if pattern.search(line):
                    problems.append(
                        f"{path.relative_to(ROOT)}:{number}: {meaning} -- "
                        f"{line.strip()}"
                    )
    assert not problems, (
        "stale statement(s) about this project's proof state:\n  "
        + "\n  ".join(problems)
    )


@pytest.mark.parametrize(
    "line",
    [
        "completeness is still a `sorry` in the Lean development",
        'echo "All theorems type-check (modulo sorry)."',
        "# exists_numeral_of_le is a sorry",
        "the limit is not yet proved to exist",
        "C5 remains a conjecture",
        "this is only a conjecture",
        "whether the constant exists is still open",
        "the development still contains sorries",
        "whether the bound holds remains open",
        "any statement added here without a proof carries a `sorry`",
    ],
)
def test_patterns_fire_on_the_shapes_they_target(line):
    assert any(p.search(line) for p, _ in STALE_PROOF_STATE_PATTERNS)


@pytest.mark.parametrize(
    "line",
    [
        # `check_claims.py`'s own status vocabulary and hedge markers.
        'VALID_STATUS = {"cited", "heuristic", "conjecture", "theorem", "open"}',
        '"conjecture", "heuristic", "not established", "not proved", "unproven",',
        "# Hedge markers required in any paragraph citing a conjecture claim.",
        # A legitimate description of what a status means.
        "| `conjecture` | Believed, not derived |",
        # An accurate historical note, correctly scoped.
        "0.51952 (conjectured when this gate was written; proved in Phase 2)",
        # An accurate current statement about a genuinely open question.
        "The secondary term is open; no proof of its constant is claimed.",
    ],
)
def test_patterns_do_not_fire_on_legitimate_vocabulary(line):
    assert not any(p.search(line) for p, _ in STALE_PROOF_STATE_PATTERNS)
