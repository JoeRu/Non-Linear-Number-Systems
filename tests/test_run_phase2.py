"""scripts/run_phase2.py has four gates -- agreement, Chernoff bound, T3 bound,
residual -- sharing one contract: on failure, exit non-zero and write nothing.
That contract already broke once during this task (the bounds CSV and its
manifest entry were written before the residual sweep's own gate ran), and it
was caught only by reading the diff, not by a test. This suite exists so a
future regression on any of the four gates is caught by running the suite.

Self-contained, following tests/test_run_phase1.py's pattern: it never touches
the real data/ or figures/ directories. It copies the real, unmodified script
into a scratch scripts/ directory under tmp_path. run_phase2.py derives every
artifact path from `Path(__file__).resolve().parents[1]`, so running the copy
from tmp_path/scripts/run_phase2.py makes tmp_path the script's ROOT and
confines every path (data/, figures/, manifest.json) inside tmp_path without
needing to patch the script itself.

Every test here uses a handful of small, real N (2, 3, 5, 8, 13, 21, 34) drawn
from data/phase1_data.csv, so the per-N gate loop runs against real, fast,
already-verified log_R_c values -- no synthetic counts, and no need to invoke
the real 37-N, ~12-second run inside the suite.
"""

import runpy
import shutil
import sys
from pathlib import Path

import capfib.interval as interval_module
import capfib.lower as lower_module
import capfib.saddle as saddle_module

REAL_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_phase2.py"

# Real small-N rows copied from data/phase1_data.csv, so the per-N gate loop
# operates on genuine, already cross-checked log_R_c values rather than
# synthetic ones -- only N and log_R_c are read by the script.
PHASE1_CSV = (
    "N,log_R_c\n"
    "2,0.6931471805599453\n"
    "3,1.0986122886681098\n"
    "5,1.6094379124341003\n"
    "8,2.0794415416798357\n"
    "13,2.70805020110221\n"
    "21,3.4965075614664802\n"
    "34,4.430816798843313\n"
)

# Sentinel content for artifacts that must not be created or touched by a
# failed run. Distinct from anything the script would ever write, and
# pre-seeded (not merely absent beforehand) so "untouched" can be checked by
# content comparison -- the actual property, stronger than "the file is
# absent".
SENTINEL_BOUNDS = "SENTINEL,phase2_bounds\n"
SENTINEL_RESIDUAL = "SENTINEL,phase2_residual\n"
SENTINEL_FIGURES = '{"sentinel": true}'
SENTINEL_MANIFEST = "[]"


def _make_scratch_repo(tmp_path: Path) -> Path:
    """Copy the real script into an isolated tmp_path/scripts/ tree.

    Returns:
        The path to the copy. Pre-seeds data/ with a real small-N Phase 1
        CSV and sentinel contents for every artifact the script could write,
        so a failed run's "nothing written" claim can be checked by content
        comparison, not just existence.
    """
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    script_copy = scripts_dir / "run_phase2.py"
    shutil.copy(REAL_SCRIPT, script_copy)

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "phase1_data.csv").write_text(PHASE1_CSV)
    (data_dir / "phase2_bounds.csv").write_text(SENTINEL_BOUNDS)
    (data_dir / "phase2_residual.csv").write_text(SENTINEL_RESIDUAL)
    (data_dir / "phase2_figures.json").write_text(SENTINEL_FIGURES)
    (data_dir / "manifest.json").write_text(SENTINEL_MANIFEST)
    return script_copy


def _assert_nothing_written(tmp_path: Path) -> None:
    """Assert every artifact the script could write is byte-identical to its
    pre-seeded sentinel, and that no figure was created."""
    data_dir = tmp_path / "data"
    assert (data_dir / "phase2_bounds.csv").read_text() == SENTINEL_BOUNDS, \
        "a failed run must not modify the bounds CSV"
    assert (data_dir / "phase2_residual.csv").read_text() == SENTINEL_RESIDUAL, \
        "a failed run must not modify the residual CSV"
    assert (data_dir / "phase2_figures.json").read_text() == SENTINEL_FIGURES, \
        "a failed run must not modify the figures JSON"
    assert (data_dir / "manifest.json").read_text() == SENTINEL_MANIFEST, \
        "a failed run must not modify the manifest"
    assert not (tmp_path / "figures").exists(), \
        "a failed run must not create any figures"


