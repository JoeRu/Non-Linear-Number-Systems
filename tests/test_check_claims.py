import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from check_claims import validate  # noqa: E402

VALID = """- id: alpha
  statement: "A."
  status: theorem
  evidence: "theory/x.md, a short proof"
  source: "s"
"""


def _write(root, claims, docs=None):
    (root / "theory").mkdir(parents=True, exist_ok=True)
    (root / "theory" / "claims.yaml").write_text(claims)
    for name, text in (docs or {}).items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)


def test_valid_ledger_passes(tmp_path):
    _write(tmp_path, VALID, {"theory/x.md": "See {claim:alpha}."})
    assert validate(tmp_path) == []


def test_unknown_reference_is_reported(tmp_path):
    _write(tmp_path, VALID, {"theory/x.md": "See {claim:missing}."})
    problems = validate(tmp_path)
    assert any("missing" in p for p in problems)


def test_bad_status_is_reported(tmp_path):
    _write(tmp_path, VALID.replace("theorem", "probably-true"))
    assert any("probably-true" in p for p in validate(tmp_path))


def test_duplicate_id_is_reported(tmp_path):
    _write(tmp_path, VALID + VALID)
    assert any("duplicate" in p.lower() for p in validate(tmp_path))


def test_missing_field_is_reported(tmp_path):
    _write(tmp_path, '- id: alpha\n  statement: "A."\n  status: theorem\n')
    assert any("evidence" in p or "source" in p for p in validate(tmp_path))


def test_verified_numeric_needs_manifest(tmp_path):
    claims = (
        '- id: alpha\n  statement: "A."\n  status: verified-numeric\n'
        '  evidence: "data/results.csv"\n  source: "s"\n'
    )
    _write(tmp_path, claims)
    assert any("manifest" in p for p in validate(tmp_path))


def test_verified_numeric_rejects_substring_match(tmp_path):
    # A manifest holding "R.csv" must not be satisfied by evidence that merely
    # contains "R.csv" as a substring of a longer, unrecorded filename.
    claims = (
        '- id: alpha\n  statement: "A."\n  status: verified-numeric\n'
        '  evidence: "verified in NOTES.R.csv-draft (never recorded)"\n'
        '  source: "s"\n'
    )
    manifest = json.dumps([{"file": "R.csv"}])
    _write(tmp_path, claims, {"data/manifest.json": manifest})
    assert any("manifest" in p for p in validate(tmp_path))


CONJECTURE = """- id: beta
  statement: "B."
  status: conjecture
  evidence: "e"
  source: "s"
"""


def test_hedged_conjecture_citation_passes(tmp_path):
    docs = {"theory/x.md": "This is expected but not established {claim:beta}."}
    _write(tmp_path, CONJECTURE, docs)
    assert validate(tmp_path) == []


def test_unhedged_conjecture_citation_is_reported(tmp_path):
    docs = {"theory/x.md": "This is true {claim:beta}."}
    _write(tmp_path, CONJECTURE, docs)
    problems = validate(tmp_path)
    assert any("beta" in p and "hedge" in p for p in problems)


def test_theorem_with_bare_prose_evidence_is_rejected(tmp_path):
    # A theorem needs a checkable proof location, not just prose asserting
    # one exists -- this is exactly the gap that let `theorem` bypass all
    # evidence checking.
    claims = (
        '- id: gamma\n  statement: "G."\n  status: theorem\n'
        '  evidence: "Immediate from the definitions; corroborated in '
        'tests/test_gamma.py."\n  source: "s"\n'
    )
    _write(tmp_path, claims)
    problems = validate(tmp_path)
    assert any("gamma" in p and "theorem" in p for p in problems)


def test_theorem_citing_theory_path_is_accepted(tmp_path):
    # The referenced file must actually exist -- shape alone (matching
    # "theory/...") is not enough, so the positive case has to create it.
    claims = (
        '- id: delta\n  statement: "D."\n  status: theorem\n'
        '  evidence: "Proved in theory/03-invariants.md (delta)."\n'
        '  source: "s"\n'
    )
    docs = {"theory/03-invariants.md": "## delta\n\nA short real proof.\n"}
    _write(tmp_path, claims, docs)
    assert validate(tmp_path) == []


def test_theorem_citing_nonexistent_path_is_rejected(tmp_path):
    # This is the case the shape-only check missed: a path that matches the
    # theory/paper/lean pattern but names a file that was never created.
    claims = (
        '- id: zeta\n  statement: "Z."\n  status: theorem\n'
        '  evidence: "Proved in theory/nonexistent.md (zeta)."\n'
        '  source: "s"\n'
    )
    _write(tmp_path, claims)
    problems = validate(tmp_path)
    assert any("zeta" in p and "does not exist" in p for p in problems)


