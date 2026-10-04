# 科研图表审查案例

七组案例展示从绘图草稿到审查修订的变化，覆盖布局、密度、标签、比较尺度与数据口径。两侧均使用 SciencePlots；每组修订基于相同的模拟源数据。

前四组使用 [自定义绘图脚本](render_visual.py)，按 Skill 规则选择图形与布局，并复用本项目的样式与导出工具；后三组由 [内置入口演示脚本](render.py) 直接调用 `plot_csv.py` 绘图函数。草稿由脚本有意构造，案例展示可复现的修订方法，不是模型成功率测评或其他产品的默认输出。

## 任务输入

适用于这些案例的用户请求：

```text
使用 research-figure 审查这些实验图及原始数据。
核对坐标范围、样本口径、缺失处理和误差线定义。
指出问题位置与依据，保留原始数值，交付修订图、绘图代码和处理记录。
```

## 多模型对比

![多模型分面修订](../../docs/images/review-multimodel.png)

**输入：** [multimodel.csv](data/multimodel.csv)。6 个模型、1 条参考曲线，每条 121 个观测点。

| 草稿问题 | 规则依据 | 修订 |
|---|---|---|
| 七条曲线在交叉处难以追踪 | R01/R04：按比较目标组织面板 | 每个面板保留一个模型与相同参考曲线 |
| 读者需要在曲线和图例之间反复查找 | R08：直接标签与非颜色区分 | 面板标题标识模型，结合线型区分 |
| 分面后仍需比较同一量纲的响应 | R04：共同尺度 | 所有面板纵轴统一为 20–85，横轴统一为 0–24 h |

验证每条模型曲线和参考曲线的数值均未改变，所有修订面板使用相同坐标范围。分面适合逐一对照参考值；若目标是精确比较模型之间某一时刻的差值，还应补充残差或局部比较图。

## 密集散点

![密集散点修订](../../docs/images/review-density.png)

**输入：** [density.csv](data/density.csv)。6,000 对模拟观测与预测。

| 草稿问题 | 规则依据 | 修订 |
|---|---|---|
| 不透明散点遮叠，无法看清集中程度 | R06：用密度表达减少遮叠 | 使用六边形分箱计数，`gridsize=32` |
| 分布密度需要连续编码 | R07：顺序色标 | 使用 cividis，色条标明每箱样本数与对数尺度 |
| 聚合后须说明处理方式与样本数 | D01/D02：记录聚合和样本口径 | 保留全部 6,000 个样本，验证分箱计数总和等于源样本数 |

两侧均为等范围、等比例坐标并保留 `y=x`。分箱改变的是显示粒度，原始样本未删除；精确点位仍需查阅数据或散点图。密度图不代表预测精度提高。

## 消融与基线比较

![长标签与排序区间修订](../../docs/images/review-labels.png)

**输入：** [labels.csv](data/labels.csv)。10 个实验配置，包含完整模型、消融配置、基线和输入条件；MAE 与 SD 均为预设演示值。

| 草稿问题 | 规则依据 | 修订 |
|---|---|---|
| 长标签倾斜，查找和横向比较费力 | R01/R10：按目标选图并确保文字可读 | 改为水平点区间图，完整展示名称 |
| 类别无自然顺序，当前排列不利于比较 | R01：明确比较对象 | 按 MAE 升序排列，标明越低越好 |
| 所有配置视觉权重相同 | R07/R09：突出关注对象 | 完整模型使用强调色，其他配置使用灰色 |
| 更换图形后不确定性仍需保留 | D03/D04：保留指标与不确定性定义 | 保留每个 MAE 与所提供的 SD，不重算指标或推断显著性 |

验证原始柱值、排序后点位及每条区间的端点。排序只调整显示顺序；没有修改数值或模型排名的计算依据。

## 跨条件比较

![共享尺度修订](../../docs/images/review-panels.png)

**输入：** [panels.csv](data/panels.csv)。三个条件、每组 121 个点，数值按相同模拟形状的 1、5、16 倍构造。

| 草稿问题 | 规则依据 | 修订 |
|---|---|---|
| 独立缩放使不同幅度的曲线看起来相似 | R04：同一物理量直接比较优先共享尺度 | 纵轴统一为 0–24，保留相同时间范围 |
| 自动缩放使读者需要逐组换算刻度 | R01/R04：围绕比较目的组织图形 | 统一刻度，直接比较绝对误差大小 |

验证两侧各条件的全部数值相同、右侧纵轴范围完全一致。独立尺度并非一律错误：研究每个条件内部的形状或微小变化时可以使用，但需要明确标注。本例的任务目标是比较条件间的绝对误差水平。

## 指标对比

