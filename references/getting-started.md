# Atlas V1 使用说明

Atlas 是工作流 Skill，配有只读 Python 工具。LLM 决定如何组织知识，工具检查能机械判定的结构。所有正式知识保存在用户指定的 Markdown 目录。

## 当前项目

入口为项目根部 `SKILL.md`；`references/` 是规范和工作流；`assets/` 是可复制模板；`scripts/` 是工具；`tests/` 是工具测试和语义验收情景。`experiments/` 保留开发实验，不应导入用户知识库。

源码目录已经构成完整 Skill 包。构建它不等于将其安装进当前账户的 Skill 发现目录；在未安装的会话，可直接要求 agent 读取实际绝对路径的 SKILL.md 并执行。

## 初次使用

用户明确一个知识库路径后，读取该路径下的 README 和 CONVENTIONS。如果是新库，先复制 assets 中两个根文件，填写范围与入口，再按首次知识输入创建所需领域目录。不要把整套空领域树复制进去。

开发项目与知识库路径可以完全不同。第一次试用建议用一个独立目录的少量笔记，保留原输入文件。

## 示例请求

使用时把示例路径替换为实际绝对路径：

- “读取 `/path/to/atlas/SKILL.md`，按 Atlas 的 ASK 在 `/path/to/kb` 查 LLVM dialect 和 LLVM IR 的区别，只用库内证据。”
- “按 Atlas 将 `/path/to/input.md` 整合进 `/path/to/kb`，先给我具体草案和 diff，等我确认后写入。”
- “执行刚才批准的整合计划，保留现有用户修改，完成后验证链接。”
- “按 Atlas 审计 `/path/to/kb`，只报告问题。”
- “按 Atlas 创建 `/path/to/new-kb`，将这段知识作为第一篇笔记加入。”

已安装并能被发现时，也可用 `$atlas` 指定 Skill；当前交付不宣称已经安装。

## 验证和依赖

工具依赖安装与所有命令见 [tooling](tooling.md)。六个用户工作流都已描述，Apply 由 agent 在授权范围内完成。没有后台服务、数据库或外部账号要求。

V1 默认中文解释、英文 identifiers、六种类型、三种 status。不同库的已定约定优先。`reviewed` 是对具体内容的人类审查，不是代码测试或 Skill 的自动认证。

## 可调整但不阻塞使用的事项

领域细分、investigation 的长期适用性、跨仓库项目笔记、双语 aliases 和来源 pinning 强度仍需真实资料验证。可局部调整约定，不必因此暂停所有 ADD/INTEGRATE。检索规模需要时再评估 QMD 或 GUI。
