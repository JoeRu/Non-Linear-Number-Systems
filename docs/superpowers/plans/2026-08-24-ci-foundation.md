# Plan A — Non-Mutation CI Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give this repository its first continuous integration — a fresh-checkout run of the suite and the claim validator on every push and pull request, a scheduled Lean build, and a job that verifies the repository's required-check configuration against a tracked inventory.

**Architecture:** Two workflow files (`ci.yml` for push and pull request, `nightly.yml` for the schedule) plus one Python checker. The checker is split into pure functions over already-fetched GitHub API payloads and a thin `main` that fetches, so its logic is unit-tested with no network — an unverifiable verifier would reproduce the defect class this spec exists to close. The required-check inventory is a tracked YAML file naming every context that must be required, including one that does not exist until Plan B, so the verifier stands red and names what is missing.

**Tech Stack:** GitHub Actions, Python 3.12, pytest, PyYAML, elan/lake for Lean 4 + Mathlib v4.14.0.

**Spec:** `docs/superpowers/specs/2026-08-23-defect-prevention-infrastructure-design.md` at commit `d114e1b` — §3A, §4 (rule 5 amendment), §9.3, §9.4. Read §9.4 before starting: it states what this plan deliberately leaves unsatisfied.

> **Superseded code blocks.** Tasks 1–4 below quote the code as first written.
> Several blocks were corrected during review — the bypass-actor default, the
> job permissions, the hardcoded workflow list, and `evaluate()`'s early return.
> The shipped files in `scripts/`, `tests/` and `.github/` are authoritative;
> where they differ from a block below, the file is right and the block is
> history.

## Global Constraints

- Python `>=3.11` is the declared floor (`pyproject.toml`). CI pins **3.12** and exercises one version only; the 3.11 floor is therefore **unverified by CI**, and Task 2 records that as a named limitation rather than leaving it implied.
- Runtime dependencies are exactly `numpy>=1.26`, `matplotlib>=3.8`, `pyyaml>=6.0`, `mpmath>=1.3`; the only dev dependency is `pytest>=8.0`. Do not add dependencies.
- **No job may carry a job-level `if:` and no job may `needs:` another.** A job skipped by a condition reports *success*, so a required context can be satisfied by a job that never ran (§9.3). This is the single most important constraint in this plan.
- The verifier must query `GET /repos/{owner}/{repo}/rules/branches/{branch}`. **Not** `GET /repos/{owner}/{repo}/rulesets`, which returns ruleset summaries carrying no required-check contexts.
- A check that cannot be performed is reported as a problem, never as a pass.
- **Out of scope, all of it Plan B:** the mutation registry, `tests/properties.py`, the `load_bearing` marker, both mutation tiers, the fingerprint, the waiver machinery, artifact publication, and CLAUDE.md rule 11. Do not create any of them. Do not add `.superpowers/registry/`.
- After this plan, **AC8 and AC9 remain unsatisfied** and AC12 is satisfied only once the workflows actually run green. Do not write anything claiming otherwise.
- Lean: never remove a `sorry` without a real proof. This plan adds no Lean code.
- Commit at the end of every task.
- **No step below states a fixed full-suite pass count as a target.** The
  suite has grown since this plan was drafted and keeps growing; treat every
  "run the full suite" step as "report the count you measure," never as "match
  the number printed here."

---

### Task 1: Required-check inventory and its verifier

**Files:**
- Create: `.github/required-checks.yml`
- Create: `scripts/check_required_contexts.py`
- Test: `tests/test_required_contexts.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `scripts/check_required_contexts.py` exposing
  `load_inventory(path: Path) -> dict` and
  `evaluate(inventory: dict, branch_rules: list[dict], ruleset_bypass: dict[int, list | None]) -> list[str]`,
  and a CLI `python scripts/check_required_contexts.py --repo OWNER/NAME`
  that exits 0 when `evaluate` returns an empty list and 1 otherwise.
  Task 2's workflow calls that CLI. The context names in the inventory —
  `tests`, `required-checks` — are the `name:` values Task 2 must give its jobs.

- [ ] **Step 1: Write the inventory**

Create `.github/required-checks.yml`:

```yaml
# Contexts that must be required for merge on the protected branch.
#
# This file is the *desired* configuration, not a description of the current
# one. `scripts/check_required_contexts.py` reads it back against the
# repository's active branch rules and fails while they disagree.
#
# `mutations-full` does not exist yet -- it ships with Plan B (the mutation
# registry). Until then the verifier fails on every run and names it. That
# standing red is deliberate: see spec section 9.4 and docs/risks.md R-007.
# Deleting this entry to make CI green would be the defect this file exists
# to prevent, so it is not an option.
branch: main