![指标对比修订](../../docs/images/review-metrics.png)

**输入：** [CSV](../metrics/data.csv)、[配置](../metrics/config.json)。三个条件、两种方法；RMSE 和 SD 均为演示值。

| 审查发现 | 依据 | 修订 |
|---|---|---|
| 左侧纵轴从 3 开始，柱长不再对应数值比例 | [R03](../../skills/research-figure/references/review-rules.md)：柱图保留零点 | 纵轴包含 0；保持所有柱值不变 |
| 已提供 SD，但草稿未展示且未解释其含义 | D03：分开表达汇总值与不确定性 | 展示已有 SD，明确标为示例值，不计算或编造区间 |
| 方法主要靠颜色区分 | R08：增加非颜色区分 | 加入纹理 |

最后一组数值为 3.3 与 5.2。截断后可见柱长比为 `(5.2−3)/(3.3−3)≈7.33`，原值比为 `5.2/3.3≈1.58`。这是**柱长比例的失真**，不是模型性能提升比例或统计显著性结论。

## 预测对比

![预测对比修订](../../docs/images/review-parity.png)

**输入：** [CSV](../parity/data.csv)、[配置](../parity/config.json)。90 行模拟样本，基线缺少一个预测值。

| 审查发现 | 依据 | 修订 |
|---|---|---|
| 草稿按各模型有效行分别绘制，样本数为 90 和 89 | D01/D02：核对比较对象与缺失口径 | 两个模型均使用 89 个共同有效样本，记录排除 CSV 第 6 行 |
| 两轴范围不同且未保持等比例 | R02：纵横比不能改变同量纲比较印象 | 等范围、等比例，并加 `y=x` |
| 两种模型使用相同点形 | R08 | 使用圆点与方点 |

样本问题依据 CSV 与绘图代码核验。仅提供截图时不能确定这一点；审查结果应将其列为待核验项。

## 时间序列

![时间序列修订](../../docs/images/review-timeseries.png)

**输入：** [CSV](../timeseries/data.csv)、[配置](../timeseries/config.json)。预期采样间隔 15 分钟。

| 审查发现 | 依据 | 修订 |
|---|---|---|
| 草稿删除空预测值后连线，跨过缺失观测 | D02：显式保留缺口 | 保留缺失值对应的断线，不做插值 |
| 11:30 与 12:15 之间缺少 11:45、12:00 两条记录 | D01/D02：结合已知间隔核对缺口 | 在时间缺口断线，记录缺口后的 CSV 行号 |
| 两条序列仅靠颜色区分 | R08 | 同时使用实线与虚线 |

程序检查有限原始值在修订图中被完整保留。断线表达“这里缺少观测”，不表示数值在该时段下降为零。

## 验证与复现

从仓库根目录执行，使用已经安装依赖的 Python：

```bash
.venv/bin/python examples/review-case/render.py --output work/review-case-new
.venv/bin/python examples/review-case/render_visual.py --output work/visual-review-new
```

输出目录必须尚不存在。每个案例输出 PNG、PDF、SVG。两个脚本分别输出 `evidence.json` 与 `visual-evidence.json`，记录输入散列及已检查的数值与图形属性。仓库保留 [基础案例验证记录](evidence.json) 和 [视觉案例验证记录](visual-evidence.json)，仅含相对路径。

前四组固定数据位于 `data/`，可直接复现图表。数据生成代码使用 NumPy 种子 `20261005`；如需另行生成，可运行：

```bash
.venv/bin/python examples/review-case/generate_visual_data.py --output work/visual-data-new
```

该命令仅生成另一份数据，不覆盖仓库输入。视觉案例脚本始终读取仓库内的固定 CSV。

脚本实际检查：柱值与零基线、误差线对象、共同样本数、散点比例、`y=x`、有限观测值保留及原文件未修改。视觉案例另检查共享尺度、分箱计数总和、排序后的数值与区间端点。规则解释和排版仍需结合图像查看；这些断言不是完整科研审查。

## English summary

Seven synthetic cases illustrate reproducible figure revisions. Both sides use SciencePlots. Four custom Matplotlib cases cover overlapping model traces, dense scatter, long category labels with supplied intervals, and cross-condition scales. Three cases call the built-in skill renderer to correct bar baselines, prediction sample selection and missing-data gaps.

Run both render commands above to reproduce all seven comparisons and their evidence files. The custom cases preserve source values, count all 6,000 samples in density bins and retain supplied SD intervals. The prediction example uses the same 89 finite rows for both methods and records the excluded row. These are rule demonstrations, not an empirical benchmark of AI review capability. Custom gallery plots do not introduce additional fixed CLI chart modes.
