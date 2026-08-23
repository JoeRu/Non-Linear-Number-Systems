"""Quoted figures must match the artifacts that generated them, in every phase.

Risk R-002: narrative documents carry hand-copied numbers while `data/` is
largely gitignored, so regeneration cannot update the prose and drift is
silent. Prose carries `<literal> {fig:key}`; this resolves each key against
the phase's figures file, formats the stored value at its recorded precision,
and requires an exact string match.

Table-driven rather than per-phase: a copy of this file for each phase would
double a guard that has already been silently disabled once, by a
`pytest.skip` on an absent sibling document.
"""

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# (name, figures file, documents, tags_required).
#
# `tags_required` is data, not a constant, because a document with zero tags
# is indistinguishable from one whose tags were stripped -- both must fail
# (see `_check_documents`'s `require_tags`). Both phases are now tagged, so
# both rows read `True` here; the field stays per-row rather than becoming a
# bare boolean constant because a phase's documents can, in general, be
# added and tagged on different schedules -- Phase 1 itself sat at `False`
# while its documents were untagged, and this row is what got flipped once
# they were (`docs/phase1.md`, `docs/phases/phase1_report.md`).
#
# That flip is not automatic, and forgetting it half-way is worse than
# forgetting it outright: if one of a phase's documents gets tagged and the
# other does not, with the row's flag still False, the untagged document's
# hand-copied numbers become permanently unchecked -- and every test stays
# green, because `tags_required=False` is exactly what tells this file not to
# look. `test_tags_required_matches_document_state` below is the mechanical
# check that catches that the moment it happens, so this comment is a second
# lock, not the only one.
#
# `docs/roadmap.md` is a Phase 1 document for this purpose: it quotes the
# Phase 1 census fraction three times in German prose, which is exactly the
# "narrative document contains hand-copied numbers" shape risk R-002 names.
# Registering it here is what lets those literals carry a `{fig:}` tag at all.
PHASES = (
    ("phase1", ROOT / "data" / "phase1_figures.json",
     ("docs/phase1.md", "docs/phases/phase1_report.md", "docs/roadmap.md"),
     True),
    ("phase2", ROOT / "data" / "phase2_figures.json",
     ("docs/phase2.md", "docs/phases/phase2_bounds.md"), True),
)

# Figure keys a phase generates but that no registered document quotes, with
# the reason. This is an allowlist, not a tolerance: the check below asserts
# the unquoted set is *exactly* this, so a newly generated key that nobody
# quotes fails, and a key here that later gets quoted fails too (remove it
# then). Before this was an assertion it was a `print`, and
# `figure keys generated but never quoted: ['n-max']` scrolled past on every
# run for as long as `docs/phase1.md` claimed in prose that every generated
# figure was tagged -- the statement and the evidence against it were in the
# same test output.
KEYS_KNOWINGLY_UNQUOTED = {
    # `residual-centre` is the mean residual over *all* sampled t, including
    # the pre-asymptotic t=10 point. The Phase 2 documents quote
    # `residual-asymptotic-centre` (t >= 20) instead, deliberately: the
    # full-sample mean mixes regimes. The key stays in the artifact because
    # `residual-full-spread`, which the documents do quote, is only
    # interpretable next to it.
    "phase2": frozenset({"residual-centre"}),
}

TAG = re.compile(r"([-+]?[\d][\d,]*(?:\.\d+)?)\s*\{fig:([a-z0-9-]+)\}")
BARE_TAG = re.compile(r"\{fig:([a-z0-9-]+)\}")


