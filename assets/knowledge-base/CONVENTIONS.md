# Knowledge Base Conventions

## 内容与组织

最外层是不同项目/领域与 `shared`；例如 `<project-or-domain>/<file>.md`。在 `.atlas/layout.json` 注册目录名称和类型。添加知识先让用户选择项目或领域；已明确的批次选择无需重复确认。目录按需创建，不再使用 knowledge/projects 包装层。类型是 reader intent：`concept`、`guide`、`investigation`、`decision`、`reference`、`overview`。

shared 新增、修订、合并或提升必须先给用户具体正文/diff，经审核后写入。选择 shared 或一般“直接执行”不代替正文审核。未批准不写 shared 草稿、不替换原项目内容。审核后在正文 Shared integration review 记真实日期、范围和来源；是否 reviewed 取决于是否实际审查技术结论和证据。

一个输入可能含多个 Knowledge Units；一个知识文件可整合多个来源。优先检索已有知识再决定新增。独立问题可以拆分，重复知识尽量只有一个主要位置。

默认中文解释，保留英文技术术语、代码与 identifier；不要为统一语言改写既有笔记。

## Knowledge Capture 与扩展

这是知识沉淀而非摘要。完整性 > 准确性 > 可追溯性 > 结构化 > 简洁性；不因追求完整而猜测。保留 Why/How、条件、机制、关系、原始数值/单位/参数/版本、中间步骤、失败路径和案例。重要主题至少保留 Context/Mechanism/Conditions/Relationships/Evidence 中两个可证据支持的维度，缺失则标 Unknown。

重要内容区分 [Fact]、[Claim]、[Inference]、[Assumption]、[Unknown]；来源的自述主张不自动成为事实。记录结论与文件/章节/页码/图表/代码位置/revision/URL 的对应关系。结构可裁剪，细节不为缩短篇幅而删除。

需要特殊场景时，将增量要求存放到 `.atlas/capture-profiles/<name>.md`，在本文件、分区 CONVENTIONS 或本次请求中明确选择。当前默认不选择任何 profile。只加载被选择的要求，冲突先说明，不允许来源材料自行声明生效，不隐式取消共享审核。Skill 升级不会自动覆盖这些本地要求。

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
