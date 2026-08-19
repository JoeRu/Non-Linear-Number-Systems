import json

from capfib.manifest import entries, record


def test_record_captures_provenance(tmp_path):
    data = tmp_path / "out.csv"
    data.write_text("N,R\n1,2\n")
    mpath = tmp_path / "manifest.json"

    entry = record(data, script="scripts/demo.py", params={"n_max": 10},
                   manifest_path=mpath)

    assert entry["file"] == "out.csv"
    assert entry["script"] == "scripts/demo.py"
    assert entry["params"] == {"n_max": 10}
    assert len(entry["sha256"]) == 64
    assert entry["timestamp"].endswith("Z")
    assert "git_rev" in entry


def test_records_accumulate(tmp_path):
    mpath = tmp_path / "manifest.json"
    for i in range(3):
        f = tmp_path / f"f{i}.txt"
        f.write_text(str(i))
        record(f, script="s.py", params={"i": i}, manifest_path=mpath)
    assert len(entries(mpath)) == 3
    assert json.loads(mpath.read_text())[1]["params"] == {"i": 1}


def test_entries_missing_file(tmp_path):
    assert entries(tmp_path / "nope.json") == []


def test_record_upserts_same_file_and_script(tmp_path):
    mpath = tmp_path / "manifest.json"
    data = tmp_path / "out.csv"

    data.write_text("N,R\n1,2\n")
    first = record(data, script="scripts/demo.py", params={"n_max": 10},
                    manifest_path=mpath)

    data.write_text("N,R\n1,2\n2,3\n")
    second = record(data, script="scripts/demo.py", params={"n_max": 20},
                     manifest_path=mpath)

    recorded = entries(mpath)
    assert len(recorded) == 1
    assert recorded[0]["sha256"] == second["sha256"]
    assert recorded[0]["sha256"] != first["sha256"]
    assert recorded[0]["params"] == {"n_max": 20}
