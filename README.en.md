# Research Figure Skill

[![Figure checks](https://github.com/wjulien888-tech/research-figure-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/wjulien888-tech/research-figure-skill/actions/workflows/ci.yml)

[![Upstream: RSS](https://img.shields.io/badge/Guidance-Royal%20Statistical%20Society-243746)](https://github.com/royal-statistical-society/datavisguide)
[![SciencePlots stars](https://img.shields.io/github/stars/garrettj403/SciencePlots?style=flat&label=SciencePlots%20stars)](https://github.com/garrettj403/SciencePlots)

**Turn Royal Statistical Society visualization guidance and SciencePlots into an executable research figure generation and review skill.**

Review data, figures or Matplotlib code; revise their presentation and deliver reproducible outputs. The workflow is model-independent and assumes no research domain or units.

[中文](README.md) · [Review cases](examples/review-case/README.md) · [Integration](docs/installation.md) · [Contributing](CONTRIBUTING.md)

## Upstream foundations

| Project | Source | Role in this skill |
|---|---|---|
| **[RSS Data Visualisation Guide](https://github.com/royal-statistical-society/datavisguide)** | *Best Practices for Data Visualisation*, published by the Royal Statistical Society | 12 adapted review rules covering axes, aspect ratios, colors, accessibility and annotations |
| **[SciencePlots](https://github.com/garrettj403/SciencePlots)** | Matplotlib scientific styles maintained by John Garrett and contributors | Actual style dependency, with no-TeX defaults, font checks and dimension-preserving export |

The project adds six data/research constraints, common-sample handling, missing-data records and reproducible scripts. See the [rule mapping](skills/research-figure/references/review-rules.md) and [versioned provenance](skills/research-figure/references/sources.md). The Stars badge belongs to SciencePlots. This is an independent downstream project.

## Review cases

**The same source data can produce a different impression when its presentation changes.**

Both panels below use SciencePlots. The left panel deliberately truncates the baseline and omits supplied uncertainty; the right panel uses the skill renderer to restore zero and display the supplied SD values.

![Synthetic metric comparison before and after review](docs/images/review-metrics.png)

In the last group, values **3.3 and 5.2** appear as visible bar lengths with a ratio of **7.33:1** on a baseline truncated at 3. Restoring zero gives the actual value ratio, **1.58:1**, without changing the values.

| Case | Issue | Revision |
|---|---|---|
| Metrics | Truncated baseline; omitted supplied SD | Zero baseline, defined error bars, model hatching |
| Prediction comparison | 90/89 samples; unequal axes | 89 common samples with excluded-row record, equal axes, y=x |
| Time series | Lines bridge missing observations | Visible gaps; finite source values preserved |

These deliberately constructed synthetic fixtures illustrate the rules; they are not evaluations of other tools or AI models. [Full cases](examples/review-case/README.md) include images, reasoning, scripts and verification records. Sample selection requires data or code, not just a screenshot.

## Workflow

**Input → data and expression checks → revision → visual inspection → reproducible delivery**

| Mode | Input | Output |
|---|---|---|
| Figure generation | Data, definitions, units and objective | Figures, scripts, configuration and processing records |
| Figure review | Image, caption and supporting data when available | Located issues, rationale and verification limits |
| Code improvement | Matplotlib code, data and requirements | Revised code, figures and change summary |

Rules guide the assistant; scripts perform deterministic processing and rendering. Built-in entry points cover time series, prediction scatter and grouped metrics. Complex figures require additional code and validation.

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
