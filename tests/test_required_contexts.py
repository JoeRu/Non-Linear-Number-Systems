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
    """And it must name the unprotected contexts, not merely the absence.

    docs/risks.md R-007 accepts a standing red that NAMES the missing tier
    instead of a merge-blocking placeholder. A run that says only "nothing is
    required" does not deliver that.
    """
    problems = crc.evaluate(INVENTORY, [], {})
    assert any("nothing is required for merge" in p for p in problems)
    assert any("mutations-full" in p and "plan-b" in p for p in problems)


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


def test_an_empty_inventory_is_rejected(tmp_path):
    """`contexts: []` verifies nothing but would otherwise report success."""
    inventory = tmp_path / "required-checks.yml"
    inventory.write_text(
        "branch: main\n"
        "expected_integration_id: 15368\n"
        "contexts: []\n"
    )
    with pytest.raises(ValueError):
        crc.load_inventory(inventory)


WORKFLOWS = ROOT / ".github" / "workflows"


def _workflow_files():
    """Every workflow in the tree, so a new one cannot escape this guard.

    The list was hardcoded as ["ci.yml", "nightly.yml"]. A workflow added
    later was therefore never checked, and the suite stayed green -- the guard
    quantified over the wrong set. Plan B adds a workflow with a mutation job,
    which is precisely the case this test exists to catch.
    """
    return sorted(
        p.name
        for p in WORKFLOWS.iterdir()
        if p.suffix in (".yml", ".yaml") and p.is_file()
    )


def test_the_workflow_scan_finds_the_known_workflows():
    """An empty or shrunken scan would make the guard below vacuous.

    Parametrising over a directory scan means the guard silently covers
    nothing if the directory is renamed or emptied, so the scan itself is
    asserted rather than trusted.
    """
    assert set(_workflow_files()) >= {"ci.yml", "nightly.yml"}, (
        f"expected at least ci.yml and nightly.yml, scanned {_workflow_files()}"
    )


