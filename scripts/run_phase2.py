#!/usr/bin/env python3
"""Phase 2: verify the certified bounds against the Phase 1 exact-value ladder.

Reads `data/phase1_data.csv` and checks T1, T3 and T5 at each of its rows --
the 37-point ladder of N at which Phase 1 recorded an exact `R_c(N)`, not
every N in that range; the exhaustive comparison is Phase 1's own
`dp`-vs-`gf` cross-check, not this script's.

Writes data/phase2_bounds.csv, data/phase2_residual.csv,
data/phase2_figures.json and figures/phase2_sandwich.png, and records all four
in data/manifest.json.

The gate (spec 5.5): the float and certified evaluations of log F_c must agree
to RELATIVE_TOL across the whole reported range, in this same run. Nothing is
written if the gate fails.

"Nothing is written" is enforced by ordering, not by hope: every value --
including the rendered PNG, which is drawn into an in-memory buffer -- is
produced before the first byte reaches `data/` or `figures/`. Rendering the
figure last while recording the CSVs first was the shape of a real defect: on
a clean checkout `figures/` did not exist, `atomic_savefig` needs its parent
directory, and the run died having already written three artifacts and three
manifest entries.
"""

import argparse
import csv
import io
import json
import math
import os
import sys
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MANIFEST = ROOT / "data" / "manifest.json"
"""Absolute, derived from this file's location -- exactly as scripts/run_phase1.py
does it. `capfib.manifest.record` defaults to the *relative* "data/manifest.json",
which resolves against the current working directory: without this the script
recorded its provenance into whatever repository it happened to be invoked from,
not the one it wrote its artifacts into. Found by the first test that ever ran
this script to success (tests/test_run_phase2.py), which runs a copy inside a
scratch tree and saw its manifest entries land in the real repository instead."""

from capfib.interval import RELATIVE_TOL, agrees_with_float
from capfib.lower import block_band_min, t3_lower_bound, t5_lower_bound
from capfib.manifest import record
from capfib.product import log_F_c
from capfib.saddle import argmin_log_s, log_R_bound_certified

RESIDUAL_T = [10.0, 20.0, 40.0, 80.0, 160.0, 320.0, 640.0, 1280.0]
"""Sampled t = log(1/s) for the residual observation. Certifying t = 1280 takes
about 7 seconds, which is why this sweep lives in the script and not the suite."""

RESIDUAL_ASYMPTOTIC_T_MIN = 20.0
"""Marks where the residual has entered its asymptotic regime: for t >= this value
the residual sits in a tight band (spread ~2e-4), while t = 10 -- retained in
RESIDUAL_T deliberately, never dropped -- sits about 0.018 away from that band,
since the leading term t^2/(4 log phi) is only an asymptotic approximation and
t = 10 is the sample furthest from the regime it approximates. Both figures are
published (see the residual-full-* and residual-asymptotic-* keys below) so a
claim about this sweep can be written from the honest range, not a narrower one
mistaken for the whole."""

FLATNESS_SLACK_A = range(8, 17)
"""Block lengths at which Lemma F's proved bound is confronted with the exact band
minimum of B(a, .). The range starts at 8 because that is where the flatness recursion
first contributes a factor above 1, and stops at 16 because the DP is O(S_a) with
S_16 = 1576239 and the whole sweep then costs about four seconds."""

PHI = (1 + 5 ** 0.5) / 2
LOG_PHI = math.log(PHI)


def atomic_write_text(path: Path, text: str) -> None:
    """Write text to `path` via a temporary file and an atomic rename.

    Args:
        path: destination file path. Its parent directory must already exist.
        text: the full contents to write.
    """
    handle = tempfile.NamedTemporaryFile(
        "w", dir=path.parent, delete=False, encoding="utf-8"
    )
    try:
        handle.write(text)
        handle.close()
        os.replace(handle.name, path)
    except BaseException:
        os.unlink(handle.name)
        raise


def render_figure(fig) -> bytes:
    """Render a figure to PNG bytes in memory, writing nothing to disk.

    Rendering is the step most likely to fail for reasons unrelated to the
    mathematics -- a missing backend, a font cache, a matplotlib upgrade -- so
    it happens before any artifact is published rather than after, and its
    result is carried as bytes.

    Args:
        fig: the matplotlib figure to render.

    Returns:
        The PNG encoding of the figure.
    """
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    return buffer.getvalue()


