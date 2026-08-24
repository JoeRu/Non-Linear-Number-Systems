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
| D9 | Two seed tiers: the named §3.6 canary and the complete §3.5 seed set. Stated by content, never by count -- the counts drifted once already (§9.5 A) | The canary is cheap enough to run on every push; the full set gates a pull request |
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

**Some guards do not fail as a node.** The oracle gate is enforced by
`pytest_sessionfinish` in `tests/conftest.py`, which inspects skips and
executions across `GATE_MODULES` and sets `session.exitstatus = 1`. No test node
goes red; the *session* does. A mutation may therefore declare a session-level
expectation instead of, or in addition to, `must_fail` node ids:

```python
must_fail_session=SessionOutcome(
    exit_status=1,
    signature=...,   # required substring of the gate's violation text
)
```

Without this the registry cannot express the two mutations whose real guard is
the session hook — removing the tracked oracle CSV, and turning the
missing-document assertion back into a skip — which are the two closest to the
recurrences this spec was written for. §9.5 records why this was added.

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
   For a mutation declaring `must_fail_session` (§3.2), the same standard applies
   one level up: the run must end with the declared exit status **and** the
   gate's violation text must match the declared signature. A session that exits
   non-zero because a node errored is not the oracle gate firing.

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
| Remove `data/phase1_data.csv` | the 12 comparison node ids, as **assertions**. `_exact()` asserts on an absent CSV — the R-002 work converted it from a skip precisely so a clean clone could not run none of them and report green — so this is an ordinary node-level kill with the `absent -- it is tracked` signature. It is **not** session-level, and the `test_oracle_gate_guard.py` tests do **not** go red: they exercise `gate_violations` over synthetic inputs and never read the CSV |
| Weaken `gate_violations` to return `[]` | exactly `test_a_skipped_gate_is_a_violation` and `test_collected_but_never_executed_is_a_violation`. Named as node ids, not as "the module": the module's other six tests do not all die from this, and §3.1 requires a mutation to kill every listed target. Registered separately because the CSV row cannot kill any of them, and a guard whose helper is gutted must still be caught |
| Remove `data/phase2_figures.json` | the figure-tag tests |
| Perturb `data/phase2_figures.json["chernoff-certified-nmax"]` | `test_every_tag_resolves_and_matches`. The key is pinned because it is **quoted**: `residual-centre` is the one phase2 key in `KEYS_KNOWINGLY_UNQUOTED`, and perturbing it survives every check |
| Strip every `{fig:}` tag from a document | the zero-tag check |
| **Turn the missing-document assertion into a `pytest.skip`, then remove one tracked document** | **session-level** (§3.2): `test_figure_tags.py` is in `GATE_MODULES`, so the skip exits 1 with the SKIPPED violation text. This is the mutation for *the recurrence this spec cites most* — a `skip` on an absent sibling silently retiring the drift detector — and it must mutate the assertion, because with the assertion in place absence is already caught |
| Drift one literal in a present tracked document | `test_every_tag_resolves_and_matches`, with the `quoted as` signature. Separate from the row above: `assert not missing` runs **before** `_check_documents`, so a combined remove-and-drift mutation dies at the absence check and never inspects the sibling — a wrong-reason kill under §3.3, with the drifted sibling as dead payload |
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

**On the schedule only:** `lake build`. The Lean layer needs a ~5 GB Mathlib
cache (measured: `lean/.lake` is 5.1 GB) and a long cold build, changes rarely,
and currently contains zero `sorry`s. Keeping it off push and pull request is a
deliberate gap, not an oversight — a Lean regression reaches `main` unremarked
until the next scheduled run — and the schedule bounds that window to a day for
the price of one cache rather than one per pull request, which is D12's
decision. An earlier draft of this paragraph read "**Not run:** `lake build` …
closing that is a follow-up", contradicting D12, §7 and AC8; see §9.5 B.

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
- **Release assets.** Revisit at a phase boundary. **Answered, 2026-08-24:**
  the boundary arrived when Phase 2 merged, and §9.2 decides them out rather
  than resetting the trigger. Read that section, not this line.

## 8. Acceptance criteria

Each is stated so that satisfying it establishes the property, rather than
resembling it.

1. `tests/properties.py` declares the guarded properties; every one has a live
   test and a mutation, or a listed exemption with an identity and a reason.