def test_theorem_citing_lean_declaration_is_accepted(tmp_path):
    # The declaration must actually be found in a project .lean file, not
    # merely look like a namespaced Lean identifier.
    claims = (
        '- id: epsilon\n  statement: "E."\n  status: theorem\n'
        '  evidence: "See NonLinearNumberSystems.Fibonacci.sum_of_squares."\n'
        '  source: "s"\n'
    )
    docs = {
        "lean/NonLinearNumberSystems/Fibonacci.lean":
            "theorem sum_of_squares : True := trivial\n",
    }
    _write(tmp_path, claims, docs)
    assert validate(tmp_path) == []


def test_theorem_citing_unfound_lean_declaration_is_rejected(tmp_path):
    # A dotted identifier that looks like a Lean declaration but is not
    # actually declared anywhere under lean/ must not pass.
    claims = (
        '- id: eta\n  statement: "H."\n  status: theorem\n'
        '  evidence: "See NonLinearNumberSystems.Fibonacci.made_up_lemma."\n'
        '  source: "s"\n'
    )
    docs = {
        "lean/NonLinearNumberSystems/Fibonacci.lean":
            "theorem sum_of_squares : True := trivial\n",
    }
    _write(tmp_path, claims, docs)
    problems = validate(tmp_path)
    assert any("eta" in p and "theorem" in p for p in problems)


def test_theorem_citing_path_traversal_is_rejected(tmp_path):
    # "theory/../README.md" matches the theory/ prefix pattern and resolves
    # to an existing file, but it resolves outside theory/, paper/, and
    # lean/ -- the traversal must be caught, not just existence.
    (tmp_path / "README.md").write_text("root readme\n")
    claims = (
        '- id: theta\n  statement: "T."\n  status: theorem\n'
        '  evidence: "Proved in theory/../README.md (theta)."\n'
        '  source: "s"\n'
    )
    _write(tmp_path, claims)
    problems = validate(tmp_path)
    assert any("theta" in p and "outside" in p for p in problems)


def test_theorem_citing_symlinked_allowed_root_escaping_repo_is_rejected(tmp_path):
    # paper/ (an allowed root, NOT theory/) is itself a symlink pointing
    # outside the repository. theory/claims.yaml is written as a REAL file
    # directly under tmp_path -- deliberately not a symlink -- so the
    # ledger-path check in validate() (see
    # test_ledger_symlinked_outside_repo_is_rejected below) does not fire
    # here and this test actually exercises the allowed_roots filter in
    # _theorem_evidence_problem. If that filter were removed, "paper/evil.md"
    # would resolve (via the symlink) to a real file and this test would
    # pass incorrectly -- confirmed by temporarily removing the filter.
    outside = tmp_path.parent / f"{tmp_path.name}-outside-paper"
    outside.mkdir()
    (outside / "evil.md").write_text("not part of this repo\n")
    (tmp_path / "paper").symlink_to(outside, target_is_directory=True)

    claims = (
        '- id: iota\n  statement: "I."\n  status: theorem\n'
        '  evidence: "Proved in paper/evil.md (iota)."\n'
        '  source: "s"\n'
    )
    _write(tmp_path, claims)

    problems = validate(tmp_path)
    assert any("iota" in p and "outside" in p for p in problems)


def test_ledger_symlinked_outside_repo_is_rejected(tmp_path):
    # theory/ is a symlink pointing outside the repo, and the external ledger
    # cites evidence that genuinely exists INSIDE this repo (paper/proof.md).
    # Filtering allowed_roots in _theorem_evidence_problem does not stop this:
    # "paper/proof.md" resolves inside the repo, so that check alone would
    # accept it. The ledger's own path must be rejected before it is parsed
    # at all.
    outside = tmp_path.parent / f"{tmp_path.name}-outside-ledger"
    outside.mkdir()
    (outside / "claims.yaml").write_text(
        '- id: mu\n  statement: "M."\n  status: theorem\n'
        '  evidence: "Proved in paper/proof.md (mu)."\n'
        '  source: "s"\n'
    )
    (tmp_path / "theory").symlink_to(outside, target_is_directory=True)
    (tmp_path / "paper").mkdir()
    (tmp_path / "paper" / "proof.md").write_text("A real proof, genuinely in-repo.\n")

    problems = validate(tmp_path)
    assert any("outside" in p.lower() and "repo" in p.lower() for p in problems)
    assert not any("claim 'mu'" in p for p in problems), (
        "the ledger must be rejected before any claim in it is parsed"
    )


VERIFIED_NUMERIC = """- id: kappa
  statement: "K."
  status: verified-numeric
  evidence: "data/results.csv"
  source: "s"
"""


