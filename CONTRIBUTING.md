# Contributing / 贡献指南

欢迎提交可复现的绘图问题、规则修正和小范围功能改进。请先说明输入、预期结果和实际结果；讨论较大的新图形或流程时，先开 issue 对齐范围。

## 本地验证

从仓库根目录执行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r skills/research-figure/requirements.txt
.venv/bin/python skills/research-figure/tests/test_plot_csv.py
.venv/bin/python skills/research-figure/scripts/demo.py --output work/demo-new --render
```

演示输出目录必须尚不存在。Windows 使用 `.venv\Scripts\python.exe`。受限环境中，如字体缓存不可写，设置本次命令的 `MPLCONFIGDIR` / `XDG_CACHE_HOME` 指向可写缓存目录。

修改数据处理或导出行为时，补充针对实际风险的回归测试。检查至少一个受影响的导出图片，不能只看命令退出码。修改中英文字体行为时，用相应文字实际出图；CI 的英文示例不代表中文字体已验证。

## 提交内容

- 新增图形需要说明输入结构、缺失处理、单位假设，并提供明确标为模拟的数据与配置。
- 不改变现有统计口径来修复视觉问题；新增筛选或聚合应可追溯。
- 图表检查规则区分上游原则与项目新增约束，提供具体来源和适用例外。
- 改动用户行为时更新 README 或使用指南；改动底层配置时更新 `references/plotting.md`。
- Issue 和 PR 不要上传真实敏感数据、凭据或包含本机路径的完整运行记录。用最小模拟数据复现问题。

提交 PR 时写清问题、最终行为、验证结果和已知限制。原创代码贡献遵循本项目 MIT 许可；改编指南遵循对应 CC BY 4.0 条款，并保留必要归属。只提交你有权贡献的内容。

## English summary

Please include a minimal synthetic reproduction, expected behavior and actual behavior. Keep changes focused. Add tests for data or rendering invariants, inspect affected exported figures and update the relevant documentation. Never submit credentials, private research datasets or unredacted machine-specific logs. Preserve upstream attribution and identify which rules are adapted versus newly introduced.
