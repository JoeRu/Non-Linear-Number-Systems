"""
lean_utils.py — Helpers for invoking Lean 4 / Lake from Python.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


LEAN_DIR = Path(__file__).parents[1] / "lean"


def run_lake_build(
    project_dir: Path = LEAN_DIR,
    *,
    verbose: bool = False,
) -> subprocess.CompletedProcess:
    """Run `lake build` in *project_dir*.

    Args:
        project_dir: Path to the Lake project root (containing lakefile.lean).
        verbose: If True, stream stdout/stderr to the terminal.

    Returns:
        The completed process result.

    Raises:
        subprocess.CalledProcessError: if `lake build` exits non-zero.
    """
    cmd = ["lake", "build"]
    result = subprocess.run(
        cmd,
        cwd=project_dir,
        capture_output=not verbose,
        text=True,
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, cmd,
            output=result.stdout,
            stderr=result.stderr,
        )
    return result


def check_lean_file(
    lean_file: Path,
    project_dir: Path = LEAN_DIR,
    *,
    verbose: bool = False,
) -> subprocess.CompletedProcess:
    """Type-check a single Lean file using `lake env lean`.

    Args:
        lean_file: Path to the `.lean` file (relative to *project_dir* or absolute).
        project_dir: Path to the Lake project root.
        verbose: If True, stream stdout/stderr to the terminal.

    Returns:
        The completed process result.
    """
    if lean_file.is_absolute():
        lean_file = lean_file.relative_to(project_dir)

    cmd = ["lake", "env", "lean", str(lean_file)]
    result = subprocess.run(
        cmd,
        cwd=project_dir,
        capture_output=not verbose,
        text=True,
    )
    return result
