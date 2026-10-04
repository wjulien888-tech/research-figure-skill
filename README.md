# Research Figure Skill

[![Figure checks](https://github.com/wjulien888-tech/research-figure-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/wjulien888-tech/research-figure-skill/actions/workflows/ci.yml)

面向科研图表生成、审查与代码改进的 Agent Skill。基于 [RSS Data Visualisation Guide](https://royal-statistical-society.github.io/datavisguide/) 和 [SciencePlots](https://github.com/garrettj403/SciencePlots)，提供可复现的绘图流程与检查规则。

[English](README.en.md) · [安装与接入](docs/installation.md) · [使用指南](docs/usage.md) · [示例数据](examples/README.md) · [贡献指南](CONTRIBUTING.md)

## 功能

| 模式 | 输入 | 输出 |
|---|---|---|
| 图表生成 | 实验数据、字段定义、单位、比较目标 | PNG/PDF/SVG、绘图代码、配置及处理记录 |
| 图表审查 | 图片、图注、使用要求 | 问题定位、依据、修改建议及核验范围 |
| 代码改进 | Matplotlib 脚本、输入数据、修改要求 | 新版脚本、图表及变更说明 |

内置时间序列对比、预测值与真实值散点图、分条件指标对比三个绘图入口。适用于论文、报告与学术演示，不预设学科或数据单位。

## 示例

| 时间序列 | 预测对比 | 指标对比 |
|---|---|---|
| ![时间序列示例](docs/images/timeseries.png) | ![预测散点示例](docs/images/parity.png) | ![指标对比示例](docs/images/metrics.png) |

示例使用模拟数据；`a.u.` 表示任意单位。对应 [CSV 与配置](examples/README.md) 可用于复现。

## 安装与兼容性

项目采用 [Agent Skills](https://agentskills.io/specification) 目录结构，不依赖特定模型 API。可通过以下方式接入：

| 接入方式 | 配置 |
|---|---|
| 支持 Agent Skills 的工具 | 将 `skills/research-figure/` 安装至工具识别的技能目录 |
| 通用大模型对话或自建 Agent | 加载 `SKILL.md` 及相关参考文件；需要出图时提供 Python 执行环境 |
| 独立脚本 | 安装 Python 依赖，按 JSON 配置执行绘图 |

[安装指南](docs/installation.md) 提供 Claude Code、Cursor、Codex 的目录配置，以及通用对话和 API 接入方式。技能指令不绑定模型；文件访问、代码执行和图像查看能力由所用平台提供。已完成 Codex 流程验证及 Python 脚本测试，其他平台的端到端验证待补充。

绘图依赖 Python 3.10+、Matplotlib、NumPy 和 SciencePlots，默认无需 LaTeX。中文标签需要可用的中文字体。

## 使用

加载技能后，提供输入文件及任务要求。以下请求不依赖特定工具的调用语法。

**图表生成**

```text
使用 research-figure，根据 results.csv 比较不同实验条件下方法 A 和方法 B 的准确率（%）。
使用中文标签，输出 PNG、PDF 和可复现代码。核对字段、单位与缺失值，保留原始数据。
```

**图表审查**

```text
使用 research-figure 审查附件图表，检查坐标轴、单位、图例、配色和字号。
列出问题位置、依据与修改建议，并注明仅凭图片无法核验的内容。
```

**代码改进**

```text
使用 research-figure 修改 plot.py，输入数据已附上。
保留数据处理与指标计算，调整字体和布局，图宽设为 90 mm。另存脚本并导出新图。
```

输入格式、交付内容及迭代方式见 [使用指南](docs/usage.md)。

## 命令行

```bash
git clone https://github.com/wjulien888-tech/research-figure-skill.git
cd research-figure-skill
python3 -m venv .venv
.venv/bin/python -m pip install -r skills/research-figure/requirements.txt
.venv/bin/python skills/research-figure/scripts/plot_csv.py --config examples/timeseries/config.json
```

输出位于 `work/timeseries/`。默认不覆盖已有文件；重新生成时显式添加 `--overwrite`。Windows 使用 `py -3 -m venv .venv` 创建环境，后续解释器路径为 `.venv\Scripts\python.exe`。

## 数据与审查原则

- 保留缺失断线，记录筛选和转换，不擅自插值、平滑或删除异常值。
- 预测对比采用共同有效样本、等比例坐标及 `y=x` 参考线。
- 柱图保留零基线；误差线必须有明确数值与定义。
- 导出后检查实际图像；渲染成功不等于科学结论或期刊要求已核验。
- 截图审查不用于还原原始数值或判断统计显著性。

复杂图形需另行编写和验证绘图代码。仓库仅包含模拟数据；`work/` 默认不纳入版本控制。

## 测试

```bash
.venv/bin/python skills/research-figure/tests/test_plot_csv.py
```

GitHub Actions 在 Python 3.10、3.12、3.14 上运行回归测试和模拟出图。检查覆盖数据处理、导出尺寸与脚本复现，不代替对模型选图判断和审查质量的评估。

## 许可

原创代码采用 **MIT**；RSS 改编指南采用 **CC BY 4.0**；SciencePlots 为 **MIT** 依赖。各部分范围、署名和改编记录见 [LICENSE.md](LICENSE.md) 与 [来源说明](skills/research-figure/references/sources.md)。本项目为独立下游项目。
