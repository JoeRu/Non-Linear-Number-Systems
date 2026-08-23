"""Cell-by-cell drift check for the two full data tables Phase 1 reproduces.

Risk R-002's Phase 1 entry (`docs/risks.md`) names three things as the
hand-copy exposure: "the census, the place-jump table and the block-extrema
table". `tests/test_figure_tags.py` closes the census (and a handful of
headline figures pulled out of the two tables) with `{fig:key}` tags, but the
two tables themselves are reproduced in `docs/phases/phase1_report.md` in
full -- 28 and 29 rows -- and tagging every cell would mean on the order of a
hundred more figure keys for tables that exist precisely so a reader does not
have to go spelunking in `data/phase1_summary.json`. Tagging every cell was
rejected for that reason (see the risk register and the Phase 1 tagging
task's report); this file is the alternative the risk's own candidate
resolutions describe: "a checker that re-reads each quoted figure from the
artifact and fails on mismatch", applied to whole tables instead of
individually tagged literals.

Anchored by an HTML comment immediately before each table
(`<!-- table:place-jumps -->`, `<!-- table:block-extrema -->`) rather than by
line number, so reordering surrounding prose cannot silently point this check
at the wrong table.
"""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "phases" / "phase1_report.md"
SUMMARY = ROOT / "data" / "phase1_summary.json"


def _load_summary():
    assert SUMMARY.exists(), (
        f"{SUMMARY.relative_to(ROOT)} absent -- it is tracked, so this means "
        f"it was deleted. Restore it from git, or regenerate with "
        f"scripts/run_phase1.py."
    )
    return json.loads(SUMMARY.read_text())


def _extract_table(text, marker):
    """Return the Markdown table's data rows (as lists of raw cell strings)
    immediately following an `<!-- table:MARKER -->` anchor.

    The header row and the `|---|---|` separator row are consumed and
    dropped; only rows that follow the separator are returned. Stops at the
    first blank line after the table starts.
    """
    anchor = f"<!-- table:{marker} -->"
    start = text.find(anchor)
    assert start != -1, f"{REPORT.name}: no {anchor!r} anchor found"
    rest = text[start + len(anchor):]
    lines = rest.lstrip("\n").splitlines()
    assert lines, f"{REPORT.name}: nothing follows the {anchor!r} anchor"
    # lines[0] is the header row, lines[1] the |---|---| separator.
    assert lines[0].startswith("|"), (
        f"{REPORT.name}: line after {anchor!r} is not a table row: "
        f"{lines[0]!r}"
    )
    assert re.match(r"^\|[-\s|]+\|$", lines[1]), (
        f"{REPORT.name}: second line after {anchor!r} is not a header "
        f"separator: {lines[1]!r}"
    )
    rows = []
    for line in lines[2:]:
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    return rows


def _decimal_places(literal):
    """How many digits follow the decimal point in a numeric literal, 0 if none."""
    return len(literal.split(".", 1)[1]) if "." in literal else 0