def _load(figures_path):
    """Load a phase's generated figures.

    The figures file is tracked (see .gitignore), so its absence is a
    deleted file, not an ungenerated one -- and while this skipped, deleting
    it turned all four drift tests into `N skipped`, which is green. The
    R-002 drift detector must fail when its data is gone, not vanish.

    Args:
        figures_path: path to the phase's `*_figures.json` file.

    Returns:
        dict: The parsed contents of the figures file, keyed by figure key,
        each mapping to {value, precision, description}.

    Raises:
        AssertionError: if the tracked file is absent or empty.
    """
    assert figures_path.exists(), (
        f"{figures_path.relative_to(ROOT)} absent -- it is tracked, so this "
        f"means it was deleted. Restore it from git, or regenerate with the "
        f"phase's run script."
    )
    figures = json.loads(figures_path.read_text())
    assert figures, (
        f"{figures_path.relative_to(ROOT)} is empty: every {{fig:key}} "
        f"lookup would then fail to resolve, so there is nothing to check "
        f"drift against"
    )
    return figures


def _format(entry):
    """Render a stored figure at its recorded precision.

    A value stored as a string is passed through unchanged. Figures that
    exceed a double's exact-integer range are serialised as strings so a
    JSON consumer backed by doubles cannot silently round them, and rounding
    such a value here to "render" it would reintroduce exactly that loss.
    """
    value = entry["value"]
    if isinstance(value, str):
        return value
    precision = entry["precision"]
    if precision == 0:
        return str(int(round(value)))
    return f"{value:.{precision}f}"


def _split_by_existence(root, documents):
    """Split `documents` into those present under `root` and those absent.

    Documents are written by different tasks and land at different times,
    so at any moment some may not exist. Absence of one must not affect the
    checking of another -- see
    `test_a_missing_document_does_not_disable_a_present_one` for why this is
    a separate function rather than an inline `if` in the loop.

    Args:
        root: repository root to resolve the relative paths against.
        documents: an iterable of repo-relative paths.

    Returns:
        tuple[list[str], list[str]]: (present, missing), each preserving the
        order of `documents`.
    """
    present, missing = [], []
    for relative in documents:
        (present if (root / relative).exists() else missing).append(relative)
    return present, missing


def _check_documents(named_texts, figures, require_tags=True):
    """Assert every {fig:KEY} in each document is a full, matching tag.

    Ruling A (task 7): a bare tag is checked against the *exact set of end
    offsets* where a full ``<literal> {fig:key}`` match ends -- not a window
    around some other tag's position -- so a tag cannot be excused by a
    number that actually belongs to a different, nearby tag.

    `require_tags` (default on) additionally rejects a document that carries
    no tags at all. Without it the check was vacuous in the one direction
    that matters most: a document whose tags had been stripped -- by an
    edit, a bad merge, or a rewrite that dropped the `{fig:}` syntax --
    passed, and the only trace was an informational "figure keys generated
    but never quoted" line that nothing asserts on.

    Args:
        named_texts: an iterable of (label, text) pairs.
        figures: the parsed figures mapping.
        require_tags: require at least one full tag per document.

    Returns:
        set[str]: the figure keys that were quoted.

    Raises:
        AssertionError: on a bare tag, an unknown key, a drifted literal, or
            (with `require_tags`) a document carrying no tags.
    """
    seen = set()
    for relative, text in named_texts:
        tag_ends = {m.end() for m in TAG.finditer(text)}
        # Bare tags first: a document whose only tag is bare gets the specific
        # "bare tag" diagnosis rather than the blanket "no tags" one.
        for bare in BARE_TAG.finditer(text):
            assert bare.end() in tag_ends, (
                f"{relative}: {{fig:{bare.group(1)}}} is not preceded by a "
                f"numeric literal (bare tag, no correspondence to check)"
            )
        if require_tags:
            assert tag_ends, (
                f"{relative}: no {{fig:key}} tag anywhere in the document, so "
                f"nothing in it is checked against the figures file. "
                f"A report with no tags is a disabled drift detector, "
                f"not a document without figures"
            )

        for match in TAG.finditer(text):
            literal, key = match.group(1).replace(",", ""), match.group(2)
            assert key in figures, f"{relative}: unknown figure key {key!r}"
            expected = _format(figures[key])
            assert literal == expected, (
                f"{relative}: {{fig:{key}}} quoted as {literal!r} "
                f"but the figures file says {expected!r} -- regenerate "
                f"the phase's data and update the prose"
            )
            seen.add(key)
    return seen


