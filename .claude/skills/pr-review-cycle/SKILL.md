---
name: pr-review-cycle
description: Use when preparing a branch for push, opening a pull request, or following up on one (including after merge) — the pre-push gate, the Codex review, the Copilot review that lands minutes after `gh pr create`, and where disputed findings are recorded.
---

# PR review cycle

A pull request in this repository is not done when `gh pr create` returns. It
is done when every reviewer's findings have been read, each one verified
against the code, and each one closed out on the record. This skill is the
procedure; the standing decisions behind it are dated 2026-08-20 (Codex) and
2026-08-21 (Copilot).

## 1. Before pushing

Run all of these; a check that did not run is a failure, never a pass.

```bash
.venv/bin/pytest -q                          # full suite, slow tests included
.venv/bin/python scripts/check_claims.py     # claim ledger
```

- **Lean touched?** `cd lean && lake build`, then `#print axioms` on every
  changed theorem. `lake build` accepts `sorry` with a warning, so the axiom
  list is the real guard: it must show only `propext`, `Classical.choice`,
  `Quot.sound`. The `lean-lsp` MCP server's `lean_verify` does the same check.
- **Clean-clone check** for anything that depends on tracked data or
  configuration: `git archive HEAD | tar -x -C <scratch>` and run the suite
  with the working directory **inside** the scratch tree. Launched from the
  repository root, `sys.path[0]` resolves `capfib` to the working tree instead.
  CI repeats this on every push; doing it first saves a round trip.

## 2. Codex review (before the push, not after)

Every code change gets a Codex review, and a **full** Codex review runs before
pushing for a pull request. Invoke it through the `codex:rescue` skill. Model
and effort are `gpt-5.6-sol` at `ultra` (`~/.codex/config.toml`); before
quoting either, check `~/.codex/models_cache.json`, which lists every slug
with its supported levels. The model's own default effort is the lowest one,
so the effort setting is what actually changes behaviour.

Writing the brief:

- **Never pre-clear a finding.** Reread every sentence that says something is
  correct, intended or fine, and delete it. "X is intended and is not a
  violation" reads as background and still hands the reviewer the answer.
- **Ask what would make it fail**, not whether it looks right. "Does this skip
  rather than pass?" got an honest yes on a gate that never ran on a clean
  clone.

## 3. Open the PR

```bash
git push -u origin <branch>
gh pr create --base main --title "..." --body "..."
```

End the body with the attribution lines the session specifies.

## 4. Wait for Copilot (about five minutes)

Copilot's review is not there when `gh pr create` returns. Wait for it with
Monitor instead of polling by hand (foreground `sleep` is blocked):

```bash
until [ "$(gh api repos/{owner}/{repo}/pulls/<n>/reviews \
  --jq '[.[] | select(.user.login | test("copilot"; "i"))] | length')" != 0 ]; do
  sleep 30; done
```

Give it a 15-minute ceiling. If nothing arrives, say so; do not report the
PR as reviewed.

## 5. Read both endpoints

```bash
gh api --paginate repos/{owner}/{repo}/pulls/<n>/reviews    # summaries
gh api --paginate repos/{owner}/{repo}/pulls/<n>/comments   # inline findings
```

Read both. The summary collapses "Suppressed comments" that contain real
content. Also run `gh pr checks <n>`. The `required-checks` context is red by
design until the mutation tier exists (`docs/risks.md` R-007); any other red
is a finding.

## 6. Verify each finding on its own

Never accept or dismiss the set wholesale. Copilot's record here goes both
ways: on PR #3 it claimed a Lean proof left its goal unsolved (disproved by
`#print axioms` and by deleting the tactic it called insufficient); on PR #4 it
found a `StopIteration` crash and a path-traversal hole that three internal
rounds and two Codex passes had missed.

For each finding:

1. **Reproduce it** with the cheapest command that could falsify it. Severity
   judged by reasoning alone is a guess; a "minor" CWD finding once turned out
   to be rewriting the real `data/manifest.json`.
2. **Close it out** in exactly one of these ways:

| Outcome | Action |
|---|---|
| Agreed defect | Fix on the branch, or in a follow-up PR if already merged. Reply to the comment with the commit. |
| Wrong | Reply with the technical reason and the command that disproves it. |
| Disputed and no further round will settle it | Add an entry to `docs/risks.md` (below) and link it in the reply. |

3. For a spec, also record the outcome in the spec's
   "Appendix — review history": what was rejected, verified, or declined and
   why.

### `docs/risks.md` entries

Only for decisions taken under disagreement, never for defects (an agreed
defect gets fixed or tracked as an issue). Each entry needs the next free
`R-NNN` id, the description, **both positions stated fairly**, and what it
would cost the roadmap's objective if the project's position is wrong. Follow
the "How to add an entry" section at the top of that file.

## 7. After merge

A merged PR is not closed until its review has been read and each finding
verified. Reviews and comments that land after the merge get the same
treatment as in step 6, with fixes going into a follow-up PR.

## Done means

- [ ] Suite, claim ledger, and (if Lean changed) build and axiom check ran green
- [ ] Codex full review done before the push; findings closed out
- [ ] Copilot review arrived, both endpoints read
- [ ] Every finding reproduced or disproved and closed out with a reply
- [ ] Disputes recorded in `docs/risks.md`
- [ ] Checks green apart from the documented `required-checks` standing red
