# 上游来源、改编与边界

检索与版本记录日期：2026-10-04。精确提交、取用文件和 SHA-256 见 [upstreams.json](upstreams.json)。版本固定用于追溯，不表示永不更新。

## RSS Data Visualisation Guide

- 项目：https://github.com/royal-statistical-society/datavisguide
- 网站：https://royal-statistical-society.github.io/datavisguide/
- 署名：Royal Statistical Society；Andreas Krause、Nicola Rennie 及指南贡献者。
- 依据：[Principles](https://royal-statistical-society.github.io/datavisguide/docs/principles.html) 与 [Styling](https://royal-statistical-society.github.io/datavisguide/docs/styling.html)。
- 许可：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，[法律文本](https://creativecommons.org/licenses/by/4.0/legalcode)。保留的上游声明在 `licenses/RSS-LICENCE.md`。
- 改编：本项目将选定原则概括为中文检查规则，加入工程实验场景、适用例外和证据边界；将上游以 R 为主的示例思路转为自编 Python 实现，没有完整搬运指南或外部配图。
- `review-rules.md` 的 R 规则及 SKILL.md 中相关原则属于改编，按 CC BY 4.0 提供。D 规则为本项目新增，随该参考文件同许可。

特别区分：柱图需要零基线；时间序列和散点图要结合目的选范围。字号建议需要结合最终成图尺寸及刊物要求。本技能的具体毫米数、字号默认值、缺失处理策略并非 RSS 强制标准。上游链接到的第三方图片、论文、网站各有自己的权利范围，不自动纳入本技能许可。

## SciencePlots

- 项目：https://github.com/garrettj403/SciencePlots
- 作者及版权声明：Copyright (c) 2018 John Garrett。
- 许可：MIT；原文保留于 `licenses/SciencePlots-MIT.txt`。
- 本项目依赖并测试了 `SciencePlots==2.2.2`，通过其公开 Matplotlib 样式接口调用；不复制一套样式文件另行维护。
- 固定提交用于本次 README/许可核验；安装依赖由版本号固定，与当前 Git 提交不是同一概念。
- 默认使用 `science` 和 `no-latex`，避免要求用户安装 TeX；可叠加已注册的风格。`ieee`、`nature` 等名称不能当作期刊最新规范或投稿检查通过证明。

这是独立下游技能，没有 RSS 或 SciencePlots 的官方认可。可复现绘图不等于核验实验设计、统计推断或数据真实性。输入数据、第三方字体、刊物规范各有独立来源，应按实际请求核对。
