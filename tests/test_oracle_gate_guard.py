"""The skip guard in tests/conftest.py needs a guard of its own.

`gate_violations` is what decides whether a session's oracle-backed gate
actually ran. If it were wrong -- returning nothing when a gate skipped -- the
suite would be back where it started: green with the gate switched off, and
now with a file named conftest.py implying otherwise. So its logic is tested
directly, and the marker's presence on the real gate tests is tested by
collection.
"""

import subprocess
import sys
from pathlib import Path

from conftest import MARKER, gate_violations

ROOT = Path(__file__).resolve().parents[1]

# The comparisons that must never skip: the certified T1 bound, T3 and T5
# against exact values. Twelve of these skipped on every clean clone while
# data/phase1_data.csv was gitignored.
REQUIRED_GATE_TESTS = (
    "test_certified_bound_holds_against_exact_values",
    "test_certified_bound_is_not_vacuous",
    "test_t3_never_exceeds_the_exact_value",
    "test_t5_never_exceeds_the_exact_value",
)


def test_a_skipped_gate_is_a_violation():
    problems = gate_violations(
        collected=12, executed=11, skipped=["tests/test_phase2_bounds.py::t"]
    )
    assert problems
    assert "SKIPPED" in problems[0]


def test_a_gate_that_ran_is_not_a_violation():
    assert gate_violations(collected=12, executed=12, skipped=[]) == []


def test_collected_but_never_executed_is_a_violation():
    """The state a collection-time skip or a module-level guard produces."""
    problems = gate_violations(collected=12, executed=0, skipped=[])
    assert problems
    assert "none executed" in problems[0]


def test_nothing_collected_is_not_reported_here():
    """`gate_violations` says nothing about an empty session; the
    "no oracle_gate tests collected at all" case is a whole-session judgement
    and lives in `pytest_sessionfinish`, which knows whether the run was
    narrowed by -k or an explicit node id."""
    assert gate_violations(collected=0, executed=0, skipped=[]) == []


def test_the_real_comparisons_carry_the_marker():
    """Collection-level check: each named comparison must be marked.

    Without this, dropping `@pytest.mark.oracle_gate` from a test would
    silently remove it from the guard's scope -- the same failure mode one
    level up.
    """
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            str(ROOT / "tests" / "test_phase2_bounds.py"),
            "--collect-only", "-q", "-m", MARKER,
        ],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    for name in REQUIRED_GATE_TESTS:
        assert name in result.stdout, (
            f"{name} is not marked `{MARKER}`, so a skip of it would no longer "
            f"fail the session:\n{result.stdout}"
        )


def test_a_skipping_gate_test_fails_the_session(tmp_path):
    """End to end: the guard must turn an all-passing session into a failure
    when a marked test skips.

    This is the property the whole file exists for, so it is checked by
    running a real pytest session rather than by reasoning about the hooks.
    """
    (tmp_path / "conftest.py").write_text(
        (ROOT / "tests" / "conftest.py").read_text()
    )
    (tmp_path / "test_fixture_gate.py").write_text(
        "import pytest\n"
        "\n"
        "@pytest.mark.oracle_gate\n"
        "def test_skips():\n"
        "    pytest.skip('oracle absent')\n"
        "\n"
        "@pytest.mark.oracle_gate\n"
        "def test_passes():\n"
        "    assert True\n"
    )
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q", str(tmp_path)],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert "1 passed" in result.stdout and "1 skipped" in result.stdout, result.stdout
    assert result.returncode != 0, (
        "a session with a skipped oracle_gate test must NOT be green:\n"
        + result.stdout
    )
    assert "ORACLE GATE FAILURE" in result.stdout, result.stdout
