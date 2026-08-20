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

## What the validator does NOT catch

`check_claims.py` includes a hedging check: a paragraph citing a `conjecture`
or `heuristic` claim must contain a hedge marker (`conjecture`, `expected`,
`not established`, `Konjektur`, `nicht bewiesen`, …). **It is a tripwire, not
a guarantee.** Adversarial testing found three ways an over-claim passes it:

- **Tables and lists.** Paragraphs are split on blank lines, so an entire
  Markdown table is one paragraph. A row asserting a conjecture as proved
  passes whenever *any other cell* in that table contains a hedge word — which
  is exactly why `theory/00-definitions.md`'s status table passes: vacuously,
  not because each row is hedged. The same holds for bullet lists.
- **Negation.** Matching is substring-only. *"The conjecture is now fully
  proved, no caveats"* passes because it contains the word `conjecture`.
- **Distance.** A hedge anywhere in a long paragraph satisfies a claim cited
  anywhere else in it.

So: **a clean `check_claims.py` run is not evidence that no drift occurred.**
It catches a bare prose over-claim — the drift class actually observed on this
project — and nothing subtler. When you promote a status, change a claim's
wording, or write a paragraph that leans on a conjecture, read it yourself and
ask whether a reader would come away believing something stronger than the
ledger says. That judgement is not automatable and the check does not replace it.

Strengthening candidates, if this ever bites: split on list items and table
rows rather than blank lines; scope the hedge to the sentence containing the
citation; detect negation around the marker.

The distinction this enforces is the epistemic content of the project. Phase 3
produces a heuristic; Phase 5 produces the theorem. Months separate them —
long enough for the difference to blur without a mechanical check.
