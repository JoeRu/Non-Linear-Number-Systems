"""The cross-check in scripts/run_phase1.py is what licenses this phase's numbers.
It is the one piece whose failure would be invisible in the data, so it gets a test."""

import filecmp
import runpy
import shutil
import sys

import capfib.dp as dp_module
from capfib.gf import coefficients


def test_crosscheck_failure_exits_nonzero_and_writes_nothing(tmp_path, monkeypatch):
    summary = "data/phase1_summary.json"
    backup = tmp_path / "summary_before.json"
    shutil.copy(summary, backup)

    real = dp_module.counts

    def corrupted(n_max, places=None):
        c = list(real(n_max, places))
        c[7] += 1      # sum-preserving: exactly what the global checksum cannot see
        c[9] -= 1
        return c

    monkeypatch.setattr(dp_module, "counts", corrupted)
    monkeypatch.setattr(sys, "argv", ["run_phase1.py", "--n-max", "3000"])

    exit_code = None
    try:
        runpy.run_path("scripts/run_phase1.py", run_name="__main__")
    except SystemExit as exc:
        exit_code = exc.code

    assert exit_code == 1, "a failed cross-check must exit non-zero"
    assert filecmp.cmp(summary, backup, shallow=False), \
        "a failed cross-check must leave artifacts untouched"
