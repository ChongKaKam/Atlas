---
type: concept
status: draft
created: 2026-09-09
updated: 2026-09-09
aliases:
  - GPRPair
  - even-odd GPR pair
tags:
  - register-class
  - risc-v
---

# LLVM RISC-V GPR Pairs

LLVM 的 RISC-V backend 使用 `GPRPair` register class 表示由两个 general-purpose registers 组成的 even/odd super-register。`sub_gpr_even` 与 `sub_gpr_odd` 提供对子寄存器的访问；每个 subregister 的宽度随 RV32/RV64 hardware mode 改变，因此整个 pair 表示两个 XLEN-wide parts。

这是 LLVM backend 的实现概念。某条 RISC-V extension、ABI 或 instruction 是否要求 register pair，必须在各自上下文中单独判断；不能从 `GPRPair` 的存在推导出所有 RISC-V 双宽值都必须使用偶数/奇数对。

## Register class shape

`RISCVRegisterInfo.td` 构造了从 `X0_Pair` 到普通连续 even/odd physical register pairs 的 super-register，并定义：

- `GPRPair`：允许的一组 pair；
- `GPRPairNoX0`：排除特殊 `X0_Pair`；
- `GPRPairC`：适合特定 compressed-register 子集的更小集合。

`X0_Pair` 使用 dummy second register，因为相关成对访存语义中使用 `x0` 时并不访问 `x1`。这是特殊语义的建模，不应推广为普通 pair 行为。

## Zilsd load/store optimization context

在当前 `RISCVLoadStoreOptimizer.cpp` 的 Zilsd post-register-allocation 路径中，一个普通 pair 必须满足：第一个 register 的 encoding 是偶数，第二个紧随其后。若 pair 有效，optimizer 用 `getMatchingSuperReg` 和 `sub_gpr_even` 找到相应 `GPRPair` super-register；若无效，则把 pseudo paired operation 拆回两个 operations。

这是一条特定 pass 与 extension 路径下的实现观察，不是所有使用 `GPRPair` 的代码路径的统一验证算法。

## Clang inline assembly context

Clang RISC-V target 把 inline assembly constraint `R` 解释为 even/odd GPR pair。它与 backend `GPRPair` 指向相关的硬件形状，但二者处于不同 abstraction layer：前者是用户可见的 constraint validation，后者是 LLVM code generation 的 register representation。应建立关联，不应把它们合并成同一个 API 概念。

## Relation to GlobalISel

当前来源只证明 `GPRPair` 的 TableGen 表示、Zilsd optimizer 使用方式和 Clang constraint，不能据此断言它参与某条 GlobalISel legalization 路径。即使后续源码证明存在该关系，target-specific representation 也不会改变 [GlobalISel Legalization](GlobalISel-legalization.md) 对 legality query 的通用定义。

## Sources and evidence

- **Source code:** [`RISCVRegisterInfo.td`](https://github.com/llvm/llvm-project/blob/main/llvm/lib/Target/RISCV/RISCVRegisterInfo.td) on `main`, accessed 2026-09-09; subregister indices, pair construction, and register classes.
- **Source code:** [`RISCVLoadStoreOptimizer.cpp`](https://github.com/llvm/llvm-project/blob/main/llvm/lib/Target/RISCV/RISCVLoadStoreOptimizer.cpp) on `main`, accessed 2026-09-09; Zilsd pair validation, fallback splitting, and super-register lookup.
- **Source code:** [`clang/lib/Basic/Targets/RISCV.cpp`](https://github.com/llvm/llvm-project/blob/main/clang/lib/Basic/Targets/RISCV.cpp) on `main`, accessed 2026-09-09; inline assembly constraint `R`.
- **Official documentation:** [User Guide for RISC-V Target — LLVM](https://llvm.org/docs/RISCVUsage.html), accessed 2026-09-09; backend scope and the need to qualify claims by supported ISA/extension context.
- **AI-assisted synthesis:** Atlas combined related representations while explicitly preserving their abstraction boundaries. Sources are mutable `main` views and no compiler experiment was run; keep this document `draft`.