# GitHub Actions' app id. A context satisfied by any other producer is not the
# check we asked for, so the producer is pinned rather than assumed.
expected_integration_id: 15368

contexts:
  - name: tests
    ships_in: plan-a
    why: the suite and the claim validator, from a fresh checkout
  - name: required-checks
    ships_in: plan-a
    why: this verifier; it is in its own inventory, because a verifier that
      is itself optional verifies nothing
  - name: mutations-full
    ships_in: plan-b
    why: the full mutation tier; acceptance criterion 8 is about this context
```

- [ ] **Step 2: Write the failing tests**

Create `tests/test_required_contexts.py`:

```python
"""Unit tests for the required-check verifier.

Every case runs against a recorded payload shape, never the network: a check
whose own correctness depends on a live API cannot be part of the suite, and
the point of this verifier is that it is checkable.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
try:
    import check_required_contexts as crc
finally:
    sys.path.remove(str(ROOT / "scripts"))


INVENTORY = {
    "branch": "main",
    "expected_integration_id": 15368,
    "contexts": [
        {"name": "tests", "ships_in": "plan-a"},
        {"name": "required-checks", "ships_in": "plan-a"},
        {"name": "mutations-full", "ships_in": "plan-b"},
    ],
}


def _rule(contexts, strict=True, ruleset_id=1):
    return {
        "type": "required_status_checks",
        "ruleset_id": ruleset_id,
        "parameters": {
            "strict_required_status_checks_policy": strict,
            "required_status_checks": contexts,
        },
    }


def _ctx(name, integration_id=15368):
    return {"context": name, "integration_id": integration_id}


ALL_THREE = [_ctx("tests"), _ctx("required-checks"), _ctx("mutations-full")]


def test_fully_configured_repository_has_no_problems():
    problems = crc.evaluate(INVENTORY, [_rule(ALL_THREE)], {1: []})
    assert problems == []


def test_no_rule_at_all_is_reported():
    problems = crc.evaluate(INVENTORY, [], {})
    assert len(problems) == 1
    assert "nothing is required for merge" in problems[0]


def test_a_missing_context_is_named_with_the_plan_that_ships_it():
    rule = _rule([_ctx("tests"), _ctx("required-checks")])
    problems = crc.evaluate(INVENTORY, [rule], {1: []})
    assert any("mutations-full" in p and "plan-b" in p for p in problems)


def test_the_verifier_does_not_exempt_itself():
    """The inventory includes `required-checks`, so its absence is a problem.

    A verifier that quantifies over everything but itself can be optional
    while reporting that everything else is required.
    """
    rule = _rule([_ctx("tests"), _ctx("mutations-full")])
    problems = crc.evaluate(INVENTORY, [rule], {1: []})
    assert any("required-checks" in p for p in problems)


def test_a_foreign_producer_cannot_satisfy_a_context():
    rule = _rule([_ctx("tests", 999), _ctx("required-checks"), _ctx("mutations-full")])
    problems = crc.evaluate(INVENTORY, [rule], {1: []})
    assert any("999" in p and "tests" in p for p in problems)


def test_a_duplicated_context_is_reported():
    rule = _rule(ALL_THREE + [_ctx("tests")])
    problems = crc.evaluate(INVENTORY, [rule], {1: []})
    assert any("required 2 times" in p for p in problems)


def test_loose_policy_is_reported():
    problems = crc.evaluate(INVENTORY, [_rule(ALL_THREE, strict=False)], {1: []})
    assert any("strict_required_status_checks_policy" in p for p in problems)


def test_a_bypass_actor_defeats_requiredness():
    problems = crc.evaluate(
        INVENTORY, [_rule(ALL_THREE)], {1: [{"actor_id": 5, "actor_type": "Team"}]}
    )
    assert any("bypass actor" in p for p in problems)


def test_unreadable_bypass_actors_are_a_problem_not_a_pass():
    """`None` means the token could not read them. That is not evidence of none.

    This is the whole spec's recurring lesson: a check that did not run must
    say so rather than report success.
    """
    problems = crc.evaluate(INVENTORY, [_rule(ALL_THREE)], {1: None})
    assert any("could not be read" in p for p in problems)


def test_two_rules_are_reported():
    rules = [_rule(ALL_THREE, ruleset_id=1), _rule(ALL_THREE, ruleset_id=2)]
    problems = crc.evaluate(INVENTORY, rules, {1: [], 2: []})
    assert any("expected exactly one" in p for p in problems)


def test_the_tracked_inventory_parses_and_names_the_plan_b_context():
    """The shipped file, not a fixture -- so a typo in it fails the suite."""
    inventory = crc.load_inventory(ROOT / ".github" / "required-checks.yml")
    names = {c["name"] for c in inventory["contexts"]}
    assert names == {"tests", "required-checks", "mutations-full"}
    assert inventory["branch"] == "main"
    plan_b = [c for c in inventory["contexts"] if c["ships_in"] == "plan-b"]
    assert [c["name"] for c in plan_b] == ["mutations-full"], (
        "the Plan B context must stay in the inventory: removing it is how "
        "this file stops reporting that Plan B has not shipped"
    )
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_required_contexts.py -q`
Expected: FAIL, collection error — `ModuleNotFoundError: No module named 'check_required_contexts'`

- [ ] **Step 4: Write the verifier**

Create `scripts/check_required_contexts.py`:

```python
"""Verify the repository's required status checks against a tracked inventory.