def test_unqualified_universal_word_citing_verified_numeric_is_rejected(tmp_path):
    # "every" attached to a verified-numeric claim, with no range
    # qualification anywhere in the paragraph -- this is the recurring
    # finite-measurement-restated-as-universal-claim pattern (docs/risks.md
    # R-005), which hedging alone does not catch because the claim's status
    # is verified-numeric, not conjecture/heuristic.
    docs = {
        "theory/x.md": "Every N satisfies this property {claim:kappa}.",
        "data/manifest.json": json.dumps([{"file": "results.csv"}]),
    }
    _write(tmp_path, VERIFIED_NUMERIC, docs)
    problems = validate(tmp_path)
    assert any("kappa" in p and "universal" in p for p in problems)


def test_range_qualified_universal_word_citing_verified_numeric_passes(tmp_path):
    # The same "every" is fine once the paragraph states the range it was
    # actually measured over.
    docs = {
        "theory/x.md": "Every N <= 1000 satisfies this property {claim:kappa}.",
        "data/manifest.json": json.dumps([{"file": "results.csv"}]),
    }
    _write(tmp_path, VERIFIED_NUMERIC, docs)
    assert validate(tmp_path) == []


def test_unobserved_is_not_a_false_exemption(tmp_path):
    # "the result was unobserved" contains "observed" as a raw substring, but
    # is not the whole word "observed" -- a bare substring test wrongly
    # exempted it before. Same sentence as the universal, so this isolates
    # the marker-matching bug from the paragraph-vs-sentence scoping bug.
    docs = {
        "theory/x.md": (
            "Every N satisfies this property; the result was unobserved "
            "{claim:kappa}."
        ),
        "data/manifest.json": json.dumps([{"file": "results.csv"}]),
    }
    _write(tmp_path, VERIFIED_NUMERIC, docs)
    problems = validate(tmp_path)
    assert any("kappa" in p and "universal" in p for p in problems)


def test_unrelated_lte_is_not_a_false_exemption(tmp_path):
    # "a condition <= 1000 applies" contains the raw substring "n <=" (the
    # tail of "conditio-n" plus " <="), which wrongly exempted it before.
    docs = {
        "theory/x.md": (
            "Every N satisfies this property; a condition <= 1000 applies "
            "{claim:kappa}."
        ),
        "data/manifest.json": json.dumps([{"file": "results.csv"}]),
    }
    _write(tmp_path, VERIFIED_NUMERIC, docs)
    problems = validate(tmp_path)
    assert any("kappa" in p and "universal" in p for p in problems)


def test_range_marker_in_different_sentence_does_not_exempt(tmp_path):
    # Sentence one carries the bare universal and the citation; sentence two
    # carries an unrelated range marker. The exemption must not leak across
    # sentence boundaries within the same paragraph.
    docs = {
        "theory/x.md": (
            "Every N satisfies this property {claim:kappa}. "
            "A different measurement used n <= 500 elsewhere."
        ),
        "data/manifest.json": json.dumps([{"file": "results.csv"}]),
    }
    _write(tmp_path, VERIFIED_NUMERIC, docs)
    problems = validate(tmp_path)
    assert any("kappa" in p and "universal" in p for p in problems)


def test_jedes_is_recognized_as_universal(tmp_path):
    # docs/roadmap.md already contains "jedes N" -- the inflected form was
    # missing from UNIVERSAL_QUANTIFIER_WORDS even though "jeder"/"jede" were
    # both listed.
    docs = {
        "theory/x.md": "Jedes N erfüllt diese Eigenschaft {claim:kappa}.",
        "data/manifest.json": json.dumps([{"file": "results.csv"}]),
    }
    _write(tmp_path, VERIFIED_NUMERIC, docs)
    problems = validate(tmp_path)
    assert any("kappa" in p and "universal" in p for p in problems)


def test_alles_is_recognized_as_universal(tmp_path):
    docs = {
        "theory/x.md": "Alles daran bestätigt sich {claim:kappa}.",
        "data/manifest.json": json.dumps([{"file": "results.csv"}]),
    }
    _write(tmp_path, VERIFIED_NUMERIC, docs)
    problems = validate(tmp_path)
    assert any("kappa" in p and "universal" in p for p in problems)


def test_docs_phase1_is_scanned_via_search_files(tmp_path):
    # docs/phase1.md is reachable only via SEARCH_FILES, not SEARCH_DIRS
    # (theory/, docs/phases/, paper/). A fixture placed only under theory/
    # would pass even if "docs/phase1.md" were silently dropped from
    # SEARCH_FILES; this fixture lives at that exact root-level path, so
    # removing the entry would make this test fail.
    _write(tmp_path, VALID, {"docs/phase1.md": "See {claim:missing}."})
    problems = validate(tmp_path)
    assert any("missing" in p for p in problems)


