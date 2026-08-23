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
import capfib.gf as gf_module

ROOT = Path(__file__).resolve().parents[1]
REAL_SCRIPT = ROOT / "scripts" / "run_phase1.py"

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
    shorter -- the shape that made the original, undefaulted
    `next(i for i in range(len(c)) if c[i] != d[i])` scan raise IndexError
    (not StopIteration: for i past len(d), evaluating `d[i]` inside the
    generator raises IndexError before the scan can ever exhaust its range
    and finish normally). The production code no longer runs that scan at
    all in this case -- gf stays full-length while dp is 5 short, so the
    `len(c) != n_max + 1 or len(d) != n_max + 1` check now catches this
    before the pointwise comparison is even attempted."""
    def truncated(n_max, places=None):
        c = list(real(n_max, places))
        return c[:-5]
    return truncated


def test_crosscheck_length_mismatch_exits_nonzero_and_writes_nothing(tmp_path, monkeypatch):
    # gf is full-length; dp's array is 5 shorter. The length check now
    # catches this before the pointwise `c != d` comparison ever runs. This
    # must be reported and exit 1, not raise IndexError.
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


def _same_truncation(real):
    """Return values truncated the same way `_truncated_counts` truncates dp
    -- so that gf and dp end up EQUAL to each other (same shorter length,
    same elements), not just individually wrong. `c != d` is False in this
    case; only an explicit length-vs-n_max check can catch it."""
    def truncated(n_max, places=None):
        c = list(real(n_max, places))
        return c[:-5]
    return truncated


def test_crosscheck_identically_truncated_arrays_exits_nonzero_and_writes_nothing(
    tmp_path, monkeypatch
):
    # Both gf and dp are truncated the same way, so they agree pointwise and
    # `c != d` is False -- the old code would report "cross-check OK" and
    # then raise IndexError trying to read c[n_max]. The fix requires both
    # arrays to have length exactly n_max + 1 before accepting equality.
    script_copy = _make_scratch_repo(tmp_path)

    real_gf = gf_module.coefficients
    real_dp = dp_module.counts
    monkeypatch.setattr(gf_module, "coefficients", _same_truncation(real_gf))
    monkeypatch.setattr(dp_module, "counts", _same_truncation(real_dp))
    monkeypatch.setattr(sys, "argv", ["run_phase1.py", "--n-max", "3000"])

    exit_code = None
    try:
        runpy.run_path(str(script_copy), run_name="__main__")
    except SystemExit as exc:
        exit_code = exc.code

    assert exit_code == 1, \
        "identically-truncated gf/dp arrays must exit non-zero, not IndexError"

    data_dir = tmp_path / "data"
    assert (data_dir / "phase1_summary.json").read_text() == SENTINEL_SUMMARY, \
        "a failed cross-check must not modify an existing summary artifact"
    assert (data_dir / "manifest.json").read_text() == SENTINEL_MANIFEST, \
        "a failed cross-check must not modify the manifest"
    assert not (data_dir / "phase1_data.csv").exists(), \
        "a failed cross-check must not create the CSV artifact"
    assert not (tmp_path / "figures").exists(), \
        "a failed cross-check must not create any figures"


def _zeroed_at(real, index):
    """Return values equal to `real` except one index is forced to 0 --
    triggering the `min(c) < 1` precondition (which guards `local_ratios`
    against division by zero) while keeping gf and dp pointwise EQUAL, so
    the cross-check itself passes and this precondition is what actually
    gets exercised."""
    def zeroed(n_max, places=None):
        c = list(real(n_max, places))
        c[index] = 0
        return c
    return zeroed


def test_min_count_precondition_exits_nonzero_and_writes_nothing(tmp_path, monkeypatch):
    # gf and dp are patched identically, so the cross-check passes -- but
    # the agreed array has a zero count, which would break local_ratios.
    # Nothing previously exercised this precondition.
    script_copy = _make_scratch_repo(tmp_path)

    real_gf = gf_module.coefficients
    real_dp = dp_module.counts
    monkeypatch.setattr(gf_module, "coefficients", _zeroed_at(real_gf, 5))
    monkeypatch.setattr(dp_module, "counts", _zeroed_at(real_dp, 5))
    monkeypatch.setattr(sys, "argv", ["run_phase1.py", "--n-max", "3000"])

    exit_code = None
    try:
        runpy.run_path(str(script_copy), run_name="__main__")
    except SystemExit as exc:
        exit_code = exc.code

    assert exit_code == 1, \
        "a zero count must exit non-zero before any artifact is written"

    data_dir = tmp_path / "data"
    assert (data_dir / "phase1_summary.json").read_text() == SENTINEL_SUMMARY, \
        "a failed precondition must not modify an existing summary artifact"
    assert (data_dir / "manifest.json").read_text() == SENTINEL_MANIFEST, \
        "a failed precondition must not modify the manifest"
    assert not (data_dir / "phase1_data.csv").exists(), \
        "a failed precondition must not create the CSV artifact"
    assert not (tmp_path / "figures").exists(), \
        "a failed precondition must not create any figures"


@pytest.mark.parametrize("bad_n_max", [0, 1, -5, 2, 7])
def test_n_max_below_floor_is_rejected(bad_n_max):
    """The CLI must refuse every n_max the run cannot actually serve.

    Two floors exist: below 2 the analysis code crashes, and below 8 the run
    reaches no Fibonacci place F=8 and so cannot emit the place-jump figures.
    The argument boundary enforces the higher one. 2 and 7 are the cases that
    regressed: argparse used to accept them and the run then failed a runtime
    precondition, so the CLI contract promised what the script refused.

    argparse rejects all of these before any coefficient is computed or any
    file is touched, so it is safe to invoke the real script directly.
    """
    result = subprocess.run(
        [sys.executable, str(REAL_SCRIPT), "--n-max", str(bad_n_max)],
        capture_output=True, text=True,
    )
    assert result.returncode == 2, \
        f"--n-max {bad_n_max} should be rejected by argparse (exit 2)"
    assert "--n-max must be >= 8" in result.stderr


def test_n_max_at_the_floor_is_accepted(tmp_path):
    """8 is the smallest accepted value, and it must actually be accepted.

    Without this, raising the floor further -- past what the figures need --
    would leave every rejection test above still green. --skip-crosscheck
    stops before any artifact is written, and cwd is a tmp_path, so this
    cannot touch the repository's data/ directory.
    """
    result = subprocess.run(
        [sys.executable, str(REAL_SCRIPT), "--n-max", "8", "--skip-crosscheck"],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert result.returncode == 0, \
        f"--n-max 8 must be accepted; stderr was:\n{result.stderr}"


def test_run_phase1_emits_a_tracked_figures_file(tmp_path):
    """Phase 1 must publish its quotable numbers the way Phase 2 does.

    Risk R-002: the Phase 1 documents quote generated numbers with nothing
    binding them to the artifacts, so regeneration cannot update the prose and
    drift is silent. The figures file is what the tag test checks against.
    """
    import json

    figures = ROOT / "data" / "phase1_figures.json"
    assert figures.is_file(), (
        "data/phase1_figures.json is absent; run scripts/run_phase1.py"
    )
    data = json.loads(figures.read_text())
    assert data, "the figures file is empty"
    for key, entry in data.items():
        assert set(entry) >= {"value", "precision", "description"}, key
        assert isinstance(entry["precision"], int), key
        assert entry["description"].strip(), f"{key} has no description"