Acceptance criterion 8 of the defect-prevention spec requires the full
mutation tier's status check to be *required for merge*, and requires that
configuration to be "verified, not assumed -- a non-required job satisfies
'the workflow exists' while blocking nothing". The pytest suite cannot supply
that verification: whether a check is required is a fact about the
repository's ruleset, not about this tree. This script is the verification,
and it runs as its own CI job.

The logic is pure functions over already-fetched payloads, so it is unit
tested without network access (`tests/test_required_contexts.py`). Only
`fetch` and `main` touch the API.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

API = "https://api.github.com"
RULE_TYPE = "required_status_checks"


def load_inventory(path: Path) -> dict:
    """Read the tracked inventory of contexts that must be required.

    Args:
        path: path to `.github/required-checks.yml`.

    Returns:
        The parsed mapping, with `branch`, `expected_integration_id` and
        `contexts` keys.

    Raises:
        KeyError: if a required key is absent -- a malformed inventory must
            stop the run rather than degrade into checking nothing.
    """
    data = yaml.safe_load(path.read_text())
    for key in ("branch", "expected_integration_id", "contexts"):
        if key not in data:
            raise KeyError(f"{path} has no {key!r} key")
    return data


def evaluate(
    inventory: dict,
    branch_rules: list[dict],
    ruleset_bypass: dict[int, list | None],
) -> list[str]:
    """Compare the tracked inventory against the branch's active rules.

    Args:
        inventory: as returned by `load_inventory`.
        branch_rules: the JSON list from
            `GET /repos/{owner}/{repo}/rules/branches/{branch}`. That endpoint
            returns the rules actually in force and omits disabled and
            evaluate-mode ones, which is why it is used instead of
            `/rulesets`.
        ruleset_bypass: maps a ruleset id to its bypass actors. A value of
            `None` means the token could not read that ruleset; it is
            reported as a problem, because "unread" is not "none".

    Returns:
        Human-readable problem strings. An empty list means the configuration
        matches the inventory.
    """
    problems: list[str] = []
    rules = [r for r in branch_rules if r.get("type") == RULE_TYPE]

    if not rules:
        return [
            f"no {RULE_TYPE} rule applies to branch {inventory['branch']!r}: "
            f"nothing is required for merge"
        ]
    if len(rules) > 1:
        problems.append(
            f"{len(rules)} {RULE_TYPE} rules apply to branch "
            f"{inventory['branch']!r}; expected exactly one, because two rules "
            f"can disagree and the weaker one wins"
        )

    seen: dict[str, list] = {}
    for rule in rules:
        for check in rule.get("parameters", {}).get(RULE_TYPE, []):
            seen.setdefault(check.get("context"), []).append(
                check.get("integration_id")
            )

    for context, integrations in sorted(seen.items()):
        if len(integrations) > 1:
            problems.append(
                f"context {context!r} is required {len(integrations)} times; "
                f"duplicates make it ambiguous which producer satisfies it"
            )

    expected = inventory["expected_integration_id"]
    for entry in inventory["contexts"]:
        name = entry["name"]
        if name not in seen:
            problems.append(
                f"context {name!r} is not required for merge "
                f"(ships in {entry['ships_in']})"
            )
            continue
        for got in seen[name]:
            if got != expected:
                problems.append(
                    f"context {name!r} expects integration {got!r}, not "
                    f"{expected!r}: another producer could satisfy this name"
                )

    for rule in rules:
        if not rule.get("parameters", {}).get(
            "strict_required_status_checks_policy"
        ):
            problems.append(
                "strict_required_status_checks_policy is not set: under the "
                "loose policy GitHub permits merging a pull request whose "
                "checks ran against a base that has since advanced"
            )

    for rule in rules:
        rid = rule.get("ruleset_id")
        actors = ruleset_bypass.get(rid)
        if actors is None:
            problems.append(
                f"bypass actors for ruleset {rid} could not be read with this "
                f"token: unverified, which is not the same as none"
            )
        elif actors:
            problems.append(
                f"ruleset {rid} has {len(actors)} bypass actor(s); a check an "
                f"actor may bypass is not required for merge"
            )

    return problems