2. Every `load_bearing`-marked test belongs to a declared property, and every
   mutation kills **all** of its property's tests, not one of them.
3. For each mutation the harness records: targets **passed** in the unmutated
   scratch tree, then failed under mutation **as assertions matching the
   declared signature**. A run where a *node* target errors, skips, times out or
   fails to collect is a harness failure, not a kill. **Amended 2026-08-24
   (§9.5 D):** a mutation declaring `must_fail_session` (§3.2) is killed by the
   declared session exit status together with the declared violation-text
   signature. Exactly one guard in this repository has no node-level signal —
   the oracle gate fires when a marked test *skips*, and a skip makes no node
   red — so this clause is the narrow exception that guard requires, not a
   general relaxation. A session that exits non-zero for any other reason is
   still a harness failure.
4. Imports in the scratch run resolve beneath the scratch root — asserted, not
   assumed.
5. The sibling-document mutation is present. **Amended 2026-08-24 (§9.5 D):**
   the original wording — "a `skip` under it is treated as **survival**" — was
   written when `test_every_tag_resolves_and_matches` skipped over an absent
   document. It now asserts, so the property to guard has inverted: the mutation
   reintroduces the `skip`, and the kill is the oracle gate catching it, since
   `test_figure_tags.py` is in `GATE_MODULES`. A skip the gate does **not**
   catch is survival. The old wording, applied to the new mutation, would have
   declared its only possible kill a survival.
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

## 9. Amendment — 2026-08-24

Written after the R-002 work that §7 pulled into scope shipped, and after §7's
phase-boundary trigger fired. **Nothing of §3 has shipped** — §3 is the mutation
registry, and it does not exist yet; an earlier draft of this sentence said "§3's
first half", which was false and contradicted §9.1's own next paragraph.

This section resolves three items the body left underdetermined, and §9.5 records
defects the review of this amendment found in §§1–8. It amends **D9** (§9.5 A)
and changes no other §2 decision. It changes no §8 acceptance criterion, but
§9.4 states which criteria each plan leaves unsatisfied. It **amends AC3 and
AC5** (§9.5 D); an earlier draft of this sentence claimed no §8 criterion
changed, which was false once §3.2 gained a session-level kill.

### 9.1 State at the time of this amendment

