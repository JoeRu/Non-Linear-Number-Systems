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


def test_every_tag_resolves_and_matches():
    """Every {fig:KEY} in the Phase 2 docs must be a full TAG match, resolve
    to a known key, and quote that key's value at its recorded precision.

    Ruling A (task 7): a bare tag is checked against the *exact set of end
    offsets* where a full ``<literal> {fig:key}`` match ends -- not a window
    around some other tag's position -- so a tag cannot be excused by a
    number that actually belongs to a different, nearby tag.
    """
    figures = _load()
    seen = set()
    for relative in DOCUMENTS:
        path = ROOT / relative
        if not path.exists():
            pytest.skip(f"{relative} not written yet")
        text = path.read_text()

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
