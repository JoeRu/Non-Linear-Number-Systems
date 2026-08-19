#!/usr/bin/env python3
"""
LeanDojo — Proof Tracing
==========================
Uses LeanDojo to trace all theorems in the Non-Linear Number Systems Lean project,
extracting proof states, tactics, and premise information.

Usage:
    python trace_proofs.py [--repo-path PATH] [--output OUTPUT]

Prerequisites:
    pip install lean-dojo
    # Lean 4 and Lake must be installed and on PATH.
    # See docs/leandojo_setup.md for full instructions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


LEAN_REPO_PATH = Path(__file__).parents[2] / "lean"


def trace_repository(repo_path: Path, output_path: Path) -> None:
    """Trace all proofs in the Lean repository using LeanDojo.

    Args:
        repo_path: Path to the Lake project root (containing lakefile.lean).
        output_path: Where to write the traced data as JSON.
    """
    try:
        from lean_dojo import LeanGitRepo, trace  # type: ignore[import]
    except ImportError:
        raise RuntimeError(
            "lean-dojo is not installed.  Run: pip install lean-dojo"
        )

    print(f"Tracing repository at {repo_path} …")
    # LeanDojo works on Git repositories; we point it at the local clone.
    repo = LeanGitRepo(str(repo_path), "HEAD")
    traced = trace(repo)

    results: list[dict] = []
    for theorem in traced.get_theorems():
        results.append({
            "name": theorem.full_name,
            "file": str(theorem.file_path),
            "pos": {"line": theorem.start.line, "col": theorem.start.column},
            "proof_steps": [
                {"state_before": step.state_before,
                 "tactic": step.tactic,
                 "state_after": step.state_after}
                for step in theorem.proof_steps
            ],
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        json.dump(results, f, indent=2)

    print(f"Traced {len(results)} theorems → {output_path}")


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description="LeanDojo proof tracer")
    parser.add_argument(
        "--repo-path", type=Path, default=LEAN_REPO_PATH,
        help="Path to the Lake project root",
    )
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).parent / "traced_proofs.json",
        help="Output JSON file for traced proofs",
    )
    args = parser.parse_args()
    trace_repository(args.repo_path, args.output)


if __name__ == "__main__":
    main()
