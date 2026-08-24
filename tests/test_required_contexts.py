"""Unit tests for the required-check verifier.

Every case runs against a recorded payload shape, never the network: a check
whose own correctness depends on a live API cannot be part of the suite, and
the point of this verifier is that it is checkable.
"""

import re
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


# Steps whose absence would empty a status context: job name -> the substring
# identifying the step that does the work that context is named for.
CORE_STEPS = {
    # check_claims.py is deliberately excluded: it carries
    # `if: ${{ !cancelled() }}` on purpose (spec: it must still run when
    # pytest fails, so both signals are visible), and that is not the false
    # positive this test guards against. Only the step that runs the suite
    # itself is required to be unconditional here.
    "tests": ("pytest",),
    "required-checks": ("check_required_contexts.py",),
}


def test_the_core_ci_steps_are_unconditional():
    """A conditional core step empties the gate while the job still reports success.

    The job-level ban on `if:` is not enough: `if: false` on the step that runs
    the suite skips the suite, the job concludes success, and the required
    context goes green with nothing behind it. The claim-validator step is
    deliberately conditional (`!cancelled()`), which is why this asserts the
    named core steps rather than banning step conditions outright.
    """
    import yaml as _yaml

    jobs = _yaml.safe_load((WORKFLOWS / "ci.yml").read_text())["jobs"]
    by_name = {job["name"]: job for job in jobs.values()}

    for job_name, markers in CORE_STEPS.items():
        for marker in markers:
            matching = [
                step
                for step in (by_name[job_name].get("steps") or [])
                if marker in str(step.get("run", ""))
            ]
            assert matching, (
                f"job {job_name!r} no longer has a step running {marker!r}"
            )
            for step in matching:
                assert "if" not in step, (
                    f"the step running {marker!r} in job {job_name!r} is "
                    f"conditional. A skipped core step leaves the job green "
                    f"with the work undone, which is the false positive this "
                    f"file exists to prevent"
                )


