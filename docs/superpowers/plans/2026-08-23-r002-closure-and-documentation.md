# R-002 Closure and the Documentation Layer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the open half of risk R-002 by binding every generated number quoted in the Phase 1 documents to the artifact that produced it, and land the documentation layer the defect-prevention spec calls for.

**Architecture:** `scripts/run_phase1.py` gains a tracked `data/phase1_figures.json` in the schema Phase 2 already uses; the two Phase 1 documents quote generated numbers as `<literal> {fig:key}`; the existing correspondence test generalises from one hard-coded phase to a table of `(figures file, documents)` pairs so both phases are checked by one mechanism. Separately and independently, two project-memory files and two `claim-ledger` skill sections record what the review loop learned.

**Tech Stack:** Python >= 3.11, pytest, the project venv at `.venv`.

**Spec:** `docs/superpowers/specs/2026-08-23-defect-prevention-infrastructure-design.md` — §1 class D, §6.1, §6.2, §7 ("Pulled in"), acceptance criteria 10 and 11.

## Global Constraints

- Python >= 3.11. Run everything through `.venv/bin/python`. The system `python3` lacks matplotlib and fails 7 unrelated tests.
- **Never hand-copy a number into a document.** Every quoted figure is produced by a script under `scripts/` and recorded via `capfib.manifest.record`.
- Every generated dataset writes an entry to `data/manifest.json`.
- **Cited artifacts must exist and match their manifest SHA-256** — `scripts/check_claims.py` enforces this as of `4375689`. A new tracked artifact must be regenerated in step with any change to the script that writes it.
- Never state a finite observation as universal. Phase 1 computed exact values for all `N <= 10^6`; Phase 2's verification ran at 37 sampled rows. Do not conflate them.
- Never weaken a test or guard to make something pass.
- Google-style docstrings on all new Python functions.
- Commit at the end of every task.

---

## File Structure

| File | Responsibility |
|---|---|
| `scripts/run_phase1.py` | **modify.** Emit `data/phase1_figures.json` alongside the existing artifacts, from values it already computes. |
| `data/phase1_figures.json` | **new, tracked.** The quotable Phase 1 figures — same `{key: {value, precision, description}}` schema as Phase 2. |
| `.gitignore` | **modify.** Negation for the new tracked artifact, with the reason. |
| `tests/test_figure_tags.py` | **new.** The generalised correspondence check, table-driven over both phases. Replaces `tests/test_phase2_figures.py`. |
| `docs/phase1.md`, `docs/phases/phase1_report.md` | **modify.** Tag every quoted generated number. |
| `.claude/skills/claim-ledger/SKILL.md` | **modify.** Add §6.1 promotion checklist and §6.2 endpoint trap. |
| `~/.claude/projects/-root-code-Non-Linear-Number-Systems/memory/` | **new files.** Two memory entries plus `MEMORY.md` pointers. |
| `docs/risks.md` | **modify.** R-002 moves to `mitigated` outright once both phases are covered. |

---

## Task 1: Emit the Phase 1 figures file

**Files:**
- Modify: `scripts/run_phase1.py`
- Modify: `.gitignore`
- Test: `tests/test_run_phase1.py`

**Interfaces:**
- Consumes: `capfib.manifest.record(path, script, params)`, and the `summary` dict `run_phase1.py` already builds.
- Produces: `data/phase1_figures.json`, schema `{key: {"value": number, "precision": int, "description": str}}` — identical to `data/phase2_figures.json`, so Task 3's generalised checker needs no special case.

