#!/usr/bin/env python3
"""Reproducible CSV figures; rendering logs are not scientific review results."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import math
from pathlib import Path
import shutil
import sys
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from figure_tools import figure_context, save_figure, positive


COMMON = {"kind", "input", "output_dir", "title", "x_label", "y_label",
          "profile", "synthetic", "labels", "styles", "width_mm", "height_mm",
          "font_size", "font_family", "formats", "dpi"}
SPECIFIC = {
    "timeseries": {"x", "x_type", "series", "expected_interval"},
    "parity": {"actual", "series"},
    "metrics": {"category", "model", "value", "error", "error_type"},
}
MISSING = {"", "na", "nan", "null", "none"}
LINESTYLES = ["-", "--", "-.", ":"]
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "<"]
HATCHES = ["", "//", "\\\\", "xx", "..", "++", "oo", "--"]


def number(cell, row, column, allow_missing=True):
    if cell.strip().lower() in MISSING:
        if allow_missing:
            return math.nan
        raise ValueError(f"CSV row {row}, {column}: missing value")
    try:
        value = float(cell)
    except ValueError as exc:
        raise ValueError(f"CSV row {row}, {column}: not numeric ({cell!r})") from exc
    if not math.isfinite(value):
        raise ValueError(f"CSV row {row}, {column}: infinite/non-finite value")
    return value


def validate_config(c):
    if not isinstance(c, dict) or c.get("kind") not in SPECIFIC:
        raise ValueError("kind must be timeseries, parity or metrics")
    unknown = set(c) - COMMON - SPECIFIC[c["kind"]]
    if unknown:
        raise ValueError(f"Unknown configuration keys: {sorted(unknown)}")
    for key in ("input", "output_dir", "x_label", "y_label"):
        if not isinstance(c.get(key), str) or not c[key].strip():
            raise ValueError(f"{key} must be a nonempty string")
    if not isinstance(c.get("synthetic"), bool):
        raise ValueError("synthetic must explicitly be true or false")
    if "title" in c and not isinstance(c["title"], str):
        raise ValueError("title must be a string")
    labels = c.get("labels", {})
    if not isinstance(labels, dict) or any(not isinstance(v, str) for v in labels.values()):
        raise ValueError("labels must map names to strings")
    if c["kind"] in {"timeseries", "parity"}:
        series = c.get("series")
        if not isinstance(series, list) or not series or any(not isinstance(s, str) or not s for s in series):
            raise ValueError("series must be a nonempty list of column names")
        if len(set(series)) != len(series):
            raise ValueError("series contains duplicate columns")
    fields = {"timeseries": ["x", "x_type"], "parity": ["actual"],
              "metrics": ["category", "model", "value"]}[c["kind"]]
    for field in fields:
        if not isinstance(c.get(field), str) or not c[field]:
            raise ValueError(f"Missing field: {field}")
    if c["kind"] == "timeseries" and c["x_type"] not in {"number", "datetime"}:
        raise ValueError("x_type must be number or datetime")
    if c["kind"] == "timeseries" and c["x"] in c["series"]:
        raise ValueError("x cannot also be a y series")
    if c["kind"] == "parity" and c["actual"] in c["series"]:
        raise ValueError("actual cannot also be a prediction series")
    if "error" in c and (not isinstance(c.get("error_type"), str) or not c["error_type"].strip()):
        raise ValueError("error_type must explain the supplied error column")
    if "error" in c and (not isinstance(c["error"], str) or not c["error"].strip()):
        raise ValueError("error must be a nonempty column name")
    if "error_type" in c and "error" not in c:
        raise ValueError("error_type requires an error column")
    if c.get("profile", "report") not in {"paper", "report", "slides"}:
        raise ValueError("Unknown profile")
    for key in ("width_mm", "height_mm", "font_size", "dpi", "expected_interval"):
        if key in c:
            positive(c[key], key)
    formats = c.get("formats", ["png", "pdf", "svg"])
    if not isinstance(formats, list) or not formats or any(f not in {"png", "pdf", "svg"} for f in formats):
        raise ValueError("formats must be a nonempty list of png, pdf and/or svg")
    return c


def load_table(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        try:
            fields = next(reader)
        except StopIteration as exc:
            raise ValueError("Empty CSV") from exc
        if not all(fields) or len(set(fields)) != len(fields):
            raise ValueError("CSV column names must be nonempty and unique")
        records = []
        for row in reader:
            if len(row) != len(fields):
                raise ValueError(f"CSV line {reader.line_num}: incorrect number of fields")
            records.append((reader.line_num, dict(zip(fields, row))))
    if not records:
        raise ValueError("CSV has no data rows")
    return set(fields), records


def prepare(c, fields, rows):
    kind = c["kind"]
    required = ([c["x"], *c["series"]] if kind == "timeseries" else
                [c["actual"], *c["series"]] if kind == "parity" else
                [c["category"], c["model"], c["value"]] + ([c["error"]] if "error" in c else []))
    if set(required) - fields:
        raise ValueError(f"Missing CSV columns: {sorted(set(required) - fields)}")
    log = {"input_rows": len(rows), "notes": [], "missing_counts": {}}
    if kind in {"timeseries", "parity"}:
        columns = list(dict.fromkeys(c["series"] + ([c["actual"]] if kind == "parity" else [])))
        values = {name: np.array([number(row[name], n, name) for n, row in rows]) for name in columns}
        log["missing_counts"] = {key: int(np.isnan(v).sum()) for key, v in values.items()}
        if kind == "parity":
            mask = np.logical_and.reduce([np.isfinite(v) for v in values.values()])
            if not mask.any():
                raise ValueError("No common finite rows across actual and predictions")
            log["used_rows"] = int(mask.sum())
            log["excluded_csv_rows"] = [rows[i][0] for i in np.flatnonzero(~mask)]
            log["notes"].append("All models use the same finite-row mask; excluded rows are listed.")
            return {"values": {key: v[mask] for key, v in values.items()}}, log
        x = []
        timezone_flags = set()
        for n, row in rows:
            if c["x_type"] == "number":
                x.append(number(row[c["x"]], n, c["x"], allow_missing=False))
            else:
                try:
                    dt = datetime.fromisoformat(row[c["x"]].strip().replace("Z", "+00:00"))
                except ValueError as exc:
                    raise ValueError(f"CSV row {n}: invalid ISO datetime") from exc
                aware = dt.utcoffset() is not None
                timezone_flags.add(aware)
                x.append(mdates.date2num(dt))
        if len(timezone_flags) > 1:
            raise ValueError("Cannot mix timezone-aware and timezone-naive datetimes")
        x = np.array(x)
        if len(x) > 1 and not np.all(np.diff(x) > 0):
            raise ValueError("x must be strictly increasing; duplicates or unsorted rows require review")
        if any(not np.isfinite(v).any() for v in values.values()):
            raise ValueError("Every series must have at least one finite observation")
        gaps = []
        if "expected_interval" in c:
            interval = positive(c["expected_interval"], "expected_interval")
            if c["x_type"] == "datetime":
                interval /= 86400
            gaps = (np.flatnonzero(np.diff(x) > interval * 1.5) + 1).tolist()
        else:
            log["notes"].append("No expected_interval supplied: absent time-row gaps were not checked.")
        log["gap_before_csv_rows"] = [rows[i][0] for i in gaps]
        log["used_rows"] = len(rows)
        if timezone_flags == {True}:
            log["notes"].append("Timezone-aware values displayed in UTC; original offsets remain in input.")
        return {"x": x, "values": values, "gaps": gaps, "utc": timezone_flags == {True}}, log
    categories, models, entries = [], [], {}
    for n, row in rows:
        cat, model = row[c["category"]], row[c["model"]]
        if not cat.strip() or not model.strip():
            raise ValueError(f"CSV row {n}: category and model cannot be empty")
        if (cat, model) in entries:
            raise ValueError(f"Duplicate category/model {cat!r}/{model!r}; choose aggregation before plotting")
        if cat not in categories: categories.append(cat)
        if model not in models: models.append(model)
        value = number(row[c["value"]], n, c["value"])
        error = number(row[c["error"]], n, c["error"]) if "error" in c else math.nan
        if "error" in c and np.isfinite(value) and not np.isfinite(error):
            raise ValueError(f"CSV row {n}: a finite value needs its supplied error value")
        if np.isfinite(error) and error < 0:
            raise ValueError(f"CSV row {n}: error must be nonnegative")
        if "error" in c and not np.isfinite(value) and np.isfinite(error):
            raise ValueError(f"CSV row {n}: error exists without a finite value")
        entries[cat, model] = (value, error)
    if not any(np.isfinite(v[0]) for v in entries.values()):
        raise ValueError("No finite metric values")
    log["missing_combinations"] = [[a, b] for a in categories for b in models if (a, b) not in entries or not np.isfinite(entries[a, b][0])]
    log["used_rows"] = sum(np.isfinite(v[0]) for v in entries.values())
    log["used_rows"] = int(log["used_rows"])
    if "error" in c: log["error_type"] = c["error_type"]
    log["notes"].append("Metric comparability and units are user-provided; no aggregation or significance tests performed.")
    return {"categories": categories, "models": models, "entries": entries}, log


def draw(c, data):
    fig, ax = plt.subplots(layout="constrained")
    labels = c.get("labels", {})
    if c["kind"] == "timeseries":
        for i, name in enumerate(c["series"]):
            x, y = data["x"], data["values"][name]
            # Add a NaN before the post-gap point, keeping all observed values.
            plot_x = np.insert(x, data["gaps"], x[data["gaps"]])
            plot_y = np.insert(y, data["gaps"], np.nan)
            ax.plot(plot_x, plot_y, label=labels.get(name, name),
                    linestyle=LINESTYLES[i % len(LINESTYLES)],
                    marker=MARKERS[i % len(MARKERS)] if len(x) <= 30 else None,
                    markersize=3, linewidth=1.2)
        if c["x_type"] == "datetime":
            locator = mdates.AutoDateLocator(minticks=3, maxticks=6, tz=timezone.utc)
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator, tz=timezone.utc))
    elif c["kind"] == "parity":
        actual = data["values"][c["actual"]]
        all_values = np.concatenate(list(data["values"].values()))
        low, high = float(all_values.min()), float(all_values.max())
        pad = 0.05 * (high - low) if high > low else max(abs(low) * .05, .5)
        limits = [low - pad, high + pad]
        ax.plot(limits, limits, color="0.45", linewidth=1, linestyle="--", label="y = x", zorder=1)
        for i, name in enumerate(c["series"]):
            ax.scatter(actual, data["values"][name], s=15, alpha=.65,
                       marker=MARKERS[i % len(MARKERS)], label=labels.get(name, name), zorder=2)
        ax.set(xlim=limits, ylim=limits)
        ax.set_aspect("equal", adjustable="box")
    else:
        x = np.arange(len(data["categories"]))
        count = len(data["models"])
        width = .8 / count
        for i, model in enumerate(data["models"]):
            entries = [data["entries"].get((cat, model), (math.nan, math.nan)) for cat in data["categories"]]
            vals = np.array([e[0] for e in entries])
            errs = np.array([e[1] for e in entries]) if "error" in c else None
            ax.bar(x + (i - (count - 1) / 2) * width, vals, width,
                   label=labels.get(model, model), hatch=HATCHES[i % len(HATCHES)],
                   edgecolor="0.25", linewidth=.45, yerr=errs,
                   capsize=2 if errs is not None else 0)
        ax.set_xticks(x, [labels.get(s, s) for s in data["categories"]])
        # Autoscaling already includes zero for normal bars; explicitly retain it.
        low, high = ax.get_ylim()
        ax.set_ylim(min(0, low), max(0, high))
        ax.axhline(0, color="0.3", linewidth=.6)
    xlabel = c["x_label"]
    if c["kind"] == "timeseries" and data.get("utc"):
        xlabel += " [UTC]"
    ylabel = c["y_label"]
    if c["kind"] == "metrics" and "error" in c:
        ylabel += f"\nError bars: {c['error_type']}"
    title = c.get("title", "")
    if c["synthetic"]:
        title = (title + "\n" if title else "") + "SIMULATED DATA"
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.legend(frameon=False, loc="best")
    return fig


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    config_path = args.config.resolve()
    c = validate_config(json.loads(config_path.read_text(encoding="utf-8")))
    input_path = (config_path.parent / c["input"]).resolve()
    output = (config_path.parent / c["output_dir"]).resolve()
    fields, rows = load_table(input_path)
    data, log = prepare(c, fields, rows)
    log.update({"kind": c["kind"], "input": str(input_path),
                "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
                "synthetic_declared": c["synthetic"],
                "scientific_review": "not_performed_by_script",
                "visual_review": "required_after_rendering"})
    if args.check_only:
        print(json.dumps(log, ensure_ascii=False, indent=2))
        return 0
    formats = c.get("formats", ["png", "pdf", "svg"])
    names = ["figure." + f for f in formats] + ["render_log.json", "config.json", "plot_csv.py", "figure_tools.py", "LICENSE.md", "requirements.txt", "licenses/SciencePlots-MIT.txt"]
    existing = [n for n in names if (output / n).exists()]
    if existing and not args.overwrite:
        raise ValueError(f"Output files already exist: {existing}. Use a new directory or --overwrite.")
    if input_path in [(output / n).resolve() for n in names]:
        raise ValueError("Input would be overwritten by output")
    texts = [c.get("title", ""), c["x_label"], c["y_label"], *c.get("labels", {}).values()]
    texts += c.get("series", []) + data.get("categories", []) + data.get("models", [])
    if "error_type" in c: texts += ["Error bars: " + c["error_type"]]
    if c["synthetic"]: texts += ["SIMULATED DATA"]
    kwargs = {key: c[key] for key in ("profile", "styles", "width_mm", "height_mm", "font_size", "font_family") if key in c}
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        with figure_context(texts=texts, **kwargs) as style:
            fig = draw(c, data)
            try:
                paths = save_figure(fig, output / "figure", formats=formats, dpi=c.get("dpi", 300))
            finally:
                plt.close(fig)
    log["style"] = style
    log["warnings"] = list(dict.fromkeys(str(w.message) for w in captured))
    log["versions"] = {n: version(n) for n in ("matplotlib", "numpy", "SciencePlots")}
    log["outputs"] = [str(p) for p in paths]
    log["reproduce"] = "python plot_csv.py --config config.json --overwrite"
    resolved = dict(c, input=str(input_path), output_dir=".")
    (output / "config.json").write_text(json.dumps(resolved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "render_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    script_root = Path(__file__).resolve().parent
    for name in ("plot_csv.py", "figure_tools.py"):
        target = output / name
        source = script_root / name
        if target.resolve() != source.resolve():
            shutil.copy2(source, target)
    # Copy notices with the standalone scripts. Support reruns from an export folder.
    package_root = script_root.parent if (script_root.parent / "SKILL.md").exists() else script_root
    for name in ("LICENSE.md", "requirements.txt", "licenses/SciencePlots-MIT.txt"):
        source, target = package_root / name, output / name
        if source.exists() and source.resolve() != target.resolve():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    print(json.dumps(log, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
