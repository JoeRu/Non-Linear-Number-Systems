"""Session-level guard: the oracle-backed gate tests must RUN, not skip.

Three separate defects on this branch were the same defect: a check that
silently did not run.

1. `tests/test_interval.py` compared intervals in a way that was blind to a
   dropped term.
2. `tests/test_phase2_figures.py` called `pytest.skip` inside its document
   loop, which disabled the R-002 drift detector whenever an unrelated
   document was absent.
3. `data/phase1_data.csv` was gitignored, so on a clean clone the twelve
   comparisons of the certified T1 bound, T3 and T5 against exact values
   skipped. `59 passed, 12 skipped` is what a fresh checkout saw, and it is
   green.

Cases 1 and 2 were fixed one at a time. This file fixes the class: every test
that can only do its job against a real oracle carries the `oracle_gate`
marker, and a session in which any such test skipped -- or in which none of
them ran at all, while the module holding them was collected -- fails, whatever
the individual test outcomes were.

The marker is deliberately not a substitute for the tests themselves failing
when their oracle is missing (they do: `_exact()` raises). It is the second
lock, for the case where a future edit reintroduces a `pytest.skip`, an
`importorskip`, or a `skipif` on one of them.
"""

import pytest

MARKER = "oracle_gate"

# Modules that must contribute at least one executed `oracle_gate` test when
# they are collected. Without this, deleting every marker -- or letting a
# collection error take out the whole module -- would leave the guard with
# nothing to complain about.
GATE_MODULES = ("test_phase2_bounds.py", "test_phase2_figures.py")


def gate_violations(collected: int, executed: int, skipped: list[str]) -> list[str]:
    """Return the reasons this session's oracle gate did not really run.

    Pure function of the counts so it can be tested directly; see
    `tests/test_oracle_gate_guard.py`.

    Args:
        collected: number of `oracle_gate` tests collected this session.
        executed: number of them that reached a call-phase outcome (passed
            or failed -- either way the comparison ran).
        skipped: node ids of `oracle_gate` tests that skipped.

    Returns:
        A list of human-readable violation strings; empty means the gate ran.
    """
    problems = []
    if skipped:
        problems.append(
            "oracle-gate tests SKIPPED rather than ran -- a skipped gate is not "
            "a gate: " + ", ".join(sorted(skipped))
        )
    if collected and executed == 0:
        problems.append(
            f"{collected} oracle-gate test(s) were collected but none executed"
        )
    return problems


class _GateState:
    def __init__(self):
        self.collected = 0
        self.executed = 0
        self.skipped: list[str] = []
        self.gate_modules_collected: set[str] = set()
        self.selection_narrowed = False


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "oracle_gate: compares a public computation against a real oracle; "
        "must run, never skip (enforced by tests/conftest.py)",
    )
    config._oracle_gate = _GateState()
    # A deliberately narrowed run (-k, --deselect, an explicit node id, or a
    # marker expression) is not a broken gate, so the whole-session
    # requirements below stand down. Skips are still reported: narrowing
    # selects tests, it does not license one of the selected ones to skip.
    config._oracle_gate.selection_narrowed = bool(
        config.option.keyword or config.option.markexpr
        or getattr(config.option, "deselect", None)
    )


def pytest_collection_modifyitems(config, items):
    state = config._oracle_gate
    for item in items:
        if item.get_closest_marker(MARKER):
            state.collected += 1
        name = item.path.name if hasattr(item, "path") else ""
        if name in GATE_MODULES:
            state.gate_modules_collected.add(name)
    # An explicit set of node ids on the command line is narrowing too.
    if config.args and any(
        "::" in a or a.endswith(".py") for a in config.args
    ):
        state.selection_narrowed = True


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    state = item.config._oracle_gate
    if not item.get_closest_marker(MARKER):
        return
    if report.when == "call" and not report.skipped:
        state.executed += 1
    if report.skipped:
        state.skipped.append(report.nodeid)


def pytest_sessionfinish(session, exitstatus):
    state = getattr(session.config, "_oracle_gate", None)
    if state is None:
        return
    problems = gate_violations(state.collected, state.executed, state.skipped)
    if not state.selection_narrowed:
        missing = [m for m in GATE_MODULES if m not in state.gate_modules_collected]
        if missing:
            # `state.selection_narrowed` already exempts narrowed runs, so no
            # further condition belongs here. An earlier version also required
            # `session.config.args` to be non-empty; that is redundant (pytest
            # fills args from `testpaths`, so it is `['tests']` on a plain run)
            # and would silently disable this check if `testpaths` were ever
            # removed from pyproject.toml.
            problems.append(
                "oracle-gate module(s) not collected at all: " + ", ".join(missing)
            )
        if state.collected == 0:
            problems.append(
                "no oracle_gate-marked tests were collected; the gate that "
                "compares T1/T3/T5 and the figure tags against real data has "
                "disappeared from the suite"
            )
    else:
        problems = [p for p in problems if "SKIPPED" in p]
    if problems:
        for p in problems:
            print(f"\nORACLE GATE FAILURE: {p}")
        session.exitstatus = 1
