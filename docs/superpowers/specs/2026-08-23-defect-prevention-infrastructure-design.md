# Preventing the Phase 1 / Phase 2 Defect Classes

**Date:** 2026-08-23
**Status:** design spec, awaiting review
**Scope:** process infrastructure — a mutation registry, one CLAUDE.md rule, two memory files, two additions to the `claim-ledger` skill
**Evidence base:** 41 controller rulings, 17 fix rounds and 14 deferred minors across Phases 1 and 2, plus `docs/risks.md` R-001…R-006

---

## 1. The problem, stated from evidence

Six defect classes recurred. They are listed by root cause, not symptom, because
the symptoms were all different and the causes were not.

| | Class | Instances |
|---|---|---|
| **A** | Gates that do not run; tests that cannot fail | 4 in Phase 2 alone, plus the promotion blind spot |
| **B** | A finite observation restated as universal | 7 in Phase 1; 5 more in Phase 2 |
| **C** | Epistemic status asserted where no validator reads | 4 stale `sorry` statements, a `(Konjektur)`, a `modulo sorry` |
| **D** | Prose numbers unbound to generated data | risk R-002 |
| **E** | Pre-drafted claims the data later contradicted | 4, including one that reached the ledger draft |
| **F** | Controller errors in how work was dispatched and adjudicated | 4, all mine |

### 1.1 The meta-pattern

**Guards kept being added, and the guards kept not working.** Class A is not
"a check was missing" — in every instance a check existed and could not fail:

- Three green tests were structurally blind to a dropped term that put the
  "certified" upper bound `2.9e-27` *below* the true value. The width test
  passed because both endpoints moved together; the agreement test's `1e-12`
  relative tolerance could not see `1e-27` on an `O(1)` value; the tail test
  exercised the bound in isolation, consistent with the integration bug.
- A `pytest.skip` on a sibling document silently disabled the figure-drift
  detector — the mitigation for the project's highest-rated open risk.
- The exact-value oracle was untracked, so twelve comparison tests skipped on
  any clean clone. They had never run outside a developer's working tree.
- Mutation probes showed the public computations could be gutted with the suite
  still green: certified T1 replaced by the constant `80.0`, every T3
  `log_count` zeroed, T5 weakened to `T3 + 0.01` above the enumeration ceiling.

Every one was found by a human or model **reading the code**. None was found by
the guard. That is the fact this spec is built around.

### 1.2 Why not more rules

`CLAUDE.md` carried ten numbered rules throughout. Every defect above occurred
with them loaded. Prose in an always-loaded file is the intervention with the
weakest measured track record here, so it receives the least of this design.

---

## 2. Decisions taken

| # | Decision | Rationale |
|---|---|---|
| D1 | Mutation discipline is the centrepiece | Class A recurred most, every existing guard failed at it at least once, and it is the only class whose fix is mechanical rather than remembered |
| D2 | Mutations are **executed**, not declared | A declaration is an unverified claim about a test — the same species of claim as "the bound was verified". Every blind test in Phase 2 would have passed a declaration bar, because its author believed it worked |
| D3 | Curated set, marked, with the curation itself checked | Mutating every test forces noise on trivial ones, which historically gets the whole thing switched off |
| D4 | Mutations run against a scratch tree from `git archive`, not monkeypatch | The needed mutations include file *absence*; monkeypatch cannot express that, and file-absence is exactly what bit us twice |
| D5 | Exemptions are explicit, reasoned and counted | Some properties resist a clean patch. A counted exemption is honest; a fake mutation is worse than none |
| D6 | One new CLAUDE.md rule, one amendment — no more | See §1.2 |
| D7 | Class F goes to project memory, not CLAUDE.md | It is about how the assistant works across sessions, not about this repository |
| D8 | Classes B/C/E extend the existing `claim-ledger` skill; no third skill | Two skills that get invoked beat three that do not |

---

## 3. The mutation registry

### 3.1 Marking

A test whose failure would otherwise be invisible carries
`@pytest.mark.load_bearing`. This is not every test — it is the set whose
silence is indistinguishable from success.

