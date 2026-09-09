---
type: concept
status: draft
created: 2026-09-09
updated: 2026-09-09
aliases:
  - GlobalISel Legalizer
  - GMIR legalization
tags:
  - codegen
  - global-isel
  - legalization
---

# GlobalISel Legalization

GlobalISel Legalizer 位于 IRTranslator 之后、Register Bank Selector 之前。它把 target 不支持的 generic machine instructions 转换成当前 target 可以继续处理的形式，从而按照 target 的能力塑造 GMIR。

Legalizer 的阶段性保证是：完成该 pass 后，不应留下非法 operation，后续 pass 也不应重新引入非法 operation。这里的 “legal” 首先是 target 能够最终选择并处理该 instruction；它不等于 “已经变成 target instruction”。

## Legality 与 legalization

应区分两个问题：

1. **Legality query:** 当前 instruction 对该 target 是否 legal？
2. **Legalization action:** 如果不 legal，怎样把它改写成更接近 legal 或已经 legal 的形式？

Legality 只能依赖 instruction 自身携带的信息，不能依赖它周围的使用上下文。确定 instruction 不 legal 之后，选择具体改写方式时可以使用上下文。这一边界使 legality 结果保持局部、可查询，同时允许 legalization 做有依据的优化选择。

例如，若某个 operand 的常量值只存在于产生该 operand 的其他 instruction 中，该值不能决定当前 instruction 的 legality；若 immediate 本来就是当前 instruction 的组成部分，则可以参与判断。

## 与 SelectionDAG legalization 的边界

GlobalISel legalization 是迭代式过程，状态保存在 GMIR 中。与 SelectionDAG 的传统描述不同，它不把 type legalization 与 operation legalization 规定为两个独立阶段。将二者强行套用成相同的 phase model 会形成错误类比。

## Minimum rule set 的意义

Target 可以较自由地定义其 legal GMIR 形态，但仍需提供足够的基础连接能力。例如，producer type set 与 consumer type set 之间需要能通过 `G_ANYEXT` 和 `G_TRUNC` 连接适当的 scalar widths。其他 conversion 可以先降低为这些基础操作与仍可继续 legalization 的 operation。

这个 minimum rule set 不是 “所有 target 具有相同 legal operations”；它只提供让 legalization 可以持续推进的最低闭包条件。

## RISC-V implementation context

RISC-V 的具体 register class 或成对寄存器约束属于 target implementation context，而不是 GlobalISel legality 的通用定义。参见 [LLVM RISC-V GPR Pairs](RISC-V-GPR-pairs.md)。

## Sources and evidence

- **Official documentation:** [Core Pipeline — LLVM](https://llvm.org/docs/GlobalISel/Pipeline.html), accessed 2026-09-09; pipeline position and the post-Legalizer invariant.
- **Official documentation:** [Legalizer — LLVM](https://llvm.org/docs/GlobalISel/Legalizer.html), accessed 2026-09-09; legality definition, context boundary, iterative model, and minimum rules.
- **AI-assisted synthesis:** Atlas combined the two documents around one retrieval question. No compiler experiment was run, so implementation-sensitive claims remain `draft`.