@pytest.mark.parametrize("workflow", _workflow_files())
def test_no_job_is_conditional_or_dependent(workflow):
    """A skipped job reports success, so neither `if:` nor `needs:` is allowed.

    Spec section 9.3. This is the rule most likely to be undone by someone
    tidying the workflow later, and undoing it produces a required check that
    cannot fail -- silently.
    """
    import yaml as _yaml

    path = WORKFLOWS / workflow
    assert path.exists(), (
        f"{workflow} is missing. Both workflows are tracked, so an absent one "
        f"is a deletion or a rename, not a file that has not been written yet "
        f"-- and skipping over it would silently retire this guard for "
        f"everything in that file"
    )
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
        assert not job.get("continue-on-error"), (
            f"job {name!r} in {workflow} sets continue-on-error; the job then "
            f"reports success when its steps fail, which is the same false "
            f"positive as a skipped job"
        )
        for index, step in enumerate(job.get("steps") or []):
            assert not step.get("continue-on-error"), (
                f"step {index} ({step.get('name') or step.get('uses')!r}) of job "
                f"{name!r} in {workflow} sets continue-on-error; the step then "
                f"fails while the job concludes success, so a required context "
                f"is satisfied without the check having passed. A step-level "
                f"`if:` is allowed and this is not: a skipped step reports no "
                f"job status, but a tolerated failure suppresses one"
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


def _triggers(document):
    """The `on:` mapping, whichever way PyYAML parsed the key.

    PyYAML implements YAML 1.1, in which a bare `on:` is the boolean True.
    """
    return document.get("on", document.get(True)) or {}


def test_ci_declares_the_events_it_promises():
    """Deleting a trigger would retire the checks silently, with a green suite.

    The push and pull_request triggers are what make every merge candidate run
    the suite from a fresh checkout; `synchronize` is what makes a later push
    to an open pull request re-run it.
    """
    import yaml as _yaml

    triggers = _triggers(_yaml.safe_load((WORKFLOWS / "ci.yml").read_text()))
    assert "push" in triggers, "ci.yml no longer runs on push"
    assert "pull_request" in triggers, "ci.yml no longer runs on pull requests"
    types = (triggers.get("pull_request") or {}).get("types") or []
    for required in ("opened", "synchronize", "reopened"):
        assert required in types, (
            f"ci.yml's pull_request trigger no longer includes {required!r}; "
            f"without it a pull request can be updated without re-running"
        )


def test_the_nightly_declares_its_schedule_and_still_builds_lean():
    """The Lean build exists only here, so losing it loses the check entirely.

    Spec D12 keeps `lake build` off the merge path deliberately, which means
    the scheduled run is the only thing that ever compiles the Lean layer.
    """
    import yaml as _yaml

    document = _yaml.safe_load((WORKFLOWS / "nightly.yml").read_text())
    triggers = _triggers(document)
    assert "schedule" in triggers, "nightly.yml no longer runs on a schedule"
    lines = [
        line.strip()
        for job in document["jobs"].values()
        for step in (job.get("steps") or [])
        for line in str(step.get("run", "")).splitlines()
    ]

    def _runs(command):
        """True when some step actually invokes `command`.

        Line-level and anchored at the start, because an earlier version
        substring-matched the joined commands and was satisfied by the string
        "lake build" appearing inside the cache step's echo message -- an
        assertion that could not fail.
        """
        return any(line.startswith(command) for line in lines)

    assert _runs("lake build"), (
        "nightly.yml no longer runs `lake build`; D12 keeps it off the merge "
        "path, so this is the only place the Lean layer is ever compiled"
    )
    assert _runs("lake update"), (
        "nightly.yml no longer runs `lake update`; lean/.lake is gitignored, so "
        "without it Mathlib is never materialised on a fresh runner"
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

    def fake_fetch_all(url, token):
        assert "/rules/branches/" in url, f"unexpected url {url}"
        return [_rule(ALL_THREE)], None

    def fake_fetch(url, token):
        assert "/rulesets/" in url, f"unexpected url {url}"
        # A 200 from a caller not privileged to see bypass actors: the key
        # is absent, not empty.
        return {"name": "prod", "enforcement": "active"}, None

    monkeypatch.setattr(crc, "fetch_all", fake_fetch_all)
    monkeypatch.setattr(crc, "fetch", fake_fetch)

    exit_code = crc.main(
        ["--repo", "owner/name", "--inventory", str(inventory), "--check-bypass"]
    )
    output = capsys.readouterr().out

    assert exit_code == 1, (
        "an unverifiable bypass-actor list must fail the check, not pass it"
    )
    assert "could not be read" in output, (
        f"expected the unread-bypass problem, got:\n{output}"
    )


def test_fetch_all_follows_pagination(monkeypatch):
    """An unpaginated GET truncates at 30 and would read as "nothing is
    required" while something is.
    """
    page1 = [_rule(ALL_THREE, ruleset_id=1)]
    page2 = [_rule(ALL_THREE, ruleset_id=2)]
    requested_urls = []

    def fake_get(url, token):
        requested_urls.append(url)
        if "page=2" not in url:
            return page1, None, '<https://api.example/next?page=2>; rel="next"'
        return page2, None, ""

    monkeypatch.setattr(crc, "_get", fake_get)

    items, error = crc.fetch_all("https://api.example/rules", None)

    assert error is None
    assert items == page1 + page2
    assert len(requested_urls) == 2


def test_fetch_all_reports_an_error_rather_than_a_short_list(monkeypatch):
    """A partial list is worse than no list, because it looks like an answer."""
    page1 = [_rule(ALL_THREE, ruleset_id=1)]

    def fake_get(url, token):
        if "page=2" not in url:
            return page1, None, '<https://api.example/next?page=2>; rel="next"'
        return None, "HTTP 500 for https://api.example/next?page=2", ""

    monkeypatch.setattr(crc, "_get", fake_get)

    items, error = crc.fetch_all("https://api.example/rules", None)

    assert items is None
    assert error is not None


def test_bypass_is_not_reported_as_unread_when_it_was_not_requested():
    """Skipping a check and failing a check are different outcomes and must
    not be conflated.
    """
    problems = crc.evaluate(INVENTORY, [_rule(ALL_THREE)], {}, check_bypass=False)
    assert not any("could not be read" in p for p in problems)

    problems = crc.evaluate(INVENTORY, [_rule(ALL_THREE)], {}, check_bypass=True)
    assert any("could not be read" in p for p in problems)


def test_main_says_plainly_when_bypass_was_not_checked(monkeypatch, tmp_path, capsys):
    """The run must state which properties it did not establish, rather than
    letting a green exit imply it checked everything.
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

    def fake_fetch_all(url, token):
        return [_rule(ALL_THREE)], None

    def fake_fetch(url, token):
        raise AssertionError(f"fetch should not be called without --check-bypass: {url}")

    monkeypatch.setattr(crc, "fetch_all", fake_fetch_all)
    monkeypatch.setattr(crc, "fetch", fake_fetch)

    exit_code = crc.main(["--repo", "owner/name", "--inventory", str(inventory)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "NOT CHECKED: ruleset bypass actors" in output


def test_the_bypass_notice_prints_even_when_the_rules_request_fails(
    monkeypatch, tmp_path, capsys
):
    """A run that fails for one reason must still state which properties it
    did not establish, or the omission is invisible exactly when things are
    going wrong.

    `main()` used to print its two error-path lines and return 1 before
    reaching the bypass notice, so a failed branch-rules request silently
    dropped the "NOT CHECKED: ruleset bypass actors" line that every other
    exit path prints.
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

    def fake_fetch_all(url, token):
        return None, "HTTP 403 for https://api.example/rules/branches/main"

    monkeypatch.setattr(crc, "fetch_all", fake_fetch_all)

    exit_code = crc.main(["--repo", "owner/name", "--inventory", str(inventory)])
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "NOT CHECKED: ruleset bypass actors" in output
