# 绘图实现

## 环境

依赖：Python 3.10+、NumPy、Matplotlib、SciencePlots，版本范围见 `requirements.txt`。新环境可在技能目录中创建 `.venv`，然后运行 `python -m pip install -r requirements.txt`。先检查已有解释器；不全局安装，不自动安装完整 TeX。

默认以 `science` + `no-latex` 使用 SciencePlots，避免未配置 TeX 导致失败。`paper`、`report`、`slides` 是本技能的输出场景默认值，不是期刊规范。用户指定期刊时可增加 `ieee` 或 `nature` 样式，并按目标尺寸覆盖配置。代码采用局部 style context，退出后恢复 rcParams。

中文字体从本机字体中选择并检查待显示字符是否覆盖；缺字时停止并报告，不能交付乱码图。可以在配置中给出 `font_family`。字体不随本技能分发。

若受限环境提示 Matplotlib 字体缓存目录不可写，可在本次命令中设置 `MPLCONFIGDIR` 和 `XDG_CACHE_HOME` 指向工作目录下的可写缓存文件夹，避免反复扫描字体；不更改用户全局环境配置。

## 可执行入口

```bash
python /path/to/research-figure/scripts/plot_csv.py --config figure.json
python /path/to/research-figure/scripts/plot_csv.py --config figure.json --check-only
```

相对 `input` / `output_dir` 路径以配置文件所在目录为基准。默认输出 PNG、PDF、SVG、解析后配置、render_log.json 和可复现脚本。默认不覆盖已有输出；用户同意替换时加 `--overwrite`。CSV 使用 UTF-8 / UTF-8 BOM。输入内容不作为命令执行。

最小公共配置：

```json
{
  "kind": "timeseries",
  "input": "data.csv",
  "output_dir": "figure-output",
  "title": "预测对比",
  "x_label": "时间",
  "y_label": "测量值（a.u.）",
  "profile": "report",
  "synthetic": false,
  "x": "timestamp",
  "x_type": "datetime",
  "series": ["actual", "model_a", "model_b"]
}
```

`synthetic` 必须明确给出布尔值，用于区分真实/模拟数据；它是用户声明，不代表技能核验了真实性。`x_label` / `y_label` 必填，不根据列名编造单位。

可选公共字段：
- `labels`：列名或模型名到显示名的映射。
- `styles`：附加 SciencePlots 样式数组，如 `["ieee"]`。不接受远程 URL 或样式文件路径。
- `width_mm`、`height_mm`、`font_size`：正数；优先于场景默认值。
- `font_family`：已安装字体名称；`formats`：`["png","pdf","svg"]` 的非空子集；`dpi`：光栅导出分辨率。

### 时间序列：宽表

字段：`x`、`x_type`（`datetime` 或 `number`）、`series`。

每行同一时刻，列为各序列。时间必须严格递增、不得重复；脚本不会自动排序或去重。日期采用 ISO 格式，可带时区，但不能混用无时区/有时区时间。时区偏移一致性按实际时间比较。不同预测步长应由上游先正确对齐，并在图注说明。

空字符串/NA/NaN/null 被识别为缺失值，保留断线并报告。没有整行记录的时间缺口，需要提供 `expected_interval`（日期为秒，数字轴为原单位）；脚本在超过其 1.5 倍的间隔断线。未提供间隔时不会猜测采样频率，日志注明间隔缺口未检查。已有行内缺失仍然断线。

### 预测值—真实值：宽表

```json
{
  "kind": "parity", "input": "predictions.csv", "output_dir": "parity-output",
  "title": "预测值与真实值", "x_label": "真实值（a.u.）", "y_label": "预测值（a.u.）",
  "synthetic": false, "actual": "actual", "series": ["model_a", "model_b"]
}
```

横轴真实值，纵轴预测值。多个模型采用所有相关列均为有限数的共同样本，日志记录剔除行号（CSV 行号包含表头）。等范围、等比例、`y=x`。不自动计算或宣称统计显著。

### 场景指标：长表

```json
{
  "kind": "metrics", "input": "metrics.csv", "output_dir": "metrics-output",
  "title": "分场景 MAE", "x_label": "场景", "y_label": "MAE（a.u.）",
  "synthetic": false, "category": "scenario", "model": "model", "value": "mae"
}
```

每行一个“场景—模型”的指标；单图只读一个指标列，不能把多种指标/单位混画成同一量。重复组合报错，由用户先确认聚合含义。缺少组合留空并报告，不补零。

可选 `error` 列与必需的 `error_type`（只要提供 error 列就必须解释，例如 `SD` 或 `95% CI half-width`）。仅支持已计算的对称、非负误差值，不自动计算 SD/CI。非对称区间改用自定义绘图代码，并保留定义。

## 自定义和已有代码

```python
from figure_tools import figure_context, save_figure
import matplotlib.pyplot as plt

with figure_context(profile="report", texts=["时间", "测量值（a.u.）"]):
    fig, ax = plt.subplots(layout="constrained")
    # 在这里使用用户数据绘图，不更改原有统计口径。
    ax.set(xlabel="时间", ylabel="测量值（a.u.）")
    save_figure(fig, "result", formats=["png", "pdf", "svg"])
```

把 `figure_tools.py` 复制到交付脚本旁，并保留包内 `licenses/SciencePlots-MIT.txt`；在脚本说明中记录 SciencePlots 依赖。`save_figure` 保留画布尺寸，不使用会改变实际导出尺寸的自动紧裁切。用 constrained layout 或显式边距解决裁切，并实际查看。

本项目优先选择可复现的小脚本。PDF/SVG 适合矢量交付，PNG 便于预览；数值完整性、图形意图、期刊合规仍需要人工/代理审查。

## 模拟演示

`python scripts/demo.py --output /path/to/new-demo --render` 生成三个可复现示例，每张图显式标注模拟数据。演示默认使用英文标签，便于在没有中文字体的环境中运行。a.u. 表示演示使用任意单位，实际绘图请填写真实单位。输出目录必须尚不存在。示例不代表真实模型效果，指标误差条也是预设演示值。
