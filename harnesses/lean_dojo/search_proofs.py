#!/usr/bin/env python3
"""
LeanDojo — Proof Search
=========================
Uses LeanDojo's tactic-level interaction to attempt automated proof search for
theorems in the Non-Linear Number Systems project.

Implements a simple best-first search (BFS) over the tactic space using a
set of candidate tactics.  For more sophisticated search, integrate ReProver
or another neural tactic generator.

Usage:
    python search_proofs.py --theorem NLNS_MATH_001
    python search_proofs.py --all-open --max-steps 50

Prerequisites:
    pip install lean-dojo
    # See docs/leandojo_setup.md for full instructions.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional


LEAN_REPO_PATH = Path(__file__).parents[2] / "lean"

# Ordered list of tactics to try at each proof step.
CANDIDATE_TACTICS: list[str] = [
    "rfl",
    "decide",
    "simp",
    "simp [*]",
    "omega",
    "ring",
    "norm_num",
    "linarith",
    "exact?",
    "apply?",
    "trivial",
    "tauto",
    "aesop",
]


def search_theorem(
    theorem_name: str,
    repo_path: Path,
    max_steps: int = 30,
    verbose: bool = True,
) -> Optional[list[str]]:
    """Attempt to find a proof for a theorem using BFS over candidate tactics.

    Args:
        theorem_name: The fully qualified Lean 4 theorem name.
        repo_path: Path to the Lake project root.
        max_steps: Maximum number of tactic steps before giving up.
        verbose: Whether to print intermediate proof states.

    Returns:
        A list of tactic strings that constitute a proof, or None if search failed.
    """
    try:
        from lean_dojo import LeanGitRepo, Dojo, ProofFinished, TacticError  # type: ignore
    except ImportError:
        raise RuntimeError(
            "lean-dojo is not installed.  Run: pip install lean-dojo"
        )

    repo = LeanGitRepo(str(repo_path), "HEAD")

    from collections import deque

    with Dojo(repo, theorem_name) as (dojo, init_state):
        if verbose:
            print(f"Initial state:\n{init_state}\n")

        # BFS: each node is (proof_so_far, current_state)
        queue: deque = deque()
        queue.append(([], init_state))

        visited_states: set[str] = {str(init_state)}

        while queue:
            proof_so_far, state = queue.popleft()

            if len(proof_so_far) >= max_steps:
                continue

            for tactic in CANDIDATE_TACTICS:
                result = dojo.run_tac(state, tactic)
                if isinstance(result, ProofFinished):
                    proof = proof_so_far + [tactic]
                    if verbose:
                        print(f"✓ Proof found: {' ; '.join(proof)}")
                    return proof
                elif not isinstance(result, TacticError):
                    new_state_str = str(result)
                    if new_state_str not in visited_states:
                        visited_states.add(new_state_str)
                        queue.append((proof_so_far + [tactic], result))

    if verbose:
        print(f"✗ No proof found for {theorem_name} within {max_steps} steps.")
    return None


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description="LeanDojo BFS proof search")
    parser.add_argument("--theorem", type=str, help="Fully qualified theorem name")
    parser.add_argument(
        "--repo-path", type=Path, default=LEAN_REPO_PATH,
        help="Path to the Lake project root",
    )
    parser.add_argument("--max-steps", type=int, default=30)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if not args.theorem:
        parser.error("--theorem is required")

    search_theorem(
        theorem_name=args.theorem,
        repo_path=args.repo_path,
        max_steps=args.max_steps,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
