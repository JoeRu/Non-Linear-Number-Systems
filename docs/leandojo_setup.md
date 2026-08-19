# LeanDojo Setup Guide

[LeanDojo](https://leandojo.org) is a Python library that provides a programmatic
interface to Lean 4, enabling automated theorem proving and proof-state extraction.

## Prerequisites

- Python ≥ 3.10
- Lean 4 installed (see `docs/lean_setup.md`)
- Git ≥ 2.25

## Installation

```bash
pip install lean-dojo
```

LeanDojo requires Docker on some platforms.  Check the
[official docs](https://leandojo.readthedocs.io) if you encounter issues.

## Tracing Proofs

The tracer extracts proof states, tactic steps, and premise information from
every theorem in the project:

```bash
python harnesses/lean_dojo/trace_proofs.py
# Output: harnesses/lean_dojo/traced_proofs.json
```

## Proof Search

The BFS proof searcher tries a set of candidate tactics at each goal:

```bash
python harnesses/lean_dojo/search_proofs.py \
    --theorem "NonLinearNumberSystems.fib_10_eq_55"
```

To integrate a neural tactic generator (e.g. ReProver), replace the
`CANDIDATE_TACTICS` list in `search_proofs.py` with a model call that takes
the current proof state as input and returns ranked tactic candidates.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `LEANDOJO_CACHE_DIR` | `~/.cache/lean_dojo` | Where traced repos are cached |
| `CONTAINER_TYPE` | `docker` | Container backend (`docker` or `native`) |

## References

- Yang et al., "LeanDojo: Theorem Proving with Retrieval-Augmented Language Models", NeurIPS 2023.
- ReProver: https://github.com/lean-dojo/ReProver