def atomic_write_bytes(path: Path, payload: bytes) -> None:
    """Write bytes to `path` via a temporary file and an atomic rename.

    The temp file keeps `path`'s suffix at the end (rather than appending
    ".tmp" after it) so the published name and the staged name differ only in
    the random middle, which keeps the rename within one directory.

    Args:
        path: destination file path. Its parent directory must already exist.
        payload: the full contents to write.
    """
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), suffix=path.suffix)
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        tmp.write_bytes(payload)
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def residual_sweep() -> list[dict]:
    """Sample the residual of log F_c against its leading term.

    Returns:
        One row per sampled t, each carrying t, the float evaluation, the
        leading term and their difference.

    Raises:
        RuntimeError: if any sampled t fails the spec 5.5 agreement gate.
    """
    rows = []
    for t in RESIDUAL_T:
        value = log_F_c(-t)
        if not agrees_with_float(t, value):
            raise RuntimeError(
                f"gate failed in the residual sweep at t={t}: float and "
                f"certified log F_c disagree beyond {RELATIVE_TOL}"
            )
        leading = t * t / (4 * LOG_PHI)
        rows.append(
            {"t": t, "log_F_c": value, "leading": leading, "residual": value - leading}
        )
    return rows


def flatness_slack_slope() -> float:
    """Least-squares slope of Lemma F's slack against the block length.

    The slack is `lambda a^2/2 - log(exact band minimum of B(a, .))`, the amount
    by which the true band minimum falls below the quadratic term. Lemma F proves
    a slope of at most 3.5057 (docs/phases/phase2_bounds.md 8.2); this measures
    what the slope actually is over FLATNESS_SLACK_A, so the note's sharpness
    remark quotes a generated number rather than an eyeballed one.

    Returns:
        The ordinary-least-squares slope over FLATNESS_SLACK_A.
    """
    xs = list(FLATNESS_SLACK_A)
    ys = [LOG_PHI * a * a / 2 - math.log(block_band_min(a)) for a in xs]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = sum((x - mean_x) ** 2 for x in xs)
    return numerator / denominator