def fetch(url: str, token: str | None) -> tuple[object | None, str | None]:
    """GET a JSON endpoint.

    Returns:
        A `(payload, error)` pair. Exactly one is `None`. Errors are returned
        rather than raised so a permissions failure becomes a reported
        problem instead of a traceback that hides which check did not run.
    """
    request = urllib.request.Request(url)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response), None
    except urllib.error.HTTPError as exc:
        return None, f"HTTP {exc.code} for {url}"
    except (urllib.error.URLError, TimeoutError) as exc:
        return None, f"{type(exc).__name__} for {url}: {exc}"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="OWNER/NAME")
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path(__file__).resolve().parents[1] / ".github"
        / "required-checks.yml",
    )
    args = parser.parse_args(argv)

    inventory = load_inventory(args.inventory)
    token = os.environ.get("GITHUB_TOKEN")

    branch = inventory["branch"]
    rules, error = fetch(
        f"{API}/repos/{args.repo}/rules/branches/{branch}", token
    )
    if error:
        print(f"PROBLEM: could not read branch rules -- {error}")
        print("Writing no verdict: an unread configuration is not a verified one.")
        return 1

    bypass: dict[int, list | None] = {}
    for rule in rules:
        if rule.get("type") != RULE_TYPE:
            continue
        rid = rule.get("ruleset_id")
        if rid in bypass:
            continue
        payload, error = fetch(
            f"{API}/repos/{args.repo}/rulesets/{rid}", token
        )
        bypass[rid] = None if error else payload.get("bypass_actors", [])

    problems = evaluate(inventory, rules, bypass)
    if not problems:
        names = ", ".join(c["name"] for c in inventory["contexts"])
        print(f"required checks verified on {branch}: {names}")
        return 0

    print(f"{len(problems)} problem(s) with the required-check configuration:")
    for problem in problems:
        print(f"  - {problem}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_required_contexts.py -q`
Expected: PASS, 11 passed

- [ ] **Step 6: Verify the CLI reports the current, unconfigured state honestly**

Run: `GITHUB_TOKEN=$(gh auth token) .venv/bin/python scripts/check_required_contexts.py --repo JoeRu/Non-Linear-Number-Systems`

Expected: exit 1, printing exactly one problem —
`no required_status_checks rule applies to branch 'main': nothing is required for merge`.

That is the correct answer today: no ruleset exists. A run that printed
"verified" here would mean the checker cannot detect an unprotected branch.

- [ ] **Step 7: Run the full suite**

Run: `.venv/bin/python -m pytest -q`
Expected: PASS, all green, 0 skipped. Do not assume a baseline count — the
suite has grown since this plan was drafted; report the number you measure.

- [ ] **Step 8: Commit**

```bash
git add .github/required-checks.yml scripts/check_required_contexts.py tests/test_required_contexts.py
git commit -m "feat: tracked required-check inventory and its verifier

The inventory names every context that must be required for merge, including
mutations-full, which does not exist until Plan B. The verifier reads it back
against GET /repos/{owner}/{repo}/rules/branches/{branch} -- not /rulesets,
which carries no required-check contexts -- and fails while they disagree.

Unreadable bypass actors are reported as a problem rather than a pass: an
unread configuration is not a verified one."
```

---

### Task 2: Push and pull-request workflow

**Files:**
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: `scripts/check_required_contexts.py --repo OWNER/NAME` from Task 1, and the context names `tests` and `required-checks` from `.github/required-checks.yml`.
- Produces: two status contexts named exactly `tests` and `required-checks`. Task 5's rollout configures those names.

- [ ] **Step 1: Write the workflow**

Create `.github/workflows/ci.yml`:

```yaml
# This repository's first CI. Its cheapest and most valuable property is that
# every run starts from a fresh checkout: the recurrence where twelve
# comparison tests silently skipped because data/phase1_data.csv was
# gitignored could not have survived one, with no mutation and no one having
# to think of it.
#
# Two rules govern the job list, and both come from spec section 9.3:
#
#   1. No job carries a job-level `if:`. A skipped job reports *success*, so a
#      required context can be satisfied by a job that never ran.
#   2. No job `needs:` another. A dependent job skips when its dependency
#      fails, which is the same false positive by another route.
#
# Adding either would make a required check that cannot fail.
name: CI

on:
  push:
    branches: ["**"]
  pull_request:
    # `edited` fires when a pull request is retargeted, so a retarget
    # re-evaluates instead of inheriting a verdict computed against the old
    # base branch.
    types: [opened, synchronize, reopened, edited]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  # Context name: `tests`. Must match .github/required-checks.yml.
  tests:
    name: tests
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          # pyproject declares requires-python >= 3.11, and CI exercises 3.12
          # only. The 3.11 floor is therefore NOT verified here; a 3.12-only
          # construct would reach main unremarked. Stated rather than implied.
          python-version: "3.12"

      - name: Install the package and its test dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e '.[dev]'

      - name: Run the test suite
        run: python -m pytest -q

      - name: Validate the claim ledger
        # Runs even when pytest fails, because the two answer different
        # questions and a reader wants both. Step-level `if` is fine: it does
        # not make the *job* skip, so it cannot report a false success.
        if: ${{ !cancelled() }}
        run: python scripts/check_claims.py

  # Context name: `required-checks`. Must match .github/required-checks.yml.
  #
  # Deliberately independent of `tests`: `needs: tests` would make this job
  # skip whenever the suite fails, and a skipped required check reports
  # success.
  #
  # This job is EXPECTED TO FAIL until Plan B ships, because the inventory
  # names the `mutations-full` context and nothing produces it yet. That
  # standing red is the design (spec section 9.4, docs/risks.md R-007). Do not
  # "fix" it by editing the inventory.
  required-checks:
    name: required-checks
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install PyYAML
        run: pip install 'pyyaml>=6.0'

      - name: Verify the required-check configuration
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python scripts/check_required_contexts.py --repo "${{ github.repository }}"
```

- [ ] **Step 2: Validate the YAML parses**

Run: `.venv/bin/python -c "import yaml,pathlib; d=yaml.safe_load(pathlib.Path('.github/workflows/ci.yml').read_text()); print(sorted(d['jobs']))"`
Expected: `['required-checks', 'tests']`

- [ ] **Step 3: Assert the two structural rules mechanically**

Add to `tests/test_required_contexts.py`:

```python
WORKFLOWS = ROOT / ".github" / "workflows"


@pytest.mark.parametrize("workflow", ["ci.yml", "nightly.yml"])
def test_no_job_is_conditional_or_dependent(workflow):
    """A skipped job reports success, so neither `if:` nor `needs:` is allowed.

    Spec section 9.3. This is the rule most likely to be undone by someone
    tidying the workflow later, and undoing it produces a required check that
    cannot fail -- silently.
    """
    import yaml as _yaml

    path = WORKFLOWS / workflow
    if not path.exists():
        pytest.skip(f"{workflow} not written yet")
    jobs = _yaml.safe_load(path.read_text())["jobs"]
    for name, job in jobs.items():
        assert "if" not in job, (
            f"job {name!r} in {workflow} carries a job-level `if:`; a skipped "
            f"job reports success, so a required context could be satisfied "
            f"by a job that never ran"
        )
        assert "needs" not in job, (
            f"job {name!r} in {workflow} uses `needs:`; a dependent job skips "
            f"when its dependency fails, which reports success the same way"
        )


def test_ci_job_names_match_the_inventory():
    """Context names come from the job's `name:`, so a rename breaks the gate."""
    import yaml as _yaml

    jobs = _yaml.safe_load((WORKFLOWS / "ci.yml").read_text())["jobs"]
    produced = {job["name"] for job in jobs.values()}
    inventory = crc.load_inventory(ROOT / ".github" / "required-checks.yml")
    plan_a = {c["name"] for c in inventory["contexts"] if c["ships_in"] == "plan-a"}
    assert plan_a <= produced, (
        f"inventory expects {sorted(plan_a)} but ci.yml produces "
        f"{sorted(produced)}; a required context no job emits can never pass"
    )
```

- [ ] **Step 4: Run the new tests**

Run: `.venv/bin/python -m pytest tests/test_required_contexts.py -q`
Expected: PASS, 13 passed and 1 skipped. The skip is the `nightly.yml`
parametrisation of `test_no_job_is_conditional_or_dependent`; Task 3 writes
that file and Task 3 step 2 is where it must stop skipping.

- [ ] **Step 5: Amend CLAUDE.md rule 5**

Replace lines 125-126 of `CLAUDE.md`:

```markdown
5. **Respect the correctness gate, and treat absence as failure.** Never present
   `capfib.dp` or `capfib.gf` output as a fact until it has passed the
   cross-checks described in Global Constraints above.

   **A gate that skips is a gate that did not run.** The same standard applies
   to a check's *absence* as to its result: a skipped comparison, an
   unreadable configuration, a test that did not collect and a guard whose
   input file is missing are all failures, never passes. Verification claims
   are checked from a clean clone rather than from a working tree — CI does
   this on every push, and `data/phase1_data.csv` is the reason it must:
   while it was gitignored, twelve T1/T3/T5 comparisons skipped on every
   clean clone and the suite still reported green.
```

- [ ] **Step 6: Confirm nothing else in CLAUDE.md renumbered**

Run: `grep -n "^[0-9]\+\." CLAUDE.md | head -12`
Expected: rules 1 through 10, unchanged in number and order.

- [ ] **Step 7: Run the full suite**

Run: `.venv/bin/python -m pytest -q`
Expected: PASS, 1 skipped, otherwise green. Three test items were added
relative to the preceding task's count (`test_no_job_is_conditional_or_dependent`
parametrises over two workflows, plus `test_ci_job_names_match_the_inventory`),
and the `nightly.yml` one skips until Task 3 — do not assume a total; report
the count you measure against the preceding task's.

