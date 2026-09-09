# Knowledge Base Conventions

## 内容与组织

按主问题选择领域目录；默认 `knowledge/<domain>/<file>.md`。项目局部知识放 `projects/<project>/`。目录按需创建。类型是 reader intent：`concept`、`guide`、`investigation`、`decision`、`reference`、`overview`。

一个输入可能含多个 Knowledge Units；一个知识文件可整合多个来源。优先检索已有知识再决定新增。独立问题可以拆分，重复知识尽量只有一个主要位置。

默认中文解释，保留英文技术术语、代码与 identifier；不要为统一语言改写既有笔记。

## 元数据与命名

Frontmatter 必填 `type`、`status`、`created`、`updated`；日期为真实 `YYYY-MM-DD`。可选字符串列表 `aliases`，推荐 `tags`。H1 为唯一标题，不重复 `title`。来源及关联使用正文而非 YAML。

状态：`draft`（待审查）、`reviewed`（人类已审查具体结论及范围）、`deprecated`（不再推荐，开头说明原因与替代位置）。允许 Apply 不等于技术 review；实质未审查更改回到 draft。保留 created，知识内容改变才更新 updated。

目录使用 lowercase-kebab-case；文件普通词之间使用 hyphen，保留 `GPRPair`、`SelectionDAG` 等 identifier 的拼写。避免空格、仅大小写差异及模糊标题。

## 链接与来源

使用标准 relative Markdown links 和 `.md` 后缀。移动时同时修复 inbound 和 outbound links，包括图片和 Sources。仅在解释关系或避免重复时链接；不使用 WikiLink。

Sources and evidence 段落写明 source URL/path、版本或 revision、必要访问日期、对应结论。区分外部陈述、实验观察、个人推断与 AI 综合。AI 本身不是证据；源码敏感结论优先 pin revision，无法取得时明确限制。

先区分补充、纠错、不同上下文和真实冲突；真实冲突保留双方证据与待验证问题。

## Tag vocabulary

标签表示跨领域技术侧面，不重复类型和目录。使用以下受维护词表；需要新 tag 时在同一变更中说明并扩展。空词表允许没有 tags。每行一个 lowercase-kebab-case tag，通常每篇 2–5 个，不能为了数量填充。

```atlas-tags
codegen
legalization
llvm-ir
lowering
memory-model
register-allocation
register-class
risc-v
```