**Background.** `data/phase1_summary.json` already holds 19 scalar and array fields — `census.decreasing`, `fluctuation_quantiles.median`, `R_c_bit_length` and so on. The documents quote a subset of these by hand. This task publishes that subset in the quotable schema; it computes nothing new.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_run_phase1.py`:

```python
def test_run_phase1_emits_a_tracked_figures_file(tmp_path):
    """Phase 1 must publish its quotable numbers the way Phase 2 does.

    Risk R-002: the Phase 1 documents quote generated numbers with nothing
    binding them to the artifacts, so regeneration cannot update the prose and
    drift is silent. The figures file is what the tag test checks against.
    """
    import json

    figures = ROOT / "data" / "phase1_figures.json"
    assert figures.is_file(), (
        "data/phase1_figures.json is absent; run scripts/run_phase1.py"
    )
    data = json.loads(figures.read_text())
    assert data, "the figures file is empty"
    for key, entry in data.items():
        assert set(entry) >= {"value", "precision", "description"}, key
        assert isinstance(entry["precision"], int), key
        assert entry["description"].strip(), f"{key} has no description"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_run_phase1.py::test_run_phase1_emits_a_tracked_figures_file -v`
Expected: FAIL — `data/phase1_figures.json is absent`.

- [ ] **Step 3: Emit the file**

In `scripts/run_phase1.py`, after the summary is written and recorded, add:

```python
    figures = {
        "n-max": {
            "value": summary["n_max"],
            "precision": 0,
            "description": "largest N for which R_c was computed exactly",
        },
        "rc-bit-length": {
            "value": summary["R_c_bit_length"],
            "precision": 0,
            "description": "bit length of R_c at the largest N",
        },
        "census-increasing": {
            "value": summary["census"]["increasing"],
            "precision": 0,
            "description": "increasing steps of R_c over the computed range",
        },
        "census-decreasing": {
            "value": summary["census"]["decreasing"],
            "precision": 0,
            "description": "decreasing steps of R_c over the computed range",
        },
        "census-flat": {
            "value": summary["census"]["flat"],
            "precision": 0,
            "description": "flat steps of R_c over the computed range",
        },
        "census-steps": {
            "value": summary["census"]["steps"],
            "precision": 0,
            "description": "total steps examined in the monotonicity census",
        },
        "decreasing-fraction": {
            "value": 100.0 * summary["census"]["decreasing"] / summary["census"]["steps"],
            "precision": 1,
            "description": "percentage of steps that decrease, over the computed range",
        },
        "fluctuation-median": {
            "value": summary["fluctuation_quantiles"]["median"],
            "precision": 6,
            "description": "median of R_c(N+1)/R_c(N) over the computed range",
        },
        "fluctuation-min": {
            "value": summary["fluctuation_quantiles"]["min"],
            "precision": 6,
            "description": "minimum local ratio over the computed range",
        },
        "fluctuation-max": {
            "value": summary["fluctuation_quantiles"]["max"],
            "precision": 1,
            "description": "maximum local ratio over the computed range",
        },
        "flat-step-count": {
            "value": len(summary["flat_step_positions"]),
            "precision": 0,
            "description": "number of flat steps found",
        },
        "flat-step-last": {
            "value": max(summary["flat_step_positions"]),
            "precision": 0,
            "description": "largest N at which a flat step occurs",
        },
    }
```

**Deliberately excluded: `dp_seconds` and `gf_seconds`.** They are in the
summary and the documents mention them, but wall-clock timings change on every
run. Tagging them would force a prose edit at each regeneration for no
epistemic gain — churn that looks like rigour and trains people to edit numbers
to make a test pass, which is the opposite of the point. They stay untagged and
are named in Task 3 Step 5's residue note.

```python
    figures_path = ROOT / "data" / "phase1_figures.json"
    atomic_write_text(figures_path, json.dumps(figures, indent=2, sort_keys=True) + "\n")
    record(
        str(figures_path.relative_to(ROOT)),
        "scripts/run_phase1.py",
        {"n_max": args.n_max},
    )
```

Match the surrounding code's names for `summary`, `args`, `ROOT`, `record` and `atomic_write_text`; if any differs, use the local name rather than introducing a new one.

- [ ] **Step 4: Track the artifact**

In `.gitignore`, beside the other negations:

```
# data/phase1_figures.json is tracked for the same reason as the artifacts
# above: the Phase 1 documents quote it by key, and tests/test_figure_tags.py
# fails when a quoted literal and the generated value disagree. A gitignored
# figures file could not keep prose and data in step on a clean clone.
!data/phase1_figures.json
```

- [ ] **Step 5: Regenerate and verify**

Run: `.venv/bin/python scripts/run_phase1.py`
Expected: completes, writes `data/phase1_figures.json`, and adds a manifest entry.

Run: `.venv/bin/python -m pytest tests/test_run_phase1.py -q` — expected PASS.
Run: `.venv/bin/python scripts/check_claims.py` — expected `claims.yaml OK`. (The artifact-existence check added in `4375689` now also covers this file if a claim cites it.)
Run: `git check-ignore -v data/phase1_figures.json; echo "exit=$?"` — expected `exit=1`, i.e. not ignored.

- [ ] **Step 6: Commit**

```bash
git add scripts/run_phase1.py .gitignore data/phase1_figures.json data/manifest.json tests/test_run_phase1.py
git commit -m "feat: publish the quotable Phase 1 figures