@pytest.mark.oracle_gate
@pytest.mark.parametrize("phase", PHASES, ids=lambda p: p[0])
def test_every_tag_resolves_and_matches(phase):
    """Every {fig:KEY} in a phase's docs that exist must resolve to a known
    key and quote that key's value at its recorded precision.

    The test skips only when *none* of the documents exist. An earlier
    version skipped the whole test on the first absent document: while
    `docs/phase2.md` was unwritten, this check silently did not run against
    `docs/phases/phase2_bounds.md` either, even though that file was present
    and full of tags. The drift detector for risk R-002 was disabled by the
    absence of an unrelated file. Absent documents are now reported and
    stepped over, not treated as grounds to stop.
    """
    name, figures_path, documents, tags_required = phase
    figures = _load(figures_path)
    present, missing = _split_by_existence(ROOT, documents)
    assert not missing, (
        f"{name} document(s) absent: {', '.join(missing)}. All of {name}'s "
        f"documents are tracked, so an absent one is a deletion, not a "
        f"document that has not been written yet -- and skipping over it "
        f"would silently retire the drift check for everything in it"
    )
    print(f"checked: {', '.join(present)}")

    seen = _check_documents(
        ((relative, (ROOT / relative).read_text()) for relative in present),
        figures,
        require_tags=tags_required,
    )
    unused = set(figures) - seen
    expected_unused = KEYS_KNOWINGLY_UNQUOTED.get(name, frozenset())
    assert unused == expected_unused, (
        f"{name}: figure keys generated but never quoted in any registered "
        f"document: {sorted(unused - expected_unused)}; keys allowlisted as "
        f"unquoted that are in fact quoted now: "
        f"{sorted(expected_unused - unused)}. A generated key that no "
        f"document quotes is a number the phase computed and then dropped on "
        f"the floor -- quote it with a {{fig:key}} tag, or record it in "
        f"KEYS_KNOWINGLY_UNQUOTED with the reason"
    )


@pytest.mark.parametrize("phase", PHASES, ids=lambda p: p[0])
def test_a_drifted_literal_is_caught(phase, tmp_path):
    """The check must fail on a wrong number, or it tests nothing."""
    _name, figures_path, _documents, _tags_required = phase
    figures = _load(figures_path)
    key = next(iter(figures))
    wrong = _format(figures[key]) + "9"
    text = f"The value is {wrong} {{fig:{key}}}."
    match = TAG.search(text)
    assert match is not None
    assert match.group(1) != _format(figures[key])
    with pytest.raises(AssertionError):
        _check_documents([("fake.md", text)], figures)


@pytest.mark.parametrize("phase", PHASES, ids=lambda p: p[0])
def test_a_missing_document_does_not_disable_a_present_one(phase, tmp_path):
    """An absent document must not silence the check on a present one.

    This is the property the original in-loop `pytest.skip` lost, and it
    lost it silently: the run reported SKIPPED, not FAILED, so nothing drew
    attention to the fact that a document full of tags had gone unchecked.
    The fixture below reproduces exactly that arrangement -- the *first*
    entry of `documents` absent, the second present and carrying a drifted
    literal -- and requires the drift to be caught anyway. Written for any
    row length, not exactly two: the phase1 row grew a third document
    (`docs/roadmap.md`) and a fixture hardcoded to two entries would have
    had to be edited to keep passing, which is how a fixture stops
    reproducing the arrangement it was written for.
    """
    _name, figures_path, documents, _tags_required = phase
    figures = _load(figures_path)
    key = next(iter(figures))
    wrong = _format(figures[key]) + "9"

    target = tmp_path / documents[1]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"The value is {wrong} {{fig:{key}}}.")
    assert not (tmp_path / documents[0]).exists()

    present, missing = _split_by_existence(tmp_path, documents)
    assert present == [documents[1]]
    assert missing == [d for d in documents if d != documents[1]]

    with pytest.raises(AssertionError, match="quoted as"):
        _check_documents(
            ((relative, (tmp_path / relative).read_text()) for relative in present),
            figures,
        )


