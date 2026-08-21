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
    """Load the generated figures, or skip the test if they do not exist yet.

    Returns:
        dict: The parsed contents of data/phase2_figures.json, keyed by
        figure key, each mapping to {value, precision, description}.
    """
    if not FIGURES.exists():
        pytest.skip("data/phase2_figures.json absent; run scripts/run_phase2.py")
    return json.loads(FIGURES.read_text())


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


def _check_documents(named_texts, figures):
    """Assert every {fig:KEY} in each document is a full, matching tag.

    Ruling A (task 7): a bare tag is checked against the *exact set of end
    offsets* where a full ``<literal> {fig:key}`` match ends -- not a window
    around some other tag's position -- so a tag cannot be excused by a
    number that actually belongs to a different, nearby tag.

    Args:
        named_texts: an iterable of (label, text) pairs.
        figures: the parsed figures mapping.

    Returns:
        set[str]: the figure keys that were quoted.

    Raises:
        AssertionError: on a bare tag, an unknown key, or a drifted literal.
    """
    seen = set()
    for relative, text in named_texts:
        tag_ends = {m.end() for m in TAG.finditer(text)}
        for bare in BARE_TAG.finditer(text):
            assert bare.end() in tag_ends, (
                f"{relative}: {{fig:{bare.group(1)}}} is not preceded by a "
                f"numeric literal (bare tag, no correspondence to check)"
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
    if not present:
        pytest.skip(
            "none of the Phase 2 documents written yet: " + ", ".join(DOCUMENTS)
        )
    if missing:
        print(f"not written yet, not checked: {', '.join(missing)}")
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


def test_a_bare_tag_is_caught():
    """A tag with no numeric literal before it has no correspondence to
    check, and must fail rather than pass vacuously."""
    figures = _load()
    key = next(iter(figures))
    with pytest.raises(AssertionError, match="bare tag"):
        _check_documents([("fake.md", f"The value is {{fig:{key}}}.")], figures)
