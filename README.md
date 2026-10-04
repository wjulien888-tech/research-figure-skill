# Research Figure Skill

[![Figure checks](https://github.com/wjulien888-tech/research-figure-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/wjulien888-tech/research-figure-skill/actions/workflows/ci.yml)

[![Upstream: RSS](https://img.shields.io/badge/Guidance-Royal%20Statistical%20Society-243746)](https://github.com/royal-statistical-society/datavisguide)
[![SciencePlots stars](https://img.shields.io/github/stars/garrettj403/SciencePlots?style=flat&label=SciencePlots%20stars)](https://github.com/garrettj403/SciencePlots)

**将英国皇家统计学会的数据可视化指南与 SciencePlots 转化为可执行的科研绘图与审查 Skill。**

从实验数据、已有图或绘图代码出发，完成表达审查、图表修订与可复现交付。兼容不同模型与 Agent 工具，不预设学科或数据单位。

[English](README.en.md) · [审查案例](examples/review-case/README.md) · [安装与接入](docs/installation.md) · [使用指南](docs/usage.md) · [贡献指南](CONTRIBUTING.md)

## 上游基础

| 上游项目 | 项目来源 | 本 Skill 的使用方式 |
|---|---|---|
| **[RSS Data Visualisation Guide](https://github.com/royal-statistical-society/datavisguide)** | 英国皇家统计学会发布的《Best Practices for Data Visualisation》 | 将坐标、比例、配色、可访问性和标注原则整理为 12 项可追溯审查规则 |
| **[SciencePlots](https://github.com/garrettj403/SciencePlots)** | John Garrett 等贡献者维护的 Matplotlib 科研绘图样式库 | 使用真实样式依赖完成排版，提供无 LaTeX 默认配置、字体检查与尺寸保留导出 |

在此基础上，本项目增加 **6 项数据与科研约束**，以及共同样本处理、缺失记录、可执行绘图和代码交付。完整映射见 [审查规则](skills/research-figure/references/review-rules.md)，引用版本与许可见 [来源记录](skills/research-figure/references/sources.md)。上方 Stars 徽章展示的是 SciencePlots 上游数据；本项目为独立下游项目。

## 审查案例

**同一份数据，图表表达可能改变读者对结果的判断。**

下例两侧均使用 SciencePlots。左侧截断柱图基线并省略已有误差线；右侧由本项目绘图入口恢复零基线、展示所提供的 SD，并增加纹理区分。

![相同模拟数据的柱图审查前后对照](docs/images/review-metrics.png)

最后一组数值为 **3.3 与 5.2**。从 3 开始的截断轴将可见柱长比放大到约 **7.33∶1**；恢复零基线后为原始数值比约 **1.58∶1**。修订没有改变这些数值。

| 案例 | 具体问题 | 修订结果 | 依据 |
|---|---|---|---|
| [指标对比](examples/review-case/README.md#指标对比) | 截断基线放大差异；省略已提供的 SD | 保留零点、展示误差定义、增加纹理 | RSS 改编规则 R03/R08；项目规则 D03 |
| [预测对比](examples/review-case/README.md#预测对比) | 两个模型分别使用 90/89 个样本；坐标比例不一致 | 统一为 89 个共同有效样本，记录排除行；等比例坐标与 y=x | R02；D01/D02 |
| [时间序列](examples/review-case/README.md#时间序列) | 缺失点和时间缺口被直接连接 | 保留 1 个缺失预测点及 2 条缺失时间记录形成的断线 | 项目规则 D02；R08 |

这些是使用模拟数据构造的教学反例，用于展示规则作用，不是对其他工具或模型的效果测评。审查前后图、逐项说明、复现脚本与验证记录均在 [完整案例](examples/review-case/README.md) 中公开。样本口径等问题需要结合数据或代码核对，不能仅凭截图确定。

## 工作流程

**输入数据或图表 → 核对表达与样本 → 执行修订 → 查看导出结果 → 交付代码与记录**

| 模式 | 输入 | 交付 |
|---|---|---|
| 图表生成 | 数据、字段定义、单位、比较目标 | PNG/PDF/SVG、绘图脚本、配置与处理记录 |
| 图表审查 | 图片、图注；有条件时提供数据和代码 | 问题位置、规则依据、修改建议及核验范围 |
| 代码改进 | Matplotlib 脚本、输入数据、修改要求 | 新版代码、修订图表及变更说明 |

内置时间序列、预测散点和分条件指标三个入口。规则指导模型审查，脚本负责确定性的数据处理与渲染；复杂图形需要另行编写和验证代码。

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
