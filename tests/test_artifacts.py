"""capfib.artifacts is the publishing path every phase runner shares.

Its two byte-level promises matter more than its convenience: CSV line
terminators reach disk unchanged (the manifest hashes the bytes, and the
tracked Phase 0/1 CSVs are CRLF while Phase 2's are LF), and a failed write
leaves neither a partial artifact nor a stray temp file behind.
"""

import csv
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from capfib.artifacts import (
    atomic_write_bytes,
    atomic_write_text,
    csv_text,
    figures_text,
    publish,
    render_figure,
)
from capfib.manifest import entries, git_rev

ROOT = Path(__file__).resolve().parents[1]


def test_csv_text_defaults_to_crlf_and_reprs_floats():
    rows = [{"N": 2, "x": 0.1 + 0.2}, {"N": 3, "x": ""}]
    assert csv_text(rows) == "N,x\r\n2,0.30000000000000004\r\n3,\r\n"


def test_csv_text_lf_matches_the_phase2_manual_join():
    """Phase 2 used to build its CSVs by joining `repr`s on "\\n"; the helper
    must produce the same bytes or the manifest hashes would change."""
    rows = [{"t": 10.0, "v": -1.25e-7, "k": 37}, {"t": 1280.0, "v": 3.0, "k": 0}]
    header = list(rows[0])
    manual = "\n".join(
        [",".join(header)] + [",".join(repr(r[k]) for k in header) for r in rows]
    ) + "\n"
    assert csv_text(rows, lineterminator="\n") == manual


@pytest.mark.parametrize(
    "name, terminator",
    [
        ("phase0_5_gate.csv", "\r\n"),
        ("phase1_data.csv", "\r\n"),
        ("phase2_bounds.csv", "\n"),
        ("phase2_residual.csv", "\n"),
    ],
)
def test_csv_text_reproduces_every_tracked_csv(name, terminator):
    """Re-serialising each tracked CSV's parsed values must give its exact
    bytes. These files are tracked, so a missing one is a failure, not a skip."""
    path = ROOT / "data" / name
    raw = path.read_bytes()

    def parse(value: str):
        if value == "":
            return ""
        try:
            return int(value)
        except ValueError:
            return float(value)

    with path.open(newline="") as fh:
        rows = [{k: parse(v) for k, v in r.items()} for r in csv.DictReader(fh)]
    assert csv_text(rows, lineterminator=terminator).encode() == raw


def test_csv_text_rejects_no_rows():
    with pytest.raises(ValueError):
        csv_text([])


def test_atomic_write_text_keeps_crlf_and_creates_parent(tmp_path):
    target = tmp_path / "new" / "out.csv"
    atomic_write_text(target, "a\r\nb\r\n")
    assert target.read_bytes() == b"a\r\nb\r\n"
    assert sorted(p.name for p in target.parent.iterdir()) == ["out.csv"]


def test_atomic_write_bytes_creates_parent(tmp_path):
    target = tmp_path / "figures" / "x.png"
    atomic_write_bytes(target, b"\x89PNG payload")
    assert target.read_bytes() == b"\x89PNG payload"
    assert sorted(p.name for p in target.parent.iterdir()) == ["x.png"]


def test_failed_text_write_leaves_target_and_no_temp(tmp_path):
    target = tmp_path / "out.txt"
    target.write_text("old")

    # A non-encodable character fails inside the write, after the temp file
    # exists -- the case the cleanup branch is for.
    with pytest.raises(UnicodeEncodeError):
        atomic_write_text(target, "fine\ud800")
    assert target.read_text() == "old"
    assert [p.name for p in tmp_path.iterdir()] == ["out.txt"]


def test_render_figure_returns_png_bytes():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([0, 1], [1, 0])
    try:
        png = render_figure(fig, dpi=50)
    finally:
        plt.close(fig)
    assert png.startswith(b"\x89PNG")


def test_figures_text_matches_the_tracked_files():
    """Serialisation must be byte-identical to what the runners wrote, and the
    tracked figures files must pass the validation."""
    for name in ("phase1_figures.json", "phase2_figures.json"):
        raw = (ROOT / "data" / name).read_text()
        assert figures_text(json.loads(raw)) == raw


@pytest.mark.parametrize(
    "entry",
    [
        {"precision": 0, "description": "no value"},
        {"value": 1, "description": "no precision"},
        {"value": 1, "precision": 0},
        {"value": 1, "precision": 1.0, "description": "float precision"},
        {"value": 1, "precision": True, "description": "bool precision"},
        {"value": 1, "precision": 0, "description": "   "},
    ],
)
def test_figures_text_rejects_malformed_entries(entry):
    with pytest.raises(ValueError):
        figures_text({"key": entry})


def test_figures_text_rejects_empty():
    with pytest.raises(ValueError):
        figures_text({})


def test_publish_writes_then_records_the_written_bytes(tmp_path):
    manifest = tmp_path / "data" / "manifest.json"
    text_path = tmp_path / "data" / "a.csv"
    png_path = tmp_path / "figures" / "b.png"

    publish(text_path, "x\r\n1\r\n", "scripts/demo.py", {"n": 1}, manifest_path=manifest)
    publish(png_path, b"\x89PNG", "scripts/demo.py", {"n": 2}, manifest_path=manifest)

    recorded = entries(manifest)
    assert [e["file"] for e in recorded] == ["a.csv", "b.png"]
    assert recorded[0]["sha256"] == hashlib.sha256(b"x\r\n1\r\n").hexdigest()
    assert recorded[1]["sha256"] == hashlib.sha256(b"\x89PNG").hexdigest()
    assert recorded[1]["params"] == {"n": 2}


def test_git_rev_returns_the_head_of_the_given_repository(tmp_path):
    # Builds its own repository rather than asking about this one: a test run
    # from `git archive` output has no .git, and must not fail for that.
    git = ["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "x"], check=True)
    head = subprocess.run(
        [*git, "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert git_rev(tmp_path) == head


def test_git_rev_outside_a_repository_is_unknown(tmp_path):
    assert git_rev(tmp_path) == "unknown"