- [ ] **Step 8: Commit**

```bash
git add .github/workflows/ci.yml tests/test_required_contexts.py CLAUDE.md
git commit -m "feat: CI on push and pull request, and the rule 5 amendment

Two jobs, `tests` and `required-checks`, neither conditional nor dependent:
a skipped job reports success, so either would produce a required check that
cannot fail. A test asserts both properties mechanically, since that is the
rule most likely to be undone by later tidying.

required-checks is expected to fail until Plan B ships -- the inventory names
mutations-full and nothing produces it yet. That standing red is the design.

CLAUDE.md rule 5 now extends the correctness gate to absence: a gate that
skips is a gate that did not run."
```

---

### Task 3: Scheduled Lean build

**Files:**
- Create: `.github/workflows/nightly.yml`

**Interfaces:**
- Consumes: the structural test from Task 2, which parametrises over `nightly.yml` and currently skips. Writing this file activates it.
- Produces: no required context. The schedule is a monitor, not a gate — spec D12 keeps `lake build` off the merge path.

- [ ] **Step 1: Write the workflow**

Create `.github/workflows/nightly.yml`:

```yaml
# The Lean layer is built on a schedule, never on push or pull request.
#
# Spec D12: Mathlib needs a large cache (measured: lean/.lake is 5.1 GB) and
# the layer changes rarely, so a nightly build bounds an unremarked regression
# to a day for the price of one cache, rather than one per pull request. The
# gap is deliberate and named in section 3A -- a Lean regression does reach
# main unremarked until the next run.
#
# The Python job is repeated here rather than reused. It is cheap, and it
# catches something the push workflow cannot: a dependency released since the
# last commit. Nothing in this repository is pinned beyond a lower bound.
name: Nightly

on:
  schedule:
    # 03:00 UTC daily.
    - cron: "0 3 * * *"
  workflow_dispatch:

permissions:
  contents: read

jobs:
  python:
    name: nightly-python
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install the package and its test dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e '.[dev]'
      - name: Run the test suite
        run: python -m pytest -q
      - name: Validate the claim ledger
        if: ${{ !cancelled() }}
        run: python scripts/check_claims.py

  lean:
    name: nightly-lean
    runs-on: ubuntu-latest
    timeout-minutes: 90
    steps:
      - uses: actions/checkout@v4

      - name: Install elan
        run: |
          curl -sSfL \
            https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
            -o elan-init.sh
          sh elan-init.sh -y --default-toolchain none
          echo "$HOME/.elan/bin" >> "$GITHUB_PATH"

      - name: Report the pinned toolchain
        working-directory: lean
        run: |
          echo "toolchain: $(cat lean-toolchain)"
          lake --version

      - name: Fetch prebuilt Mathlib artifacts
        working-directory: lean
        # Mathlib is pinned to the official v4.14.0 tag, so its own build cache
        # has artifacts for exactly this revision -- a cold build of ~5 GB is
        # avoidable. `cache get` is best-effort: if it misses, `lake build`
        # below still produces a correct answer, only slowly.
        run: lake exe cache get || echo "cache miss; lake build will compile"

      - name: Build
        working-directory: lean
        run: lake build
```

