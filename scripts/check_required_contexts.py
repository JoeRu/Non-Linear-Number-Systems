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
        bypass[rid] = None if error else payload.get("bypass_actors")

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
