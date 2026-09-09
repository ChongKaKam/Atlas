# Phase 2 Pilot 1 Report

> Status: initial curation example complete; independent workflow validation pending  
> Date: 2026-09-09

## Scope and method

本 pilot 使用七个 LLVM Project 官方文档或源码页面作为真实输入，先建立 [`integration-plan.md`](integration-plan.md)，再依据 Atlas v0.1 创建隔离知识库。没有复制输入文档结构，也没有使用 QMD、Obsidian、向量数据库或自定义脚本。

补充方法限制：该计划和最终文件在同一批编辑中生成，没有保存逐阶段的 Create → Merge → Extend 前后状态，也没有测试对既有用户知识库进行整合或重复导入。因此它是多来源整理示例，不能作为 INTEGRATE 幂等性、迁移安全性或完整 Review → Apply 行为已通过的证据。

语言假设：中文作为解释性正文的默认语言，LLVM/MLIR/RISC-V identifiers 与上游术语保持原文。这个假设需要在扩大 Phase 2 前由用户确认。

## Operations performed

### ADD

从一个大型 MLIR reference page 中提取 “LLVM dialect 如何映射 LLVM IR 语义” 这一 reader promise，创建 [`knowledge/mlir/LLVM-dialect.md`](knowledge-base/knowledge/mlir/LLVM-dialect.md)。生成的 operation catalog 和大量细节没有进入该 concept document。

结果：`concept` 边界清楚；`aliases` 对 “LLVM IR dialect” 与 “MLIR LLVM dialect” 有直接检索价值；primary domain 选择 `mlir/` 没有歧义。

### INTEGRATE — GlobalISel

把 Core Pipeline 与 Legalizer 两个来源中的重叠定义合并到 [`knowledge/llvm/GlobalISel-legalization.md`](knowledge-base/knowledge/llvm/GlobalISel-legalization.md)，并把 context rule 与 minimum rule set 作为紧密支持 KU 扩展进去。

结果：`Merge` 与 `Extend` 的区别可操作。若把 minimum rules 或完整 API 全部写入当前文件，会开始破坏单一 reader promise，因此进行了明确 Skip。

### INTEGRATE — RISC-V GPR pairs

把 TableGen register representation、load/store optimizer behavior 与 Clang inline assembly constraint 组织到 [`knowledge/llvm/RISC-V-GPR-pairs.md`](knowledge-base/knowledge/llvm/RISC-V-GPR-pairs.md)。

结果：三者可以共享一个上位 concept document，但必须保留 abstraction context。当前 primary question 是 LLVM 如何表示和使用 pair，所以选择 `llvm/` 并用 `risc-v` tag 表达跨域关系。若未来加入纯 ISA requirement，应建立 `isa/` document 并从这里链接。

## ASK evaluation

以下四项是撰写者在同一会话中对答案覆盖范围的自查。撰写者此前已读过来源，未隔离记忆，也没有独立检索执行记录；因此只能说明正文包含回答线索，不能证明 ASK 检索性能或工作流通过。早期报告中的 Pass 应按此限制理解。后续需要在新会话用本地文件检索重测。

### Query 1

**Question:** GlobalISel Legalizer 结束后保证什么？legality 判断能否查看 use context？

**Retrieved:** `knowledge/llvm/GlobalISel-legalization.md`

**Answer:** 结束后不应留下 illegal operations，后续 pass 也不应重新引入它们。Legality query 只能依赖 instruction 本身；确定其 illegal 后，选择 legalization action 时可以利用 context。

**Assessment:** Pass. 一个文件直接回答，无需回到来源页面。

### Query 2

**Question:** MLIR LLVM dialect 是否只是另一种 LLVM IR 文本语法？

**Retrieved:** `knowledge/mlir/LLVM-dialect.md`

**Answer:** 不是。它保持 LLVM IR 对应语义，但适配 MLIR 结构，例如以 block arguments 表示 PHI 数据流、以 operations 产生 context-level values，并复用兼容的 MLIR built-in types。

**Assessment:** Pass. `aliases` 与 H1 都能自然命中该问题。

### Query 3

**Question:** LLVM 中的 RISC-V `GPRPair` 是否意味着所有双宽 RISC-V 值都必须使用 even/odd registers？

**Retrieved:** `knowledge/llvm/RISC-V-GPR-pairs.md`

**Answer:** 不能这样推导。`GPRPair` 是 backend representation；具体 extension、ABI 或 instruction 的限制需要单独确认。Zilsd optimizer 与 Clang `R` constraint 是两个明确但不同 abstraction contexts。

**Assessment:** Pass. 文档中的 scope guard 阻止了从实现细节错误推广到 ISA。

### Query 4

**Question:** LLVM dialect 和 GlobalISel Legalizer 是同一层的 legalization 机制吗？

**Retrieved:** `knowledge/mlir/LLVM-dialect.md`, `knowledge/llvm/GlobalISel-legalization.md`

**Answer:** 不是。LLVM dialect 是 MLIR 中映射 LLVM IR 语义的 dialect；GlobalISel Legalizer 是 LLVM code-generation pipeline 中塑造 GMIR 以满足 target legality 的 pass。

**Assessment:** Pass. Domain separation improved the answer rather than fragmenting it.

## Findings against v0.1

| Hypothesis | Result | Evidence |
|---|---|---|
| Domain-first placement is predictable. | Supported, with one useful ambiguity. | LLVM dialect clearly belongs to `mlir/`; `GPRPair` belongs to `llvm/` only after stating the primary question. |
| A KU is not an input document. | Supported. | Two GlobalISel inputs became one document; one large LLVM dialect input contributed only selected KUs. |
| Six document types are sufficient. | Not tested. | All created knowledge documents are `concept`; this pilot did not test `guide`, `investigation`, `decision`, `reference`, or `overview`. |
| Body provenance is adequate without `source` frontmatter. | Supported for this sample. | Multiple sources, scope, mutability, and AI role were expressible without YAML objects. |
| Standard relative Markdown links are sufficient. | Supported. | Cross-document relationships and pilot navigation work without WikiLinks. |
| Three-state status model supports review-first. | Supported. | `draft` accurately signals unpinned mutable sources and absence of human review/experiments. |
| Flat tags remain small. | Supported. | Seven vocabulary entries cover three documents without hierarchy or spelling variants. |

## Specification changes recommended

Do not change the core v0.1 rules after only this pilot. Two Phase 2 questions have been added to the specification before a broader corpus is integrated:

1. **Language policy:** default prose language, treatment of bilingual aliases, and whether translated technical terms should be normalized.
2. **Source revision policy:** whether source-code-derived `reviewed` documents must pin a commit/tag, or whether `main` plus access date is acceptable for low-risk knowledge.

These questions are evidence from actual curation friction, not speculative metadata requests.

## Next experiment

The next pilot should use user-authored material rather than public reference pages and should deliberately include:

- one reproducible experiment or debugging record, to test `investigation` versus `guide`;
- one overlapping note with an incorrect or stale claim, to test Correction versus True Conflict;
- one project-specific note that may be promoted into reusable knowledge;
- at least one document containing several unrelated KUs.

This requires a small sample of the user’s real Markdown notes and confirmation of the preferred prose language. Until then, expanding the public-source corpus would add volume but would not test the remaining high-risk assumptions.