- [ ] **Step 2: Validate the YAML and the structural rules**

Run: `.venv/bin/python -m pytest tests/test_required_contexts.py -q`
Expected: PASS, 14 passed and **0 skipped**. The `nightly.yml` parametrisation
of `test_no_job_is_conditional_or_dependent` now runs. A skip here means the
file was written to the wrong path — check it is `.github/workflows/nightly.yml`.

- [ ] **Step 3: Confirm the toolchain and Mathlib pin the workflow relies on**

Run: `cat lean/lean-toolchain && grep -A1 'require mathlib' lean/lakefile.lean`
Expected: `leanprover/lean4:v4.14.0`, and Mathlib required at `"v4.14.0"`.

If either differs, the "official tag, so `cache get` has artifacts" reasoning in the workflow comment is wrong and the comment must be corrected before committing.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/nightly.yml
git commit -m "feat: nightly workflow with the Lean build

lake build runs on the schedule only, per D12: Mathlib needs a 5.1 GB cache
and the layer changes rarely, so a nightly run bounds an unremarked
regression to a day for one cache rather than one per pull request. The gap
is real and named -- a Lean regression reaches main until the next run.

Mathlib is pinned to the official v4.14.0 tag, so `lake exe cache get` can
fetch prebuilt artifacts instead of cold-building; the step tolerates a miss.

