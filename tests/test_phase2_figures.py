"""Every figure quoted in the Phase 2 documents must match the generated data.

Prose carries `<literal> {fig:key}`; this test resolves each key against
data/phase2_figures.json, formats the stored value at the recorded precision,
and requires an exact string match. Membership alone would not establish
correspondence (spec 7).
"""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "data" / "phase2_figures.json"
DOCUMENTS = ("docs/phase2.md", "docs/phases/phase2_bounds.md")

TAG = re.compile(r"([-+]?[\d][\d,]*(?:\.\d+)?)\s*\{fig:([a-z0-9-]+)\}")
BARE_TAG = re.compile(r"\{fig:([a-z0-9-]+)\}")


def _load():
    """Load the generated figures.

    `data/phase2_figures.json` is tracked (see .gitignore), so its absence is
    a deleted file, not an ungenerated one -- and while this skipped, deleting
    it turned all four drift tests into `4 skipped`, which is green. The R-002
    drift detector must fail when its data is gone, not vanish.

    Returns:
        dict: The parsed contents of data/phase2_figures.json, keyed by
        figure key, each mapping to {value, precision, description}.

    Raises:
        AssertionError: if the tracked file is absent or empty.
    """
    assert FIGURES.exists(), (
        f"{FIGURES.relative_to(ROOT)} absent -- it is tracked, so this means it "
        f"was deleted. Restore it from git, or regenerate with: "
        f".venv/bin/python scripts/run_phase2.py"
    )
    figures = json.loads(FIGURES.read_text())
    assert figures, (
        f"{FIGURES.relative_to(ROOT)} is empty: every {{fig:key}} lookup would "
        f"then fail to resolve, so there is nothing to check drift against"
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

    The Phase 2 documents are written by different tasks and land at
    different times, so at any moment some may not exist. Absence of one
    must not affect the checking of another -- see
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
    no tags at all. Without it the check was vacuous in the one direction that
    matters most: a document whose tags had been stripped -- by an edit, a bad
    merge, or a rewrite that dropped the `{fig:}` syntax -- passed, and the
    only trace was an informational "figure keys generated but never quoted"
    line that nothing asserts on. Every document in `DOCUMENTS` is a Phase 2
    report full of generated numbers; zero tags in one of them is a broken
    drift detector, not a tag-free document.

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
                f"nothing in it is checked against data/phase2_figures.json. "
                f"A Phase 2 report with no tags is a disabled drift detector, "
                f"not a document without figures"
            )

        for match in TAG.finditer(text):
            literal, key = match.group(1).replace(",", ""), match.group(2)
            assert key in figures, f"{relative}: unknown figure key {key!r}"
            expected = _format(figures[key])
            assert literal == expected, (
                f"{relative}: {{fig:{key}}} quoted as {literal!r} "
                f"but data/phase2_figures.json says {expected!r} -- regenerate "
                f"with scripts/run_phase2.py and update the prose"
            )
            seen.add(key)
    return seen


@pytest.mark.oracle_gate
def test_every_tag_resolves_and_matches():
    """Every {fig:KEY} in the Phase 2 docs that exist must resolve to a known
    key and quote that key's value at its recorded precision.

    The test skips only when *none* of the documents exist. An earlier
    version skipped the whole test on the first absent document, and
    `docs/phase2.md` is first in `DOCUMENTS`: while it was unwritten, this
    check silently did not run against `docs/phases/phase2_bounds.md`
    either, even though that file was present and full of tags. The drift
    detector for risk R-002 was disabled by the absence of an unrelated
    file. Absent documents are now reported and stepped over, not treated as
    grounds to stop.
    """
    figures = _load()
    present, missing = _split_by_existence(ROOT, DOCUMENTS)
    assert not missing, (
        f"Phase 2 document(s) absent: {', '.join(missing)}. Both are tracked "
        f"and both carry {{fig:}} tags, so an absent one is a deletion, not a "
        f"document that has not been written yet -- and skipping over it would "
        f"silently retire the drift check for everything in it"
    )
    print(f"checked: {', '.join(present)}")

    seen = _check_documents(
        ((relative, (ROOT / relative).read_text()) for relative in present), figures
    )
    unused = sorted(set(figures) - seen)
    if unused:
        print(f"figure keys generated but never quoted: {unused}")


def test_a_drifted_literal_is_caught(tmp_path):
    """The check must fail on a wrong number, or it tests nothing."""
    figures = _load()
    key = next(iter(figures))
    wrong = _format(figures[key]) + "9"
    text = f"The value is {wrong} {{fig:{key}}}."
    match = TAG.search(text)
    assert match is not None
    assert match.group(1) != _format(figures[key])
    with pytest.raises(AssertionError):
        _check_documents([("fake.md", text)], figures)


def test_a_missing_document_does_not_disable_a_present_one(tmp_path):
    """An absent document must not silence the check on a present one.

    This is the property the original in-loop `pytest.skip` lost, and it
    lost it silently: the run reported SKIPPED, not FAILED, so nothing drew
    attention to the fact that a document full of tags had gone unchecked.
    The fixture below reproduces exactly that arrangement -- the *first*
    entry of `DOCUMENTS` absent, the second present and carrying a drifted
    literal -- and requires the drift to be caught anyway.
    """
    figures = _load()
    key = next(iter(figures))
    wrong = _format(figures[key]) + "9"

    target = tmp_path / DOCUMENTS[1]
    target.parent.mkdir(parents=True)
    target.write_text(f"The value is {wrong} {{fig:{key}}}.")
    assert not (tmp_path / DOCUMENTS[0]).exists()

    present, missing = _split_by_existence(tmp_path, DOCUMENTS)
    assert present == [DOCUMENTS[1]]
    assert missing == [DOCUMENTS[0]]

    with pytest.raises(AssertionError, match="quoted as"):
        _check_documents(
            ((relative, (tmp_path / relative).read_text()) for relative in present),
            figures,
        )


def test_a_document_with_no_tags_is_caught():
    """Zero tags must fail, not pass vacuously.

    Found by the pre-PR gate: a document with no `{fig:}` tags satisfied every
    assertion in `_check_documents`, and the only signal was the unused-keys
    line, which is printed and never asserted on. A stripped document therefore
    read as a clean pass.
    """
    figures = _load()
    with pytest.raises(AssertionError, match="no .fig:key. tag"):
        _check_documents(
            [("fake.md", "Prose with numbers like 3.14 and no tags at all.")],
            figures,
        )


@pytest.mark.oracle_gate
def test_every_real_document_carries_tags():
    """And the real documents must each carry at least one, not merely be
    checkable in principle."""
    figures = _load()
    for relative in DOCUMENTS:
        text = (ROOT / relative).read_text()
        assert TAG.search(text), f"{relative} carries no {{fig:}} tag"


def test_a_bare_tag_is_caught():
    """A tag with no numeric literal before it has no correspondence to
    check, and must fail rather than pass vacuously."""
    figures = _load()
    key = next(iter(figures))
    with pytest.raises(AssertionError, match="bare tag"):
        _check_documents([("fake.md", f"The value is {{fig:{key}}}.")], figures)