def test_the_elan_installer_is_pinned_and_verified_before_execution():
    """The installer runs as root-equivalent on a runner holding the repo token.

    An earlier version piped elan-init.sh from the mutable `master` branch into
    sh, after checkout had already installed the repository credential. Pinning
    it to an immutable release and checking the digest is the fix; this asserts
    the fix, including that verification precedes execution -- a checksum
    checked after the archive is unpacked proves nothing.
    """
    import yaml as _yaml

    document = _yaml.safe_load((WORKFLOWS / "nightly.yml").read_text())
    steps = [
        step
        for job in document["jobs"].values()
        for step in (job.get("steps") or [])
        if "elan" in str(step.get("run", ""))
    ]
    assert steps, "nightly.yml no longer installs elan"
    script = "\n".join(str(step.get("run", "")) for step in steps)
    env = {}
    for step in steps:
        env.update(step.get("env") or {})

    assert "raw.githubusercontent.com" not in script, (
        "the elan installer is fetched from a mutable ref again; a force-update "
        "of that branch would run arbitrary code on a runner that already holds "
        "this repository's credential"
    )
    assert "releases/download" in script, (
        "the elan installer is no longer fetched from an immutable release asset"
    )
    assert env.get("ELAN_VERSION"), "the elan release version is no longer pinned"
    assert re.fullmatch(r"[0-9a-f]{64}", env.get("ELAN_SHA256", "") or ""), (
        "the elan release checksum is missing or is not a sha256 digest"
    )

    lines = [line.strip() for line in script.splitlines()]
    verify = next(
        (i for i, line in enumerate(lines) if "sha256sum -c" in line), None
    )
    execute = next(
        (i for i, line in enumerate(lines) if line.startswith("./elan-init")), None
    )
    assert verify is not None, "the elan checksum is no longer verified"
    assert execute is not None, "the elan installer is no longer executed"
    assert verify < execute, (
        "the elan archive is executed before its checksum is verified, so a "
        "substituted asset would run before the check could reject it"
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


def test_the_ci_jobs_still_run_what_their_names_promise():
    """A context whose job no longer runs anything is a green check with no gate.

    `test_ci_job_names_match_the_inventory` proves the context names exist.
    That is not the same as the work behind them existing, and the names are
    what the required-check configuration keys on.
    """
    import yaml as _yaml

    jobs = _yaml.safe_load((WORKFLOWS / "ci.yml").read_text())["jobs"]
    by_name = {job["name"]: job for job in jobs.values()}

    def _command_lines(job):
        return [
            line.strip()
            for step in (job.get("steps") or [])
            for line in str(step.get("run", "")).splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    # Print commands whose first word means "the rest of this line is a
    # string to display", not "run the rest of this line".
    _PRINTERS = {"echo", "printf"}

    def _invokes(job, fragment):
        """True when a real command line invokes `fragment`.

        Line-level and comment-stripped: an earlier version joined the raw run
        text and substring-matched, so `echo check_required_contexts.py` would
        have satisfied it. The nightly command test carried the same defect and
        was fixed the same way -- but line-scoping alone is not enough, because
        `echo check_required_contexts.py` is still one line that contains the
        fragment. A line is only a real invocation when its own first word is
        not a printer that would make the rest of the line inert text.
        """
        for line in _command_lines(job):
            if fragment not in line:
                continue
            first_word = line.split(None, 1)[0] if line.split() else ""
            if first_word in _PRINTERS:
                continue
            return True
        return False

    assert _invokes(by_name["tests"], "pytest"), (
        "ci.yml's `tests` job no longer runs pytest; the context would still "
        "report, so a required check would pass with no suite behind it"
    )
    assert _invokes(by_name["tests"], "check_claims.py"), (
        "ci.yml's `tests` job no longer runs the claim validator"
    )

    assert _invokes(by_name["required-checks"], "check_required_contexts.py"), (
        "ci.yml's `required-checks` job no longer runs the verifier; an empty "
        "job reports success, which is the false positive this whole file exists "
        "to prevent"
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
    push = triggers.get("push")
    assert "push" in triggers, "ci.yml no longer runs on push"
    if isinstance(push, dict):
        assert not push.get("branches-ignore"), (
            f"ci.yml's push trigger excludes branches "
            f"({push['branches-ignore']}), so the fresh-checkout run -- the "
            f"structural fix this workflow exists for -- would not fire on them"
        )
        branches = push.get("branches")
        assert branches is None or "**" in branches, (
            f"ci.yml's push trigger is narrowed to {branches}; it ran on all "
            f"branches, and narrowing it silently drops coverage"
        )
    assert "pull_request" in triggers, "ci.yml no longer runs on pull requests"
    types = (triggers.get("pull_request") or {}).get("types") or []
    for required in ("opened", "synchronize", "reopened", "edited"):
        assert required in types, (
            f"ci.yml's pull_request trigger no longer includes {required!r}; "
            f"without `synchronize` a pull request can be updated without "
            f"re-running, and without `edited` a retargeted pull request keeps "
            f"a verdict computed against its old base"
        )


def test_the_nightly_declares_its_schedule_and_still_builds_lean():
    """The Lean build exists only here, so losing it loses the check entirely.

    Spec D12 keeps `lake build` off the merge path deliberately, which means
    the scheduled run is the only thing that ever compiles the Lean layer.
    """
    import yaml as _yaml

    document = _yaml.safe_load((WORKFLOWS / "nightly.yml").read_text())
    triggers = _triggers(document)
    schedule = triggers.get("schedule")
    assert schedule, (
        "nightly.yml has no active schedule. D12 keeps `lake build` off the "
        "merge path, so an empty or absent schedule removes the Lean layer's "
        "only CI coverage entirely"
    )
    assert any(entry.get("cron") for entry in schedule), (
        "nightly.yml's schedule contains no cron entry, so it never fires"
    )
    assert "workflow_dispatch" in triggers, (
        "nightly.yml can no longer be triggered manually; the rollout's "
        "post-merge Lean verification depends on it, because a scheduled run "
        "cannot be waited for"
    )
    for forbidden in ("push", "pull_request"):
        assert forbidden not in triggers, (
            f"nightly.yml now runs on {forbidden!r}. Spec D12 keeps `lake build` "
            f"off the merge path deliberately -- Mathlib needs a ~5 GB cache and "
            f"the layer changes rarely -- so adding a merge-path trigger here "
            f"reverses a decision rather than extending coverage"
        )

    lean_jobs = [j for j in document["jobs"].values() if j.get("name") == "nightly-lean"]
    assert len(lean_jobs) == 1, (
        f"expected exactly one job named 'nightly-lean', found {len(lean_jobs)}"
    )
    lean_job = lean_jobs[0]

    lines = [
        line.strip()
        for step in (lean_job.get("steps") or [])
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

    lake_steps = [
        step
        for step in (lean_job.get("steps") or [])
        if any(
            line.strip().startswith("lake")
            for line in str(step.get("run", "")).splitlines()
        )
    ]
    assert lake_steps, "nightly-lean runs no lake command at all"
    for step in lake_steps:
        assert step.get("working-directory") == "lean", (
            f"step {step.get('name')!r} runs lake outside `working-directory: "
            f"lean`; the Lean project lives in lean/, so the command would "
            f"target the repository root and build nothing"
        )

    order = [
        index
        for index, line in enumerate(lines)
        if line.startswith("lake update") or line.startswith("lake exe cache get")
    ]
    first, second = lines[order[0]], lines[order[1]]
    assert first.startswith("lake update"), (
        "nightly.yml runs `lake exe cache get` before `lake update`. lean/.lake "
        "is gitignored, so on a fresh runner the `cache` executable does not "
        "exist yet -- it lives inside the Mathlib package -- and the `|| echo` "
        "on the cache step would mask that while `lake build` proceeded without "
        "its dependency. The order is the fix, not an accident"
    )
    assert second.startswith("lake exe cache get")

    assert _runs("git diff --quiet -- lake-manifest.json") or any(
        "lake-manifest.json" in line for line in lines
    ), (
        "nightly.yml no longer checks whether `lake update` rewrote the "
        "dependency lock; without it a scheduled run can validate a different "
        "Mathlib than this repository pins and report success"
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


def test_a_requested_bypass_check_that_could_not_run_says_so(
    monkeypatch, tmp_path, capsys
):
    """Asking for the bypass check and not getting it must not be silent.

    `--check-bypass` is the maintainer's rollout path. If the branch-rules
    request fails, `main` returns before any ruleset is fetched, so bypass
    actors go unverified. An operator who requested the check, did not get it,
    and was told nothing could reasonably assume an earlier run's verdict still
    holds. Spec section 9.3 and docs/risks.md R-009 both require every run to
    state what it did not establish.
    """
    inventory = tmp_path / "required-checks.yml"
    inventory.write_text(
        "branch: main\n"
        "expected_integration_id: 15368\n"
        "contexts:\n"
        "  - name: tests\n"
        "    ships_in: plan-a\n"
    )

    monkeypatch.setattr(
        crc, "fetch_all", lambda url, token: (None, f"HTTP 403 for {url}")
    )

    exit_code = crc.main(
        ["--repo", "owner/name", "--inventory", str(inventory), "--check-bypass"]
    )
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "NOT CHECKED: ruleset bypass actors" in output, (
        f"a requested-but-unrun bypass check must be reported; got:\n{output}"
    )
    assert "went unverified" in output, (
        "the message must say the check did not run, not merely that it was "
        f"skipped by default; got:\n{output}"
    )
