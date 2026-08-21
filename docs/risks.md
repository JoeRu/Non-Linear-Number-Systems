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

**Status:** open · **Raised by:** Copilot, 2026-08-21 · **Phase:** 1

**Description.** `docs/phase1.md` and `docs/phases/phase1_report.md` embed the
census, the place-jump table and the block-extrema table as literal Markdown.
`data/` is gitignored, so regenerating the artifacts does not update these
pages; they can silently drift from the citable summary.

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

**Revisit when:** Phase 4 regenerates data at a different `n_max`, which is the
first moment drift can actually occur.

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
- *Project:* the limitation is disclosed in both the spec and the report rather
  than hidden, and `tests/test_fib.py` pins the convention and the boundary
  cases separately. The residual gap is an interior corruption of the Fibonacci
  sequence itself.

**Mitigation in place.** Disclosure, plus convention and boundary tests.
**Mitigation missing.** No test asserts the complete expected place list.

**Risk to the roadmap.** Medium. Every numerical claim in Phase 1, and every
later phase that builds on this data, rests on the place set being right. A
silent corruption would invalidate the data without failing a single test.
Cheap to close: assert the full list at the production boundary.

**Revisit when:** immediately — this is the one entry here with an obvious fix,
and the argument documented in the spec depends on it.

---

## R-004 — Lean proof references are validated by grepping text

**Status:** accepted · **Raised by:** Codex, 2026-08-20 · **Phase:** 1

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

**Revisit when:** any claim's evidence first cites a Lean declaration. That
event should be treated as blocking until this is closed.

---

## R-005 — Finite observations keep being restated as universal ones

**Status:** open · **Raised by:** Codex and Copilot · **Phase:** 1

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

**Revisit when:** the check above is implemented and has run clean across the
repository for a full phase. Until then this stays open — a guard that has not
yet survived a phase of real writing has not been shown to work.

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

**Risk to the roadmap.** Low. A mixed generation would most likely be caught by
the next `check_claims.py` run via a hash mismatch. Its cost is a confusing
debugging session, not a wrong published number.

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