**Operational test, so this is not a judgement call:** delete the test in your
head. Would any *other* test go red for the same defect? If yes, it is not
load-bearing — something else covers the property. If no, it is the only thing
standing between a defect and a green suite, and it carries the marker.

By that test, all four Phase 2 recurrences qualify: nothing else covered the
dropped term, the disabled drift detector, the skipped comparisons, or the
gutted T1/T3/T5 computations — which is exactly why each stayed green.

### 3.2 Registration

Each mutation names three things:

```python
Mutation(
    name="certified-T1-replaced-by-a-constant",
    apply=...,          # a function taking the scratch tree root
    must_fail=[...],    # pytest node ids that must go red
    reason=...,         # what property this proves is live
)
```

`apply` performs one of: a source edit, a file removal, or a value perturbation.

### 3.3 Execution

For each mutation the harness:

1. builds a scratch tree with `git archive HEAD | tar -x` — tracked files only,
   so `lean/.lake` (≈5 GB) and `.venv` never enter, and the tree is exactly what
   a clone would give;
2. applies the mutation;
3. runs **only** the `must_fail` node ids there, with the project venv;
4. asserts a non-zero exit and reports which named tests did not fail.

### 3.4 Meta-tests

- Every `load_bearing`-marked test appears in at least one mutation's
  `must_fail`, or in the exemption list.
- Every mutation names symbols, files and node ids that exist.
- The exemption list is printed with its reasons and its count.

### 3.5 Seed set

Drawn from what actually failed, not from what is easy to mutate:

| Mutation | Must fail |
|---|---|
| Certified T1 → constant `80.0` | the T1 identity assertions |
| Every T3 `log_count` → `0.0` | the T3 product identity |
| T5 → `T3 + 0.01` for `N >= 1000` | the large-`N` T5 property |
| Drop the break-index term in `log_F_c_interval` | `test_enclosure_contains_an_independently_summed_reference` |
| Remove `data/phase1_data.csv` | the oracle-gate guard and the 12 comparisons |
| Remove `data/phase2_figures.json` | the figure-tag tests |
| Perturb one stored figure value | the figure-tag correspondence test |
| Strip every `{fig:}` tag from a document | the zero-tag check |
| Revert `THEOREM_PATH_TOKEN_RE` to drop `docs/phases` | the proof-root regression test |
| Inject a stale `sorry` statement into `capfib/` | `test_epistemic_staleness` |
| Corrupt one interior place value | `test_places_up_to_production_boundary` |
| Make a `run_phase2` gate pass that should fail | the writes-nothing tests |

### 3.6 Cost and cadence

Marked slow. Run by a dedicated command and before opening a pull request — not
on every `pytest`. Wall time is the honest price of a guard that has been seen
red.

---

## 4. CLAUDE.md

**New rule 11 — a guard you have not seen fail is not a guard.** Any test whose
failure would otherwise be invisible carries `@pytest.mark.load_bearing` and a
registered mutation. Adding such a test without one is incomplete work, not a
follow-up. The rule cites the four Phase 2 recurrences by name, so it carries
its own evidence rather than asserting a principle.

**Amendment to rule 5.** The correctness gate currently governs what may be
*reported*. Extend the same standard to *absence*: a gate that skips is a gate
that did not run, and verification claims are checked from a clean clone rather
than from a working tree.

Nothing else is added. See §1.2.

---

## 5. Project memory

Two files, both `type: feedback`, both about how the assistant works across
sessions and neither derivable from the repository.

### 5.1 `never-pre-clear-findings-in-reviewer-briefs`

Task 1's reviewer brief stated that `capfib/interval.py` generating its own
Fibonacci place values "is intended and is not a violation" of the
constructed-in-`fib.py`-and-nowhere-else constraint. It was a violation, in the
module that certifies the headline upper bound, and risk R-003 is precisely the
documented case that a wrong place set is invisible to the cross-check. The
final whole-branch review caught it eight tasks later.

