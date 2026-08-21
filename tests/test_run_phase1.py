"""The cross-check in scripts/run_phase1.py is what licenses this phase's numbers.
It is the one piece whose failure would be invisible in the data, so it gets a test.

This test is self-contained: it never touches the real `data/` or `figures/`
directories, which are gitignored and may not exist on a clean clone. Instead
it copies the real, unmodified script into a scratch `scripts/` directory
under `tmp_path`. `scripts/run_phase1.py` derives every artifact path from
`Path(__file__).resolve().parent.parent`, so running the copy from
`tmp_path/scripts/run_phase1.py` makes `tmp_path` the script's REPO_ROOT and
confines every path (data/, figures/, manifest.json) inside `tmp_path`
without needing to patch the script itself.
"""

import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import capfib.dp as dp_module

REAL_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_phase1.py"

# Sentinel content for artifacts that must not be created or touched by a
# failed cross-check. Distinct from anything the script would ever write.
SENTINEL_SUMMARY = '{"sentinel": true}'
SENTINEL_MANIFEST = "[]"


def _make_scratch_repo(tmp_path: Path) -> Path:
    """Copy the real script into an isolated tmp_path/scripts/ tree.

    Returns the path to the copy. Pre-seeds data/ with sentinel files so a
    failed cross-check's "nothing written" claim can be checked by content
    comparison, not just existence.
    """
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    script_copy = scripts_dir / "run_phase1.py"
    shutil.copy(REAL_SCRIPT, script_copy)

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "phase1_summary.json").write_text(SENTINEL_SUMMARY)
    (data_dir / "manifest.json").write_text(SENTINEL_MANIFEST)
    return script_copy


def _corrupted_counts(real):
    def corrupted(n_max, places=None):
        c = list(real(n_max, places))
        c[7] += 1      # sum-preserving: exactly what the global checksum cannot see
        c[9] -= 1
        return c
    return corrupted


def test_crosscheck_failure_exits_nonzero_and_writes_nothing(tmp_path, monkeypatch):
    script_copy = _make_scratch_repo(tmp_path)

    real = dp_module.counts
    monkeypatch.setattr(dp_module, "counts", _corrupted_counts(real))
    monkeypatch.setattr(sys, "argv", ["run_phase1.py", "--n-max", "3000"])

    exit_code = None
    try:
        runpy.run_path(str(script_copy), run_name="__main__")
    except SystemExit as exc:
        exit_code = exc.code

    assert exit_code == 1, "a failed cross-check must exit non-zero"

    data_dir = tmp_path / "data"
    assert (data_dir / "phase1_summary.json").read_text() == SENTINEL_SUMMARY, \
        "a failed cross-check must not modify an existing summary artifact"
    assert (data_dir / "manifest.json").read_text() == SENTINEL_MANIFEST, \
        "a failed cross-check must not modify the manifest"
    assert not (data_dir / "phase1_data.csv").exists(), \
        "a failed cross-check must not create the CSV artifact"
    assert not (tmp_path / "figures").exists(), \
        "a failed cross-check must not create any figures"


def _truncated_counts(real):
    """Return values that agree with `real` on their shared prefix but are
    shorter -- the shape that made `next(i for i in range(len(c)) if ...)`
    raise StopIteration instead of reporting a length mismatch."""
    def truncated(n_max, places=None):
        c = list(real(n_max, places))
        return c[:-5]
    return truncated


def test_crosscheck_length_mismatch_exits_nonzero_and_writes_nothing(tmp_path, monkeypatch):
    # gf and dp agree pointwise on their shared prefix but dp's array is
    # shorter -- `c != d` is true, but scanning for a differing index never
    # finds one. This must be reported and exit 1, not raise StopIteration.
    script_copy = _make_scratch_repo(tmp_path)

    real = dp_module.counts
    monkeypatch.setattr(dp_module, "counts", _truncated_counts(real))
    monkeypatch.setattr(sys, "argv", ["run_phase1.py", "--n-max", "3000"])

    exit_code = None
    try:
        runpy.run_path(str(script_copy), run_name="__main__")
    except SystemExit as exc:
        exit_code = exc.code

    assert exit_code == 1, \
        "a length-mismatched cross-check must exit non-zero, not raise"

    data_dir = tmp_path / "data"
    assert (data_dir / "phase1_summary.json").read_text() == SENTINEL_SUMMARY, \
        "a failed cross-check must not modify an existing summary artifact"
    assert (data_dir / "manifest.json").read_text() == SENTINEL_MANIFEST, \
        "a failed cross-check must not modify the manifest"
    assert not (data_dir / "phase1_data.csv").exists(), \
        "a failed cross-check must not create the CSV artifact"
    assert not (tmp_path / "figures").exists(), \
        "a failed cross-check must not create any figures"


@pytest.mark.parametrize("bad_n_max", [0, 1, -5])
def test_n_max_below_2_is_rejected(bad_n_max):
    # argparse rejects this before any coefficient is computed or any file
    # is touched, so it is safe to invoke the real script directly.
    result = subprocess.run(
        [sys.executable, str(REAL_SCRIPT), "--n-max", str(bad_n_max)],
        capture_output=True, text=True,
    )
    assert result.returncode == 2, \
        f"--n-max {bad_n_max} should be rejected by argparse (exit 2)"
    assert "--n-max must be >= 2" in result.stderr