@pytest.mark.parametrize("phase", PHASES, ids=lambda p: p[0])
def test_a_document_with_no_tags_is_caught(phase):
    """Zero tags must fail, not pass vacuously.

    Found by the pre-PR gate: a document with no `{fig:}` tags satisfied
    every assertion in `_check_documents`, and the only signal was the
    unused-keys line, which is printed and never asserted on. A stripped
    document therefore read as a clean pass.
    """
    _name, figures_path, _documents, _tags_required = phase
    figures = _load(figures_path)
    with pytest.raises(AssertionError, match="no .fig:key. tag"):
        _check_documents(
            [("fake.md", "Prose with numbers like 3.14 and no tags at all.")],
            figures,
        )


@pytest.mark.oracle_gate
@pytest.mark.parametrize("phase", PHASES, ids=lambda p: p[0])
def test_every_real_document_carries_tags(phase):
    """And the real documents must each carry at least one, not merely be
    checkable in principle -- for phases where tags are required.

    Both phases are `tags_required=True` now (Phase 1's documents were tagged
    to close the open half of risk R-002), so this asserts for real on both.
    The `if tags_required` guard stays rather than being dropped, so a future
    phase added with `tags_required=False` -- documents not yet written or
    tagged -- still runs this case and passes vacuously instead of being
    skipped, and a document that starts tagged but later loses its tags is
    still caught by `test_every_tag_resolves_and_matches`'s `require_tags`
    check either way.
    """
    _name, figures_path, documents, tags_required = phase
    figures = _load(figures_path)
    for relative in documents:
        text = (ROOT / relative).read_text()
        if tags_required:
            assert TAG.search(text), f"{relative} carries no {{fig:}} tag"


@pytest.mark.parametrize("phase", PHASES, ids=lambda p: p[0])
def test_a_bare_tag_is_caught(phase):
    """A tag with no numeric literal before it has no correspondence to
    check, and must fail rather than pass vacuously."""
    _name, figures_path, _documents, _tags_required = phase
    figures = _load(figures_path)
    key = next(iter(figures))
    with pytest.raises(AssertionError, match="bare tag"):
        _check_documents([("fake.md", f"The value is {{fig:{key}}}.")], figures)


@pytest.mark.oracle_gate
@pytest.mark.parametrize("phase", PHASES, ids=lambda p: p[0])
def test_tags_required_matches_document_state(phase):
    """`tags_required=False` must not survive a document actually getting
    tagged.

    This is the mechanical version of the comment above `PHASES`: a code
    comment asking a later task to remember to flip a flag is precisely the
    enforcement that has already failed on this project four times (see
    `tests/conftest.py`'s history). If a phase is marked
    `tags_required=False` but one of its documents already carries a
    `{fig:}` tag, that document's numbers are being quoted right now while
    nothing checks them for drift -- and every other test in this file
    stays green, because `require_tags=False` is exactly the setting that
    tells `_check_documents` not to look. This test looks instead, directly
    at the real files, independent of `require_tags`.

    Once a phase's flag is `True` this test has nothing to add -- the rest
    of the suite already enforces tagging for it -- so it passes trivially
    for `tags_required=True` phases.
    """
    name, _figures_path, documents, tags_required = phase
    if tags_required:
        return
    tagged = [
        relative for relative in documents
        if (ROOT / relative).exists() and TAG.search((ROOT / relative).read_text())
    ]
    assert not tagged, (
        f"{name}: tags_required is False in PHASES, but {', '.join(tagged)} "
        f"already carries a {{fig:}} tag. Its numbers are quoted with nothing "
        f"checking them for drift. Set the {name} row's tags_required to True "
        f"in tests/test_figure_tags.py now, not after every document in the "
        f"phase is tagged -- otherwise the untagged sibling's numbers stay "
        f"unchecked indefinitely while this whole file reports green"
    )


