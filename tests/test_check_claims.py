import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from check_claims import validate  # noqa: E402

VALID = """- id: alpha
  statement: "A."
  status: theorem
  evidence: "e"
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
