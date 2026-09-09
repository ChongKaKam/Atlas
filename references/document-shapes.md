# 文档形状

这些是选择正文结构的提示，不是强制所有文件填写的字段。小 KU 可以只用两三节。保留上游 identifier；默认中文解释，已有库语言优先。Frontmatter schema 见 [规范](knowledge-base-spec.md)。

| Type | 读者问题 | 有用的正文顺序 |
|---|---|---|
| concept | 是什么、为什么 | 核心解释 → 范围/不变量 → 机制和例子 → 限制 → 来源 |
| guide | 怎样完成或排查 | 目标与前提 → 操作/判断分支 → 成功判据 → 失败处理 → 来源 |
| investigation | 做了什么、观察到什么 | 问题 → 版本/target/环境 → 操作与原始结果定位 → 观察 → 推断 → 局限与下一验证 |
| decision | 为什么选它 | 背景 → 选项 → 决定及状态 → 代价/后果 → 重审条件 → 证据 |
| reference | 快速查具体事实 | 适用范围/版本 → 精炼表格或条目 → 例外 → 来源 |
| overview | 如何进入这个领域 | 领域范围 → 心智结构 → 少量有理由的入口链接 → 边界与缺口 |

通用开头示例（日期仅为示例，创建时读取真实日期）：

```markdown
---
type: concept
status: draft
created: 2026-09-09
updated: 2026-09-09
aliases:
  - 可检索的真实别名
tags:
  - codegen
---

# 清楚的读者标题

先回答这个文档的主要问题，并限定适用的上下文。

## Sources and evidence

- **Source code:** 仓库路径和 commit/tag；哪些结论由这份代码支持。
- **Personal inference:** 根据哪些证据推断，哪些尚未验证。
```

创建文档时删除没有证据的示例条目及空 headings；不要把占位文字写进正式库。