def main() -> int:
    """Run the Phase 2 verification over the Phase 1 exact-value ladder.

    Checks T1, T3 and T5 at each of `data/phase1_data.csv`'s rows (37 sampled
    N, not every N in the range), runs the residual sweep, and writes the
    artifacts only if every gate passes.

    Returns:
        0 on success (all artifacts written); 1 if any gate, bound check or
        the figure rendering fails, in which case nothing is written.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--n-max", type=int, default=1_000_000, help="largest N to verify"
    )
    args = parser.parse_args()
    if args.n_max < 2:
        parser.error("--n-max must be at least 2")

    data_path = ROOT / "data" / "phase1_data.csv"
    if not data_path.exists():
        print(
            f"FAILED: {data_path} absent. It is tracked, so on a clean checkout "
            f"it is there; if it is not, restore it from git or regenerate it "
            f"with scripts/run_phase1.py first"
        )
        return 1
    with data_path.open() as handle:
        exact = {
            int(r["N"]): float(r["log_R_c"])
            for r in csv.DictReader(handle)
            if int(r["N"]) <= args.n_max
        }
    if not exact:
        print(f"FAILED: no Phase 1 rows at or below N = {args.n_max}. Writing nothing.")
        return 1

    rows = []
    for n in sorted(exact):
        if n < 2:
            continue
        log_s, hit_boundary = argmin_log_s(math.log(n))
        t = -log_s
        if not agrees_with_float(t, log_F_c(log_s)):
            print(
                f"GATE FAILED at N={n}: float and certified log F_c disagree "
                f"beyond {RELATIVE_TOL}. Writing nothing."
            )
            return 1
        certified = log_R_bound_certified(n)
        if certified < exact[n]:
            print(
                f"BOUND VIOLATED at N={n}: certified {certified} < exact {exact[n]}. "
                "Writing nothing."
            )
            return 1
        t3 = t3_lower_bound(n)
        lower, a, c, m_count = (
            t3.log_count,
            t3.fixup_block,
            t3.top_place,
            t3.counting_places,
        )
        if lower > exact[n]:
            print(
                f"LOWER BOUND VIOLATED at N={n}: T3 {lower} > exact {exact[n]}. "
                "Writing nothing."
            )
            return 1
        t5 = t5_lower_bound(n)
        if t5.log_count > exact[n]:
            print(
                f"LOWER BOUND VIOLATED at N={n}: T5 {t5.log_count} > exact "
                f"{exact[n]}. Writing nothing."
            )
            return 1
        rows.append(
            {
                "N": n,
                "log_R_c": exact[n],
                "t3_lower": lower,
                "t5_lower": t5.log_count,
                "t5_log_free": t5.log_free,
                "t5_log_block": t5.log_block,
                "t5_block_a": t5.block,
                "chernoff_certified": certified,
                "asymptotic_upper": math.log(n) ** 2 / (4 * LOG_PHI),
                "asymptotic_lower": math.log(n) ** 2 / (8 * LOG_PHI),
                "fixup_block_a": a,
                "top_place_c": c,
                "counting_places": m_count,
                "boundary_hit": int(hit_boundary),
            }
        )

    # The residual sweep's own gate (spec 5.5) is checked here, before any
    # file is written: computing it after the bounds CSV was already on disk
    # would mean a residual-sweep gate failure left a partial artifact behind,
    # contradicting "nothing is written if the gate fails".
    try:
        residual_rows = residual_sweep()
    except RuntimeError as exc:
        print(f"{exc}. Writing nothing.")
        return 1

    header = list(rows[0].keys())
    lines = [",".join(header)]
    lines += [",".join(repr(r[k]) for k in header) for r in rows]
    bounds_csv = "\n".join(lines) + "\n"

    residuals = [r["residual"] for r in residual_rows]
    residual_centre = sum(residuals) / len(residuals)
    residual_full_spread = max(residuals) - min(residuals)
    asymptotic_residuals = [
        r["residual"] for r in residual_rows if r["t"] >= RESIDUAL_ASYMPTOTIC_T_MIN
    ]
    asymptotic_ts = [r["t"] for r in residual_rows if r["t"] >= RESIDUAL_ASYMPTOTIC_T_MIN]
    residual_asymptotic_centre = sum(asymptotic_residuals) / len(asymptotic_residuals)
    residual_asymptotic_spread = max(asymptotic_residuals) - min(asymptotic_residuals)
    residual_asymptotic_t_min = min(asymptotic_ts)
    residual_lines = ["t,log_F_c,leading,residual"]
    residual_lines += [
        f"{r['t']!r},{r['log_F_c']!r},{r['leading']!r},{r['residual']!r}"
        for r in residual_rows
    ]
    residual_csv = "\n".join(residual_lines) + "\n"

    biggest = rows[-1]
    figures = {
        "residual-centre": {
            "value": residual_centre,
            "precision": 4,
            "description": "mean residual of log F_c against its leading term over the sampled t",
        },
        "residual-full-spread": {
            "value": residual_full_spread,
            "precision": 6,
            "description": (
                "max minus min residual over all sampled t in "
                "[10, 1280], including the pre-asymptotic t=10 point"
            ),
        },
        "residual-asymptotic-centre": {
            "value": residual_asymptotic_centre,
            "precision": 4,
            "description": (
                f"mean residual over the samples with t >= "
                f"{RESIDUAL_ASYMPTOTIC_T_MIN:.0f} (the asymptotic regime; "
                f"excludes the pre-asymptotic t=10 point)"
            ),
        },
        "residual-asymptotic-spread": {
            "value": residual_asymptotic_spread,
            "precision": 6,
            "description": (
                f"max minus min residual over the samples with t >= "
                f"{RESIDUAL_ASYMPTOTIC_T_MIN:.0f}"
            ),
        },
        "residual-asymptotic-t-min": {
            "value": residual_asymptotic_t_min,
            "precision": 0,
            "description": (
                "smallest sampled t in the asymptotic-regime subset "
                "(t >= RESIDUAL_ASYMPTOTIC_T_MIN)"
            ),
        },
        "residual-t-min": {
            "value": min(RESIDUAL_T),
            "precision": 0,
            "description": "smallest sampled t = log(1/s) in the residual sweep",
        },
        "residual-t-max": {
            "value": max(RESIDUAL_T),
            "precision": 0,
            "description": "largest sampled t = log(1/s) in the residual sweep",
        },
        "chernoff-slack-nmax": {
            "value": biggest["chernoff_certified"] - biggest["log_R_c"],
            "precision": 4,
            "description": "certified bound minus exact log R_c at the largest N verified",
        },
        "chernoff-certified-nmax": {
            "value": biggest["chernoff_certified"],
            "precision": 4,
            "description": "certified Chernoff bound at the largest N verified",
        },
        "log-rc-nmax": {
            "value": biggest["log_R_c"],
            "precision": 4,
            "description": "exact log R_c at the largest N verified",
        },
        "t3-lower-nmax": {
            "value": biggest["t3_lower"],
            "precision": 3,
            "description": "T3 construction evaluated at the largest N verified",
        },
        "flatness-slack-slope": {
            "value": flatness_slack_slope(),
            "precision": 4,
            "description": (
                "least-squares slope, per unit of a, of Lemma F's slack "
                "lambda a^2/2 - log(exact band minimum of B(a, .)) over "
                f"a = {min(FLATNESS_SLACK_A)}..{max(FLATNESS_SLACK_A)}; "
                "Lemma F proves this slope is at most 3.5057"
            ),
        },
        "flatness-slack-a-max": {
            "value": max(FLATNESS_SLACK_A),
            "precision": 0,
            "description": "largest block length at which Lemma F's slack was measured",
        },
        "t5-lower-nmax": {
            "value": biggest["t5_lower"],
            "precision": 3,
            "description": "T5 construction evaluated at the largest N verified",
        },
        "t5-log-block-nmax": {
            "value": biggest["t5_log_block"],
            "precision": 3,
            "description": (
                "the T5 construction's block factor -- the proved flatness bound "
                "on log B(a, m) -- at the largest N verified"
            ),
        },
        "t5-block-nmax": {
            "value": biggest["t5_block_a"],
            "precision": 0,
            "description": "T5 block boundary a at the largest N verified",
        },
        "fixup-block-nmax": {
            "value": biggest["fixup_block_a"],
            "precision": 0,
            "description": "fixup block boundary a at the largest N verified",
        },
        "counting-places-nmax": {
            "value": biggest["counting_places"],
            "precision": 0,
            "description": "number of counting places at the largest N verified",
        },
        "n-max-verified": {
            "value": biggest["N"],
            "precision": 0,
            "description": "largest N at which the certified bound was verified",
        },
        "upper-constant": {
            "value": 1 / (4 * LOG_PHI),
            "precision": 4,
            "description": "1 / (4 log phi), the T2 upper constant",
        },
        "lower-constant": {
            "value": 1 / (8 * LOG_PHI),
            "precision": 4,
            "description": "1 / (8 log phi), the T3 lower constant",
        },
        "ratio-nmax": {
            "value": biggest["log_R_c"] / math.log(biggest["N"]) ** 2,
            "precision": 4,
            "description": "log R_c(N) / (log N)^2 at the largest N verified",
        },
    }

    # The figure is rendered to bytes HERE, before anything is published. It
    # used to be drawn last, after three artifacts and three manifest entries
    # were already on disk -- so on a clean checkout, where `figures/` does not
    # exist and the atomic rename has no parent directory to land in, the run
    # failed having already published most of a generation. Rendering first
    # makes a rendering failure cost nothing.
    ns = [r["N"] for r in rows]
    try:
        fig, ax = plt.subplots(figsize=(9, 5.5))
        try:
            ax.plot(ns, [r["chernoff_certified"] for r in rows], label="certified Chernoff bound (T1)")
            ax.plot(ns, [r["log_R_c"] for r in rows], label="exact log R_c(N)")
            ax.plot(ns, [r["t3_lower"] for r in rows], label="T3 construction")
            ax.set_xscale("log")
            ax.set_xlabel("N")
            ax.set_ylabel("log R_c(N)")
            ax.set_title("Phase 2 sandwich: exact values between the proved bounds")
            ax.legend()
            ax.grid(alpha=0.3)
            figure_png = render_figure(fig)
        finally:
            plt.close(fig)
    except Exception as exc:
        print(f"FIGURE FAILED: {exc!r}. Writing nothing.")
        return 1

    # Everything above is in memory and every gate has passed. Only now is
    # anything published, and the manifest entries follow their own artifacts.
    figures_dir = ROOT / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    csv_path = ROOT / "data" / "phase2_bounds.csv"
    atomic_write_text(csv_path, bounds_csv)
    record(
        csv_path,
        "scripts/run_phase2.py",
        {"n_max": args.n_max, "relative_tol": RELATIVE_TOL},
        manifest_path=MANIFEST,
    )

    residual_path = ROOT / "data" / "phase2_residual.csv"
    atomic_write_text(residual_path, residual_csv)
    record(
        residual_path,
        "scripts/run_phase2.py",
        {"t_values": RESIDUAL_T},
        manifest_path=MANIFEST,
    )

    figures_path = ROOT / "data" / "phase2_figures.json"
    atomic_write_text(figures_path, json.dumps(figures, indent=2, sort_keys=True) + "\n")
    record(
        figures_path,
        "scripts/run_phase2.py",
        {"n_max": args.n_max},
        manifest_path=MANIFEST,
    )

    figure_path = figures_dir / "phase2_sandwich.png"
    atomic_write_bytes(figure_path, figure_png)
    record(
        figure_path,
        "scripts/run_phase2.py",
        {"n_max": args.n_max},
        manifest_path=MANIFEST,
    )

    print(f"OK: gate passed and both bounds held at all {len(rows)} sampled N")
    print(f"  largest N verified: {biggest['N']}")
    print(f"  certified slack there: {figures['chernoff-slack-nmax']['value']:.4f}")
    print(
        f"  residual, full range t in [{min(RESIDUAL_T):.0f}, {max(RESIDUAL_T):.0f}]: "
        f"spread {residual_full_spread:.6f} (centre {residual_centre:.4f})"
    )
    print(
        f"  residual, asymptotic regime t >= {RESIDUAL_ASYMPTOTIC_T_MIN:.0f}: "
        f"{residual_asymptotic_centre:.4f} +/- {residual_asymptotic_spread:.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
