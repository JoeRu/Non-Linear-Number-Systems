---
name: claim-ledger
description: Use when adding, editing, or citing a mathematical statement in theory/, docs/phases/, or paper/ — keeps conjectures, heuristics and theorems distinguishable.
---

# The claim ledger

Every mathematical statement in this project lives in `theory/claims.yaml` with
an explicit epistemic status. Documents cite claims as `{claim:some-id}`.

## Statuses

| Status | Meaning |
|---|---|
| `cited` | Established elsewhere; `source` names the reference |
| `verified-numeric` | Supported by computation; `evidence` names a file in `data/manifest.json` |
| `heuristic` | Derived by a non-rigorous argument |
| `conjecture` | Believed, not derived |
| `theorem` | Proved, here or in a cited source |
| `open` | Stated, unresolved |

## Rules

1. **A new statement gets a ledger entry before it appears in prose.**
2. **Never promote a status without the corresponding work.** Numerical support
   makes a conjecture `verified-numeric` at most — never `theorem`.
3. **`verified-numeric` requires provenance.** The `evidence` field must name a
   file present in `data/manifest.json`, or the validator fails.
4. Use the project venv created by `scripts/setup.sh`; `capfib` is installed
   only there, so a bare `pytest` fails with an import error rather than a
   real gate result. Run `.venv/bin/python scripts/check_claims.py` after
   every edit to `theory/claims.yaml` or to any document citing a claim.

The distinction this enforces is the epistemic content of the project. Phase 3
produces a heuristic; Phase 5 produces the theorem. Months separate them —
long enough for the difference to blur without a mechanical check.