The Python job is repeated rather than reused: it catches a dependency
released since the last commit, which the push workflow cannot."
```

- [ ] **Step 5: Verification cannot happen until after merge**

This is the one task whose correctness cannot be established locally, and it
cannot be established from this branch either: GitHub only accepts
`workflow_dispatch` for a workflow that exists on the repository's default
branch, so `gh workflow run nightly.yml --ref ci-workflow` fails while
`nightly.yml` lives only on `ci-workflow`. The actual trigger-and-watch step
moves to Task 5's rollout sequence, after the merge to `main` that puts
`nightly.yml` on the default branch — see Task 5's post-merge step.

If, once triggered, `lake exe cache get` fails because the `cache` executable
is unavailable before dependencies are materialised, insert `lake update`
before it and re-run. Record whichever sequence worked in the workflow
comment — do not leave the file describing a sequence that was not the one
used.

---

### Task 4: Document what Plan A does not do

**Files:**
- Modify: `docs/risks.md` (append to the R-007 entry)

**Interfaces:**
- Consumes: nothing.
- Produces: nothing later tasks read.

- [ ] **Step 1: Append the delivery record to R-007**

`docs/risks.md` already carries R-007 ("The required-check inventory reports Plan B's absence but cannot compel it"). Append to that entry, immediately before its `**What would close it.**` line:

```markdown
**Delivery record.** Plan A shipped the inventory
(`.github/required-checks.yml`), its verifier
(`scripts/check_required_contexts.py`) and the workflows on
`YYYY-MM-DD`. From that date the `required-checks` job fails on every run,
naming `mutations-full` as absent. That failure is the intended state and
must not be resolved by editing the inventory. Acceptance criteria 8 and 9
remain open; AC12 is met for the Python half only, the Lean half resting on
the nightly run.
```

Replace `YYYY-MM-DD` with the actual date of the Task 2 commit — `git log -1 --format=%ad --date=short` on that commit. A literal `YYYY-MM-DD` reaching the file is a plan failure.

- [ ] **Step 2: Verify the claim validator still passes**

Run: `.venv/bin/python scripts/check_claims.py`
Expected: `claims.yaml OK`

- [ ] **Step 3: Run the full suite**

Run: `.venv/bin/python -m pytest -q`
Expected: PASS, 284 passed, 0 skipped — the count reported by the preceding
task; do not assume a number, report the one you measure.

- [ ] **Step 4: Commit**

```bash
git add docs/risks.md
git commit -m "docs: record Plan A's delivery and what it leaves open in R-007"
```

---

### Task 5: Rollout — STOPS FOR THE MAINTAINER

**Files:** none. This task changes repository configuration, not the tree.

**Interfaces:**
- Consumes: the contexts `tests` and `required-checks` produced by Task 2.
- Produces: the configuration Task 1's verifier reads back.

> **This task performs an outward-facing configuration change to a shared
> repository and must not be executed by a subagent.** Steps 2 onward require
> the maintainer. An implementer reaching this task should complete step 1,
> then stop and hand the remaining steps to the maintainer with the run URLs.

- [ ] **Step 1: Push the branch and open the pull request**

```bash
git push -u origin ci-workflow
gh pr create --base main --title "Plan A: CI foundation" \
  --body "Implements Plan A of docs/superpowers/specs/2026-08-23-defect-prevention-infrastructure-design.md.

Ships: the workflows, the tracked required-check inventory and its verifier, and the CLAUDE.md rule 5 amendment.

The \`required-checks\` job is EXPECTED TO FAIL. The inventory names \`mutations-full\`, which ships with Plan B; until then the verifier stands red and names it. See spec section 9.4 and docs/risks.md R-007.

Leaves open: AC8, AC9, and the Lean half of AC12."
```

