# Pilot Knowledge Base Conventions

本实验遵循 [`Atlas Knowledge Base Specification v0.1`](../../../references/knowledge-base-spec.md)。这里只记录实际使用到的最小约定，避免复制完整规范。

- 主目录按领域组织；文档类型不进入路径。
- 文档类型使用 `concept`、`guide`、`investigation`、`decision`、`reference`、`overview`。
- 当前状态使用 `draft`、`reviewed`、`deprecated`；本 pilot 的 AI 综合内容全部先为 `draft`。
- H1 是唯一标题；Frontmatter 不重复 `title`。
- 技术名称使用上游拼写；普通 filename 词组使用 hyphen。
- 链接使用带 `.md` 后缀的相对 Markdown link。
- 本 pilot 使用的 tags：`codegen`、`global-isel`、`legalization`、`llvm-ir`、`lowering`、`register-class`、`risc-v`。
- 来源、实验观察和推断写在正文 `Sources and evidence` 中。