def _run_script(script_copy: Path, monkeypatch, capsys) -> tuple[int, str]:
    """Run the scratch script's __main__ and capture (exit_code, stdout)."""
    monkeypatch.setattr(sys, "argv", ["run_phase2.py"])
    exit_code = None
    try:
        runpy.run_path(str(script_copy), run_name="__main__")
    except SystemExit as exc:
        exit_code = exc.code
    return exit_code, capsys.readouterr().out


def test_agreement_gate_failure_exits_nonzero_and_writes_nothing(tmp_path, monkeypatch, capsys):
    # The per-N agreement gate is the first check in the main loop; a
    # universal failure trips it at the smallest N (2), before any bound is
    # even computed.
    script_copy = _make_scratch_repo(tmp_path)
    monkeypatch.setattr(interval_module, "agrees_with_float", lambda *a, **k: False)

    exit_code, out = _run_script(script_copy, monkeypatch, capsys)

    assert exit_code == 1, "a failed agreement gate must exit non-zero"
    assert "GATE FAILED at N=2" in out, \
        "the failure message must name the gate and the N it failed at"
    _assert_nothing_written(tmp_path)


def test_chernoff_bound_violation_exits_nonzero_and_writes_nothing(tmp_path, monkeypatch, capsys):
    # Force the certified Chernoff bound below every exact value, tripping
    # the BOUND VIOLATED check at the smallest N.
    script_copy = _make_scratch_repo(tmp_path)
    monkeypatch.setattr(saddle_module, "log_R_bound_certified", lambda n, **k: -1.0)

    exit_code, out = _run_script(script_copy, monkeypatch, capsys)

    assert exit_code == 1, "a violated Chernoff bound must exit non-zero"
    assert "BOUND VIOLATED at N=2" in out, \
        "the failure message must name the gate and the N it failed at"
    _assert_nothing_written(tmp_path)


def test_t3_lower_bound_violation_exits_nonzero_and_writes_nothing(tmp_path, monkeypatch, capsys):
    # Force the T3 construction above every exact value, tripping the LOWER
    # BOUND VIOLATED check at the smallest N. log_R_bound_certified is left
    # real: at these small, genuine N it legitimately holds, so only the T3
    # check is exercised.
    script_copy = _make_scratch_repo(tmp_path)
    real_t3 = lower_module.t3_lower_bound
    monkeypatch.setattr(
        lower_module,
        "t3_lower_bound",
        lambda n: real_t3(n)._replace(log_count=1e9),
    )

    exit_code, out = _run_script(script_copy, monkeypatch, capsys)

    assert exit_code == 1, "a violated T3 lower bound must exit non-zero"
    assert "LOWER BOUND VIOLATED at N=2" in out, \
        "the failure message must name the gate and the N it failed at"
    _assert_nothing_written(tmp_path)


def test_residual_sweep_gate_failure_writes_nothing_even_though_bounds_already_passed(
    tmp_path, monkeypatch, capsys
):
    """Regression test for the exact bug found in this task's self-review:
    the bounds CSV must not be written even though every per-N gate and bound
    already passed by the time the residual sweep's own gate fails.

    Fails only at t = 10.0 -- the smallest, first-checked sample -- so the
    real (slow, ~7s at t=1280) computation for the larger t values is never
    reached, keeping this test fast. The main per-N loop, over real small N,
    still calls the genuine agrees_with_float for its own t values (all well
    under 10), so this isolates the residual sweep's gate specifically.
    """
    script_copy = _make_scratch_repo(tmp_path)
    real_agrees = interval_module.agrees_with_float

    def fails_only_at_t10(t, float_value, guard=40):
        if t == 10.0:
            return False
        return real_agrees(t, float_value, guard=guard)

    monkeypatch.setattr(interval_module, "agrees_with_float", fails_only_at_t10)

    exit_code, out = _run_script(script_copy, monkeypatch, capsys)

    assert exit_code == 1, "a failed residual-sweep gate must exit non-zero"
    assert "gate failed in the residual sweep at t=10.0" in out, \
        "the failure message must name the gate and the t it failed at"
    _assert_nothing_written(tmp_path)


def test_n_max_below_2_is_rejected():
    import subprocess

    for bad_n_max in (0, 1, -5):
        result = subprocess.run(
            [sys.executable, str(REAL_SCRIPT), "--n-max", str(bad_n_max)],
            capture_output=True, text=True,
        )
        assert result.returncode == 2, \
            f"--n-max {bad_n_max} should be rejected by argparse (exit 2)"
        assert "--n-max must be at least 2" in result.stderr