The Phase 1 documents quote generated numbers with nothing binding them to the
artifacts that produced them -- risk R-002, the project's highest-rated open
risk. This publishes them in the schema Phase 2 already uses, so one mechanism
can check both phases. It computes nothing new; every value is already in
data/phase1_summary.json."
```

---

## Task 2: Generalise the correspondence check to both phases

**Files:**
- Create: `tests/test_figure_tags.py`
- Delete: `tests/test_phase2_figures.py`
- Test: itself

**Interfaces:**
- Consumes: `data/phase1_figures.json` from Task 1; `data/phase2_figures.json`, already tracked.
- Produces: `PHASES`, a table of `(figures_path, documents)` pairs that Task 3 extends by adding tagged documents, not by editing test logic.

**Why replace rather than duplicate.** `tests/test_phase2_figures.py` hard-codes one figures file and two documents. Copying it for Phase 1 would double a guard that has already had one silent-disablement bug (`pytest.skip` on a missing sibling). One table-driven checker, extended by data, is the smaller surface.

**Preserve every property the existing file has.** Read it first. It must keep: exact literal-vs-stored comparison at the recorded precision; the offset-based bare-tag rejection (**not** a proximity window — that version accepted a tag whose number belonged to a neighbouring tag); per-document `continue` rather than a session-wide skip; the "a missing document does not disable a present one" test; and the unused-key report.

- [ ] **Step 1: Write the new file**

Create `tests/test_figure_tags.py` by moving the existing tests across and replacing the two module constants with a table:

```python
"""Quoted figures must match the artifacts that generated them, in every phase.

Risk R-002: narrative documents carry hand-copied numbers while `data/` is
largely gitignored, so regeneration cannot update the prose and drift is
silent. Prose carries `<literal> {fig:key}`; this resolves each key against the
phase's figures file, formats the stored value at its recorded precision, and
requires an exact string match.

Table-driven rather than per-phase: a copy of this file for each phase would
double a guard that has already been silently disabled once, by a `pytest.skip`
on an absent sibling document.
"""

ROOT = Path(__file__).resolve().parents[1]

PHASES = (
    ("phase1", ROOT / "data" / "phase1_figures.json",
     ("docs/phase1.md", "docs/phases/phase1_report.md")),
    ("phase2", ROOT / "data" / "phase2_figures.json",
     ("docs/phase2.md", "docs/phases/phase2_bounds.md")),
)
```

Parametrise every existing test over `PHASES` with `ids=lambda p: p[0]`, keeping each assertion exactly as it was.

- [ ] **Step 2: Run it — Phase 2 must still be fully checked**

Run: `.venv/bin/python -m pytest tests/test_figure_tags.py -v`
Expected: PASS. The Phase 2 cases must **run**, not skip — both documents exist and carry tags. The Phase 1 cases pass trivially for now, since those documents carry no tags yet.

- [ ] **Step 3: Prove the guard did not weaken in the move**

Temporarily change one literal in `docs/phase2.md` (for example `13.5505` → `13.5506`), run the test, confirm it FAILS naming the key and file, then restore the file and confirm it passes. Record both outputs in your report.

- [ ] **Step 4: Remove the superseded file**

```bash
git rm tests/test_phase2_figures.py
```

Then run the full suite: `.venv/bin/python -m pytest -q` — expected PASS with the same count minus the removed duplicates.

- [ ] **Step 5: Commit**

```bash
git add tests/test_figure_tags.py
git commit -m "test: check figure tags for every phase from one table

