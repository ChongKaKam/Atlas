# Atlas deterministic tools

本页的 `atlas.py` 工具只读本地知识库，不作语义合并、技术纠错、网络请求、自动删除或 Git 操作。`build-index` 也只输出 Markdown 到 stdout，由调用者审阅后按现有写入授权保存。另有可写配置与更新 Skill 的 `atlas_user.py`，边界见 [用户配置与升级](user-management.md)。

## 环境

需要 Python 3.10+ 和 `scripts/requirements.txt` 中的 PyYAML、markdown-it-py。使用解析库以支持合法 YAML 和标准 Markdown 引用式/图片链接，避免用简陋正则模拟完整解析。

在选定的环境中运行（将路径替换为实际绝对路径）：

```sh
python3 -m venv /path/to/atlas-venv
/path/to/atlas-venv/bin/python -m pip install -r /path/to/atlas/scripts/requirements.txt
/path/to/atlas-venv/bin/python /path/to/atlas/scripts/atlas.py audit /path/to/knowledge-base
```

不覆盖已有虚拟环境，不自动改系统 Python。安装失败时报告缺失依赖；可继续语义工作、用 `rg` 搜索 inbound links 和人工检查 metadata，明确未执行的自动检查。

## 命令

知识库位置参数可以省略，此时按项目配置、环境变量、全局配置解析（见用户配置说明）；从用户项目工作目录执行，不要为了调用脚本先切到 Skill 目录。配置失效直接报错。显式路径仍兼容原有命令。

```sh
python /path/to/atlas/scripts/atlas.py validate /path/to/kb
python /path/to/atlas/scripts/atlas.py check-links /path/to/kb
python /path/to/atlas/scripts/atlas.py audit /path/to/kb --json
python /path/to/atlas/scripts/atlas.py audit /path/to/kb --strict
python /path/to/atlas/scripts/atlas.py build-index /path/to/kb
python /path/to/atlas/scripts/atlas.py build-index /path/to/kb --check
```

- `validate`：必填 metadata、枚举/类型、真实日期与顺序、唯一 H1、tags 格式/词表、未知字段、重名/大小写碰撞、WikiLinks、简单格式提示。
- `check-links`：解析 inline、reference links 和 images；检查相对路径存在性。忽略 code blocks 与 inline code；不访问网络。
- `audit`：前两者，加根控制文件及无入链候选。INDEX 的自动链接不算知识组织上的有效入链，目录链接也不算指向每个文件。
- `build-index`：按路径排序生成稳定 INDEX，包含 H1、type、status，不含运行时间；无技术知识可丢失。schema 错误时不输出索引。warning 发到 stderr。`--check` 比较现有 INDEX 是否相同，不写入。

退出码：0 无 error（可能有 warning）；1 检查有 error，或 `--strict` 下有 warning；2 无效参数/根路径/操作错误。`--json` 返回 findings/errors/warnings，适用于检查和 `build-index --check`。命令并不强制人工填写 recommended tags 数量。

## 范围与局限

- layout v2 按 `.atlas/layout.json` 扫描注册的项目、领域与 shared 中的 Markdown（包括草稿）；无注册表的旧库仍扫描 `knowledge/**/*.md` 和 `projects/**/*.md`。JSON 输出包含识别的 layout，非法/未知版本不静默回退。根控制文件和 v2 分区根 README/CONVENTIONS/TAGS/INDEX 不要求知识元数据。词表来自 KB 根控制文件。
- v2 未注册的顶层目录给出 `unregistered-scope` 警告，不扫描正文；注册但缺失的目录报错。隐藏目录、场景 profile 及 assets 目录不当作知识扫描。旧库只扫描 legacy 范围；源码/非 Markdown assets 只作为链接目标。范围不是“全磁盘扫描”。
- Symlink 文件和目录不读取；指向库外的相对链接标为 warning，不检查其目标。库内指向 symlink 且解析到库外也作此处理。
- Heading anchors 只提示 `anchor-unchecked`（info），不伪装成已验证；移动或改标题时必须人工确认 renderer 的 anchor 规则。HTML links 提示未检查。未定义的 Markdown reference 可能被 CommonMark 当普通文本，不报告为 broken link，需人工检查。
- 不验证远程 URL 存活、来源可靠性、技术真伪、人类是否审查过、同义 tag、语义重复或孤立文档的价值。
- 默认 schema 与旧库不一致时保留旧约定，说明工具兼容性结果；不能为了消除工具警告而进行未要求的迁移。

## Tag vocabulary

在 `CONVENTIONS.md` 或 `TAGS.md` 中保留恰好一个 fenced block，每行一个规范 tag：

````markdown
```atlas-tags
codegen
register-class
risc-v
```
````

没有此块时只验证 tag syntax，并给出 `vocabulary-missing`，不从自由文字猜词表。现有库的自然语言词表依然可人工使用；缺少此机器可读块不等同于没有维护约定。新 tag 不在词表是 warning，`--strict` 可用于受控新库。

## 验证开发

```sh
python -m unittest discover -s /path/to/atlas/tests -v
```

测试均在临时目录；覆盖实际解析、诊断、只读保证和索引再生成行为。Skill 语义验收情景另见 [acceptance](../tests/acceptance.md)，不把单元测试当成 LLM 工作流成功率。
