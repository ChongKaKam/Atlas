# Knowledge Base

本库保存可复用技术知识和需要保留上下文的项目记录。Markdown 为权威载体。

## 使用

通过文件名、H1、aliases 和正文检索知识。建立领域目录后在这里加入少量入口链接。

- 最外层是用户选择的项目/领域目录（如 `compiler-x/`、`llvm/`），按实际需要注册和创建。
- `shared/`：共享知识；具体正文/diff 经用户审核后才能融入，空目录不代表已有获批内容。
- `.atlas/layout.json`：分区名称与 project/domain/shared 类型的注册表；添加知识时先选择归属。
- `.atlas/capture-profiles/`：可选场景要求，由用户或维护约定明确选择，不随 Skill 更新覆盖。
- [维护约定](CONVENTIONS.md)：元数据、命名、来源与词表。

`draft` 是未经过完整人工审查的知识；使用结论前查看范围和来源。