# --- Discovery: a document that quotes a figure but is not in PHASES -------
#
# Everything above assumes a document worth checking is already named in a
# `PHASES` row. Nothing about `PHASES` or `_check_documents` discovers a
# document on its own -- it is a closed, hardcoded tuple, and a future
# phase's narrative document quoting real generated figures is exactly as
# unprotected as if it were never written, until someone remembers to add a
# row for it. This was demonstrated directly during review: a scratch file
# `docs/phases/phase3_scratch.md` containing `999 {fig:n-max}` -- a wrong
# value against a real n_max of `1000000` -- made every test in this file
# pass, because nothing here ever looks at a document PHASES does not name.
#
# Directories that legitimately quote a `{fig:...}` figure without being
# registered. Kept short and explicit, not a broad pattern, per review:
#   - `docs/superpowers/`: dated specs and plans are historical snapshots of
#     prose written *at* a past commit (some genuinely embed real,
#     literal-backed tags, e.g. the plan for this very task) -- registering
#     them would mean validating a finished plan's numbers forever after the
#     work it describes is done.
#
# Only prefixes that lie *under* `DOC_SEARCH_ROOTS` can do anything here: the
# walk below never leaves those roots, so an entry naming a tree outside them
# excludes nothing and merely reads as though the walk were repository-wide.
# `.superpowers/` (the session scratch workspace) was such an entry and has
# been dropped for that reason -- it is not reachable, and keeping it
# described a mechanism that does not exist.
UNREGISTERED_DOC_PREFIXES = ("docs/superpowers/",)

# Root files/directories that can hold narrative prose quoting generated
# figures. Not the whole repository -- walking `.venv/`, `.git/`, or
# `capfib.egg-info/` would be slow and finds nothing relevant. Extend this
# list the day a real document appears somewhere new; that is a one-line
# change, not a redesign.
#
# `paper/` is in the list because it is the publication target: an unbound
# number costs more there than anywhere else in the repository, and
# `scripts/check_claims.py` has always treated it as a prose tree
# (`SEARCH_DIRS`). The two lists disagreeing about where prose lives is the
# same defect this file exists to catch, so
# `test_doc_search_roots_cover_the_claim_checker_trees` below asserts they
# agree rather than leaving it to memory.
DOC_SEARCH_ROOTS = ("docs", "theory", "paper", "README.md", "CLAUDE.md")

# Prose extensions to walk. `.tex` is here for `paper/`: a LaTeX source is a
# narrative document like any other, and a `{fig:...}` tag in it is checked
# by the same rule.
DOC_SUFFIXES = (".md", ".tex")


def _registered_documents():
    """The set of document paths named by some `PHASES` row, repo-relative
    with forward slashes -- the same format `DOC_SEARCH_ROOTS` files are
    reported in below, so a straight set-membership check is enough."""
    return {doc for _name, _figs, docs, _req in PHASES for doc in docs}


def _discoverable_documents():
    """Every `DOC_SUFFIXES` file under `DOC_SEARCH_ROOTS`, repo-relative
    (forward-slash), excluding `UNREGISTERED_DOC_PREFIXES`.

    Returns:
        A sorted list of repo-relative path strings.
    """
    found = []
    for root_name in DOC_SEARCH_ROOTS:
        root_path = ROOT / root_name
        if root_path.is_file():
            candidates = [root_path] if root_path.suffix in DOC_SUFFIXES else []
        elif root_path.is_dir():
            candidates = sorted(
                p for suffix in DOC_SUFFIXES for p in root_path.rglob(f"*{suffix}")
            )
        else:
            continue
        for path in candidates:
            relative = path.relative_to(ROOT).as_posix()
            if any(relative.startswith(prefix) for prefix in UNREGISTERED_DOC_PREFIXES):
                continue
            found.append(relative)
    return sorted(found)