Delivered on `main`: AC10 (both memory files with `MEMORY.md` pointers, and
`claim-ledger` §6.1/§6.2) and AC11 (the Phase 1 documents brought under the
figure-tag mechanism, closing R-002's open half) — PRs #7 and #8. Delivered
ahead of this spec because it was live on `main`: artifact existence-and-hash
checking in `check_claims.py` (`4375689`).

Outstanding: AC1–AC9 and AC12. Nothing of the registry exists yet — no
`tests/properties.py`, no mutation package, no `load_bearing` marker, no
`.github/workflows`.

**The §3.5 seed set was re-checked against the tree, because the R-002 work
renamed test modules after this spec was written.** Every row still names a
symbol or file that exists — including `tests/test_epistemic_staleness.py`, a
module rather than a test function, and the figure-tag tests, which now live in
`tests/test_figure_tags.py` rather than the `test_phase2_figures.py` the spec was
drafted against.

**Anchor existence was the wrong property to check, and an earlier draft of this
paragraph stopped there.** A row is usable only if its declared targets actually
go red, for the declared reason, under §3.1's rule that a mutation must kill
*every* listed test. Three rows failed that test and are revised in §3.5:

- **Remove `data/phase1_data.csv`** listed "the oracle-gate guard" as a target.
  `tests/test_oracle_gate_guard.py` exercises `gate_violations` over synthetic
  arguments and never reads the CSV, so it cannot go red. An earlier draft of
  this bullet then claimed the real signal was the session gate firing on skips.
  That was also wrong: `_exact()` **asserts** on an absent CSV — its docstring
  says "this must fail rather than skip", because while it skipped a clean clone
  ran none of the twelve comparisons and still reported green — and
  `pytest_runtest_makereport` counts a failed call phase as *executed*, so
  `state.skipped` stays empty and the gate never fires. The row is an ordinary
  node-level kill over the twelve comparisons, plus a separate row naming the
  two `gate_violations` unit tests that a gutted helper actually kills.
- **Perturb one stored figure value** was underdetermined. `residual-centre` is
  in `KEYS_KNOWINGLY_UNQUOTED`, so perturbing it survives every check and proves
  nothing. Pinned to `chernoff-certified-nmax`, which the documents quote.
- **Remove one tracked document, leave a drifted sibling** dies at
  `assert not missing` in `test_every_tag_resolves_and_matches`, which runs
  before `_check_documents` inspects any sibling. The drifted sibling is dead
  payload and the kill is a wrong-reason kill under §3.3. Split into a
  session-level mutation that turns the assertion into a `skip` — the actual
  recurrence — and a plain drift mutation on a present document.

The seed set is therefore **15 rows**, not thirteen. The count is recorded here
as an observation; D9 no longer states one (§9.5 A).

### 9.2 The baseline fingerprint is a tracked file (resolves §3.7)

§3.7 requires the workflow to fail "when the fingerprint moves without a matching
waiver". That presupposes a stored baseline to compare against, which the body
never locates. D13 rejects machine-local hash files. The baseline is therefore
tracked in the repository, at `.superpowers/registry/fingerprint.json`, and is
updated in the same commit as the waiver authorising the move.

**Where the base is read from is the whole mechanism, and must be stated.**
Two implementations satisfy the sentence above and only one of them detects
anything. Recomputing the fingerprint and comparing it with `fingerprint.json`
*from the same candidate checkout* observes no transition — the author already
updated that file — and `HEAD^` is no better, because a multi-commit pull request
can stage the baseline change in an earlier candidate-controlled commit. The
comparison must therefore read the base from outside the candidate's control:

- On a pull request, `base` is `fingerprint.json` **at the protected target
  SHA**. On a push, `base` comes from the event's `before` SHA.
- `new` is computed independently from the candidate tree, and the tracked
  `fingerprint.json` must **equal** that computed value — otherwise the file is
  decoration.
- The waiver must be **newly added relative to that base**, and must bind the
  protected base commit, the base fingerprint, the new fingerprint, and the
  canonical result diff.
- Waiver identities are retained in an append-only ledger checked against
  protected history, so a previously-used waiver cannot be replayed — which is
  what §3.7's "rejected when … reused" and AC7 already require.
- **Multi-commit:** `base` is always the protected target SHA, never `HEAD^`.
- **Initial baseline:** when no `fingerprint.json` exists at the base, the
  transition is `genesis -> new`. It still requires a waiver, of a distinguished
  `genesis` form, so the first baseline is authored deliberately rather than
  arriving as an unremarked new file.
- **Deletion:** removing `fingerprint.json` is a transition to `absent`, not an
  exemption from the check. It requires a waiver like any other move; a missing
  file never means "nothing to compare".
- **Force-push:** if the push event's `before` SHA is not an ancestor of the
  candidate, the comparison **fails closed** rather than falling back to the
  candidate tree.
- **Pull-request retargeting:** the waiver binds the target ref as well as the
  base SHA, and the workflow runs on `pull_request` `edited` so a retarget
  re-evaluates instead of inheriting a verdict computed against the old base.
- **Merge queue:** `merge_group` is a separate event with its own provenance.
  Either the workflow handles it explicitly or the merge queue is not enabled;
  leaving it unhandled would let a queued merge bypass the comparison entirely.
- **Obsolete bases:** the ruleset must set `strict_required_status_checks_policy`.
  Under the loose policy GitHub permits merging a pull request whose checks ran
  against a base that has since advanced, so a comparison against the *old*
  protected target could be accepted after the target moved.

An earlier draft replaced this list with the single sentence "Initial-baseline
creation, force-push, file deletion and multi-commit behaviour are each defined,
not left to the implementer" — a claim that they were defined, in place of
defining them.

**Self-authorisation is open, and the reason is staffing, not impossibility.**
An earlier draft asserted that a non-author approval requirement "cannot exist
here" because the repository has one maintainer. That is false. GitHub does not
let an author approve their own pull request, so required reviews or path-scoped
CODEOWNERS over the registry, waiver, checker and workflow paths would be
genuinely enforceable — as soon as a second write-authorised reviewer exists.
The obstacle is that no such person is on this project today, which is a
staffing decision the spec cannot make and must not disguise as a technical
limit.

Until one exists, the object is a **waiver explanation**: it forces a
coordinated weakening to be written down and to appear in a diff, and it
authenticates nothing. That is §3.7 residue 1. Adding a reviewer is recorded as
the available closure, not as unreachable.

The reason for tracking the baseline at all is the one §3.7 already gives for
wanting a waiver: the mechanism's value is *the diff a reviewer reads*. A tracked baseline puts the
fingerprint change and its justification in a single reviewable diff, and it
survives a clone as D13 demands. A CI-artifact-only record provides neither —
artifacts expire, and they never appear in a diff.

It sits inside the trust domain of the change under review. §3.7 residue 2
already states that boundary and names branch protection as the mitigation; this
choice does not widen it.

**Release assets: decided, not deferred again.** §7 parked them with "revisit at
a phase boundary". Phase 2 merged on 2026-08-23, so this is that boundary, and
the trigger is being answered rather than reset. They stay out. Reading the
baseline from a Release would take it out of the reviewer's diff — surrendering
§3.7's stated purpose to buy a trust-domain improvement that residue 2 has
already recorded as unclosed — and would add a network dependency to the merge
gate. An earlier draft also claimed that reading a Release puts a **write token**
on the merge path. That is false: reading a public release asset needs at most
`Contents: read` and can be unauthenticated. Only *publishing* needs write
access, and publishing can happen after merge or by hand. Publishing a dated Release at a phase close
remains available as a citation convenience for the paper; nothing depends on it.

### 9.3 AC8 states a requirement without a mechanism

AC8 requires the full tier's status check to be required for merge, with the
configuration "verified, not assumed — a non-required job satisfies 'the workflow
exists' while blocking nothing". The body states this and supplies no mechanism,
and the pytest suite cannot supply one: whether a check is required is a fact
about the repository's ruleset, not about this tree.

**A job that checks its own required-ness does not satisfy AC8.** An earlier
draft proposed exactly that, and it fails for the reason AC8 itself names: the
verifier can be required and green while the full mutation tier stays optional
and blocks nothing. AC8 is about the *full tier's* required-ness, so a verifier
quantifying over itself measures the wrong thing — §3.1's error, one level up.

The verification is a workflow job that:

- reads a **tracked inventory** of the contexts that must be required — the
  full mutation tier's context among them — so the desired end state is written
  down rather than inferred from whatever is configured;
- queries the paginated `GET /repos/{owner}/{repo}/rules/branches/{branch}` for
  the protected target branch. **Not** `GET /repos/{owner}/{repo}/rulesets`,
  which returns ruleset summaries carrying no required-check contexts; the
  branch-rules endpoint returns the active rules and excludes disabled and
  evaluate-mode ones;
- fails when any inventory context is absent from the `required_status_checks`
  rule, checks the expected Actions `integration_id` so another producer cannot
  satisfy a context name, and rejects duplicate contexts;
- runs **unconditionally** on pull requests — and so does the full-tier job
  itself. A job skipped by a job-level condition reports success, so a required
  context can be satisfied by a job that never ran; making only the verifier
  unconditional leaves the job that matters skippable;
- includes **itself** in the inventory, accepting that its own context is
  configured during the bootstrap below rather than existing beforehand.
  Excluding it would leave the verifier optional, which is the defect this
  section exists to fix;
- reads the ruleset's **bypass actors** and fails when any is configured for the
  registry's contexts. A required check that a bypass actor may skip is not
  required for merge, which is what AC8 asks about.

**Rollout order matters, and the naive order does not work.** GitHub will not
let a context be added as required until it has actually been reported — the
producing app must have submitted a check recently — so "configure each context
externally, then rerun", which an earlier draft stated, cannot be executed for a
context no job has ever emitted. The achievable order is:

1. Plan B's full-tier job runs at least once on a branch, emitting its context.
2. Both contexts are then configured as required, with the strict policy set and
   no bypass actors.
3. The workflow reruns, and the verifier reads the configuration back.
4. AC8 is accepted only on a successful read-back — never on the configuration
   step alone.

This is a further reason AC8 cannot close in Plan A: step 1 needs the registry.

Verified at the time of writing: the repository is public, Actions are enabled
with `allowed_actions: all`, and `GET /repos/JoeRu/Non-Linear-Number-Systems/rules/branches/main`
returns HTTP 200 with `[]`. That empty result on its own proves only that no
*active applicable* rule exists — disabled, evaluate-mode and non-matching
rulesets would also produce it. The stronger statement, that no ruleset exists
at all, rests on `GET /repos/JoeRu/Non-Linear-Number-Systems/rulesets` also
returning `[]`, since that endpoint enumerates rulesets regardless of state.

Consequently the shape of a `required_status_checks` rule is taken from GitHub's
documentation and has **not** been observed on this repository. Creating a
ruleset to observe it is a configuration change, not a spec activity.

### 9.4 Delivery order: two plans, continuous integration first

The remaining work ships as two plans, not one.

**Plan A — the non-mutation CI foundation.** Not "the §3A workflow": §3A's push
tier includes the canary and its pull-request tier includes the full tier and
waiver enforcement, and Plan A has none of those. It is the part of §3A that does
not depend on the registry. Concretely: the workflow on push and pull request
(fresh checkout, install, `pytest`, `scripts/check_claims.py`), the §9.3
required-check verification job, the scheduled run including `lake build`, and
the §4 **rule 5 amendment** — which is about a gate's *absence* and so belongs
with the fresh-checkout run rather than with the registry.

**Plan B — the mutation registry.** §3.1–§3.8 entire: `tests/properties.py` and
the `load_bearing` marker, the scratch-tree harness, the §3.5 seed mutations,
the meta-tests, the fingerprint and one-shot waiver checker, both tiers wired
into the workflow Plan A created, **publication of the result mapping and
fingerprint as the pull-request artifact §3A requires** — which Plan A cannot do,
because there is no registry to produce it, and which an earlier draft of this
list simply omitted — and the §4 **rule 11**.

The order follows from what §3A already says about its own contents: the
fresh-checkout run "is the *structural* fix for the clean-clone class … no
mutation required, and no one needing to think of it. That property comes free
with CI existing at all, and it is the single cheapest thing in this document."
Shipping the cheapest structural fix behind the most expensive one is the wrong
way round. The split also bounds risk — the ~5 GB Mathlib cache is the one
genuinely uncertain piece, and it is better discovered on a four-task plan than
a fifteen-task one — and it keeps each diff small enough to be reviewed, which
is not hypothetical: Copilot reported "24/25 files reviewed" on PR #8 without
naming the file it skipped.

**The risk in splitting is §3.6's own warning, one level up.** "Tiering is how a
fast set quietly becomes the only set that ever runs" applies to plans as readily
as to mutation tiers: Plan A is the cheap tier, and Plan B is what quietly never
happens.

An earlier draft offered two mitigations that do not mitigate. Shipping rule 11
with Plan B keeps a rule from depending on a registry that does not exist — a
consistency measure, not a delivery one. And calling the required-check set
"visibly incomplete" encoded no target, no tracking and no failure; nothing
would have gone red.

What holds instead is §9.3's **tracked inventory**. It names every context that
must be required, including the full mutation tier's, and the verifier fails
while any of them is absent. After Plan A that job therefore fails on every run,
naming the missing tier — a standing red that cannot be mistaken for completion,
and that no one has to remember. It does not *block* merges, which is deliberate:
a hard block would stop Phase 3 and Phase 4 research on a single-maintainer
repository for as long as Plan B takes. The residue is that a standing red can be
ignored by a maintainer who chooses to; that is a smaller residue than a blocked
repository, and it is stated rather than hidden.

**Which criteria each plan leaves unsatisfied, stated plainly.** AC1–AC7 belong
to Plan B. **AC8 is not satisfied by Plan A** — the full tier does not exist, so
its context cannot be required; Plan A ships the inventory and the verifier, and
AC8 closes in Plan B. **AC9 is satisfied only by the conjunction** — rule 5 in A,
rule 11 in B, neither alone. **AC12 is attributable to Plan A only once its runs
actually pass**: installing a job is not satisfying a criterion that requires a
green fresh-checkout run and a clean `lake build`. §8 remains the bar, and after
Plan A the honest statement is that most of it is still open.

### 9.5 Defects this amendment's review found in §§1–8

The two Codex reviews of §9 (2026-08-24) found defects in the already-approved
body. They are recorded here so the edits are attributable rather than silent.
A and B are closed. C was **wrong as first written** and its correction forced
D, which amends two acceptance criteria — so the amendment does change §8, and
§9.1 no longer says otherwise.

**A. D9's cardinalities were stale.** D9 read "a 4-mutation canary and the full
12". §3.5 held **13** rows at the time — the 2026-08-23 review had already
rejected the count once and the table grew afterwards — and §3.6's named canary
has **six** members, because T1, T3 and T5 are three rows. D9 is now
content-addressed and states no number; §9.1's revisions took the seed set to 15,
which is why counting it in a decision cell was the wrong shape to begin with.
This is the one §2 decision §9 amends.

**B. §3A contradicted D12, §7 and AC8 about Lean.** §3A read "**Not run:**
`lake build` … closing that is a follow-up", while D12 decides schedule-only, §7
records it as partly accepted on the schedule, and AC8 requires a scheduled run
including it. §3A now reads "On the schedule only", keeping its cache rationale.
The measured cache size is 5.1 GB, and Mathlib is pinned to the official
`v4.14.0` tag, so the scheduled job can fetch prebuilt oleans rather than cold-
building — cheaper than the paragraph assumed.

**C. §3.2's kill model could not express one seed mutation — not two.**
`must_fail` took pytest node ids, but the oracle gate fails a *session*, not a
node: `pytest_sessionfinish` in `tests/conftest.py` inspects skips across
`GATE_MODULES` and sets `session.exitstatus = 1`, and a skip leaves every node
green. §3.2 gained `must_fail_session` and §3.3 extends the right-reason
requirement to it.

The first draft of this entry claimed **two** such mutations, including the
removal of `data/phase1_data.csv`. That was false, and the tree says so
plainly: `_exact()` asserts on an absent CSV, with a docstring recording that it
was converted from a skip for exactly this reason, and
`pytest_runtest_makereport` counts a failed call phase as executed — so nothing
skips and the gate never fires. That row is an ordinary node-level kill. Only
the missing-document mutation, which reintroduces a `skip`, needs the session
model.

**D. Amending AC3 and AC5 (forced by C).** AC3 said any target that skips is a
harness failure; AC5 said a `skip` under the sibling mutation is *survival*.
Both predate the tree's conversion of that skip into an assertion. Left
unchanged, they would have declared the session-level mutation's only possible
kill a survival. AC3 now carries a narrow exception for a declared
`must_fail_session`, and AC5 is inverted to the property that is now real: the
mutation reintroduces the skip, the gate must catch it, and a skip the gate does
not catch is survival.

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

**2026-08-24, Codex `gpt-5.6-sol` effort `ultra`, amendment gate (CLAUDE.md rule 6).**
Verdict on §9: FLAWED on all five questions put to it, plus two contradictions
inside the approved body. Every finding was verified against the repository
before acting; the one rejection is recorded with its reason.

| Finding | Outcome |
|---|---|
| §9.2 never says where the base fingerprint is read from; comparing against the candidate checkout's own file observes no transition, and `HEAD^` fails on a multi-commit PR | **Accepted.** §9.2 now reads `base` from the protected target SHA (or the push event's `before`), recomputes `new` independently, and requires the tracked file to equal it. |
| Waivers need replay detection, newly-added-relative-to-base binding, and defined force-push / initial-baseline / deletion behaviour | **Accepted.** Enumerated in §9.2. |
| Require non-author approval (CODEOWNERS) for registry and waiver paths | **Rejected, with reason.** Single-maintainer repository: the author is the only human who can approve, so this control could never fire — §1.1's own defect pattern. §9.2 instead names the object a *waiver explanation* and states self-authorisation as admitted residue. |
| `GET /rulesets` returns summaries carrying no required-check contexts; `GET /rules/branches/{branch}` is the correct endpoint | **Accepted.** §9.3 rewritten. Endpoint verified live (HTTP 200); it returns `[]` since no ruleset exists, so the rule payload shape is documentation-sourced and §9.3 says so. |
| A verifier asserting its **own** required-ness does not establish AC8, which is about the full tier's — it can be required and green while the mutation job blocks nothing | **Accepted.** This was §9.3's central mechanism and it did not work. Replaced with a tracked inventory of required contexts, plus `integration_id` checking, duplicate rejection, and unconditional jobs (a skipped job reports success). |
| §9.4's two mitigations against Plan B never shipping are consistency measures, not delivery mitigations | **Accepted.** Replaced by the §9.3 inventory, which leaves the verifier standing red and naming the missing tier until Plan B lands. A blocking placeholder was considered and declined: it would stop Phase 3/4 research on a solo repository. |
| AC8 false as allocated; AC9 valid only as the conjunction; AC12 needs actual passing runs, not installed jobs | **Accepted.** §9.4 now states which criteria each plan leaves open. |
| "§3's first half shipped" is false — nothing of §3 exists; the shipped work came from §7 | **Accepted.** §9.1 corrected. |
| Plan B omitted §3A's required PR artifact publication | **Accepted.** Added to §9.4. |
| "Reading a Release baseline puts a write token on the merge path" is false | **Accepted.** Reading a public asset needs no write token; only publishing does. §9.2 corrected, and the surviving reason — the baseline leaves the reviewer's diff — is kept. |
| §9.1's "all thirteen rows name live anchors" checked the wrong property: existence, not registrability. Three rows cannot be registered as written | **Accepted, and it was the most valuable finding.** The CSV row's named guard tests run on synthetic input and cannot go red; the perturbation row was satisfiable by `residual-centre`, which no document quotes; and the sibling row dies at `assert not missing` before the drifted sibling is read — a wrong-reason kill of the recurrence this spec cites most. §3.5 revised to 15 rows; §9.1 rewritten. |
| D9's cardinalities are stale, so §9's "changes no §2 decision" is untrue | **Accepted.** D9 content-addressed; §9.5 A records it as the one §2 amendment. |
| §3A's "Not run: `lake build`" contradicts D12, §7 and AC8 | **Accepted.** §3A now reads "On the schedule only"; §9.5 B. |

