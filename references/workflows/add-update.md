# ADD 与 UPDATE

先读 [Review 与 Apply](../review-apply.md)，再按 [规范](../knowledge-base-spec.md) 的 KU、类型、来源和冲突章节判断。

新增时先按 [分区规则](../scopes.md) 提示用户选择项目或领域。内容编写使用 [Knowledge Capture](../../assets/knowledge-capture-prompt.md) 及用户选择的场景 profile；UPDATE 保留已有过程和精确细节，不退化成更短的摘要。涉及 shared 的变更先提交具体草案待审核。

## ADD

输入可以是短想法、一个主题、代码阅读结论或完整文章。主题缺乏证据时只写明为假设或 personal-understanding；不要用 LLM 记忆填成 verified fact。

1. 用一句话明确 reader question、版本/环境和来源。若输入包含多个独立问题，转 INTEGRATE。
2. 按 ASK 的本地检索方法寻找 canonical home，实际阅读候选。语义重复且来源相同才 Skip；新来源能提高可追溯性时仍可能需要 Merge。
3. 在已选分区内有合适 home 时 Merge 或 Extend；否则按主问题选择类型，Create。一条 KU 可以只是已有文档的一节。跨区复用优先链接，跨区写入需对应授权，shared 必须审核。
4. 用文档形状准备内容，默认 `draft`。仅填写真实日期、来源和上下文；用真实 H1，aliases 收录可识别的别名，tags 从本地词表选取。
5. 应用并检查改动；报告选择现有位置或新建的原因。

## UPDATE

1. 确定目标，不凭同名文件猜测。读取完整相关段落及其来源、上下文和链接。
2. 将新证据与旧说法分类为 Supplement、Correction、Different Context 或 True Conflict。较新日期不是充分纠错理由。
3. Supplement 增补；Correction 用证据改正并说明重要影响；Different Context 并列限定；True Conflict 保留两方及验证问题。
4. 仅修改相关知识，保留正确的既有细节。因输入有事实错误而拒绝更新时说明证据；不要按文风强行改写。
5. 实质变更把 reviewed 改为 draft（除非人类已审查具体最终变更）；轻微拼写修复保持状态。执行适用的结构/链接检查。

过期文档仍可能对旧版本有用。优先给旧上下文明确标识，再决定 deprecated 或拆分；deprecated 的开头须说明原因和替代位置。
