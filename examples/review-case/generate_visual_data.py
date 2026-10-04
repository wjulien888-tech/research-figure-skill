#!/usr/bin/env python3
"""Generate synthetic fixtures for the visual review gallery; never overwrite."""
import argparse
import csv
from pathlib import Path
import numpy as np


def generate(output):
    output.mkdir(parents=True, exist_ok=False)
    rng = np.random.default_rng(20261005)
    t = np.linspace(0, 24, 121)
    reference = 50 + 16 * np.sin(t / 3) + 7 * np.cos(t / 1.5)
    models = [reference + (i - 2.5) * 1.3 + (1.3 + i * .45) * np.sin(t / (1.1 + i * .15))
              + rng.normal(0, .65, len(t)) for i in range(6)]
    x = np.concatenate([rng.normal(30, 7, 4000), rng.normal(70, 8, 2000)])
    y = .88 * x + 9 + rng.normal(0, 2.8 + .075 * x)
    names = ["Full model", "Without feature selection", "Without normalization", "Without temporal context",
             "Without regularization", "Without calibration", "Linear baseline", "Tree baseline",
             "Reduced training set", "Noisy input condition"]
    means = [4.7, 6.3, 7.6, 9.1, 6.8, 5.6, 11.2, 8.4, 9.8, 10.5]
    supplied_sd = [.25, .42, .55, .67, .47, .31, .78, .61, .70, .73]
    shape = 1 + .28 * np.sin(t / 2.8) + .10 * np.cos(t / 1.2)
    fixtures = {
        "multimodel.csv": (["time", "observed", *[f"method_{i+1}" for i in range(6)]], zip(t, reference, *models)),
        "density.csv": (["observed", "predicted"], zip(x, y)),
        "labels.csv": (["method", "mae", "sd"], zip(names, means, supplied_sd)),
        "panels.csv": (["time", "condition_1", "condition_2", "condition_3"], zip(t, shape, shape * 5, shape * 16)),
    }
    for name, (header, rows) in fixtures.items():
        with (output / name).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(header)
            for row in rows:
                writer.writerow([v if isinstance(v, str) else f"{v:.6f}" for v in row])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    generate(parser.parse_args().output)
