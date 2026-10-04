# Research Figure Skill

[![Figure checks](https://github.com/wjulien888-tech/research-figure-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/wjulien888-tech/research-figure-skill/actions/workflows/ci.yml)

An Agent Skill for research figure generation, review and Matplotlib code improvement. Combines guidance adapted from the [RSS Data Visualisation Guide](https://royal-statistical-society.github.io/datavisguide/) with [SciencePlots](https://github.com/garrettj403/SciencePlots).

[中文](README.md) · [Integration](docs/installation.md) · [Examples](examples/README.md) · [Contributing](CONTRIBUTING.md)

## Capabilities

| Mode | Input | Output |
|---|---|---|
| Figure generation | Data, field definitions, units and comparison objective | Figures, scripts, configuration and processing records |
| Figure review | Image, caption and requirements | Located issues, rationale, recommendations and verification limits |
| Code improvement | Matplotlib script, input data and requested changes | Revised script, figures and change summary |

Three built-in entry points cover time series, observed/predicted scatter plots and grouped metric comparisons. No research domain or data units are assumed.

## Examples

![Synthetic time-series example](docs/images/timeseries.png)

Bundled examples are synthetic; `a.u.` means arbitrary units. [CSV files and configurations](examples/README.md) are provided for reproduction.

## Installation and compatibility

The package follows the [Agent Skills](https://agentskills.io/specification) directory format and has no model-specific API dependency.

- **Skills-compatible tools:** install `skills/research-figure/` in the host's skills directory.
- **General chat interfaces or custom agents:** load `SKILL.md` and the required reference files. Provide Python execution for rendering and image access for visual review.
- **Standalone use:** execute the Python scripts with a JSON configuration.

Project-level destinations include `.claude/skills/research-figure/` for Claude Code, `.cursor/skills/research-figure/` for Cursor and `.agents/skills/research-figure/` for Codex. See the [integration guide](docs/installation.md) for sources, setup and manual loading.

Instructions are model-independent; execution capabilities depend on the host. The Codex workflow and Python scripts have been validated. End-to-end tests for other hosts remain pending. A text-only model can assist with code and instructions but cannot claim to have rendered or visually inspected a figure.

Requires Python 3.10+, Matplotlib, NumPy and SciencePlots. TeX is not required by default. Non-Latin labels need a suitable installed font. The optional `agents/openai.yaml` contains Codex UI metadata; it is not required by the core workflow.

## Usage

After loading the skill, provide accessible input files and a task description:

```text
Use research-figure to compare Method A and Method B across experimental
conditions in results.csv. The metric is accuracy (%). Deliver PNG, PDF and
reproducible code. Check fields, units and missing values; preserve source data.
```

For review, provide an image and request located issues, rationale and recommendations. For code improvement, provide the script and its input data, specifying which calculations must remain unchanged. Invocation syntax is host-specific; the task description is portable.

## Command line

```bash
git clone https://github.com/wjulien888-tech/research-figure-skill.git
cd research-figure-skill
python3 -m venv .venv
.venv/bin/python -m pip install -r skills/research-figure/requirements.txt
.venv/bin/python skills/research-figure/scripts/plot_csv.py --config examples/timeseries/config.json
```

Outputs are written to `work/timeseries/`. Add `--overwrite` to replace existing outputs explicitly. On Windows, use `py -3 -m venv .venv` and `.venv\Scripts\python.exe`.

## Data and review principles

Preserve missing-data gaps and record filtering. Use common finite rows and equal axes for prediction comparisons. Retain zero baselines for bars, and require supplied values and definitions for error bars. Do not invent data, uncertainty or significance.

Rendered figures require visual inspection. Successful execution does not establish scientific validity or journal compliance. Screenshot-only review cannot validate source values. Complex figures require additional code and validation.

## Tests

```bash
.venv/bin/python skills/research-figure/tests/test_plot_csv.py
```

GitHub Actions runs regression checks and synthetic rendering on Python 3.10, 3.12 and 3.14. These checks cover data and rendering invariants, not every model decision or review judgment.

## License

Original code: **MIT**. RSS-adapted guidance: **CC BY 4.0**. SciencePlots: **MIT** dependency. See [LICENSE.md](LICENSE.md) and [upstream provenance](skills/research-figure/references/sources.md). This is an independent downstream project.