**2026-08-24, Codex `gpt-5.6-sol` effort `ultra`, second amendment gate.** Scoped
re-review of the revisions above. Two findings restated (partly closed), three
new defects — including one the first revision introduced.

| Finding | Outcome |
|---|---|
| §9.2's "initial-baseline creation, force-push, file deletion and multi-commit behaviour are each defined" asserts they are defined without defining any of them | **Accepted.** All four are now written out, plus PR retargeting, `merge_group`, and `strict_required_status_checks_policy` — under the loose policy GitHub permits merging checks that ran against a base which has since advanced. |
| "A non-author approval requirement cannot exist here" is false: GitHub forbids self-approval, so required reviews or CODEOWNERS become enforceable once a second write-authorised reviewer exists | **Accepted; the earlier rejection was wrong.** The obstacle is staffing, not impossibility, and §9.2 now says so. Recorded as available closure rather than unreachable. |
| §9.3's rollout order is unachievable: GitHub will not accept a context as required until it has been reported, and after Plan A the full-tier context has never been emitted | **Accepted.** Order corrected to preflight → configure → rerun → read-back, which is a further reason AC8 cannot close in Plan A. |
| §9.3 left the inventory silent about the verifier itself, made only the verifier unconditional, and ignored ruleset bypass actors | **Accepted.** All three fixed; a context a bypass actor may skip is not required for merge. |
| The CSV mutation is impossible as written — `_exact()` asserts rather than skips, and a failed call phase counts as executed, so no SKIPPED signature appears | **Accepted, and it invalidated the first revision's central claim.** The tree is explicit: `_exact()`'s docstring records that it was converted from a skip so a clean clone could not run none of the twelve comparisons and still report green. The row is an ordinary node-level kill; only the missing-document mutation needs the session model. §9.5 C rewritten. |
| The `gate_violations` row names a module, but only two of its eight tests die | **Accepted.** Named as exact node ids. |
| The session-level mutation contradicts unchanged AC2, AC3 and AC5, which require node kills and call this very skip "survival" | **Accepted.** AC3 gains a narrow exception; AC5 is inverted to the property that is now real. §9 no longer claims it changes no acceptance criterion — §9.5 D. |
| §9.3 infers "no ruleset exists" from an empty branch-rules result, which proves only that no *active applicable* rule exists | **Accepted.** The claim now rests on `GET /rulesets` also returning `[]`, which enumerates rulesets regardless of state. |
| §9.5's blanket "they are fixed in place" was false once C proved wrong | **Accepted.** Preamble rewritten to say which entries closed and which forced further change. |
| The §9.4 inventory improves observability but is non-blocking and therefore ignorable, so it does not close the risk of Plan B never shipping | **Acknowledged, not closed.** This is the residue of the deliberate choice not to block merges on a single-maintainer repository mid-Phase-3; §9.4 already states it. Recorded in `docs/risks.md` rather than argued further. |


| Lean CI is load-bearing for the spec's own goal | **Partly accepted.** Added on the schedule rather than per pull request: it bounds the window to a day for one cache, and the Lean layer changes rarely. |