tests/test_phase2_figures.py hard-coded one figures file and two documents.
Copying it for Phase 1 would double a guard that has already been silently
disabled once, by a pytest.skip on an absent sibling. This is the same checks,
parametrised over a table of (figures file, documents) pairs, so adding a phase
is data rather than logic."
```

---

## Task 3: Tag the Phase 1 documents

**Files:**
- Modify: `docs/phase1.md`
- Modify: `docs/phases/phase1_report.md`

**Interfaces:**
- Consumes: the keys published in Task 1 and the checker from Task 2.
- Produces: two documents whose generated numbers are machine-checked.

**Scope, precisely.** Tag every literal that came out of `data/phase1_summary.json` or `data/phase1_data.csv`. Do **not** tag mathematical constants (`1/(4 log phi)`), structural numbers (section numbers, dates, `N = 10^6` used as a range bound in prose rather than as a measured result), or numbers quoted from the literature. If a literal is generated but has no key, add the key in `scripts/run_phase1.py` and regenerate — do not hand-copy it.

**The residue must be stated, not hidden.** After tagging, some literals will remain untagged by design. Add a short note to `docs/phase1.md` saying which categories are untagged and why, so a reader knows the guarantee's edge. An unstated edge is how "mitigated" turns into "assumed safe".

- [ ] **Step 1: Inventory what is generated**

Run:

```bash
.venv/bin/python - <<'EOF'
import json, re, pathlib
figs = json.load(open('data/phase1_figures.json'))
for doc in ('docs/phase1.md', 'docs/phases/phase1_report.md'):
    text = pathlib.Path(doc).read_text()
    print(f"\n== {doc}")
    for key, entry in sorted(figs.items()):
        p = entry['precision']
        s = str(int(round(entry['value']))) if p == 0 else f"{entry['value']:.{p}f}"
        if s in text:
            print(f"   {s:>14}  ->  {{fig:{key}}}")
EOF
```

This lists the literals already present that have a key. Work through them, then read both documents for generated numbers that printed no match — those either need a new key or are legitimately untagged.

- [ ] **Step 2: Tag them**

Rewrite each generated literal as `<literal> {fig:key}`. Example:

```markdown
Of the 1000000 {fig:census-steps} steps examined, 495548 {fig:census-decreasing}
decrease — 49.6 {fig:decreasing-fraction}% of them.
```

The literal must match the stored value formatted at its recorded precision **exactly**; the test compares strings.

- [ ] **Step 3: Run the checker**

Run: `.venv/bin/python -m pytest tests/test_figure_tags.py -v`
Expected: PASS, with the Phase 1 cases now exercising real tags. If a literal mismatches, fix the **prose**, never the stored value.

- [ ] **Step 4: Verify the claim validator still passes**

Run: `.venv/bin/python scripts/check_claims.py`
Expected: `claims.yaml OK`. If the universal-quantifier guard fires on a paragraph you edited, the prose changes — never the guard.

- [ ] **Step 5: Record the residue**

Add to `docs/phase1.md`, near the top:

```markdown
> **On the numbers below.** Every figure produced by `scripts/run_phase1.py` is
> quoted with a `{fig:...}` tag and checked against `data/phase1_figures.json`
> by `tests/test_figure_tags.py`; a quoted value that drifts from the generated
> one fails the suite. Mathematical constants, section and equation numbers, and
> values quoted from the literature carry no tag and are not machine-checked.
> Wall-clock timings are excluded on purpose: they change on every run, so
> tagging them would force a prose edit at each regeneration.
```

- [ ] **Step 6: Commit**

```bash
git add docs/phase1.md docs/phases/phase1_report.md
git commit -m "docs: bind the Phase 1 documents' generated numbers to their artifacts

Closes the open half of risk R-002. Every number produced by run_phase1.py is
now quoted by key and checked against data/phase1_figures.json, so regeneration
and prose cannot drift apart silently. The untagged residue -- mathematical
constants, structural numbers, literature values -- is stated in the document
rather than left for a reader to discover."
```

---

## Task 4: Retire R-002's open half

**Files:**
- Modify: `docs/risks.md`

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: a risk register that matches the code.

**Why this is its own task.** This branch fired three of its own `Revisit when:` triggers and updated none until a reviewer noticed. A register that goes stale when its triggers fire is worse than no register, because it is read as current.

- [ ] **Step 1: Update the entry**

R-002 currently reads `mitigated for the Phase 2 documents … open for the Phase 1 ones`. Change it to `mitigated`, and say in the body: the mechanism is `{fig:key}` tags checked by `tests/test_figure_tags.py` against per-phase figures files; both phases are covered; the residue is the untagged categories named in `docs/phase1.md`. Update `Revisit when:` to name what would reopen it — a new narrative document that quotes generated numbers without being added to `PHASES`.

- [ ] **Step 2: Verify**

Run: `.venv/bin/python -m pytest -q` and `.venv/bin/python scripts/check_claims.py` — both expected clean.

- [ ] **Step 3: Commit**

```bash
git add docs/risks.md
git commit -m "docs: R-002 mitigated for both phases

