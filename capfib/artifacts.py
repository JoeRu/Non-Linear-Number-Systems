"""Writing generated artifacts: atomic files, CSV text, the figures file.

Every phase runner publishes the same kinds of artifact -- a CSV, a JSON
summary, a PNG, the tracked figures file -- and records each one in the
manifest. The machinery for that lives here so the runners hold only their
phase's mathematics.

Every writer here is atomic: it stages into a temp file in the destination's
own directory and renames over the target, so a failure cannot leave a
partial artifact that later looks validated. Temp files carry mkstemp's
default "tmp" prefix; tests/test_run_phase2.py checks none survive.
"""

import csv
import io
import json
import os
import tempfile
from pathlib import Path

from capfib.manifest import DEFAULT_MANIFEST, record

FIGURE_FIELDS = ("value", "precision", "description")
"""Keys every entry of a `data/phase*_figures.json` file must carry.
tests/test_figure_tags.py formats `value` at `precision` and requires the
result to match the prose literal tagged `{fig:key}`."""


def atomic_write_text(path: Path, text: str) -> None:
    """Write text to `path` via a temporary file and an atomic rename.

    The parent directory is created if missing. The file is opened with
    `newline=""` so the text's line terminators are written verbatim: the
    csv module's CRLF rows must reach disk unchanged, because the manifest
    hashes the bytes.

    Args:
        path: destination file path.
        text: the full contents to write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def atomic_write_bytes(path: Path, payload: bytes) -> None:
    """Write bytes to `path` via a temporary file and an atomic rename.

    The temp file keeps `path`'s suffix at the end (rather than appending
    ".tmp" after it) so the published name and the staged name differ only in
    the random middle. The parent directory is created if missing.

    Args:
        path: destination file path.
        payload: the full contents to write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), suffix=path.suffix)
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        tmp.write_bytes(payload)
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def atomic_savefig(fig, path: Path, **kwargs) -> None:
    """Save a matplotlib figure via a temp file and an atomic rename.

    matplotlib infers the format from the filename, so the temp file keeps the
    target's suffix. A runner that must render before publishing anything
    should use `render_figure` and `atomic_write_bytes` instead.

    Args:
        fig: the matplotlib figure to save.
        path: destination file path. Its parent is created if missing.
        **kwargs: passed through to `fig.savefig` (e.g. `dpi`).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=path.suffix)
    os.close(fd)
    try:
        fig.savefig(tmp, **kwargs)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def render_figure(fig, **kwargs) -> bytes:
    """Render a figure to PNG bytes in memory, writing nothing to disk.

    Rendering is the step most likely to fail for reasons unrelated to the
    mathematics -- a missing backend, a font cache, a matplotlib upgrade -- so
    a runner can do it before any artifact is published and carry the result
    as bytes.

    Args:
        fig: the matplotlib figure to render.
        **kwargs: passed through to `fig.savefig` (e.g. `dpi`); the format is
            always PNG.

    Returns:
        The PNG encoding of the figure.
    """
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", **kwargs)
    return buffer.getvalue()


def csv_text(rows: list[dict], lineterminator: str = "\r\n") -> str:
    """Serialise rows to CSV text, with a header taken from the first row.

    Floats are written with `repr`, so they round-trip exactly. The default
    terminator is the csv module's RFC-4180 CRLF, which the tracked Phase 0
    and Phase 1 CSVs carry; Phase 2's are LF-terminated, and a runner keeps
    its own choice because the manifest hashes the bytes.

    Args:
        rows: one dict per row, all with the first row's keys in its order.
        lineterminator: the row terminator.

    Returns:
        The CSV text, ending with a terminator.

    Raises:
        ValueError: if `rows` is empty, since there is no header to write.
    """
    if not rows:
        raise ValueError("no rows: a CSV artifact needs at least a header row")
    sio = io.StringIO()
    writer = csv.DictWriter(sio, fieldnames=list(rows[0]), lineterminator=lineterminator)
    writer.writeheader()
    writer.writerows(rows)
    return sio.getvalue()


def figures_text(figures: dict[str, dict]) -> str:
    """Validate and serialise a phase's quotable-figures mapping.

    The figures file is what tests/test_figure_tags.py resolves `{fig:key}`
    tags against, so an entry without a value, an integer precision or a
    description cannot be quoted. Checking that here, before anything is
    written, keeps a malformed entry from ever reaching `data/`.

    Args:
        figures: maps each figure key to a dict with at least `value`,
            `precision` (int) and `description` (non-empty str).

    Returns:
        The JSON text: two-space indented, keys sorted, newline-terminated.

    Raises:
        ValueError: if `figures` is empty or any entry is malformed.
    """
    if not figures:
        raise ValueError("no figures: the figures file must not be empty")
    for key, entry in figures.items():
        missing = [f for f in FIGURE_FIELDS if f not in entry]
        if missing:
            raise ValueError(f"figure {key!r} is missing {missing}")
        # bool is an int subclass; a precision of True is a bug, not a 1.
        if not isinstance(entry["precision"], int) or isinstance(entry["precision"], bool):
            raise ValueError(f"figure {key!r} has a non-integer precision")
        if not isinstance(entry["description"], str) or not entry["description"].strip():
            raise ValueError(f"figure {key!r} has no description")
    return json.dumps(figures, indent=2, sort_keys=True) + "\n"


def publish(
    path: Path,
    payload: str | bytes,
    script: str,
    params: dict,
    manifest_path: str | Path = DEFAULT_MANIFEST,
) -> dict:
    """Atomically write one artifact, then record it in the manifest.

    The manifest entry follows its artifact, never precedes it, so the
    manifest cannot describe a file that is not there.

    Args:
        path: destination file path. Pass an absolute path: `record` hashes
            whatever `path` resolves to (see `capfib.manifest.record`).
        payload: the contents; `str` is written as text, `bytes` as binary.
        script: repo-relative path of the generating script.
        params: the parameters the generator ran with.
        manifest_path: where to upsert the entry. Absolute, for the same reason.

    Returns:
        The manifest entry that was written.
    """
    if isinstance(payload, bytes):
        atomic_write_bytes(path, payload)
    else:
        atomic_write_text(path, payload)
    return record(path, script=script, params=params, manifest_path=manifest_path)
