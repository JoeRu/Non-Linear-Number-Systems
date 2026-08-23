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
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# (name, figures file, documents, tags_required).
#
# `tags_required` is data, not a constant, because the two phases are at
# different points in the tagging lifecycle right now: Phase 2's documents
# are already tagged, and a document with zero tags is indistinguishable
# from one whose tags were stripped -- both must fail (see
# `_check_documents`'s `require_tags`). Phase 1's documents carry no tags
# yet; a future task adds them. Marking that phase `tags_required=False` lets
# its cases run and pass honestly in the meantime, instead of either (a)
# hard-failing on a gap this task was not asked to close, or (b) special-
# casing phase1 in the test bodies. When Phase 1's documents are tagged,
# flipping this to True is the same kind of data change that adding a new
# phase is -- not a change to test logic.
#
# That flip is not automatic, and forgetting it half-way is worse than
# forgetting it outright: if one of a phase's documents gets tagged and the
# other does not, with the row's flag still False, the untagged document's
# hand-copied numbers become permanently unchecked -- and every test stays
# green, because `tags_required=False` is exactly what tells this file not to
# look. `test_tags_required_matches_document_state` below is the mechanical
# check that catches that the moment it happens, so this comment is a second
# lock, not the only one.
PHASES = (
    ("phase1", ROOT / "data" / "phase1_figures.json",
     ("docs/phase1.md", "docs/phases/phase1_report.md"), False),
    ("phase2", ROOT / "data" / "phase2_figures.json",
     ("docs/phase2.md", "docs/phases/phase2_bounds.md"), True),
)

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
    """Render a stored figure at its recorded precision."""
    precision = entry["precision"]
    if precision == 0:
        return str(int(round(entry["value"])))
    return f"{entry['value']:.{precision}f}"


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
    unused = sorted(set(figures) - seen)
    if unused:
        print(f"figure keys generated but never quoted: {unused}")


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
    literal -- and requires the drift to be caught anyway.
    """
    _name, figures_path, documents, _tags_required = phase
    figures = _load(figures_path)
    key = next(iter(figures))
    wrong = _format(figures[key]) + "9"

    target = tmp_path / documents[1]
    target.parent.mkdir(parents=True)
    target.write_text(f"The value is {wrong} {{fig:{key}}}.")
    assert not (tmp_path / documents[0]).exists()

    present, missing = _split_by_existence(tmp_path, documents)
    assert present == [documents[1]]
    assert missing == [documents[0]]

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

    Phase 1's documents carry no tags yet (`tags_required=False`); the next
    task adds them and flips that flag. Until then this case runs and
    passes vacuously rather than being skipped, so a future document that
    starts tagged but then loses its tags is still caught by
    `test_every_tag_resolves_and_matches`'s `require_tags` check, and this
    test still executes for the oracle-gate guard's purposes.
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
