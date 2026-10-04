#!/usr/bin/env python3
"""Four reproducible layout/readability cases using unchanged synthetic fixtures.

These illustrate skill-guided custom Matplotlib work, not additional fixed CLI
chart modes and not an empirical AI benchmark. Both sides use SciencePlots.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).with_name("data")
sys.path.insert(0, str(ROOT / "skills/research-figure/scripts"))
from figure_tools import figure_context, save_figure

COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#56B4E9", "#8B5E3C"]
STYLES = ["-", "--", "-.", ":", "-", "--"]


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def col(rows, name):
    return np.array([float(r[name]) for r in rows])


def frame(title, before, after):
    fig = plt.figure(layout="constrained")
    left, right = fig.subfigures(1, 2, wspace=.09)
    fig.suptitle(title + "\nSIMULATED DATA · SAME SOURCE VALUES · SCIENCEPLOTS ON BOTH SIDES",
                 fontsize=11, fontweight="bold")
    left.suptitle("Draft / " + before, fontsize=11)
    right.suptitle("Reviewed / " + after, fontsize=11)
    return fig, left, right


def tidy(ax, grid=True):
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(top=False, right=False, which="both")
    if grid:
        ax.grid(axis="y", color=".91", linewidth=.65)
        ax.set_axisbelow(True)


def multimodel():
    rows = read("multimodel.csv")
    t, observed = col(rows, "time"), col(rows, "observed")
    fig, left, right = frame("01 / MULTI-MODEL COMPARISON", "seven overlapping traces", "shared-scale small multiples")
    ax = left.subplots()
    ax.plot(t, observed, color=".2", label="Observed", linewidth=1.3)
    for i in range(6):
        ax.plot(t, col(rows, f"method_{i+1}"), color=COLORS[i], linewidth=1.1, label=f"Method {i+1}")
    ax.set(xlabel="Time (h)", ylabel="Response (a.u.)", xlim=(0, 24), ylim=(20, 85))
    ax.legend(loc="upper right", fontsize=8, frameon=True)
    axes = right.subplots(3, 2, sharex=True, sharey=True)
    for i, other in enumerate(axes.flat):
        other.plot(t, observed, color=".72", linewidth=1.4)
        line, = other.plot(t, col(rows, f"method_{i+1}"), color=COLORS[i], linewidth=1.15,
                           linestyle=STYLES[i])
        other.set(title=f"Method {i+1}", xlim=(0, 24), ylim=(20, 85))
        other.set_xticks([0, 12, 24]); other.set_yticks([25, 50, 75]); tidy(other)
        np.testing.assert_allclose(line.get_ydata(), ax.lines[i+1].get_ydata())
        np.testing.assert_allclose(other.lines[0].get_ydata(), observed)
    right.supxlabel("Time (h) · gray line: observed", fontsize=9)
    right.supylabel("Response (a.u.)", fontsize=9)
    assert all(a.get_ylim() == (20, 85) for a in axes.flat)
    return fig, {"methods": 6, "observations_per_trace": len(t), "all_values_preserved": True,
                 "shared_y_limits": [20, 85], "reference_in_every_panel": True}


def density():
    rows = read("density.csv")
    x, y = col(rows, "observed"), col(rows, "predicted")
    low = np.floor(min(x.min(), y.min()) / 10) * 10
    high = np.ceil(max(x.max(), y.max()) / 10) * 10
    fig, left, right = frame("02 / DENSE PREDICTION DATA", "opaque scatter", "sample density")
    ax, bx = left.subplots(), right.subplots()
    dots = ax.scatter(x, y, s=17, color=COLORS[0], alpha=1, edgecolors="none")
    bins = bx.hexbin(x, y, gridsize=32, extent=(low, high, low, high), mincnt=1,
                     bins="log", cmap="cividis", linewidths=0)
    bar = right.colorbar(bins, ax=bx, shrink=.65, pad=.035)
    bar.set_label("Samples / bin (log scale)", fontsize=9)
    for a in (ax, bx):
        a.plot([low, high], [low, high], color=".4", linestyle="--", linewidth=.85)
        a.set(xlabel="Observed (a.u.)", ylabel="Predicted (a.u.)", xlim=(low, high), ylim=(low, high))
        a.set_aspect("equal", adjustable="box"); tidy(a, grid=False)
    assert int(bins.get_array().sum()) == len(rows) == len(dots.get_offsets())
    assert ax.get_xlim() == bx.get_xlim() and ax.get_ylim() == bx.get_ylim()
    return fig, {"source_samples": len(rows), "sum_of_bin_counts": int(bins.get_array().sum()),
                 "gridsize": 32, "count_color_scale": "log", "same_axes": True,
                 "transformation": "hexagonal count aggregation; no sample removal"}


def labels():
    rows = read("labels.csv")
    names, values, sd = [r["method"] for r in rows], col(rows, "mae"), col(rows, "sd")
    fig, left, right = frame("03 / ABLATION COMPARISON", "rotated category labels", "ranked horizontal intervals")
    ax, bx = left.subplots(), right.subplots()
    bars = ax.bar(np.arange(len(rows)), values, yerr=sd, color=COLORS[0], capsize=2)
    ax.set_xticks(np.arange(len(rows)), names, rotation=65, ha="right", fontsize=8)
    ax.set(ylabel="MAE (a.u.) · supplied SD", ylim=(0, 13))
    order = np.argsort(values, kind="stable")
    ranked = values[order]; errors = sd[order]
    for j, index in enumerate(order):
        color = COLORS[0] if names[index] == "Full model" else "#788796"
        bx.errorbar(values[index], j, xerr=sd[index], fmt="o", markersize=4.5, color=color,
                    elinewidth=1.2, capsize=3)
    bx.set_yticks(np.arange(len(rows)), [names[i] for i in order], fontsize=8)
    bx.invert_yaxis()
    bx.set(xlabel="MAE (a.u.) · supplied SD · lower is better", xlim=(0, 13))
    tidy(bx, grid=False); bx.grid(axis="x", color=".91"); bx.set_axisbelow(True)
    np.testing.assert_allclose([b.get_height() for b in bars], values)
    np.testing.assert_allclose([c.lines[0].get_xdata()[0] for c in bx.containers], ranked)
    intervals = [c.lines[2][0].get_segments()[0][:, 0] for c in bx.containers]
    np.testing.assert_allclose(intervals, np.column_stack((ranked - errors, ranked + errors)))
    return fig, {"categories": len(rows), "all_values_and_supplied_sd_preserved": True,
                 "display_order": [names[i] for i in order], "ordering": "ascending MAE",
                 "uncertainty": "supplied synthetic SD; not estimated by the renderer"}


def panels():
    rows = read("panels.csv")
    t = col(rows, "time")
    fig, left, right = frame("04 / CROSS-CONDITION COMPARISON", "independent y-scales", "shared y-scale")
    axes = left.subplots(3, 1, sharex=True)
    revised = right.subplots(3, 1, sharex=True, sharey=True)
    ranges = []
    for i, (ax, bx) in enumerate(zip(axes, revised)):
        y = col(rows, f"condition_{i+1}")
        for a in (ax, bx):
            a.plot(t, y, color=COLORS[i], linewidth=1.4)
            a.text(.02, .85, f"Condition {i+1}", transform=a.transAxes, fontsize=8)
            a.set(xlim=(0, 24)); tidy(a)
        ranges.append(list(ax.get_ylim()))
        bx.set(ylim=(0, 24)); bx.set_yticks([0, 10, 20])
        np.testing.assert_allclose(ax.lines[0].get_ydata(), bx.lines[0].get_ydata())
    for sub in (left, right):
        sub.supxlabel("Time (h)", fontsize=9); sub.supylabel("Absolute error (a.u.)", fontsize=9)
    assert len(set(tuple(a.get_ylim()) for a in revised)) == 1
    return fig, {"conditions": 3, "observations_per_condition": len(rows), "all_values_preserved": True,
                 "draft_y_limits": ranges, "reviewed_y_limits": [0, 24]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New directory")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Choose a new output directory")
    args.output.mkdir(parents=True)
    report = {"synthetic": True, "type": "illustrative custom-plot revisions; not an AI benchmark", "cases": {}}
    for name, build in [("multimodel", multimodel), ("density", density), ("labels", labels), ("panels", panels)]:
        source = DATA / (name + ".csv")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        with figure_context(profile="report", width_mm=320, height_mm=163, font_size=9):
            fig, checks = build()
            save_figure(fig, args.output / ("review-" + name), formats=("png", "pdf", "svg"), dpi=170)
            plt.close(fig)
        assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
        report["cases"][name] = {"input": str(source.relative_to(ROOT)), "sha256": digest,
                                  "source_unchanged": True, "checks": checks}
    (args.output / "visual-evidence.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
