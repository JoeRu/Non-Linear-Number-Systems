#!/usr/bin/env python3
"""Phase 0.5 -- measure the leading constant before developing the heuristic.

Candidates:
    1 / (2 log phi) = 1.03904   (no cap effect; Coons-Kristensen-Laursen)
    1 / (4 log phi) = 0.51952   (roadmap Phase 3 conjecture)
    1 / (8 log phi) = 0.25976   (naive count; a lower bound only)

The estimator is the local slope d(log R)/d((log N)^2), which converges far
faster than the plain ratio log R / (log N)^2.
"""

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from capfib.manifest import record  # noqa: E402
from capfib.saddle import log_R_bound  # noqa: E402

PHI = (1 + 5 ** 0.5) / 2
LOG_PHI = math.log(PHI)
EXPONENTS = [50, 100, 200, 400, 800, 1600, 3200]
DATA = Path("data/phase0_5_gate.csv")
FIGURE = Path("figures/phase0_5_gate.png")


def main() -> None:
    rows = []
    prev = None
    for e in EXPONENTS:
        log_n = e * math.log(10)
        value = log_R_bound(log_n)
        sq = log_n * log_n
        slope = "" if prev is None else (value - prev[0]) / (sq - prev[1])
        rows.append({
            "log10_N": e,
            "log_R_bound": value,
            "ratio": value / sq,
            "local_slope": slope,
        })
        prev = (value, sq)
        print(f"1e{e:<6} log R = {value:16.2f}  ratio = {value / sq:.6f}  slope = {slope}")

    DATA.parent.mkdir(parents=True, exist_ok=True)
    with DATA.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    slopes = [(r["log10_N"], r["local_slope"]) for r in rows if r["local_slope"] != ""]
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot([x for x, _ in slopes], [y for _, y in slopes], "o-", label="local slope")
    for c, lab in ((2, "1/(2 log phi)"), (4, "1/(4 log phi)"), (8, "1/(8 log phi)")):
        ax.axhline(1 / (c * LOG_PHI), ls="--", lw=1, label=lab)
    ax.set_xscale("log")
    ax.set_xlabel("log10 N")
    ax.set_ylabel("d(log R) / d((log N)^2)")
    ax.set_title("Phase 0.5: leading constant of log R_c(N)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=150)

    final = slopes[-1][1]
    print(f"\nfinal local slope: {final:.6f}")
    print(f"1/(4 log phi):     {1 / (4 * LOG_PHI):.6f}")
    print(f"absolute error:    {abs(final - 1 / (4 * LOG_PHI)):.6f}")

    record(DATA, script="scripts/run_phase0_gate.py",
           params={"exponents": EXPONENTS})
    record(FIGURE, script="scripts/run_phase0_gate.py",
           params={"exponents": EXPONENTS})


if __name__ == "__main__":
    main()
