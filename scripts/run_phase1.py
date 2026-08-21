#!/usr/bin/env python3
"""Phase 1 -- exact computation of R_c(N) and its structural analyses.

The cross-check is the point. `dp` and `gf` are structurally different
algorithms over the same place set; comparing every coefficient to n_max is
what licenses reporting values three orders of magnitude past the range the
standing gate covers. It costs ~5 minutes at 10^6 and is not optional.
"""

import argparse
import csv
import io
import json
import math
import os
import resource
import subprocess
import tempfile
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from capfib.dp import counts as dp_counts  # noqa: E402
from capfib.fib import places_up_to  # noqa: E402
from capfib.gf import coefficients  # noqa: E402
from capfib.manifest import record  # noqa: E402
from capfib.stats import (  # noqa: E402
    block_extrema,
    local_ratios,
    monotonicity_census,
    place_jumps,
    summatory,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_CSV = REPO_ROOT / "data" / "phase1_data.csv"
SUMMARY_JSON = REPO_ROOT / "data" / "phase1_summary.json"
FIG_GROWTH = REPO_ROOT / "figures" / "phase1_growth.png"
FIG_FLUCT = REPO_ROOT / "figures" / "phase1_fluctuation.png"
MANIFEST = REPO_ROOT / "data" / "manifest.json"


def git_rev() -> str:
    try:
        out = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def atomic_write_text(path: Path, text: str) -> None:
    """Write via a temp file and rename, so a failure cannot leave a partial
    artifact that later looks validated."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline="") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def atomic_savefig(fig, path: Path, **kwargs) -> None:
    """Save a figure via a temp file and rename, matching atomic_write_text.

    matplotlib infers the format from the filename, so the temp file keeps the
    target's suffix.
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


def ladder(n_max: int) -> list[int]:
    """Decades and half-decades from 100, plus every distinct place value."""
    pts = set()
    j = 4
    while True:
        n = round(10 ** (j / 2))
        if n > n_max:
            break
        pts.add(n)
        j += 1
    # Exclude place value 1: F_1 = F_2 = 1 is a degenerate duplicate place
    # (capfib.stats.place_jumps/block_extrema apply the same p >= 2 filter),
    # and log(1) = 0 would divide-by-zero in the log_N_sq ratio below.
    pts.update(p for p in set(places_up_to(n_max)) if 1 < p <= n_max)
    pts.add(n_max)
    return sorted(pts)


def _n_max_type(raw: str) -> int:
    """argparse type for --n-max: reject anything below 2.

    n_max=0 divides by zero in the decreasing-steps percentage; n_max in
    {0, 1} leaves local_ratios empty, so the quantile indexing raises;
    n_max=1 also divides by log(1)**2 == 0 in the CSV ratio column; negative
    values leave the counts array empty, so min(c) raises. All of these are
    confusing crashes deep in analysis code rather than a clear rejection at
    the argument boundary.
    """
    n = int(raw)
    if n < 2:
        raise argparse.ArgumentTypeError(
            f"--n-max must be >= 2 (got {n}); N=0 and N=1 have no ratio to "
            f"compute and negative N is not meaningful"
        )
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-max", type=_n_max_type, default=1_000_000)
    ap.add_argument("--skip-crosscheck", action="store_true",
                    help="DEVELOPMENT ONLY: skips the precondition and refuses "
                         "to write to the real artifact paths.")
    args = ap.parse_args()
    n_max = args.n_max

    print(f"computing gf.coefficients({n_max}) ...")
    t0 = time.time()
    c = coefficients(n_max)
    gf_seconds = time.time() - t0
    print(f"  gf took {gf_seconds:.1f}s")

    if args.skip_crosscheck:
        print("WARNING: cross-check skipped; refusing to write real artifacts.")
        crosscheck = "skipped"
        dp_seconds = None
    else:
        print(f"computing dp.counts({n_max}) for the cross-check (slow) ...")
        t0 = time.time()
        d = dp_counts(n_max)
        dp_seconds = time.time() - t0
        print(f"  dp took {dp_seconds:.1f}s")
        if c != d:
            first = next(i for i in range(len(c)) if c[i] != d[i])
            print(f"CROSS-CHECK FAILED: first disagreement at N={first}: "
                  f"gf={c[first]} dp={d[first]}")
            print("Writing nothing.")
            return 1
        crosscheck = f"dp==gf pointwise for all N <= {n_max}"
        print(f"cross-check OK: {crosscheck}")

    assert min(c) >= 1, "a zero count would break local_ratios"

    census = monotonicity_census(c)
    sc = summatory(c)
    ratios = local_ratios(c)
    jumps = place_jumps(c)
    blocks = block_extrema(c)

    print(f"census: {census}")
    print(f"decreasing steps: {census['decreasing']} of {census['steps']} "
          f"({100 * census['decreasing'] / census['steps']:.1f}%)")

    if args.skip_crosscheck:
        print("skip-crosscheck set: analyses ran, nothing written.")
        return 0

    rows = []
    for n in ladder(n_max):
        log_n = math.log(n)
        rows.append({
            "N": n,
            "R_c": c[n],
            "log_R_c": math.log(c[n]),
            "log_N_sq": log_n * log_n,
            "ratio": math.log(c[n]) / (log_n * log_n),
            "S_c": sc[n],
            "log_S_c": math.log(sc[n]),
        })
    sio = io.StringIO()
    w = csv.DictWriter(sio, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
    atomic_write_text(DATA_CSV, sio.getvalue())

    srt = sorted(ratios)
    summary = {
        "n_max": n_max,
        "git_rev": git_rev(),
        "crosscheck": crosscheck,
        # spec section 9 criterion 4: every measurement the design quotes must be
        # re-derived here, so no figure in the spec rests on an unrecorded run.
        "gf_seconds": round(gf_seconds, 1),
        "dp_seconds": None if dp_seconds is None else round(dp_seconds, 1),
        "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024),
        "census": census,
        "flat_step_positions": [n for n in range(1, n_max + 1) if c[n] == c[n - 1]],
        "min_count": min(c),
        "R_c_at_n_max": str(c[n_max]),
        "R_c_bit_length": c[n_max].bit_length(),
        "place_jumps": jumps,
        "block_extrema": [
            {**b, "max": str(b["max"]), "min": str(b["min"])} for b in blocks
        ],
        "fluctuation_quantiles": {
            "min": srt[0],
            "p25": srt[len(srt) // 4],
            "median": srt[len(srt) // 2],
            "p75": srt[3 * len(srt) // 4],
            "max": srt[-1],
        },
    }
    atomic_write_text(SUMMARY_JSON, json.dumps(summary, indent=2) + "\n")

    # --- figures: distinct colours, matchable legend entries ---
    xs = [r["log_N_sq"] for r in rows]
    FIG_GROWTH.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(xs, [r["log_R_c"] for r in rows], "o-", color="#1f77b4", label="log R_c(N)")
    ax.plot(xs, [r["log_S_c"] for r in rows], "s--", color="#d62728", label="log S_c(N)")
    ax.set_xlabel("(log N)^2")
    ax.set_ylabel("log")
    ax.set_title(f"Phase 1: growth of R_c and S_c (exact, N <= {n_max})")
    ax.legend()
    fig.tight_layout()
    atomic_savefig(fig, FIG_GROWTH, dpi=150)
    plt.close(fig)

    step = max(1, n_max // 20_000)
    idx = list(range(1, n_max, step))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(idx, [ratios[i] for i in idx], ".", markersize=1,
            color="#1f77b4", label="R_c(N+1)/R_c(N)")
    ax.plot(idx, [1 + c[i + 1] / sc[i] for i in idx], "-",
            color="#d62728", label="1 + R_c(N+1)/S_c(N)  (S_c increment)")
    ax.axhline(1.0, ls=":", color="#555555", label="1")
    ax.set_xscale("log")
    ax.set_xlabel("N")
    ax.set_ylabel("relative increment")
    ax.set_title("Phase 1: R_c fluctuates, S_c does not")
    ax.legend()
    fig.tight_layout()
    atomic_savefig(fig, FIG_FLUCT, dpi=150)
    plt.close(fig)

    params = {"n_max": n_max, "crosscheck": crosscheck}
    for path in (DATA_CSV, SUMMARY_JSON, FIG_GROWTH, FIG_FLUCT):
        record(path, script="scripts/run_phase1.py", params=params,
               manifest_path=MANIFEST)

    print(f"wrote {DATA_CSV.name}, {SUMMARY_JSON.name}, "
          f"{FIG_GROWTH.name}, {FIG_FLUCT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
