#!/usr/bin/env python3
"""Reproduce deliberately flawed / reviewed figures from bundled synthetic CSVs.

This is an illustrative fixture, not a benchmark of an AI assistant.
Both columns use SciencePlots; fixes come from data and expression checks.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skills/research-figure/scripts"))
from plot_csv import load_table, prepare, draw, number, validate_config
from figure_tools import figure_context, save_figure


def before(ax, kind, config, data, rows):
    if kind == "metrics":
        positions = np.arange(len(data["categories"]))
        for i, model in enumerate(data["models"]):
            values = [data["entries"][category, model][0] for category in data["categories"]]
            ax.bar(positions + (i - .5) * .35, values, .35, label=model)
        ax.set_xticks(positions, data["categories"])
        ax.set(ylim=(3, 12), xlabel="Condition", ylabel="RMSE (a.u.)")
        ax.legend(loc="upper right", frameon=False)
        # Deliberate defects: nonzero baseline and omitted supplied error bars.
    elif kind == "parity":
        observed = np.array([number(row[config["actual"]], n, config["actual"]) for n, row in rows])
        for name in config["series"]:
            prediction = np.array([number(row[name], n, name) for n, row in rows])
            valid = np.isfinite(observed) & np.isfinite(prediction)
            ax.scatter(observed[valid], prediction[valid], s=16, alpha=.65,
                       label=f"{config['labels'][name]} (n={valid.sum()})")
        ax.set(xlim=(-5, 150), ylim=(-5, 95), xlabel="Observed (a.u.)", ylabel="Predicted (a.u.)")
        ax.legend(loc="lower right", frameon=False)
        # Deliberate defects: per-model masks, unequal ranges, no y=x, same markers.
    else:
        for name in config["series"]:
            finite = np.isfinite(data["values"][name])
            ax.plot(data["x"][finite], data["values"][name][finite], label=config["labels"][name])
        locator = mdates.AutoDateLocator(minticks=3, maxticks=5)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
        ax.set(xlabel=config["x_label"], ylabel=config["y_label"])
        ax.legend(loc="upper right", frameon=False)
        # Deliberate defects: connect across missing values and absent time rows.


def verify_after(ax, kind, data, log):
    """Assert the advertised changes against actual artists and parsed data."""
    if kind == "metrics":
        assert ax.get_ylim()[0] == 0
        assert len(ax.containers) == 4  # 2 BarContainers + 2 ErrorbarContainers.
        expected = [data["entries"][cat, model][0] for model in data["models"] for cat in data["categories"]]
        np.testing.assert_allclose([p.get_height() for p in ax.patches], expected)
        a = data["entries"]["Condition 3", "Method A"][0]
        b = data["entries"]["Condition 3", "Baseline"][0]
        return {"zero_baseline": True, "supplied_error_bars": True, "bar_values_preserved": True,
                "condition_3_value_ratio": b / a,
                "condition_3_draft_visible_bar_ratio": (b - 3) / (a - 3)}
    if kind == "parity":
        assert ax.get_xlim() == ax.get_ylim() and ax.get_aspect() == 1
        assert [len(c.get_offsets()) for c in ax.collections] == [log["used_rows"]] * 2
        np.testing.assert_equal(ax.lines[0].get_xdata(), ax.lines[0].get_ydata())
        return {"equal_limits_and_aspect": True, "reference_y_equals_x": True,
                "common_samples_per_model": log["used_rows"], "excluded_csv_rows": log["excluded_csv_rows"]}
    for line, values in zip(ax.lines, data["values"].values()):
        rendered = np.asarray(line.get_ydata())
        np.testing.assert_allclose(rendered[np.isfinite(rendered)], values[np.isfinite(values)])
    assert np.isnan(ax.lines[0].get_ydata()).sum() == len(data["gaps"])
    assert np.isnan(ax.lines[1].get_ydata()).sum() == len(data["gaps"]) + 1
    return {"finite_values_preserved": True, "missing_counts": log["missing_counts"],
            "gap_before_csv_rows": log["gap_before_csv_rows"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New directory")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error("Output directory already exists; choose a new directory")
    output.mkdir(parents=True)
    evidence = {"synthetic": True, "fixture": "deliberately constructed issues; not an AI benchmark", "cases": {}}
    subtitles = {
        "metrics": ("Truncated baseline; supplied uncertainty omitted", "Zero baseline; supplied SD; model hatching"),
        "parity": ("Different samples; unequal axes; no reference", "Common samples (n=89); equal axes; y = x"),
        "timeseries": ("Missing observations connected as a trend", "Missing observations remain visible gaps"),
    }
    for kind in ("metrics", "parity", "timeseries"):
        config_path = ROOT / "examples" / kind / "config.json"
        config = validate_config(json.loads(config_path.read_text(encoding="utf-8")))
        source = config_path.parent / config["input"]
        original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        fields, rows = load_table(source)
        data, log = prepare(config, fields, rows)
        with figure_context(profile="report", width_mm=290, height_mm=132, font_size=10):
            fig, axes = plt.subplots(1, 2, layout="constrained", gridspec_kw={"wspace": .12})
            before(axes[0], kind, config, data, rows)
            draw(config, data, ax=axes[1])  # Use the actual skill renderer, not an imitation.
            checked = verify_after(axes[1], kind, data, log)
            for ax, title, subtitle in zip(axes, ("Styled draft | constructed issues", "Reviewed figure"), subtitles[kind]):
                ax.set_title("", loc="center")
                ax.set_title(title + "\n" + subtitle, fontsize=10.5, pad=12, loc="left")
            fig.suptitle("RESEARCH FIGURE  /  " + kind.upper() + "\nSIMULATED DATA · BOTH PANELS USE SCIENCEPLOTS", fontsize=11, fontweight="bold")
            save_figure(fig, output / ("review-" + kind), formats=("png", "pdf", "svg"), dpi=180)
            plt.close(fig)
        assert hashlib.sha256(source.read_bytes()).hexdigest() == original_hash
        evidence["cases"][kind] = {"source": str(source.relative_to(ROOT)), "sha256": original_hash,
                                    "source_unchanged": True, "checks": checked}
    (output / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
