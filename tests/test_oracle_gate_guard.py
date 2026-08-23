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


def _write_gate_module_fixture(tmp_path):
    """A tmp session shaped like the real suite for the two tests below:
    a real copy of `conftest.py`, two `GATE_MODULES` entries that collect
    and execute one `oracle_gate` test each, and a third -- also a
    `GATE_MODULES` entry, `test_phase1_tables.py` -- that fails to *collect*
    (a bad import), the same failure mode a corrupted or half-written module
    produces. The other two existing so the module-collection check has
    something to report *against*: without them, an absent module and a
    present-but-broken one would be indistinguishable to the hook, and this
    fixture exists specifically to isolate the broken-collection case.
    """
    (tmp_path / "conftest.py").write_text(
        (ROOT / "tests" / "conftest.py").read_text()
    )
    for name in ("test_phase2_bounds.py", "test_figure_tags.py"):
        (tmp_path / name).write_text(
            "import pytest\n\n"
            "@pytest.mark.oracle_gate\n"
            "def test_ok():\n"
            "    assert True\n"
        )
    (tmp_path / "test_phase1_tables.py").write_text(
        "from capfib import this_name_does_not_exist  # noqa: F401\n"
    )


def test_a_module_that_fails_to_collect_is_named_by_the_gate(tmp_path):
    """The property `GATE_MODULES` exists to provide: a `GATE_MODULES`
    module that fails to *collect* -- not merely one whose tests skip --
    must fail the session and name that module specifically, in a normal
    (unscoped) run.

    Before `test_phase1_tables.py` was added to `GATE_MODULES`
    (`tests/conftest.py`), this same fixture would still have failed the
    session -- `gate_violations` reports "N oracle-gate test(s) were
    collected but none executed" whenever collection is aborted, regardless
    of `GATE_MODULES` -- but it would not have named the broken module. That
    distinction is the whole point of `GATE_MODULES`, so it is what this
    test checks for, not just a nonzero exit code.
    """
    _write_gate_module_fixture(tmp_path)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q", str(tmp_path)],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert result.returncode != 0, result.stdout
    assert (
        "oracle-gate module(s) not collected at all: test_phase1_tables.py"
        in result.stdout
    ), result.stdout


def test_a_single_module_run_is_exempt_from_the_module_check(tmp_path):
    """Scoping the run to the broken module itself
    (`pytest test_phase1_tables.py`) must NOT produce the module-named
    failure -- not because collection aborts before the hook runs, but
    because `pytest_collection_modifyitems` deliberately sets
    `selection_narrowed = True` for any `.py`-suffixed command-line
    argument, and `pytest_sessionfinish` stands the whole `GATE_MODULES`
    check down whenever a run is narrowed (see the comment beside that
    line in `tests/conftest.py`). This is the distinction a fix round of
    this task's review flagged: an earlier report described this as a
    collection-ordering accident, which this test disproves by construction
    -- `selection_narrowed` is set from `config.args` alone, independent of
    whether the named file actually collected anything.
    """
    _write_gate_module_fixture(tmp_path)
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q",
            str(tmp_path / "test_phase1_tables.py"),
        ],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert "ORACLE GATE FAILURE" not in result.stdout, (
        "a run scoped to a single (even broken) module is a deliberate "
        "exemption, not something the gate should have an opinion about:\n"
        + result.stdout
    )
    # pytest itself still reports the ImportError and a non-green outcome --
    # this is not a claim that a broken module is fine, only that it is not
    # the oracle gate's job to say so when the run was scoped there on
    # purpose.
    assert result.returncode != 0, result.stdout
    assert "ImportError" in result.stdout, result.stdout
