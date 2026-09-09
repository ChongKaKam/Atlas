---
type: concept
status: draft
created: 2026-09-09
updated: 2026-09-09
aliases:
  - LLVM IR dialect
  - MLIR LLVM dialect
tags:
  - llvm-ir
  - lowering
---

# MLIR LLVM Dialect

LLVM dialect 是 MLIR 中对 LLVM IR operations、types 和相关语义的建模层，不是把一段 LLVM IR 文本原封不动地嵌入 MLIR。除非文档明确说明，LLVM dialect operation 的语义应与对应 LLVM IR instruction 一致；但表示形式会适配 MLIR 的结构与基础设施。

这一区分很重要：**语义对应不等于结构同构**。

## 为什么放在 `mlir/`

这个 KU 的主要问题是 “MLIR 如何表达 LLVM IR 语义”，因此主要所有者是 MLIR。LLVM IR 是被映射的语义来源，不是该 document 的组织归属。

## 结构适配

### PHI 与 block arguments

MLIR 使用 block arguments 在 block 之间传递值，因此 LLVM dialect 不需要一个与 LLVM IR `phi` instruction 一一对应的 operation。Terminator 把 successor operands 传给目标 block arguments，表达等价的数据流。

### Context-level values

LLVM IR 中某些 context-owned values 在 LLVM dialect 中由普通 operation 产生，例如 `llvm.mlir.constant`、`llvm.mlir.undef`、`llvm.mlir.poison` 与 `llvm.mlir.zero`。`mlir` 前缀说明这些是为 MLIR 表示而提供的辅助 operation，而不是对应的 LLVM IR instruction 名称。

### Types

LLVM dialect 会尽量复用兼容的 MLIR built-in types，只为没有合适 built-in 表示的 LLVM IR types 定义补充类型。因此 `i32` 可以直接使用，而 pointer、array、LLVM function type 等使用 `!llvm.*` 形式。

## Dependency boundary

LLVM dialect 不应依赖需要 `LLVMContext` 的 LLVM IR objects，而使用适合 MLIR 基础设施的替代表示。这说明它是独立的 MLIR dialect abstraction，而不是 LLVM IR object model 的薄包装。

## Sources and evidence

- **Official documentation:** [‘llvm’ Dialect — MLIR](https://mlir.llvm.org/docs/Dialects/LLVM/), accessed 2026-09-09; semantic correspondence, dependency boundary, PHI adaptation, context-level values, and type compatibility.
- **AI-assisted synthesis:** Atlas selected concept-level material from a much larger reference page and skipped the generated operation catalog. The technical summary remains `draft` pending human review.