@pytest.mark.oracle_gate
def test_every_tagged_document_is_registered():
    """A document that quotes a real, literal-backed `{fig:...}` figure must
    be named by some `PHASES` row, or nothing ever checks it for drift.

    Deliberately uses `TAG` (literal + tag), not `BARE_TAG`, as the
    "quotes a figure" signal -- the same distinction `_check_documents`
    draws elsewhere in this file. `docs/risks.md` mentions the bare
    `{fig:key}` syntax three times while describing this very mechanism in
    prose (e.g. "a bare `{fig:key}` with no literal in front of it fails
    too"); none of those are preceded by a numeric literal, so `TAG` does
    not match them and `docs/risks.md` is correctly not flagged for needing
    a `PHASES` row it has no figures file to check against. A document that
    *does* carry a literal-backed tag is, by construction, a document whose
    number can silently drift the moment `PHASES` fails to name it -- which
    is the exact gap this test closes.
    """
    registered = _registered_documents()
    unregistered = []
    for relative in _discoverable_documents():
        text = (ROOT / relative).read_text()
        if TAG.search(text) and relative not in registered:
            unregistered.append(relative)
    assert not unregistered, (
        "document(s) quote a generated {fig:...} figure but no PHASES row "
        "in tests/test_figure_tags.py names them, so nothing checks them "
        "for drift: " + ", ".join(unregistered) + " -- add a PHASES row (or "
        "add the document to an existing phase's row) that names it, "
        "pointing at the figures file it should be checked against"
    )


def _claim_checker_prose_paths():
    """The prose trees `scripts/check_claims.py` reads, as repo-relative
    forward-slash strings.

    Imported from the script rather than restated, so the two lists cannot be
    kept in step by memory alone.
    """
    scripts_dir = str(ROOT / "scripts")
    sys.path.insert(0, scripts_dir)
    try:
        import check_claims  # noqa: PLC0415

        return tuple(check_claims.SEARCH_DIRS) + tuple(check_claims.SEARCH_FILES)
    finally:
        # Leaving the entry behind makes later imports in the same session
        # order-dependent on whether this test ran.
        try:
            sys.path.remove(scripts_dir)
        except ValueError:
            pass


def test_doc_search_roots_cover_the_claim_checker_trees():
    """Everywhere `scripts/check_claims.py` looks for prose must be walked
    here too.

    The repository held two hardcoded answers to "where does narrative prose
    live" -- `DOC_SEARCH_ROOTS` in this file and `SEARCH_DIRS`/`SEARCH_FILES`
    in `scripts/check_claims.py` -- and they disagreed: `paper/` was a prose
    tree for the claim checker and invisible to the drift discovery, which is
    the tree where an unbound number costs the most. Two hardcoded lists
    drifting apart is the defect this branch fixed twice already
    (`tests/conftest.py`'s `GATE_MODULES`, `PHASES` itself), so it is asserted
    rather than remembered.

    Coverage is one-directional on purpose. Every claim-checker path must be
    under some `DOC_SEARCH_ROOTS` entry; the converse is not required,
    because this file walks whole trees (`docs/`) where the claim checker
    names individual files inside them (`docs/roadmap.md`), and walking more
    prose for figure tags than for claim references is not a defect.
    """
    roots = DOC_SEARCH_ROOTS
    uncovered = [
        path for path in _claim_checker_prose_paths()
        if not any(path == r or path.startswith(r + "/") for r in roots)
    ]
    assert not uncovered, (
        "scripts/check_claims.py treats these as prose trees but "
        "DOC_SEARCH_ROOTS in tests/test_figure_tags.py does not walk them, "
        "so a {fig:...} tag in one of them would never be discovered: "
        + ", ".join(uncovered)
    )
