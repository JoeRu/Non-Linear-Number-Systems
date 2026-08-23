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
    """argparse type for --n-max: reject anything below 8.

    Two floors, and the argument boundary enforces the higher of them.

    Below 2 the analysis code crashes confusingly: n_max=0 divides by zero in
    the decreasing-steps percentage; n_max in {0, 1} leaves local_ratios
    empty, so the quantile indexing raises; n_max=1 divides by log(1)**2 == 0
    in the CSV ratio column; negative values leave the counts array empty, so
    min(c) raises.

    Below 8 the run cannot produce its figures file: `place-jump-f8` needs the
    place F=8, and a run that always writes figures cannot accept an argument
    that guarantees it will refuse to. Accepting 2..7 and then failing a
    runtime precondition made the CLI contract say one thing and the script do
    another, so the floor lives here instead.
    """
    n = int(raw)
    if n < 8:
        raise argparse.ArgumentTypeError(
            f"--n-max must be >= 8 (got {n}); below 2 there is no ratio to "
            f"compute, and below 8 the run cannot reach Fibonacci place F=8, "
            f"which the place-jump figures require"
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
        # Length must be checked before equality: two identically-truncated
        # arrays compare equal (Python list equality is pointwise AND
        # length-sensitive, but "identically truncated" means both sides
        # agree on every element they share, including their -- too-short --
        # length), so `c != d` would be False and the cross-check would
        # report success. The later `c[n]` lookups for n up to n_max would
        # then raise IndexError instead of this being caught here.
        if len(c) != n_max + 1 or len(d) != n_max + 1:
            print(f"CROSS-CHECK FAILED: expected arrays of length {n_max + 1} "
                  f"from both gf and dp, got gf={len(c)}, dp={len(d)}")
            print("Writing nothing.")
            return 1
        if c != d:
            # The length check above guarantees len(c) == len(d) == n_max + 1
            # here, so c and d being unequal guarantees some index in
            # range(n_max + 1) differs -- this can never exhaust the range
            # without finding one, so there is no "differ in length" case
            # left to report at this point.
            first = next(i for i in range(n_max + 1) if c[i] != d[i])
            print(f"CROSS-CHECK FAILED: first disagreement at N={first}: "
                  f"gf={c[first]} dp={d[first]}")
            print("Writing nothing.")
            return 1
        crosscheck = f"dp==gf pointwise for all N <= {n_max}"
        print(f"cross-check OK: {crosscheck}")

    if min(c) < 1:
        print("PRECONDITION FAILED: a non-positive count would break local_ratios.")
        print("Writing nothing.")
        return 1

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

    jump_by_place = {j["place"]: j["ratio"] for j in jumps}
    if 8 not in jump_by_place:
        # The place-jump-f2/f3/f8 figures below assume the run reaches
        # Fibonacci place F=8, i.e. n_max >= 8. _n_max_type now rejects
        # anything below 8, so no CLI invocation reaches here; this stays as
        # the second line of defence for callers that import main() and
        # build args themselves, and because a figures file silently missing
        # a key is worse than a refusal. Every other precondition in this
        # function prints a clear message and returns 1 rather than crashing
        # with a raw traceback, so this one follows suit instead of
        # asserting.
        print(f"PRECONDITION FAILED: --n-max {n_max} does not reach "
              f"Fibonacci place F=8; the place-jump-f2/f3/f8 figures assume "
              f"it does.")
        print("Writing nothing.")
        return 1

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
    # The `log-rc-at-nmax` and `ratio-at-nmax` figures below read `rows[-1]`
    # and are described as "at the largest N computed", so the ladder's last
    # row has to be N = n_max. `ladder()` always includes n_max as its
    # maximum, so this is a precondition on a helper rather than on user
    # input -- but it is checked here, before anything is written, and in the
    # same print-and-return-1 shape as every other precondition in this
    # function. It used to be a bare `assert` sitting *after* the CSV, the
    # summary and both PNGs had already been written and recorded in the
    # manifest: on failure it raised a bare traceback and left a published,
    # manifest-recorded generation with no figures file beside it.
    if not rows or rows[-1]["N"] != n_max:
        last = rows[-1]["N"] if rows else None
        print(f"PRECONDITION FAILED: the ladder's last row is N={last}, not "
              f"n_max={n_max}; the log-rc-at-nmax and ratio-at-nmax figures "
              f"would not be at the largest N computed.")
        print("Writing nothing.")
        return 1
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

    # Deliberately excluded: dp_seconds, gf_seconds and peak_rss_mb -- the
    # wall-clock timings *and* the peak-memory figure. They are in `summary`
    # and the documents mention them, but all three change from run to run and
    # from machine to machine. Tagging them would force a prose edit at each
    # regeneration for no epistemic gain -- churn that looks like rigour and
    # trains people to edit numbers to make a test pass, which is the opposite
    # of the point.
    #
    # The other half of that decision, learned the hard way: because they are
    # untagged, prose must not quote them as *specific values* either. Three
    # regenerations on one branch left `docs/phases/phase1_report.md` saying
    # "8.7 s / 286.9 s / 273 MB" of a run that had recorded 8.9 / 286.1 / 274
    # -- risk R-002's exact failure mode, inside the branch that closed it.
    # The report now states them rounded ("roughly nine seconds", "under
    # 300 MB"), which regeneration cannot falsify.
    #
    # Also deliberately excluded: the full `place_jumps` and `block_extrema`
    # arrays and `flat_step_positions` list. The documents reproduce those in
    # full as tables/lists read straight from data/phase1_summary.json;
    # `tests/test_phase1_tables.py` checks every cell of both tables against
    # this file directly (anchored on the `<!-- table:... -->` markers in
    # `docs/phases/phase1_report.md`), so they do not need a `{fig:key}` per
    # cell -- that would be on the order of a hundred more keys. Only the
    # specific values pulled out of them into prose as headline figures (a
    # handful of individual place-jump ratios, the block count, the flat-step
    # extremes) are promoted to a key here and checked that way instead.
    # `rows[-1]["N"] == n_max` is checked above, before anything is written.
    figures = {
        "n-max": {
            "value": summary["n_max"],
            "precision": 0,
            "description": "largest N for which R_c was computed exactly",
        },
        "rc-bit-length": {
            "value": summary["R_c_bit_length"],
            "precision": 0,
            "description": "bit length of R_c at the largest N",
        },
        "census-increasing": {
            "value": summary["census"]["increasing"],
            "precision": 0,
            "description": "increasing steps of R_c over the computed range",
        },
        "census-decreasing": {
            "value": summary["census"]["decreasing"],
            "precision": 0,
            "description": "decreasing steps of R_c over the computed range",
        },
        "census-flat": {
            "value": summary["census"]["flat"],
            "precision": 0,
            "description": "flat steps of R_c over the computed range",
        },
        "census-steps": {
            "value": summary["census"]["steps"],
            "precision": 0,
            "description": "total steps examined in the monotonicity census",
        },
        "decreasing-fraction": {
            "value": 100.0 * summary["census"]["decreasing"] / summary["census"]["steps"],
            "precision": 1,
            "description": "percentage of steps that decrease, over the computed range",
        },
        "fluctuation-median": {
            "value": summary["fluctuation_quantiles"]["median"],
            "precision": 4,
            "description": "median of R_c(N+1)/R_c(N) over the computed range",
        },
        "fluctuation-min": {
            "value": summary["fluctuation_quantiles"]["min"],
            "precision": 4,
            "description": "minimum local ratio over the computed range",
        },
        "fluctuation-max": {
            "value": summary["fluctuation_quantiles"]["max"],
            "precision": 1,
            "description": "maximum local ratio over the computed range",
        },
        "flat-step-count": {
            "value": len(summary["flat_step_positions"]),
            "precision": 0,
            "description": "number of flat steps found",
        },
        "flat-step-last": {
            "value": max(summary["flat_step_positions"]),
            "precision": 0,
            "description": "largest N at which a flat step occurs",
        },
        "fluctuation-p25": {
            "value": summary["fluctuation_quantiles"]["p25"],
            "precision": 4,
            "description": "25th-percentile order statistic of R_c(N+1)/R_c(N) over the computed range",
        },
        "fluctuation-p75": {
            "value": summary["fluctuation_quantiles"]["p75"],
            "precision": 4,
            "description": "75th-percentile order statistic of R_c(N+1)/R_c(N) over the computed range",
        },
        "min-count": {
            "value": summary["min_count"],
            "precision": 0,
            "description": "minimum representation count over the computed range",
        },
        "block-count": {
            "value": len(summary["block_extrema"]),
            "precision": 0,
            "description": "number of Fibonacci blocks with recorded extrema over the computed range",
        },
        "rc-value": {
            # Serialised as a string, matching how phase1_summary.json stores
            # R_c_at_n_max. It is a 99-bit integer: Python's json reads it
            # losslessly either way, but a JSON consumer backed by doubles
            # silently rounds anything past 2**53, and this artifact is meant
            # to be readable outside this repository.
            "value": str(c[n_max]),
            "precision": 0,
            "description": "exact value of R_c at the largest N computed",
        },
        "log-rc-at-nmax": {
            "value": rows[-1]["log_R_c"],
            "precision": 2,
            "description": "log R_c(N) at the largest N computed",
        },
        "ratio-at-nmax": {
            "value": rows[-1]["ratio"],
            "precision": 4,
            "description": "log R_c(N) / (log N)^2 at the largest N computed",
        },
        "place-jump-f2": {
            "value": jump_by_place[2],
            "precision": 1,
            "description": "R_c(F)/R_c(F-1) at place F=2",
        },
        "place-jump-f3": {
            "value": jump_by_place[3],
            "precision": 1,
            "description": "R_c(F)/R_c(F-1) at place F=3",
        },
        "place-jump-f8": {
            "value": jump_by_place[8],
            "precision": 3,
            "description": "R_c(F)/R_c(F-1) at place F=8",
        },
        "place-jump-largest": {
            "value": jumps[-1]["ratio"],
            "precision": 6,
            "description": "R_c(F)/R_c(F-1) at the largest distinct place in the computed range",
        },
    }
    figures_path = REPO_ROOT / "data" / "phase1_figures.json"
    atomic_write_text(figures_path, json.dumps(figures, indent=2, sort_keys=True) + "\n")
    record(figures_path, script="scripts/run_phase1.py", params={"n_max": n_max},
           manifest_path=MANIFEST)

    print(f"wrote {DATA_CSV.name}, {SUMMARY_JSON.name}, "
          f"{FIG_GROWTH.name}, {FIG_FLUCT.name}, {figures_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