@pytest.mark.oracle_gate
def test_place_jump_table_matches_artifact():
    """Every row of the place-jump table must match `place_jumps` exactly.

    The comparison's precision is not a second, invented convention: it is
    read off the quoted literal itself (however many decimals the document
    chose to display), then the stored float is formatted to that same
    number of decimals and compared as a string -- the same technique
    `tests/test_figure_tags.py` uses with a stored `precision` field, just
    without a separate `{fig:key}` per cell.

    Reading the precision from the document is what makes the cell-by-cell
    comparison possible without a hundred figure keys, and it is also its
    weak point: a cell rewritten with *fewer* decimals is compared at that
    lower precision and passes. Editing the `F = 832040` row from
    `1.000653` to `1.0` was verified to pass before the two guards below
    were added. They close the two ways that loses information:

    1. Every ratio cell must quote the same number of decimals. A single
       cell down-rounded while its neighbours keep six is a drifted cell,
       and this is what catches it.
    2. A cell whose stored ratio differs from 1 must not be quoted at a
       precision that renders it as exactly 1. That is derived from the
       data, not an invented floor: it is the point at which the row stops
       carrying the thing the table exists to show.

    **Known limitation that remains.** Re-rendering the *whole* column at a
    lower uniform precision -- every cell to three decimals, say -- still
    passes, because each cell then genuinely matches the artifact at the
    precision quoted and no cell collapses to 1 until three decimals is
    itself too coarse. That is a loss of resolution rather than a drift
    between prose and data, so it is out of scope for a drift detector; the
    values would still be right. Guarding against it would mean pinning the
    display precision in the document, which is the invented convention this
    approach set out to avoid.
    """
    summary = _load_summary()
    jumps = summary["place_jumps"]
    rows = _extract_table(REPORT.read_text(), "place-jumps")
    assert len(rows) == len(jumps), (
        f"place-jump table has {len(rows)} rows but data/phase1_summary.json "
        f"has {len(jumps)} place_jumps entries -- table and artifact have "
        f"drifted in length, not just content"
    )
    precisions = set()
    for i, (row, jump) in enumerate(zip(rows, jumps)):
        assert len(row) == 2, f"place-jump table row {i}: expected 2 cells, got {row!r}"
        place_cell, ratio_cell = row
        precisions.add(_decimal_places(ratio_cell))

        expected_place = str(jump["place"])
        assert place_cell == expected_place, (
            f"place-jump table row {i}, column 'place': quoted {place_cell!r} "
            f"but data/phase1_summary.json place_jumps[{i}]['place'] is "
            f"{expected_place!r}"
        )

        precision = _decimal_places(ratio_cell)
        expected_ratio = f"{jump['ratio']:.{precision}f}"
        assert ratio_cell == expected_ratio, (
            f"place-jump table row {i} (F={jump['place']}), column 'ratio': "
            f"quoted {ratio_cell!r} but data/phase1_summary.json "
            f"place_jumps[{i}]['ratio'] is {jump['ratio']!r}, which at "
            f"{precision} decimal place(s) is {expected_ratio!r} -- "
            f"regenerate the phase's data and update the table"
        )

        # A cell may not be quoted at a precision that turns a ratio which
        # is not 1 into a literal 1: that passes the comparison above (the
        # stored value rounds to it) while deleting the only thing the row
        # records. Derived from the row's own data, not a fixed floor.
        if jump["ratio"] != 1.0:
            assert ratio_cell != f"{1.0:.{precision}f}", (
                f"place-jump table row {i} (F={jump['place']}), column "
                f"'ratio': quoted {ratio_cell!r}, which is the recorded "
                f"ratio {jump['ratio']!r} rounded until it is "
                f"indistinguishable from 1. The comparison passes at that "
                f"precision and the row stops saying anything -- quote "
                f"enough decimals for the ratio to differ from 1"
            )

    assert len(precisions) == 1, (
        f"place-jump table: the ratio column mixes decimal precisions "
        f"{sorted(precisions)}. Precision is read off each cell, so a single "
        f"cell rewritten with fewer decimals would be compared -- and pass -- "
        f"at that lower precision while its neighbours keep the generated "
        f"one. Quote the whole column at one precision"
    )


_BLOCK_RANGE = re.compile(r"^\[(\d+),\s*(\d+)\)")


@pytest.mark.oracle_gate
def test_block_extrema_table_matches_artifact():
    """Every row of the block-extrema table must match `block_extrema` exactly.

    `max`/`min` are arbitrary-precision integers stored as strings in
    `data/phase1_summary.json` (they can exceed 60 digits by the last rows),
    so they are compared as exact strings rather than through a float
    precision at all -- there is no rounding to invent here.
    """
    summary = _load_summary()
    blocks = summary["block_extrema"]
    rows = _extract_table(REPORT.read_text(), "block-extrema")
    assert len(rows) == len(blocks), (
        f"block-extrema table has {len(rows)} rows but "
        f"data/phase1_summary.json has {len(blocks)} block_extrema entries "
        f"-- table and artifact have drifted in length, not just content"
    )
    for i, (row, block) in enumerate(zip(rows, blocks)):
        assert len(row) == 5, (
            f"block-extrema table row {i}: expected 5 cells, got {row!r}"
        )
        range_cell, argmax_cell, max_cell, argmin_cell, min_cell = row

        # The last row carries a trailing `\*` footnote marker after the
        # closing paren (`[832040, 1000001)\*`); the range regex only
        # anchors on the leading `[lo, hi)` and ignores anything after it.
        m = _BLOCK_RANGE.match(range_cell)
        assert m, (
            f"block-extrema table row {i}, column 'block': {range_cell!r} "
            f"does not look like '[lo, hi)'"
        )
        lo_cell, hi_cell = m.group(1), m.group(2)

        checks = (
            ("lo", lo_cell, str(block["lo"])),
            ("hi", hi_cell, str(block["hi"])),
            ("argmax", argmax_cell, str(block["argmax"])),
            ("max", max_cell, str(block["max"])),
            ("argmin", argmin_cell, str(block["argmin"])),
            ("min", min_cell, str(block["min"])),
        )
        for column, quoted, expected in checks:
            assert quoted == expected, (
                f"block-extrema table row {i} (block [{block['lo']}, "
                f"{block['hi']})), column {column!r}: quoted {quoted!r} but "
                f"data/phase1_summary.json block_extrema[{i}][{column!r}] is "
                f"{expected!r} -- regenerate the phase's data and update the "
                f"table"
            )
