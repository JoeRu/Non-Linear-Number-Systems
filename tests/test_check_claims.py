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