def test_bare_observed_qualification_is_rejected(tmp_path):
    # "observed" and "gemessen" no longer count as range qualifiers on their
    # own -- neither names a finite bound, so a sentence carrying a universal
    # claim and the bare word "observed" must still be rejected. This is
    # exactly the shape that let "`R_c` jumps at every Fibonacci place
    # observed" through before: the hedge word and the exemption word were
    # the same word.
    docs = {
        "theory/x.md": (
            "Every N satisfies this property; the result was observed "
            "{claim:kappa}."
        ),
        "data/manifest.json": json.dumps([{"file": "results.csv"}]),
    }
    _write(tmp_path, VERIFIED_NUMERIC, docs)
    problems = validate(tmp_path)
    assert any("kappa" in p and "universal" in p for p in problems)


def test_unrelated_single_letter_variable_does_not_exempt(tmp_path):
    # "a <= 1000" has the right shape (single letter, "<=", a number) but "a"
    # is not one of the variables this project bounds ranges by (N/n, F).
    # Restricting the regex to those variables must not accept this as a
    # qualifier for an unrelated universal claim.
    docs = {
        "theory/x.md": "Every N satisfies this property; a <= 1000 {claim:kappa}.",
        "data/manifest.json": json.dumps([{"file": "results.csv"}]),
    }
    _write(tmp_path, VERIFIED_NUMERIC, docs)
    problems = validate(tmp_path)
    assert any("kappa" in p and "universal" in p for p in problems)


def test_latex_le_range_expression_is_accepted(tmp_path):
    # These are mathematical documents that write bounds in LaTeX, e.g.
    # "$N \le 10^6$" -- not just ASCII "<=" or unicode "≤". That must be
    # recognized as a real range qualifier, not rejected as unscoped prose.
    docs = {
        "theory/x.md": r"Every $N \le 10^6$ satisfies this property {claim:kappa}.",
        "data/manifest.json": json.dumps([{"file": "results.csv"}]),
    }
    _write(tmp_path, VERIFIED_NUMERIC, docs)
    assert validate(tmp_path) == []


def test_jeden_is_recognized_as_universal(tmp_path):
    # docs/roadmap.md-style prose can use "jeden" (accusative) as well as
    # "jeder"/"jedes" -- another inflection that must trigger the guard.
    docs = {
        "theory/x.md": "Für jeden N gilt diese Eigenschaft {claim:kappa}.",
        "data/manifest.json": json.dumps([{"file": "results.csv"}]),
    }
    _write(tmp_path, VERIFIED_NUMERIC, docs)
    problems = validate(tmp_path)
    assert any("kappa" in p and "universal" in p for p in problems)


def test_each_is_recognized_as_universal(tmp_path):
    # "each" is a synonym for "every" that slipped through unnoticed --
    # docs/phases/phase1_report.md said "R_c jumps at each Fibonacci place",
    # an overclaim the guard could not see because "each" was not in
    # UNIVERSAL_QUANTIFIER_WORDS.
    docs = {
        "theory/x.md": "The result holds at each place {claim:kappa}.",
        "data/manifest.json": json.dumps([{"file": "results.csv"}]),
    }
    _write(tmp_path, VERIFIED_NUMERIC, docs)
    problems = validate(tmp_path)
    assert any("kappa" in p and "universal" in p for p in problems)


def test_muessen_is_recognized_as_universal(tmp_path):
    # Only the singular "muss" was listed; "müssen" (infinitive/plural, as
    # in "Die Werte müssen positiv sein") is just as common in this
    # project's German prose and must trigger the guard too.
    docs = {
        "theory/x.md": "Die Werte müssen positiv sein {claim:kappa}.",
        "data/manifest.json": json.dumps([{"file": "results.csv"}]),
    }
    _write(tmp_path, VERIFIED_NUMERIC, docs)
    problems = validate(tmp_path)
    assert any("kappa" in p and "universal" in p for p in problems)


def test_verified_numeric_requires_all_artifacts_recorded(tmp_path):
    # Naming one recorded artifact alongside one unrecorded artifact must not
    # be enough to pass -- every data-artifact token must be recorded.
    claims = (
        '- id: alpha\n  statement: "A."\n  status: verified-numeric\n'
        '  evidence: "data/unrecorded_run.csv (cf. phase0_5_gate.csv)"\n'
        '  source: "s"\n'
    )
    manifest = json.dumps([{"file": "phase0_5_gate.csv"}])
    _write(tmp_path, claims, {"data/manifest.json": manifest})
    assert any("manifest" in p for p in validate(tmp_path))