Expected: `tests` green; `required-checks` red, printing
`context 'mutations-full' is not required for merge (ships in plan-b)`.

Both outcomes are correct. A green `required-checks` here would mean the verifier cannot detect an unconfigured repository.

- [ ] **Step 2: (maintainer) Wait for Copilot's review**

CLAUDE.md rule 7: the review lands minutes after `gh pr create`, not on return. Read both the summary and the inline comments, verify each finding against the tree, and adapt before merging.

```bash
gh api repos/JoeRu/Non-Linear-Number-Systems/pulls/{n}/reviews
gh api repos/JoeRu/Non-Linear-Number-Systems/pulls/{n}/comments
```

- [ ] **Step 3: (maintainer) Merge, so the contexts exist on `main`**

A context cannot be marked required until it has been reported. This is why the ruleset is configured *after* merge, not before — the order in spec §9.3.

- [ ] **Step 4: (maintainer) Trigger and watch the nightly workflow**

This is the verification Task 3 step 5 deferred: `nightly.yml` now exists on
the default branch, so `workflow_dispatch` can accept it.

```bash
gh workflow run nightly.yml --ref main
gh run watch
```

Expected: `nightly-python` green; `nightly-lean` green. If `lake exe cache get`
fails because the `cache` executable is unavailable before dependencies are
materialised, insert `lake update` before it and re-run; record whichever
sequence worked in the workflow comment.

- [ ] **Step 5: (maintainer) Run the workflow and read the `required-checks` job's log**

Confirm it fails with exactly two problems: the `mutations-full` context is
not required for merge (ships in Plan B), and the printed
`NOT CHECKED: ruleset bypass actors` line, since the workflow's `GITHUB_TOKEN`
runs with `--check-bypass` off by default (§9.3, R-009). Confirm the `tests`
job is green.

- [ ] **Step 6: (maintainer) Create the ruleset — mark only `tests` required**

On `main`, require exactly `tests`, with:
- **Require branches to be up to date before merging** enabled — this is
  `strict_required_status_checks_policy`; without it GitHub permits merging
  checks that ran against a base which has since advanced.
- **No bypass actors.**

Do **not** mark `required-checks` required, and do **not** add
`mutations-full`: `mutations-full` has never been reported, so GitHub will not
accept it, and `required-checks` is designed to fail until Plan B ships
`mutations-full` — requiring it now would make every merge to `main`
impossible. `required-checks` becomes required only when Plan B ships
`mutations-full`. Until then it is an informational red. Requiring it now is
the merge-blocking placeholder `docs/risks.md` R-007 declined.

- [ ] **Step 7: (maintainer) Read the configuration back, including bypass actors**

```bash
GITHUB_TOKEN=$(gh auth token) \
  .venv/bin/python scripts/check_required_contexts.py --repo JoeRu/Non-Linear-Number-Systems --check-bypass
```

Run this locally with the maintainer's own admin token — `--check-bypass`
needs write access to the ruleset, which `GITHUB_TOKEN` in Actions does not
have (§9.3, R-009). Expected: exit 1, with exactly the two remaining
problems — `context 'required-checks' is not required for merge` and
`context 'mutations-full' is not required for merge (ships in plan-b)`. Any
*other* problem means the ruleset does not match the inventory.

- [ ] **Step 8: (maintainer) Confirm AC8 is still open, in writing**

AC8 is **not** satisfied by this rollout: neither `required-checks` nor
`mutations-full` is required, because `mutations-full` does not exist yet.
Nothing in the repository should claim otherwise. Confirm by grepping for any
accidental claim (see the corrected command in §3c of the remediation
dispatch / the grep below):

```bash
grep -rn "AC8\|acceptance criterion 8" docs/ CLAUDE.md \
  --exclude=2026-08-24-ci-foundation.md \
  | grep -iv "open\|unsatisfied\|remains\|not satisfied\|cannot close\|not met"
```

Expected: no output. If a line appears, it is a claim that AC8 is satisfied,
and it is wrong.

---

## What this plan deliberately does not deliver

Stated here so a reader of the plan alone cannot mistake its completion for the spec's:

- **AC1–AC7** — the mutation registry entire. Plan B.
- **AC8** — the full tier's context does not exist, so it cannot be required. Plan B, after a preflight run emits it.
- **AC9** — rule 5 lands here; rule 11 lands with Plan B. The criterion needs both.
- **AC12** — the Python half is met by the push workflow. The Lean half rests on the nightly run and is met only once one has passed.
- **§3A's pull-request artifact publication** — there is no registry to produce a fingerprint. Plan B.
