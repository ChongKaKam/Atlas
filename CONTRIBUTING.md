# Contributing to Atlas

Atlas 的目标是让人和 agent 都能维护普通 Markdown 知识库。修改应解决可复现的知识整理问题；语义判断保留在工作流中，确定性检查放入工具。

## 提交前

1. 先阅读 `SKILL.md` 与相关 references，明确修改影响的工作流。
2. 保持变更聚焦；不要同时混入大规模目录调整和无关的知识改写。
3. 工具行为变化时加入能验证实际输入/输出的回归测试，并在临时目录中运行。
4. 修改说明或模板时检查链接、命名、状态及来源规则的一致性。
5. 使用虚构或可公开分享的输入；不要提交个人知识库、内部文档、凭据或本机缓存。

## 验证命令

在仓库根目录、安装好 scripts/requirements.txt 的 Python 环境中运行：

```sh
python -m unittest discover -s tests -v
python scripts/atlas.py audit experiments/phase-2-pilot-1/knowledge-base
```

现有 pilot 有已知 warnings，见 references/validation.md；不要为让输出变干净而扩大变更。

语义工作流的测试情景见 tests/acceptance.md。报告时区分自动测试、作者自审和独立会话验证；说明未覆盖范围，不把脚本检查当成知识准确性证明。

## 分发

使用 `python scripts/package_skill.py --output dist/<version>.zip` 生成包。检查压缩包结构和依赖说明后再发布。`dist/` 不进入源码版本控制，发布附件由维护者单独上传。

根 README 的安装步骤应保持通用，不写入开发者机器的绝对路径。公共代码、许可选择、Release 和远端发布由维护者决定。
