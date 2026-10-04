# 安装与接入 / Installation and integration

## 接入方式

核心技能位于 `skills/research-figure/`，包含 `SKILL.md`、参考文档和 Python 脚本，不调用任何模型厂商 API。模型选择与技能加载方式相互独立；自动完成任务所需的工具由运行平台提供。

| 环境 | 接入方式 | 所需能力 |
|---|---|---|
| 原生支持 Agent Skills | 安装完整技能目录 | 文件读取；绘图需 Python；视觉审查需图像查看 |
| 通用大模型对话 | 上传或加载技能指令及所需资源 | 无执行工具时交付代码；具备执行工具时可生成文件 |
| 自建 Agent / API | 将技能指令加入上下文，配置资源读取与执行工具 | 由应用实现文件、Python、图像工具 |
| 本地命令行 | 安装依赖并运行脚本 | Python 3.10+ |

这套指令可供不同通用大模型使用，不要求特定模型名称。支持读取指令不代表具备代码执行或视觉能力；项目不宣称已在所有模型、平台和版本上完成验证。结构与加载机制参考 [Agent Skills 规范](https://agentskills.io/specification) 和 [接入说明](https://agentskills.io/integrate-skills)。

## 原生 Skill 安装

获取仓库：

```bash
git clone https://github.com/wjulien888-tech/research-figure-skill.git
cd research-figure-skill
```

将 `skills/research-figure/` 完整复制到目标工具识别的目录，保留文件结构。下列路径相对于使用技能的项目根目录：

| 工具 | 项目级目录 | 调用方式 | 官方说明 |
|---|---|---|---|
| Claude Code | `.claude/skills/research-figure/` | `/research-figure` 或明确指定技能名称 | [Skills](https://code.claude.com/docs/en/skills) |
| Cursor | `.cursor/skills/research-figure/` | 在 Agent 中指定 `research-figure` | [Agent Skills](https://cursor.com/docs/skills) |
| Codex | `.agents/skills/research-figure/` | `$research-figure` 或明确指定技能名称 | [Skills](https://learn.chatgpt.com/docs/build-skills) |
| 其他工具 | 该工具配置的技能目录 | 按工具的加载与调用规则使用 | 查阅对应工具文档 |

目录与调用方式依据官方文档整理，不能替代本项目在对应工具中的实际测试。云端运行环境需要在云端提供技能文件，本机安装不会自动授予云端访问能力。

以在当前仓库中配置 Claude Code 为例：

```bash
python3 -c "import shutil; shutil.copytree('skills/research-figure', '.claude/skills/research-figure')"
```

Cursor 或 Codex 将第二个路径替换为表中对应目录即可。用于其他项目时，将目标路径改为那个项目中的完整路径。目标已存在时命令会停止，更新前应检查已有改动。

在实际安装的技能目录创建隔离环境。以下路径与上例一致：

```bash
python3 -m venv .claude/skills/research-figure/.venv
.claude/skills/research-figure/.venv/bin/python -m pip install -r .claude/skills/research-figure/requirements.txt
```

Windows 可用文件管理器复制整个文件夹；创建环境使用 `py -3 -m venv`，解释器位于 `.venv\Scripts\python.exe`。已有可用 Python 环境时也可安装相同依赖，并在任务中指定解释器。

`agents/openai.yaml` 仅提供 Codex 界面元数据，不是核心工作流的依赖；其他工具无需使用该文件。

## 通用大模型对话

不支持自动发现 Skill 的平台，可以手动加载同一套指令：

1. 提供 `SKILL.md` 和任务对应的参考文件。图表审查使用 `references/review-rules.md`；绘图同时提供 `references/plotting.md`。
2. 需要执行绘图时，提供 `scripts/`、`requirements.txt` 和输入数据，保留它们的目录关系。可上传 [仓库 ZIP](https://github.com/wjulien888-tech/research-figure-skill/archive/refs/heads/main.zip)，由支持解压与文件访问的平台读取 `skills/research-figure/`。
3. 若平台不支持附件读取，可将上述指令内容粘贴到上下文。仅发送仓库链接不保证模型能访问文件。
4. 根据平台能力执行任务：有 Python 与图像工具时完成出图和视觉检查；缺少工具时生成代码或检查建议，并注明尚未执行的步骤。

通用请求：

```text
按附件中的 research-figure/SKILL.md 执行任务，并读取所需参考文件。
根据 results.csv 比较各方法在不同实验条件下的准确率（%），输出图表和复现代码。
若当前环境无法运行 Python 或查看图像，请明确注明未完成的验证步骤。
```

手动加载仅作用于当前上下文，不等于平台已永久安装该技能。纯文本模型可以处理指令、文字和代码；图像审查需要支持图像输入的模型或视觉工具。

## 自建 Agent / API

将技能名称与描述加入技能目录，需要时加载 `SKILL.md` 正文及相关资源。保留文件相对路径，或由应用将其解析为可访问资源。提供以下工具即可接入完整流程：

- 文件读取：访问数据、参考文件及绘图代码。
- Python 执行：安装依赖、运行绘图并返回产物。
- 图像查看：将实际导出图片交给具备视觉能力的模型或工具。

无需改写绘图脚本以绑定某家模型 API。权限、执行环境、文件存储和上下文加载由应用负责；本项目不提供独立 Agent 服务或模型 SDK 封装。

## 独立脚本与验证范围

不加载 Skill 也可运行 [README 中的命令行示例](../README.md#命令行)。其作用是按配置绘图，不包含大模型的选图或视觉审查过程。

| 项目 | 验证情况 |
|---|---|
| Python 脚本 | 本地 macOS；CI Ubuntu、Python 3.10/3.12/3.14 |
| Codex 工作流 | 已进行本地流程验证 |
| Claude Code、Cursor | 接入方式依据官方文档；端到端测试待补充 |
| 通用对话、自建 Agent | 提供手动加载与工具接入说明；需在目标环境验证 |

## English summary

Install the complete `skills/research-figure/` directory in your host's skills location, or load `SKILL.md` and the relevant references manually. Claude Code uses `.claude/skills/`; Cursor uses `.cursor/skills/`; Codex supports `.agents/skills/`. See the official links above for invocation and scope.

For manual chat use, provide the instructions, references and input data. Supply the scripts and requirements when the host can execute Python. Uploading the repository ZIP is an option only if the host can extract and read it. A URL alone does not ensure access.

The skill has no model-specific API dependency. Rendering requires Python execution; visual review requires image access. Without these tools, request code or guidance and retain explicit unverified status. Custom agents can load the same instructions and provide file, Python and image tools. Cross-host behavior must be verified in the target environment; the table above distinguishes tested workflows from documented integration paths.