`subagent-driven-development` forbids this in terms: *"If the prompt you are
writing contains 'do not flag,' 'don't treat X as a defect,' 'at most Minor,' or
'the plan chose' — stop: you are pre-judging."* The violation was committed in
softer words, which is why it did not trip self-recognition.

**Rule:** if a brief is about to tell a reviewer something is fine, delete that
sentence. Let the finding be raised and adjudicate it afterwards, on the record.

### 5.2 `verify-before-downgrading-a-finding`

Codex's manifest-CWD finding was parked as Minor by reasoning about it. One
command would have shown that a test run in a scratch tree had been rewriting
the real repository's `data/manifest.json`, and that `_sha256` was hashing the
wrong file — correct only by coincidence when run from the repository root.

The same file carries a second lesson. Task 7's reviewer was asked whether the
figure-tag test "skips visibly rather than passing vacuously". The answer was a
correct "yes" — and the gate still never ran on a clean clone, because the
question tested the wrong property.

**Rules:** severity assessed by reasoning is a guess; spend the cheapest command
that would falsify it before downgrading. And ask reviewers "what change would
make this fail?", never "does this look right?".

---

## 6. The `claim-ledger` skill

Two sections added to the existing skill. No third skill is created.

### 6.1 Promoting a claim

A five-step checklist, each step earned:

1. **Grep the claim id and read every citing paragraph by hand.** Promotion to
   `theorem` silently removes the hedging guard from those paragraphs — in the
   same commit that makes them stale.
2. **Check whatever text *justifies* the promotion still matches it.** The
   roadmap's `saddle-tightness` bullet argued from a false intermediate and
   concluded the superseded `O(t log t)`, contradicting the ledger entry it
   existed to support.
3. **Check the inverse error.** A claim may now be *proved* while still marked
   `heuristic`. `saddle-tightness` sat under-claimed for a full round.
   Understating is the same defect as overstating, pointed the other way.
4. **Check trees no validator reads** — `capfib/`, `scripts/`, skills, Lean
   prose, assertion messages.
5. **Re-read `Revisit when:` triggers in `docs/risks.md`.** Phase 2 fired three
   of its own and updated none until a reviewer noticed.

### 6.2 Writing about generated data

Three Phase 2 sentences were wrong in one identical way: a qualitative summary
of a finite series asserted from its endpoints.

- "rising from about 0.79 to about 0.88" — the sequence dips at `10^4`
- "strictly between the bounds at every sampled `N`" — three points sit outside
- "stayed below the exact value" — one point is exactly equal

All three passed careful human and model review, because the sentence is
checkable only against data nobody re-read, and `check_claims.py` cannot see
them: those paragraphs carry no claim token by design.

**Rule:** before writing any trend, comparison or superlative over generated
data, read the whole series and check every point — not the endpoints. If it is
not monotone, say so or quote the values.

---

## 7. Out of scope

- Extending `scripts/check_claims.py` to read `capfib/`, `scripts/`, skills or
  YAML statement prose, and adding range-vs-evidence or SHA-256 verification.
  Codex's pre-PR review found the validator already promises checks it does not
  perform; widening it before making it honest would compound that. Recorded as
  a follow-up, not built here.
- Closing risk R-002 for the Phase 1 documents by extending the figure-tag
  mechanism to them.
- Classical mutation testing over the whole suite.

## 8. Acceptance criteria

1. `@pytest.mark.load_bearing` is registered in `pyproject.toml` and applied to
   the §3.5 set.
2. The harness runs every registered mutation against a `git archive` scratch
   tree and asserts the named tests fail; it is marked slow.
3. The meta-tests hold: no marked test lacks a mutation or a counted exemption;
   every mutation resolves.
4. **Each seed mutation is demonstrated to make its named tests fail** — the
   registry's own output is the evidence, not a claim about it.
5. `CLAUDE.md` carries rule 11 and the rule 5 amendment, and nothing else new.
6. The two memory files exist with `MEMORY.md` pointers.
7. `claim-ledger` carries §6.1 and §6.2.
8. Full suite green; `scripts/check_claims.py` OK; `lake build` clean.
