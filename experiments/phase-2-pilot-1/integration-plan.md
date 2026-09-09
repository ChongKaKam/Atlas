# Phase 2 Pilot 1 Integration Plan

> Status: applied, awaiting human review  
> Date: 2026-09-09  
> Specification under test: `references/knowledge-base-spec.md` v0.1

## Objective

用一组公开、真实、可追溯的 LLVM/MLIR 技术资料验证 Atlas v0.1 对 ADD、INTEGRATE 和 ASK 的基本判断。该实验不验证 QMD、Obsidian、脚本或完整 workflow。

## Input sources

| ID | Source | Input role |
|---|---|---|
| S1 | [GlobalISel Core Pipeline](https://llvm.org/docs/GlobalISel/Pipeline.html) | GlobalISel 流水线以及 Legalizer 的阶段性保证。 |
| S2 | [GlobalISel Legalizer](https://llvm.org/docs/GlobalISel/Legalizer.html) | legality、legalization、上下文使用限制和 minimum rule set。 |
| S3 | [MLIR LLVM dialect](https://mlir.llvm.org/docs/Dialects/LLVM/) | LLVM dialect 的定位、与 LLVM IR 的语义关系及结构差异。 |
| S4 | [LLVM RISC-V Target Guide](https://llvm.org/docs/RISCVUsage.html) | RISC-V 后端的官方范围与版本敏感性背景。 |
| S5 | [`RISCVRegisterInfo.td`](https://github.com/llvm/llvm-project/blob/main/llvm/lib/Target/RISCV/RISCVRegisterInfo.td) | `sub_gpr_even`、`sub_gpr_odd`、`GPRPair` 与具体寄存器对定义。 |
| S6 | [`RISCVLoadStoreOptimizer.cpp`](https://github.com/llvm/llvm-project/blob/main/llvm/lib/Target/RISCV/RISCVLoadStoreOptimizer.cpp) | Zilsd 成对访存对偶数/奇数连续寄存器的检查，以及 super-register 构造。 |
| S7 | [`clang/lib/Basic/Targets/RISCV.cpp`](https://github.com/llvm/llvm-project/blob/main/clang/lib/Basic/Targets/RISCV.cpp) | Clang inline assembly 约束 `R` 的前端含义。 |

All sources were accessed on 2026-09-09. GitHub `main` sources are intentionally recorded as mutable sources because this pilot could not pin them to a commit; resulting claims therefore remain `draft`.

## Candidate Knowledge Units

| KU | Inputs | Question | Decision | Target |
|---|---|---|---|---|
| KU-1 | S1, S2 | GlobalISel Legalizer 在流水线中的职责和保证是什么？ | **Create**, then **Merge** overlapping definitions from S1/S2. | `knowledge/llvm/GlobalISel-legalization.md` |
| KU-2 | S2 | legality 判断何时可以依赖上下文？ | **Extend** KU-1 because the rule changes how the same Legalizer concept should be understood. | Section in KU-1 target. |
| KU-3 | S2 | 所有 target 必须满足哪些最小 legalization 连接能力？ | **Extend** KU-1 with a deliberately narrow summary; do not reproduce the full rule catalog. | Section in KU-1 target. |
| KU-4 | S3 | LLVM dialect 是 LLVM IR 本身，还是 MLIR 中的映射？ | **Create** under MLIR, not LLVM, because the primary owner is an MLIR dialect. | `knowledge/mlir/LLVM-dialect.md` |
| KU-5 | S3 | PHI、context-level values 与 types 如何适配 MLIR 结构？ | **Extend** KU-4; these are supporting mechanisms for the same reader promise. | Sections in KU-4 target. |
| KU-6 | S5, S6 | LLVM RISC-V backend 如何表示和验证 even/odd GPR pairs？ | **Create**, then **Merge** TableGen representation with optimizer behavior. | `knowledge/llvm/RISC-V-GPR-pairs.md` |
| KU-7 | S7 | Clang inline assembly 中 `R` 约束表达什么？ | **Extend** KU-6 as a separate context, explicitly not equating frontend constraint with backend register class. | Section in KU-6 target. |

## Explicitly skipped material

- S2 的完整 Legalizer API 和逐 opcode rule catalog：它们属于更细的 guide/reference KUs，不是本 pilot 的问题。
- S3 自动生成的全部 operation reference：体量大且不会改善 “LLVM dialect 是什么” 的回答。
- S4 的全部 extension/support 表：只保留后端范围和版本敏感性的背景。
- S5/S6 中与寄存器对无关的寄存器类和 load/store 优化逻辑。

这些内容是按 retrieval intent 跳过，而不是判断为无价值；未来出现对应问题时可以单独 ADD 或 INTEGRATE。

## Review gates

- 所有文档保持 `status: draft`，直到人类核对其技术范围与表述。
- `RISC-V-GPR-pairs.md` 不将 LLVM 实现细节冒充为 RISC-V ISA 的一般规则。
- 不把上游文档结构一比一复制进知识库。
- 不因两个来源使用不同抽象层次而标记 Conflict。