Its trigger fired and the mechanism it named as a candidate resolution now
exists for Phase 1 as well as Phase 2. The residue -- the untagged categories --
is named rather than implied."
```

---

## Task 5: The documentation layer

**Files:**
- Modify: `.claude/skills/claim-ledger/SKILL.md`
- Create: `~/.claude/projects/-root-code-Non-Linear-Number-Systems/memory/never-pre-clear-findings-in-reviewer-briefs.md`
- Create: `~/.claude/projects/-root-code-Non-Linear-Number-Systems/memory/verify-before-downgrading-a-finding.md`
- Modify: `~/.claude/projects/-root-code-Non-Linear-Number-Systems/memory/MEMORY.md`

**Interfaces:**
- Consumes: nothing. Independent of Tasks 1–4 and of Plan 2.
- Produces: the skill and memory content specified in spec §5 and §6.

**This task is independent** — it can run first, last, or in parallel with the rest, and it is the one part of this plan that cannot break the suite.

- [ ] **Step 1: Add the promotion checklist to the skill**

Add a `## Promoting a claim` section to `.claude/skills/claim-ledger/SKILL.md` with the five steps of spec §6.1, each with the incident that produced it: the hedge guard disappearing on promotion; the roadmap bullet that argued from a false intermediate; `saddle-tightness` sitting under-claimed for a round; trees no validator reads; and `docs/risks.md` triggers firing unnoticed.

- [ ] **Step 2: Add the endpoint trap**

Add a `## Writing about generated data` section with spec §6.2 — the three Phase 2 sentences that were true at the ends and false between, and the rule: read the whole series, check every point, and if it is not monotone say so or quote the values.

- [ ] **Step 3: Write the two memory files**

Use the frontmatter format the existing memory files use (`name`, `description`, `metadata.type: feedback`). Content from spec §5.1 and §5.2 — the pre-cleared finding in Task 1's reviewer brief, and the finding parked as Minor that one command would have shown was serious, together with the too-weak review question.

- [ ] **Step 4: Add the `MEMORY.md` pointers**

One line each, in the existing `- [Title](file.md) — hook` form.

- [ ] **Step 5: Verify the skill still parses**

Run:

```bash
.venv/bin/python -c "
import yaml, pathlib
t = pathlib.Path('.claude/skills/claim-ledger/SKILL.md').read_text()
print('frontmatter:', yaml.safe_load(t.split('---')[1])['name'])"
```

Expected: `frontmatter: claim-ledger`.

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/claim-ledger/SKILL.md
git commit -m "docs(skill): record the promotion checklist and the endpoint trap

Both earned. Promotion silently removes the hedging guard from every paragraph
citing a claim, in the same commit that makes those paragraphs stale. And three
Phase 2 sentences were wrong the same way -- a qualitative summary of a finite
series asserted from its endpoints, true at the ends and false between."
```

(The memory files live outside the repository and are not committed.)

---

## Notes for the executor

- **Task 5 is independent** of everything else and cannot break the suite. Tasks 1 → 2 → 3 → 4 are strictly ordered.
- **Task 1 regenerates artifacts.** `scripts/run_phase1.py` takes several minutes at `n_max = 10^6`, and its outputs are tracked and hash-checked, so the manifest must be committed in the same commit.
- **If a quoted literal and a generated value disagree, the prose is wrong** — the whole point is that the artifact wins.
- **Do not weaken the tag checker while moving it.** The offset-based bare-tag rejection replaced a proximity window that accepted a tag whose number belonged to a neighbouring tag; Task 2 Step 3 exists to prove the move preserved that.
