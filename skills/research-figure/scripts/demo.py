#!/usr/bin/env python3
"""Generate three explicitly synthetic datasets and runnable example configs."""
import argparse
import csv
from datetime import datetime, timedelta
import json
from pathlib import Path
import subprocess
import sys

import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New output directory")
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    root = args.output.resolve()
    if root.exists():
        parser.error("Choose a new output directory; demo never overwrites files")
    root.mkdir(parents=True)
    rng = np.random.default_rng(20261004)
    t = np.arange(49)
    actual = 70 * np.maximum(0, np.sin(np.pi * t / 48))
    predicted = np.maximum(0, actual + rng.normal(0, 4, len(t)))
    start = datetime(2026, 10, 1, 6)
    time_rows = []
    for i in range(len(t)):
        if i in (23, 24):
            continue  # Demonstrates an absent-time-row gap, not interpolation.
        time_rows.append([(start + timedelta(minutes=15 * i)).isoformat(),
                          f"{actual[i]:.3f}", "" if i == 12 else f"{predicted[i]:.3f}"])
    obs = rng.uniform(0, 80, 90)
    parity_rows = [[f"{a:.3f}", f"{max(0, a + e):.3f}",
                    "" if i == 4 else f"{max(0, a + b):.3f}"]
                   for i, (a, e, b) in enumerate(zip(obs, rng.normal(0, 4, 90), rng.normal(0, 8, 90))) ]
    metric_rows = [[scenario, model, value, sd]
                   for scenario, values in [("Condition 1", [(4.1, .4), (6.0, .7)]),
                                             ("Condition 2", [(7.2, .8), (10.5, 1.1)]),
                                             ("Condition 3", [(3.3, .3), (5.2, .5)])]
                   for model, (value, sd) in zip(("Method A", "Baseline"), values)]
    examples = {
        "timeseries": (["time", "actual", "predicted"], time_rows, {
            "x": "time", "x_type": "datetime", "series": ["actual", "predicted"],
            "expected_interval": 900, "x_label": "Time", "y_label": "Response (a.u.)",
            "title": "Time-series comparison", "labels": {"actual": "Observed", "predicted": "Predicted"}}),
        "parity": (["actual", "model_a", "baseline"], parity_rows, {
            "actual": "actual", "series": ["model_a", "baseline"],
            "x_label": "Observed (a.u.)", "y_label": "Predicted (a.u.)",
            "title": "Observed vs. predicted", "labels": {"model_a": "Method A", "baseline": "Baseline"},
            "height_mm": 135}),
        "metrics": (["scenario", "model", "rmse", "sd"], metric_rows, {
            "category": "scenario", "model": "model", "value": "rmse", "error": "sd",
            "error_type": "SD (illustrative)", "x_label": "Condition", "y_label": "RMSE (a.u.)",
            "title": "Metric comparison"}),
    }
    for kind, (fields, rows, extra) in examples.items():
        folder = root / kind
        folder.mkdir()
        with (folder / "data.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(fields)
            writer.writerows(rows)
        config = dict(kind=kind, input="data.csv", output_dir="rendered", synthetic=True,
                      profile="report", **extra)
        config_path = folder / "input_config.json"
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.render:
            result = subprocess.run([sys.executable, str(Path(__file__).with_name("plot_csv.py")),
                                     "--config", str(config_path)], capture_output=True, text=True)
            if result.returncode:
                print(result.stderr, file=sys.stderr)
                return result.returncode
        print(config_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
