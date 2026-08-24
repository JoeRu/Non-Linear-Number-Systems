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


def test_main_treats_an_unprivileged_ruleset_read_as_unverified(
    monkeypatch, tmp_path, capsys
):
    """`main()` must not read an absent `bypass_actors` key as an empty list.

    `GET /repos/{owner}/{repo}/rulesets/{id}` returns 200 with the key absent
    when the caller cannot see bypass actors. Defaulting that to `[]` reports
    "no bypass actors" for a ruleset that may well have some -- unread treated
    as none, which is the defect class this script exists to prevent.

    This test drives `main()` rather than recomputing its expression, so
    reinstating the default fails here. An earlier version recomputed
    `payload.get("bypass_actors")` in the test body; it passed against the
    defect and guarded nothing.
    """
    inventory = tmp_path / "required-checks.yml"
    inventory.write_text(
        "branch: main\n"
        "expected_integration_id: 15368\n"
        "contexts:\n"
        "  - name: tests\n"
        "    ships_in: plan-a\n"
        "  - name: required-checks\n"
        "    ships_in: plan-a\n"
        "  - name: mutations-full\n"
        "    ships_in: plan-b\n"
    )

    def fake_fetch(url, token):
        if "/rules/branches/" in url:
            return [_rule(ALL_THREE)], None
        if "/rulesets/" in url:
            # A 200 from a caller not privileged to see bypass actors: the key
            # is absent, not empty.
            return {"name": "prod", "enforcement": "active"}, None
        raise AssertionError(f"unexpected url {url}")

    monkeypatch.setattr(crc, "fetch", fake_fetch)

    exit_code = crc.main(["--repo", "owner/name", "--inventory", str(inventory)])
    output = capsys.readouterr().out

    assert exit_code == 1, (
        "an unverifiable bypass-actor list must fail the check, not pass it"
    )
    assert "could not be read" in output, (
        f"expected the unread-bypass problem, got:\n{output}"
    )
