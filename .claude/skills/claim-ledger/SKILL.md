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

**Promotion silently removes the guard.** The hedging check applies only to
paragraphs citing a `conjecture` or `heuristic`. The moment a claim is promoted
to `theorem`, every paragraph citing it stops being checked — in the same commit
that makes those paragraphs stale, because they were written to hedge a claim
that no longer needs hedging. So a promotion is exactly when the prose most
needs re-reading and exactly when the tool stops looking. This is structural,
not a one-off: every future promotion repeats it. Observed on this project when
`leading-constant` moved from `conjecture` to `theorem` in Phase 2. **After
promoting any claim, grep for its id and read every citing paragraph by hand.**

Strengthening candidates, if this ever bites: split on list items and table
rows rather than blank lines; scope the hedge to the sentence containing the
citation; detect negation around the marker.

The distinction this enforces is the epistemic content of the project, and the
roadmap's original division of labour — Phase 3 produces the heuristic, Phase 5
produces the theorem — no longer describes where things stand. C5 of
`docs/phases/phase2_bounds.md` §8 proved the leading constant in **Phase 2**,
elementarily and without a saddle point, so `leading-constant` is a `theorem`
already. What Phase 3 still owes is an *explanation* of that constant from the
saddle point, and what Phase 5 still owes is the secondary term
(`saddle-correction-constant` and `secondary-term-constant`, both open).

That a phase can deliver a result years earlier than planned is exactly why
the check is mechanical: the statuses moved, and every paragraph written
against the old plan went stale in the same commit.

## Promoting a claim

Five checks, each earned by a specific promotion going wrong. Run all five
whenever a claim's status field changes.

1. **Grep the claim id and read every citing paragraph by hand.** Promotion to
   `theorem` silently removes the hedging guard from those paragraphs — the
   guard only fires for `conjecture` and `heuristic` — in the same commit that
   makes them stale, because they were written to hedge a claim that no longer
   needs hedging. See "What the validator does NOT catch" above; this is the
   same failure, at the moment it is most likely to bite.
2. **Check whatever text *justifies* the promotion still matches it.** On this
   project, a roadmap bullet arguing for the `saddle-tightness` promotion
   reasoned from a false intermediate result and concluded the superseded
   bound `O(t log t)` — directly contradicting the ledger entry the bullet
   existed to support. A promotion built on stale justification text is wrong
   even when the target status is right.
3. **Check the inverse error too.** Understating is the same defect as
   overstating, pointed the other way, and it is just as easy to miss because
   nothing alerts on it: `saddle-tightness` itself sat marked `heuristic` for
   a full review round after the proof that would have justified `theorem`
   had already landed. Look for claims that are quietly *more* proved than
   their status says, not only less.
4. **Check trees no validator reads.** `check_claims.py` only sees
   `theory/claims.yaml` and documents that cite `{claim:...}` tokens. Claims
   about proof state routinely get restated in `capfib/`, `scripts/`, skill
   files, Lean docstrings, and assertion messages — none of them checked by
   anything. A promotion is not done until those copies are found and updated.
5. **Re-read the `Revisit when:` triggers in `docs/risks.md`.** They exist to
   fire exactly when a claim's status changes underneath them. On this
   project three of them fired during Phase 2 and none were updated until a
   reviewer noticed independently — the trigger existing did not mean anyone
   looked at it.

## Writing about generated data

Three sentences in Phase 2 were wrong in the identical way: a qualitative
summary of a finite series, asserted from its endpoints instead of the whole
thing.

- *"rising from about 0.79 to about 0.88"* — true at both ends; the sequence
  actually dips in the middle, around `N = 10^4`.
- *"strictly between the bounds at every sampled `N`"* — true for most points;
  three sampled points sit outside the bounds.
- *"stayed below the exact value"* — true almost everywhere; one point is
  exactly equal, not below.

All three survived careful review — human and model — because a sentence like
this is checkable only against the data itself, and nobody re-read the data.
`check_claims.py` cannot catch this class either: these paragraphs cite no
claim token by design, so the hedging and provenance checks never look at them.

**Rule:** before writing any trend, comparison, or superlative about generated
data, read the whole series and check every point, not just the ends. If the
series is not monotone, either say so explicitly or quote the values instead
of characterizing them.
