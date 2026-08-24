# Risk Register

When a review dispute does not resolve — the reviewer holds a position, the
project holds another, and no further round will settle it — it is recorded
here rather than dropped. Each entry names the positions honestly, including
the one the project did not take, and states what it could cost the roadmap's
objective: a rigorous, publishable asymptotic for `R_c(N)`.

An entry is not a defect. Defects get fixed. An entry is a *decision made under
disagreement*, kept visible so it can be revisited when the cost becomes real.

**Status values:** `open` (live disagreement) · `accepted` (the project has
knowingly taken the risk) · `mitigated` (reduced, not eliminated) · `closed`
(resolved; kept for the record).

---

## R-001 — Measured figures retained in the design spec

**Status:** accepted · **Raised by:** Codex, 2026-08-20 · **Phase:** 1

**Description.** The design spec states three measured quantities: `R_c(10^6)`
is 99 bits, `min(counts) == 1`, and the place-jump ratios. All three are
recorded in `data/phase1_summary.json` and agree with it.

**Positions.**

- *Codex:* the project's stated rule is that exactly one place holds real
  numbers — the report, backed by the artifact. Measured values in a design
  document belong in the report regardless of whether they are backed. It
  blocked the push on this.
- *Project:* the rule as originally phrased ("the spec may print no measured
  quantity") was over-broad, and was written by this project, not by Codex. The
  defensible rule is that a number must trace to a recorded artifact *and agree
  with it*. Unreproducible timings failed both tests and were removed. These
  three fail neither. Removing them would also strip §6 of the very values that
  record the *correction* of a false claim.

**Risk to the roadmap.** Low. If the position is wrong, a reader takes a figure
from the spec rather than the report and, should the two ever diverge, cites a
stale number in the paper. The mitigation is that they currently agree and both
trace to the same artifact.

**Revisit when:** the spec and the report ever disagree on any shared figure.

---

## R-002 — Narrative documents contain hand-copied numbers

**Status:** mitigated for the documents named in `PHASES` — see "What is bound,
and what is not" below, which states the residual rather than leaving it inside
the word "mitigated" · **Raised by:** Copilot, 2026-08-21 · **Phase:** 1

**Description.** `docs/phase1.md` and `docs/phases/phase1_report.md` embed the
census, the place-jump table and the block-extrema table as literal Markdown.
`data/` was gitignored in its entirety when this was raised, so regenerating
the artifacts did not update these pages and they could silently drift from
the citable summary. (`data/` is still gitignored by default; the artifacts
the documents and validators need are now tracked by explicit exception, each
with its reason in `.gitignore`.)

**Positions.**

- *Copilot:* this violates the project's own numerics rule ("never hand-copy a
  number into a document"). Generate the tables from the recorded artifact, or
  link to it instead of duplicating.
- *Project:* a phase report is prose written for a human reader, and prose whose
  numbers are all transcluded is not a report. The rule was written for numbers
  that no artifact records; these all trace to
  `data/phase1_summary.json`. No generation mechanism exists yet, and inventing
  one is a real piece of tooling.

**Unresolved.** Both positions are right about something. The drift risk is real
and the rule genuinely says what Copilot says it says; equally, no one has
proposed a way to write a readable narrative report without numbers in it.

**Risk to the roadmap.** **Medium — the highest in this register.** These
documents are the draft material for the eventual paper. A figure that drifts
from its artifact and is carried into a publication is the exact failure the
whole claim-ledger apparatus exists to prevent, and it would be found by a
referee rather than by us.

**Candidate resolutions:** a checker that re-reads each quoted figure from the
artifact and fails on mismatch (cheap, catches drift without changing how the
prose is written); or a transclusion step at build time (heavier, and makes the
sources unreadable in isolation).

**Mitigation in place — Phase 2 documents only.** Phase 2 built the first of
those two candidates. `tests/test_figure_tags.py` resolves every
`<literal> {fig:key}` tag in `docs/phase2.md` and
`docs/phases/phase2_bounds.md` against `data/phase2_figures.json`, renders the
stored value at its recorded precision, and requires an exact string match; a
bare `{fig:key}` with no literal in front of it fails too, so the tag cannot
be used to dodge the comparison. `data/phase2_figures.json` is tracked while
the rest of `data/` is gitignored, precisely so the artifact a fresh clone
checks against is the one the prose was written from. For those two documents
the hand-copied number and the artifact can no longer drift apart silently.
`docs/phase2.md` refers to this entry as handled; that reference is accurate
for Phase 2 and for Phase 2 only.

**Mitigation in place — Phase 1 documents.** The census and the headline
figures pulled out of the two tables (specific place-jump ratios, the block
count, the flat-step extremes, and others) are tagged the same way as Phase
2: `data/phase1_figures.json` is tracked, and `tests/test_figure_tags.py`
resolves every `<literal> {fig:key}` tag in `docs/phase1.md` and
`docs/phases/phase1_report.md` against it. That mechanism does not, by
itself, reach the place-jump and block-extrema tables themselves — tagging
every cell of a 28-row and a 29-row table would mean on the order of a
hundred more keys, for tables that exist so a reader does not have to go
spelunking in `data/phase1_summary.json`. Those two tables are instead
covered by `tests/test_phase1_tables.py`, which locates each table in
`docs/phases/phase1_report.md` by an `<!-- table:... -->` anchor, parses
every row, and compares every cell against `data/phase1_summary.json`'s
`place_jumps` and `block_extrema` arrays directly — no tag required, and
nothing in either table can drift from the artifact unnoticed. Between the
two mechanisms, all three things this entry names (the census, the
place-jump table, the block-extrema table) are now checked; the remaining
untagged residue (the `flat_step_positions` list, mathematical constants,
structural numbers, literature values, **wall-clock timings and the
peak-memory figure**) is stated explicitly in `docs/phase1.md`'s own residue
note rather than left for a reader to discover.

`docs/roadmap.md` is registered as a third Phase 1 document. It quoted the
census fraction three times with no tag — a narrative document containing
hand-copied numbers, which is the literal title of this entry. Two of the
three now carry `{fig:decreasing-fraction}`; the third was German prose using
a decimal comma (`49,6 %`). The tag regex *does* match a comma literal placed
directly in front of a tag — confirmed by running `TAG.search` on the
roadmap's original wording, which had that literal immediately followed by
the decreasing-fraction tag: the match captures `49,6`, and
`_check_documents` then strips the comma (`literal.replace(",", "")`) to
compare it as `496` against the figures file's `49.6`, so a tagged `49,6`
would have been matched and rejected as drift, not ignored. It cannot be
accommodated without making `49,6` ambiguous against the
thousands-separator handling built into `[\d][\d,]*`, which is why it was
rewritten to state the finding in words ("knapp die Hälfte der Schritte
fällt") instead of tagging it, so that it no longer carries a number to
drift.

**What is bound, and what is not.** Bound: every `<literal> {fig:key}` tag in
`docs/phase1.md`, `docs/phases/phase1_report.md`, `docs/roadmap.md`,
`docs/phase2.md` and `docs/phases/phase2_bounds.md`; every cell of the two
Phase 1 tables; and every key in either figures file, which must be quoted in
some registered document or listed in `KEYS_KNOWINGLY_UNQUOTED` with a reason.
Registration itself is enforced: `test_every_tagged_document_is_registered`
walks `docs/`, `theory/`, `paper/`, `README.md` and `CLAUDE.md` (`.md` and
`.tex`), except for `docs/superpowers/`, a deliberate carve-out for dated
historical specs and plans (`UNREGISTERED_DOC_PREFIXES` in
`tests/test_figure_tags.py`), and fails on any other document that carries a
literal-backed tag without a `PHASES` row.

Not bound, and stated plainly because no mechanism covers it: **a number that
is generated but never tagged.** The discovery test triggers on
`TAG.search(text)`, so a document that quotes a generated figure as a bare
literal — which is what `docs/roadmap.md`'s `49.6` was until this branch — is
invisible to it, and to everything else here. Detecting that means recognising
a generated value in arbitrary prose without a marker; it is genuinely hard,
no such detector exists in this repository, and none is planned. A reviewer
reading a document against its figures file remains the only thing that
catches it. Two further gaps are narrower: `paper/` is walked but contains no
tagged prose yet (`paper/main.tex` is a stub), so that coverage is untested
against real content; and a document quoting *another* phase's figure cannot
be tagged at all, because `PHASES` binds one document to one figures file
(`docs/phases/phase1_report.md` quoting Phase 2's `upper-constant`,
`docs/phase2.md` quoting Phase 1's `decreasing-fraction`). This file is in the
same position: it quotes `49.6%` in R-005 and cannot be registered, because
its prose spells out the bare `{fig:key}` syntax while describing the
mechanism, which the bare-tag check rejects by design.

**Revisit when:** Phase 4 regenerates data at a different `n_max`, which is
the first moment drift can actually occur for the bound documents; or when a
generated-but-untagged number is next found by a reader rather than by a
guard — that is the residual named above, and the signal that it has started
costing something; or when `paper/` acquires real prose, at which point the
walk over it stops being untested coverage.

---

## R-003 — The cross-check cannot detect a wrong place set

**Status:** mitigated · **Raised by:** Codex and Copilot independently · **Phase:** 1

**Description.** Reported values are licensed by `capfib.dp` and `capfib.gf`
agreeing on every coefficient. Both — and `brute` — obtain their place values
from `capfib.fib.places_up_to`. An error in the shared place set is invisible to
the comparison by construction.

**Positions.**

- *Copilot:* the production boundary test pins only the number of places, the
  largest place, and the first excluded value. A corrupted interior value — 13
  replaced by 14 — satisfies all three while both algorithms consume it
  identically. The claimed conditional independence is therefore not
  established.
- *Project:* the limitation was disclosed in both the spec and the report rather
  than hidden. Copilot's point was accepted rather than argued with, and the
  test it asked for was written.

**Mitigation in place.** `tests/test_fib.py:28-58` hard-codes the complete
expected place list through `10^6` — all 30 values, written out from the
recurrence rather than obtained by calling `places_up_to`, so it cannot pass by
construction — asserts equality against `places_up_to(1_000_000)`, and
additionally checks that the hard-coded list itself satisfies
`F_k = F_{k-1} + F_{k-2}`. The interior corruption Copilot described (13
replaced by 14) fails that equality. Disclosure and the convention/boundary
tests remain alongside it.

**Residual gap.** None identified in the place set itself. What the test cannot
cover is the *convention* being wrong in a way both the test and the code agree
on — the duplicated `F_1 = F_2 = 1` — which is pinned separately by
`test_sum_of_squares_identity`, an identity that fails under any other
convention.

**Risk to the roadmap.** Low, since the mitigation landed. It was Medium while
open: every numerical claim in Phase 1, and every later phase built on that
data, rests on the place set being right, and a silent corruption would have
invalidated the data without failing a single test.

**Revisit when:** the place set is ever generated by a route other than
`capfib.fib.places_up_to`, or the production `n_max` moves above `10^6` — the
pinned list stops at the last place `<= 10^6` and would need extending.

---

## R-004 — Lean proof references are validated by grepping text

**Status:** accepted — trigger fired in Phase 2, risk remains dormant · **Raised by:** Codex, 2026-08-20 · **Phase:** 1

**Description.** `scripts/check_claims.py` requires a `theorem` claim's evidence
to cite a proof location. For repository paths it now checks the file exists.
For Lean declarations it greps `lean/*.lean` for `theorem|lemma|def <name>`,
matching only the final namespace segment and not excluding comments or strings.

**Positions.**

- *Codex:* a commented-out declaration, a wrong-namespace declaration, or a
  stale unbuilt file would validate. The check gives a false sense of
  enforcement.
- *Project:* correct, and dormant — no claim uses that route today. Doing it
  properly means asking Lean rather than reading text, which deserves its own
  design. The limitation is documented in a comment beside the code.

**Risk to the roadmap.** Low while dormant, high the moment it is used. If a
Lean-backed claim ever enters the ledger, a `theorem` could be certified by a
declaration that does not compile — in a project whose thesis is the separation
of proved from believed.

**Trigger fired in Phase 2 — and the risk is still dormant.** Three `theorem`
claims now name a Lean declaration in their evidence:
`completeness-no-gaps`, `leading-constant` and `sandwich-bounds`, all citing
`exists_numeral_of_le`. By the revisit condition below that is blocking. It
was traced through `_theorem_evidence_problem` instead, and the grep route is
not what validates any of the three: each evidence string *also* contains a
real repository path (`theory/01-background.md`,
`docs/phases/phase2_bounds.md`), the path-token branch runs first and returns
on it, and the Lean-declaration branch is never reached. Confirmed by
deleting `docs/phases` from `THEOREM_PATH_TOKEN_RE`: `saddle-tightness`,
whose evidence names only a `docs/phases/` path, then fails, but
`leading-constant` and `sandwich-bounds` keep validating anyway — not
through the Lean grep, but because each evidence string *also* contains a
`lean/` path token (`lean/NonLinearNumberSystems/Completeness.lean`) that
survives the deletion, and `_theorem_evidence_problem` returns from the
path-token branch on that token (`scripts/check_claims.py:236`), which
checks only that the path resolves to an existing file, never that the file
contains the declaration the claim cites. The Lean-declaration branch is
never reached, before or after the mutation. It could not have validated
either claim regardless: `LEAN_DECL_RE` requires a capitalised dotted
identifier, so from that same evidence string it extracts only the filename
`Completeness.lean`, and `_lean_declaration_exists(root, "Completeness.lean")`
returns `False`. So the surviving validation is by a path token naming a
Lean file whose contents are never inspected — a file that, read, proves a
smaller, different statement than the claims cite it for. That is the
failure this entry describes, arriving as a *silent pass* rather than a
false certification, and it is now pinned by
`test_theorem_citing_docs_phases_path_is_accepted` in
`tests/test_check_claims.py`, whose fixture names only a `docs/phases/` path
and so goes red if that root is dropped.

So the trigger has fired and the entry does **not** close. What changed is
only the reason it is dormant: previously no claim cited a Lean declaration at
all; now three do, and they are saved by carrying a checkable path alongside.
Remove the path from any of those three evidence strings and the grep becomes
load-bearing that same moment.

**Revisit when:** any claim's evidence cites a Lean declaration *without* also
citing an existing path under `theory/`, `paper/`, `lean/` or `docs/phases/` —
at which point the grep is the only thing standing behind a `theorem`, and
that should be treated as blocking until this is closed.

---

## R-005 — Finite observations keep being restated as universal ones

**Status:** mitigated · **Raised by:** Codex and Copilot · **Phase:** 1

**Description.** The Phase 1 finding — 49.6% of steps decrease over `N ≤ 10^6`
— was written four separate times as a universal claim ("the direct attack is
unavailable", "any Tauberian attack must", "jeder Tauber-Angriff muss"). Each
was corrected; a fourth instance was found in the roadmap after the first three
were fixed.

**Positions.**

- *Reviewers:* a finite census cannot establish that a method fails for all `N`.
  Every such sentence is an overstatement.
- *Project:* agreed on the substance in every instance. The dispute is not about
  whether the wording is wrong — it is about whether case-by-case correction can
  keep up with a pattern that has now recurred four times across three
  documents and one docstring.

**Risk to the roadmap.** Medium. The project's credibility rests on never
overstating; a single surviving "must" in a published paper does more damage
than the finding is worth. Recurrence at this rate suggests prose review alone
is not sufficient.

**Candidate resolution:** extend `scripts/check_claims.py` to flag universal
quantifiers ("any", "every", "must", "unavailable", "jeder", "muss") in a
paragraph citing a `verified-numeric` claim. Cheap, imperfect, and would have
caught all four.

**Outcome — the check exists and Phase 2 ran clean, within its reach.** The
candidate resolution was implemented: `_check_universal_claims` in
`scripts/check_claims.py` flags an unqualified universal word in any citation
scope that cites a `verified-numeric` claim, unless that sentence carries an
explicit range qualification. It ran across the repository throughout Phase 2
and reported no surviving overclaim, and Phase 2's own prose was written under
it. That is what the revisit condition asked for, so the entry moves from open
to mitigated.

It does not close, because "ran clean" means clean *within its scope*, and the
scope is narrow in two ways that this branch demonstrated rather than
hypothesised. First, the check only reads Markdown, and only under `theory/`,
`docs/phases/`, `paper/` and five named files — a fourth stale epistemic
statement was found in this branch in a Python docstring
(`capfib/stats.py`, asserting completeness was still a `sorry` after it had
been proved), which the check structurally cannot see. That specific gap is
now covered by `tests/test_epistemic_staleness.py`, a phrase grep over
`capfib/`, `scripts/` and `.claude/skills/`; it caught a second instance in
`scripts/run_lean.sh` on its first run. Second, both guards are pattern
matchers: they catch the recurring *shapes* ("every … {claim:…}", "still a
`sorry`"), not the proposition. A paragraph that overstates a finite census in
words neither guard enumerates still passes, and a reviewer remains the
backstop.

**Revisit when:** a stale or overstated epistemic statement is next found by a
human reviewer rather than by either guard. That is the signal that the
patterns have stopped keeping up with the prose, and the point to ask again
whether pattern matching is the right instrument.

---

## R-006 — Artifacts and manifest can record different generations

**Status:** accepted · **Raised by:** Codex and Copilot · **Phase:** 1

**Description.** `scripts/run_phase1.py` writes each artifact atomically, then
records each in the manifest one at a time. A failure between the first artifact
replacement and the last manifest write leaves a new CSV alongside an old
summary, or fresh files with stale hashes.

**Positions.**

- *Reviewers:* stage all four artifacts, validate, then publish and update the
  manifest once. As it stands, a claim check can bless a mixed generation.
- *Project:* the window is a partial failure of a script run manually, minutes
  long, on one machine, whose output is regenerable in about five minutes. The
  spec was corrected to describe per-file atomicity accurately rather than
  claiming all-or-nothing.

**Risk to the roadmap.** Low. This entry originally claimed `check_claims.py`
would catch a mixed generation "via a hash mismatch"; for a long time that was
false, and the entry was corrected to say so. It is now true, by a different
route than the entry first imagined.

`check_claims.py` used to test only that the artifact *basename* named in a
`verified-numeric` claim's evidence appeared in `data/manifest.json`. That is
membership in an index, not evidence: an external review found ten claims
citing four artifacts that were never tracked, so on a clean clone the
validator printed `claims.yaml OK` while every cited artifact was absent. The
validator now requires each cited artifact to **exist** and to match the
SHA-256 `data/manifest.json` recorded for it, and the four cited artifacts are
tracked (24 KB in total). A file whose contents have moved on from its recorded
hash now fails by name, and so does one that is missing.

The cost of a mixed generation therefore surfaces immediately rather than
through a bound check failing or a `{fig:}` literal drifting, and remains a
regeneration of about five minutes rather than a wrong published number.

**Revisit when:** `scripts/run_phase1.py` is next modified, or when a claim
first depends on more than one artifact from the same run — that is the point
at which a mixed generation stops being merely confusing.

---

## How to add an entry

An entry belongs here when a review dispute has run its course and no further
round will settle it. Record the ID, the description, both positions stated
fairly, the cost to the roadmap objective if the project's position is wrong,
and what should trigger a revisit. Do not use this file to park defects — a
defect that everyone agrees is a defect gets fixed or tracked as an issue.

---

## R-007 — The required-check inventory reports Plan B's absence but cannot compel it

**Status:** accepted · **Raised by:** Codex, 2026-08-24 · **Phase:** 2/3 boundary

**Description.** The defect-prevention spec ships in two plans: Plan A, the
non-mutation CI foundation, and Plan B, the mutation registry. Acceptance
criterion 8 requires the full mutation tier's status check to be *required for
merge*, which Plan A cannot satisfy — the tier does not exist, and GitHub will
not accept a context as required until it has been reported at least once.

§9.3's tracked inventory names every context that must be required, including
the full tier's. After Plan A the verifier therefore fails on every run, naming
the missing tier. That is a standing red, not a block.

**Positions.**

- *Codex:* a non-blocking signal does not reduce the probability of Plan B never
  shipping. The remedy is to configure a deliberately failing placeholder under
  the final full-tier context and mark it required, so every pull request is
  blocked until Plan B replaces it. Only that is a delivery mitigation; the rest
  is observability.
- *Project:* correct on the mechanics, and the trade is still refused. Blocking
  every merge on a single-maintainer repository would halt Phase 3 and Phase 4
  research for as long as Plan B takes, to protect against a maintainer ignoring
  a red check they see on every run. The standing red is chosen deliberately
  over a stopped repository, and §3.6's own warning — that the cheap tier
  becomes the only tier that ships — is acknowledged as applying here.

**Risk to the roadmap.** Moderate, and it is a process risk rather than a
mathematical one. If Plan B never ships, acceptance criteria 1–8 stay open, the
mutation discipline that motivated the whole spec never exists, and the guards
added in Phases 1 and 2 keep the property that made them worth writing down:
none has been seen to fail. The mathematics is unaffected — no claim, proof or
artifact depends on the registry — but the defect classes it was written to
close stay open, and the evidence of Phases 1 and 2 is that they recur.

**What would close it.** Plan B shipping. Failing that, a decision to accept the
classes as open, recorded here rather than left implicit.

## R-008 — Waivers are self-authorised

**Status:** accepted · **Raised by:** Codex, 2026-08-24 · **Phase:** 2/3 boundary

**Description.** §3.7's tamper-evidence rests on a coordinated weakening having
to move the registry fingerprint and produce a waiver a reviewer reads. On a
single-maintainer repository the author writes the production change, the test,
the mutation, the fingerprint and the waiver, and no independent party reads any
of it.

**Positions.**

- *Codex:* GitHub forbids an author approving their own pull request, so
  required reviews or path-scoped CODEOWNERS over the registry, waiver, checker
  and workflow paths would be genuinely enforceable. An earlier draft of the
  spec called this control impossible here; that was false, and rejecting it
  discards achievable independent authorisation.
- *Project:* the finding is accepted — the obstacle is that no second
  write-authorised reviewer exists on this project, which is a staffing decision
  the spec cannot make. §9.2 now names the object a *waiver explanation*: it
  forces a weakening to be written down and to appear in a diff, and it
  authenticates nothing.

**Risk to the roadmap.** Low for the mathematics, real for the guard system. The
registry remains tamper-*evident* to a reader who looks, and offers no
resistance to an author who does not want to be caught. Since the author here is
also the person the guards exist to help, the practical exposure is a lapse of
attention rather than an adversary.

**What would close it.** Adding a second write-authorised reviewer and
path-scoped CODEOWNERS over the registry, waiver, checker and workflow paths.
