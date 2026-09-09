# Atlas

A local-first, Markdown-first knowledge curator for Codex.

Atlas 帮助你长期整理、检索和维护技术知识库，适合 LLVM、MLIR、Compiler、AI Compiler、ISA / RISC-V、Hardware、Runtime 等主题。

核心原则是 **Document ≠ Knowledge Unit**：一篇输入可能拆出多个知识单元，多篇来源也可以整合到同一篇知识文档。Atlas 先理解知识和上下文，再决定新增、合并、扩展、拆分、跳过或保留冲突。

## 功能

| 工作流 | 用途 |
|---|---|
| ASK | 从已有笔记回答问题，引用本地依据并说明缺口 |
| ADD | 查找已有知识后添加一个主题或结论 |
| INTEGRATE | 将一个或多个来源整合进现有知识库 |
| UPDATE | 根据证据修订知识，保留版本和上下文差异 |
| ORGANIZE | 整理知识边界、移动文件并修复关联链接 |
| AUDIT | 检查结构、链接、标签、来源和知识边界 |

Markdown 是知识的权威载体。语义决策由 agent 完成，Python 工具处理确定性检查。工具默认只读；索引也先输出供审阅。QMD、Obsidian 和数据库均不是必需依赖。

## 安装

以下命令适用于 macOS / Linux。Windows 可将同样的文件夹放到用户目录下的 `.agents/skills/atlas`，并使用对应的 Python 虚拟环境命令。

### 从 GitHub 安装

需要 Git 以及该仓库的访问权限。首次安装：

```sh
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/ChongKaKam/Atlas.git "$HOME/.agents/skills/atlas"
```

安装结果应为 `$HOME/.agents/skills/atlas/SKILL.md`。已有同名 Skill 时先确认其来源，不要直接覆盖。

Codex 支持个人目录 `.agents/skills` 和软链接。如果没有发现新安装的 Skill，重启 Codex。参见 [官方 Skill 文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)。

### 本地开发安装

如果已经把仓库克隆到其他目录，可以软链接到个人 Skill 目录，避免维护两份源码。将下面的路径替换为实际仓库绝对路径：

```sh
mkdir -p "$HOME/.agents/skills"
ln -s /absolute/path/to/Atlas "$HOME/.agents/skills/atlas"
```

### 安装检查工具依赖

阅读和执行 Skill 指令不需要 Python；运行自动检查需要 **Python 3.10+**、PyYAML 和 markdown-it-py。

```sh
python3 -m venv "$HOME/.local/share/atlas/venv"
"$HOME/.local/share/atlas/venv/bin/python" -m pip install \
  -r "$HOME/.agents/skills/atlas/scripts/requirements.txt"
```

告诉 agent 使用这个虚拟环境的 Python 来运行 Atlas 工具。不要覆盖已有的其他用途虚拟环境。

### 更新

Git 安装可在检查本地改动后更新：

```sh
git -C "$HOME/.agents/skills/atlas" status --short
git -C "$HOME/.agents/skills/atlas" pull --ff-only
```

依赖文件变化时，在原虚拟环境重新执行依赖安装。个人知识库应保存在 Skill 目录之外，不随 Skill 更新而移动。

## 开始使用

安装后，在支持 Skill 提及的 Codex 界面中选择 Atlas，或显式要求它按 Atlas 执行；CLI / IDE 可用 `$atlas`。

先选定一个独立知识库路径。例如：

```text
使用 Atlas，在 /absolute/path/to/KnowledgeBase 创建技术知识库。
默认中文解释，保留英文技术术语。按实际需要创建领域目录。
```

整合文档：

```text
使用 Atlas，将 /absolute/path/to/notes/input.md 整合进
/absolute/path/to/KnowledgeBase。
先检索已有知识，给出整合计划、正文草案与 diff，等我确认后写入。
```

查询知识：

```text
使用 Atlas，只根据 /absolute/path/to/KnowledgeBase 内的笔记，
解释 LLVM dialect 和 LLVM IR 的区别，并引用对应文件。
```

审计知识：

```text
使用 Atlas，审计 /absolute/path/to/KnowledgeBase，
报告断链、元数据和需要语义审查的问题，暂不修改文件。
```

用户明确授权的改动可以直接应用并展示差异；用户要求先审阅时，先交付具体草案。新知识默认 `draft`，允许写入不等于人类已审查技术结论。

## 命令行工具

下面的 `python` 指安装了依赖的虚拟环境解释器；从仓库根目录执行：

```sh
python scripts/atlas.py validate /absolute/path/to/KnowledgeBase
python scripts/atlas.py check-links /absolute/path/to/KnowledgeBase
python scripts/atlas.py audit /absolute/path/to/KnowledgeBase --json
python scripts/atlas.py build-index /absolute/path/to/KnowledgeBase
```

`build-index` 只输出 Markdown，不写文件。`--check` 比较已保存 INDEX 是否过期；`--strict` 将警告也视作检查失败。工具不会联网验证来源或自动修复笔记。具体覆盖范围与退出码见 [工具说明](references/tooling.md)。

## 项目结构

```text
SKILL.md              Skill 入口和工作流路由
agents/               Codex 展示元数据
references/           知识规范、工作流和使用说明
assets/               新库与整合计划模板
scripts/              确定性检查与打包工具
tests/                工具回归测试及语义验收情景
experiments/          开发实验，非正式用户知识库
```

## 开发与验证

在仓库根目录建立开发环境并运行测试：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

目前工具包含 21 项回归测试。独立 LLM 工作流评估及用户真实知识库验收尚待完成，不能把工具测试视作技术知识准确性的认证。详细记录见 [验证说明](references/validation.md)，贡献约定见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 打包与分享

无需额外依赖即可生成独立 Skill ZIP：

```sh
python3 scripts/package_skill.py
```

默认输出 `dist/atlas.zip`。如果输出已存在，命令会拒绝覆盖；可用 `--output dist/atlas-v1.0.1.zip` 指定新的文件名。压缩包包含顶层 `atlas/`，排除开发实验、Git 数据、缓存和虚拟环境。发布前可将生成的 ZIP 上传到 GitHub Release；生成 ZIP 不会自动发布。

接收者可将 ZIP 解压到 `.agents/skills`，确认 `atlas/SKILL.md` 直接位于其中，再安装工具依赖。需要应用内分发体验时可另行封装为 Plugin；本仓库当前提供独立 Skill。

## 文档

- [Skill 入口](SKILL.md)
- [知识库规范](references/knowledge-base-spec.md)
- [使用说明](references/getting-started.md)
- [Review 与 Apply](references/review-apply.md)
- [语义验收情景](tests/acceptance.md)

## 许可证

目前尚未指定开源许可证。发布者确认许可后会在仓库根目录补充 LICENSE。
