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
| D9 | Two seed tiers: a 4-mutation canary and the full 12 | The canary is cheap enough to run on every push; the full set gates a pull request |
| D10 | The fingerprint binds **mutation source, test source, failure signature, exemptions and the property inventory** — not the result alone | The registry cannot catch its own subversion. A result-only fingerprint is *invariant* under coordinated weakening (§3.7's counterexample) — loud about a harmless rename, silent about the harmful change |
| D11 | A fingerprint change fails CI unless a tracked waiver explains it | Publishing alone is a log, not a gate. The waiver converts "a number changed" into "someone had to say why" |
| D12 | CI runs the suite and validator on a fresh checkout on push and PR; `lake build` on the **schedule** only | The fresh-checkout run is the *structural* fix for the clean-clone class. Lean is load-bearing for this spec's goal but changes rarely: a nightly build bounds an unremarked regression to a day for one cache, rather than one per pull request |
| D13 | Machine-local hash files are rejected | They do not survive a clone, are invisible to CI and reviewers, and go stale silently — reproducing the very pattern being fixed |
| D14 | The load-bearing unit is a **property**, not a test, with a required inventory checked in the reverse direction | "Would any other test go red?" fails under redundant coverage — two tests covering one property make each other unmarked. A meta-test quantifying only over marked tests cannot see an unmarked one |
| D15 | A mutation must show its targets **passing** unmutated, then failing **as a declared assertion** | A non-zero exit is also produced by collection errors, import errors and timeouts. Red is not evidence of the right reason |
| D16 | Waivers are one-shot authorisations of `(base, new, diff)`, negative-tested | "Any non-empty line permits any drift" is a signature box, not a gate |
| D17 | Class D's only open instance — the Phase 1 documents — is pulled into scope | A design that names a defect class and excludes its only live case can pass every acceptance criterion with the risk it cites still open |

---

## 3. The mutation registry

### 3.1 Marking — over properties, not tests

An earlier draft defined the marker with an operational test: *delete the test
in your head; would any other test go red for the same defect?* That test is
**wrong under redundant coverage**. Two tests covering one property each make
the other non-load-bearing, so neither is marked and the property is unguarded.
`test_every_tag_resolves_and_matches` and `test_every_real_document_carries_tags`
are exactly such a pair.

So the unit is the **property**, not the test. `tests/properties.py` holds a
declared inventory:

```python
Property(
    id="figure-literals-match-generated-data",
    why="risk R-002: prose numbers drift from the artifacts they quote",
    tests=[...],      # every node id that covers it
)
```

A property is load-bearing when its loss would be silent. Its tests carry
`@pytest.mark.load_bearing`, and the mutation must kill **every** listed test,
not merely one — otherwise a red sibling masks a surviving defect.

**The inventory is required, not derived.** A meta-test quantifying only over
marked tests cannot see a load-bearing test that was never marked. The reverse
direction is what binds: `tests/properties.py` names the properties this
repository must guard, and a meta-test asserts each has at least one live test
and at least one mutation. This mirrors `tests/test_oracle_gate_guard.py`,
which already solved the same one-level-up problem with a hard-coded inventory.

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

1. builds a scratch tree with `git archive HEAD | tar -x`, then **restores the
   git metadata the tree needs** — `capfib/manifest.py` shells out to
   `git rev-parse HEAD` and silently records `"unknown"` on failure, so an
   archive alone is not "what a clone would give";
2. **runs the target tests unmutated and requires them to pass.** Without this
   baseline a mutation can appear to "kill" a test that was already failing, or
   that fails to collect at all;
3. applies the mutation;
4. re-runs **only** the target node ids, with `python -m pytest` invoked from
   the scratch root, and asserts every imported project module's `__file__`
   lies beneath that root — the project installs `capfib` editable, so an
   unguarded run imports the *unmutated* worktree and proves nothing;
5. requires each target to fail **as an assertion, in the expected test phase**,
   matching a declared failure signature. A non-zero exit is not enough:
   collection errors, import errors, timeouts, missing node ids and unexpected
   exceptions are all non-zero and none of them shows the guard did its job.
   A mutation named `drop-break-index-term` that instead makes the function
   raise produces the same red node and proves nothing about the dropped term.

### 3.4 Meta-tests

- Every property in `tests/properties.py` has at least one live test and at
  least one mutation, or a counted exemption (the **reverse** inventory check).
- Every `load_bearing`-marked test belongs to a declared property.
- Every mutation names symbols, files and node ids that exist.
- Exemptions are listed with identities and reasons, not merely counted — an
  exemption count alone is invariant under swapping which guard is exempt.

### 3.5 Seed set

Drawn from what actually failed, not from what is easy to mutate. The
sibling-document row exists because the recurrence this spec cites most often —
a `pytest.skip` on an absent sibling silently disabling the drift detector — was
**absent from an earlier draft's seed set**. Removing the JSON does not stand in
for it: that fails at `_load()`, for an unrelated reason, before document
existence is examined.

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
| **Remove one tracked document, leave a drifted sibling, run the real orchestration** | the tag-correspondence tests — **and a `skip` counts as mutation survival, not a kill** |
| Revert `THEOREM_PATH_TOKEN_RE` to drop `docs/phases` | the proof-root regression test |
| Inject a stale `sorry` statement into `capfib/` | `test_epistemic_staleness` |
| Corrupt one interior place value | `test_places_up_to_production_boundary` |
| Make a `run_phase2` gate pass that should fail | the writes-nothing tests |

### 3.6 Two tiers

| Tier | Contents | Cadence |
|---|---|---|
| **Canary** | the four Phase 2 recurrences, named rather than counted: dropped break-index term; sibling-document skip; missing-oracle skip; and the T1, T3 and T5 gutting mutations, which are three rows because one red test must not mask two surviving submutations | every push |
| **Full** | the whole §3.5 set | every pull request, and on a schedule |

Tiering is how a fast set quietly becomes the only set that ever runs. The full
tier's job is therefore **required for merge**; its absence must be as visible
as its failure.

### 3.7 The external record, and why the registry needs one

The registry as described in §3.1–§3.5 **cannot catch its own subversion.** A
single commit can weaken a load-bearing test *and* its registered mutation
together: the suite passes, the registry passes, nothing signals. That is the
same failure class this spec exists to close, one level up.

The fix is an external, dated record of what the registry actually *did*.

**What is fingerprinted — and why node ids alone are not enough.** An earlier
draft fingerprinted `{mutation_name -> red node ids}`. That is **invariant under
the attack it exists to expose.** Concretely: change production `T1` to the
constant `80`, weaken the same-named identity test to expect `80`, and change
the same-named registered mutation to return `81`. The unmutated suite is green,
the same node ids go red under the mutation, the fingerprint does not move, and
no waiver is required. Meanwhile a harmless node rename *does* move it. The
mechanism was loud about the harmless and silent about the harmful.

The fingerprint therefore binds **intent and execution together**:

```
{ mutation_id -> ( sha256 of the mutation's source,
                   sha256 of each target test's source,
                   sha256 of the declared failure signature,
                   sorted node ids that went red ) }
```

Any coordinated weakening must edit at least one of the mutation, the test, or
the expected signature — so it moves the fingerprint and demands a waiver whose
diff a reviewer reads. The registry's **exemption list and property inventory
are hashed into the same record**, because otherwise a guard can be neutralised
by moving it to exemptions without any result changing.

**How it binds.** The workflow fails when the fingerprint moves without a
matching waiver. A waiver is a **one-shot authorisation of a specific
transition** — it names the base fingerprint, the new fingerprint, and the
result diff it permits — and is rejected when stale, reused, malformed, or
pointing at a different base. "Any non-empty line permits any drift" is not a
gate; it is a signature box.

**The honest limit.** This is tamper-*evidence*, not tamper-proofing, and the
boundary is narrower than an earlier draft claimed. Three paths remain:

1. A change that edits production, test, mutation and waiver together is
   *visible and attributable* but not prevented. That is the intended residue.
2. The workflow, harness and waiver checker live in the same trust domain as
   the change under review. A pull request can preserve a job name while
   altering the harness to emit a stale mapping. Mitigating that needs branch
   protection requiring the exact status check and restricting workflow edits —
   external configuration this spec depends on and cannot itself enforce, so it
   is stated as an assumption rather than a guarantee.
3. Mutations are fixed points, not properties. `log_R_bound_certified` promises
   an upper bound for every `n >= 2`; a branch returning a wrong value at one
   untested `n` survives every fixed mutant. Closing that needs property-based
   testing over the declared domain, which §7 records as a follow-up.

### 3.8 Cost and cadence

Marked slow. Run by a dedicated command and before opening a pull request — not
on every `pytest`. Wall time is the honest price of a guard that has been seen
red.

---

## 3A. Continuous integration

This repository has no CI today; this is its first workflow. The tracked tree is
0.8 MB and the suite runs in about 145 s, so the Python side is cheap.

**On every push:** fresh checkout, install, `pytest`, `scripts/check_claims.py`,
the canary mutation tier.

**On every pull request:** the above plus the full mutation tier, publishing the
result mapping and fingerprint as an artifact and enforcing the waiver (§3.7).

**Not run:** `lake build`. The Lean layer needs a ~5 GB Mathlib cache and a long
cold build, changes rarely, currently contains zero `sorry`s, and is already
gated locally and before a pull request. Recorded as a deliberate gap, not an
oversight — a Lean regression would reach `main` unremarked, and closing that is
a follow-up whose cost is the cache.

**Why the workflow earns its place beyond the mutations.** A run from a fresh
checkout is the *structural* fix for the clean-clone class. The recurrence where
twelve T1/T3/T5 comparisons silently skipped because the oracle was untracked
could not have survived it — no mutation required, and no one needing to think
of it. That property comes free with CI existing at all, and it is the single
cheapest thing in this document.

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

## 7. Scope changes forced by review, and what stays out

**Pulled in.** Extending the figure-tag mechanism to the Phase 1 documents.
Class D is *defined* in §1 as prose numbers unbound to generated data, and the
Phase 1 documents are its only open instance — `docs/risks.md` R-002 rates them
the highest open risk and names Phase 4 regeneration as the trigger. A design
that names a class and then excludes its only live case can satisfy every
acceptance criterion while the risk it cites stays open. Included.

**Pulled in.** Requiring cited artifacts to exist and match their manifest
hash. Already delivered ahead of this spec, because it was live on `main`: ten
`verified-numeric` claims cited four untracked artifacts, so `claims.yaml OK`
on a clean clone said nothing about any of them. An acceptance criterion reading
"`check_claims.py` OK" was worthless until that was true.

**Stays out, with the cost named.**

- **`lake build` per push.** Kept out of push and pull-request runs; added on
  the **schedule** only. Codex is right that a Lean regression reaching `main`
  unremarked is load-bearing for this spec's own goal, and wrong that the fix
  must be per-PR: the Lean layer changes rarely, and a nightly build bounds the
  window to a day for the price of one cache rather than one per pull request.
- **Range-vs-evidence checking in the validator** — a claim may still say
  "every `N <= 10^6`" while its evidence covers 37 rows. Mechanising the
  relation between a stated range and an artifact's actual coverage is its own
  design; §6.2's rule covers it by discipline meanwhile.
- **YAML `statement` prose.** `validate()` never reads it, so a `theorem`-status
  claim whose statement says it remains conjectural passes. Small and worth
  doing; not this spec.
- **Property-based testing over declared domains**, per §3.7's third residue.
- **Classical mutation testing over the whole suite.**
- **Release assets.** Revisit at a phase boundary.

## 8. Acceptance criteria

Each is stated so that satisfying it establishes the property, rather than
resembling it.

1. `tests/properties.py` declares the guarded properties; every one has a live
   test and a mutation, or a listed exemption with an identity and a reason.
2. Every `load_bearing`-marked test belongs to a declared property, and every
   mutation kills **all** of its property's tests, not one of them.
3. For each mutation the harness records: targets **passed** in the unmutated
   scratch tree, then failed under mutation **as assertions matching the
   declared signature**. A run where a target errors, skips, times out or fails
   to collect is a harness failure, not a kill.
4. Imports in the scratch run resolve beneath the scratch root — asserted, not
   assumed.
5. The sibling-document mutation is present, and a `skip` under it is treated as
   **survival**.
6. The fingerprint includes mutation source, test source, failure signature,
   exemptions and the property inventory — demonstrated by showing that the
   coordinated-weakening transition of §3.7 **moves** it.
7. A waiver authorises exactly one `(base, new, diff)` transition. Negative
   tests: stale, reused, malformed, and wrong-base waivers are each rejected.
8. CI runs on push and pull request; the full tier's status check is **required
   for merge**, and a scheduled run exists including `lake build`. Configuration
   is verified, not assumed — a non-required job satisfies "the workflow exists"
   while blocking nothing.
9. `CLAUDE.md` carries rule 11 and the rule 5 amendment, and nothing else new.
10. The two memory files exist with `MEMORY.md` pointers; `claim-ledger` carries
    §6.1 and §6.2.
11. Phase 1 documents are covered by the figure-tag mechanism, closing R-002's
    open half.
12. Full suite green; `scripts/check_claims.py` OK **on a fresh clone**;
    `lake build` clean.

---

## Appendix — review history

**2026-08-23, Codex `gpt-5.6-sol` effort `ultra`, spec gate (CLAUDE.md rule 6).**
Verdict: *"no, I would not implement this spec as written."* Every finding below
was verified against the repository before acting.

| Finding | Outcome |
|---|---|
| The RESULT fingerprint is invariant under the coordinated weakening it exists to expose — concrete counterexample given | **Accepted.** §3.7 now binds mutation source, test source and failure signature, not node ids alone. This was the spec's central mechanism and it did not work. |
| The sibling-document `pytest.skip` recurrence — the one the spec cites most — was absent from the seed set | **Accepted.** Added to §3.5, with `skip` counted as survival. |
| Red node ≠ right reason: a mutation that makes the target raise produces the same mapping | **Accepted.** §3.3 requires a baseline pass and an assertion matching a declared signature. |
| The `load_bearing` operational test fails under redundant coverage — two tests covering one property make each other unmarked | **Accepted.** §3.1 moves the unit from test to property, with a required inventory in the reverse direction, following `test_oracle_gate_guard.py`'s existing solution. |
| `git archive` is not "what a clone would give" — no git metadata; and editable installs may import the unmutated worktree | **Accepted.** §3.3 restores metadata and asserts import provenance. |
| Class D's only open instance (Phase 1 documents) was excluded, so acceptance could pass with the highest-rated risk open | **Accepted.** Pulled into scope (§7). |
| `check_claims.py` never verifies a cited artifact exists or matches its hash, so "claims.yaml OK" was not evidence | **Accepted and already fixed** in `4375689`, ahead of this spec, because it was live on `main`. |
| The waiver schema is undefined; any non-empty line permits any drift | **Accepted.** §3.7 makes waivers one-shot `(base, new, diff)` authorisations, negative-tested in AC7. |
| Exemptions sit outside the tamper-evidence boundary | **Accepted.** Hashed into the fingerprint (§3.7). |
| "Four-mutation canary" is irreconcilable with a 12-row seed set | **Accepted.** §3.6 names the canary's members instead of counting them. |
| Workflow, harness and checker share the attacker's trust domain | **Accepted as an assumption, not a guarantee.** §3.7 residue 2 states the branch-protection dependency this spec cannot itself enforce. |
| Fixed mutants cannot close conditional defects at untested points | **Accepted as a residue.** §3.7 residue 3; property-based testing recorded as a follow-up in §7. |
| Lean CI is load-bearing for the spec's own goal | **Partly accepted.** Added on the schedule rather than per pull request: it bounds the window to a day for one cache, and the Lean layer changes rarely. |
