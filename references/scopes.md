# 项目、领域与共享知识

新知识库采用 layout v2：最外层直接放项目或领域，以及唯一的 `shared`。不再要求 `knowledge/`、`projects/` 包装层。

```text
KnowledgeBase/
├── README.md
├── CONVENTIONS.md
├── .atlas/
│   ├── layout.json
│   └── capture-profiles/       # 用户可选的场景要求，独立于 Skill 安装
├── compiler-x/                # project
│   ├── CONVENTIONS.md          # 可选：项目范围、所选场景要求
│   └── Legalization.md
├── llvm/                      # domain
│   └── GPRPair.md
└── shared/                    # 用户审核过融入方案的跨项目/领域知识
    └── Register-pair-model.md
```

目录名使用 lowercase-kebab-case，项目或领域的身份记录在 `.atlas/layout.json`，不从名字猜测。`shared` 固定为共享分区；`assets`、`knowledge`、`projects` 是保留名。每篇文档只有一个主要归属，用相对链接表达跨区关系；下级目录按实际主题需要创建，不按文档类型分树。

```json
{
  "version": 2,
  "scopes": {
    "shared": {"kind": "shared"},
    "compiler-x": {"kind": "project"},
    "llvm": {"kind": "domain"}
  }
}
```

初始化只创建根控制文件、注册表和空 `shared`，不创建假设的项目/领域。空 `shared` 不包含任何获批知识。

## 添加知识时选择归属

1. 解析 KB 根目录，运行 `atlas_user.py scopes`，读取根 README/CONVENTIONS 以及候选分区的约定。
2. 提示用户选择已有项目、已有领域或新分区，并说明推荐理由。用户本次已明确选择，或此前已明确设定本轮批次目标时，展示选择并继续，不反复询问。项目 KB 根路径不等于已选库内分区；不得仅凭打开的源码目录替用户决定。
3. 新分区名称/类型明确后，用 `scopes --add <name> --kind project|domain` 注册和创建。读操作只列分区，不创建目录。现有非空目录可按用户授权注册，但不改写内容。
4. 查重优先选中分区与 `shared`，再按证据和关系检索其他相关分区；跨区候选不等于跨区写入授权。可链接已有共享知识，不为减少重复而强制提升。
5. 每个 KU 记录归属；混合批次允许多个已选分区。归属不明的部分先留在回复/隔离草案中，不自动放进 `shared` 或创建 inbox。

## 共享融入审核（强于一般 Apply 授权）

写入 `shared` 的新增、补充、纠错、合并，以及从项目/领域提升知识，都先提供**具体正文或 diff**：来源分区与 KU、泛化后保留的条件/参数、证据、目标路径、原文保留或链接替代方案、涉及的链接修复。等待用户审核该版本后才写入。

「这可能通用」「整理全部」「直接执行」「选择 shared」本身不是对具体正文的审核。已有对同一草案的明确批准可直接执行；批准后实质改变内容则重审。未获批准时不写 shared 草稿、不标 reviewed、不删除或替换项目原文；已授权的非共享部分可以继续。共享区删除/移出和纯格式/链接修复也应展示对应 diff 并得到明确授权，防止绕过审核边界。

审核通过后，在共享文档正文 `Shared integration review` 简记实际审核日期、批准内容/范围与来源文档；不编造姓名或审核事件，不记录多余私人会话。共享融入审核确认的是内容与归属；只有用户确实审查了技术结论、证据和范围才设 `status: reviewed`，否则保持 `draft`。机器检查不能证明人类确实审核过。

## 旧库兼容与迁移

无 `.atlas/layout.json` 的库按 legacy v1 读取 `knowledge/`、`projects/`，不擅自生成 v2 注册表。注册新分区前先给迁移方案：例如 `knowledge/llvm/A.md → llvm/A.md`、`projects/compiler-x/B.md → compiler-x/B.md`。明确每项新归属、跨库外部链接和路径冲突；获准后移动、修复入链/出链并创建注册表。不能只加注册表而让旧文档从扫描范围消失。

**旧 knowledge 不自动等于 shared。** 普通知识可以归到领域分区，任何进入 shared 的内容仍须审核。升级 Skill 只报告旧布局需要适配，不能借升级之名迁移或发布知识。

工具只扫描注册分区；未注册的顶层目录给出警告，隐藏扩展配置与 assets 不当知识文档检查。分区根 README/CONVENTIONS/TAGS/INDEX 可作为导航控制文件，不要求知识 frontmatter；标签词表仍以 KB 根约定为准。
