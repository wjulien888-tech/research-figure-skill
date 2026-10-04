# Examples / 可复现示例

All values are synthetic and generated with NumPy seed `20261004`. These are plotting examples, not evidence of model quality. `a.u.` means arbitrary units. Error bars in the metric example are illustrative supplied values, not estimated from repeated experiments.

所有示例都是模拟数据，不代表任何真实实验；误差条也是预设的演示值。CSV 与配置可直接读取，不含本机绝对路径。

| Example | Input | Configuration | What to inspect |
|---|---|---|---|
| Time series | [CSV](timeseries/data.csv) | [JSON](timeseries/config.json) | One missing prediction and two absent time rows; gaps remain visible. |
| Observed vs. predicted | [CSV](parity/data.csv) | [JSON](parity/config.json) | One row missing from baseline; both methods use 89 common rows out of 90. |
| Metric comparison | [CSV](metrics/data.csv) | [JSON](metrics/config.json) | A zero baseline, grouped conditions, supplied illustrative SD bars. |

From the repository root, after installing dependencies as described in the main README:

```bash
.venv/bin/python skills/research-figure/scripts/plot_csv.py --config examples/timeseries/config.json
.venv/bin/python skills/research-figure/scripts/plot_csv.py --config examples/parity/config.json
.venv/bin/python skills/research-figure/scripts/plot_csv.py --config examples/metrics/config.json
```

Outputs go to ignored `work/<example>/` directories. Use a new output directory or explicitly add `--overwrite` to rerun. On Windows, replace `.venv/bin/python` with `.venv\Scripts\python.exe`.

To create fresh synthetic input files and render all three examples:

```bash
.venv/bin/python skills/research-figure/scripts/demo.py --output work/demo-new --render
```

The output directory must not already exist. The generator uses English labels so it runs without CJK fonts. You can set Chinese labels in the configuration when a suitable local font is available; see [plotting reference](../skills/research-figure/references/plotting.md).

Published preview PNGs are in [docs/images](../docs/images). Generated logs and resolved configurations contain runtime paths for reproducibility, so they are intentionally excluded from this repository. When sharing your own logs, remove machine-specific paths and sensitive content.
