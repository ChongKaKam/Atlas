# 用户配置与 Skill 升级

管理工具 `scripts/atlas_user.py` 使用 Python 3.10+ 标准库。初始化会写配置；`update` 默认从已配置的 GitHub upstream 拉取并更新 Skill，`update --check` 才是仅预检查（保留 `--apply` 兼容旧命令）。升级的知识库审计需要同一 Python 环境已安装 `scripts/requirements.txt`。用户调用 Atlas 的 `update` 默认更新 Skill；明确指向知识内容的修订仍走知识 UPDATE。

## 首次初始化

用户要求初始化但没给路径时，只询问：「你希望把全局知识库放在哪个绝对路径？已有目录也可以。」不把 Skill 目录、开发实验或当前源码仓库擅自当作知识库；不修改 shell 启动文件。已有明确路径和初始化授权时直接执行，无需重复确认。

从任意目录执行（以下 `python` 为选定解释器）：

```sh
# 注册已有目录，不移动、不修改其中笔记
python /path/to/atlas/scripts/atlas_user.py init --kb /absolute/path/to/KnowledgeBase

# 仅在用户要求创建新库时使用；目录必须不存在或为空
python /path/to/atlas/scripts/atlas_user.py init --kb /absolute/path/to/KnowledgeBase --create
```

全局配置默认保存至 `~/.config/atlas/config.json`；设置了绝对路径 `XDG_CONFIG_HOME` 时保存至其 `atlas/config.json`。格式：

```json
{"version": 1, "kb_root": "/absolute/path/to/KnowledgeBase"}
```

新库复制 README 与 CONVENTIONS 模板，创建 `.atlas/layout.json` 和空 shared；Agent 随后按用户范围填写模板，添加知识时请用户选择项目或领域。完整组织规则见 [分区与共享审核](scopes.md)。注册已有库不会强制更改其格式或添加控制文件。已有定位配置仅更新 `kb_root`，保留其他键；无效或不支持的配置版本拒绝覆盖。

```sh
# 列出当前库的分区和可用场景扩展；只读
python /path/to/atlas/scripts/atlas_user.py scopes
# 用户选定新项目/领域后注册；不写知识正文
python /path/to/atlas/scripts/atlas_user.py scopes --add compiler-x --kind project
python /path/to/atlas/scripts/atlas_user.py scopes --add llvm --kind domain
```

## 定位与项目覆盖

优先级从高到低：

1. 本次请求的显式 KB 路径（命令行 `--kb` 或检查工具的位置参数）。
2. 从用户工作目录向上查找最近的 `.atlas/config.json`；其中相对 `kb_root` 相对于该项目根目录，而不是 `.atlas/`。
3. 环境变量 `ATLAS_KB_ROOT`，必须是非空绝对路径，支持 `~` 展开。
4. 用户全局配置。

环境变量适合终端临时覆盖；持久配置避免桌面应用未继承终端环境时无法定位。项目覆盖优先于环境变量。本次显式路径不持久化。命中的配置损坏、目录不存在或无权限时终止，不尝试更低优先级。

```sh
export ATLAS_KB_ROOT="/absolute/path/to/KnowledgeBase"

# 将已有目录设置为这个项目的知识库；不改变全局默认
python /path/to/atlas/scripts/atlas_user.py init \
  --project /absolute/path/to/Project --kb /absolute/path/to/Project/docs/knowledge

python /path/to/atlas/scripts/atlas_user.py resolve --cwd /absolute/path/to/Project
```

`resolve` 输出最终 `root` 和 `source`，只检查配置和路径，不扫描笔记。项目配置保存相对路径，便于项目内知识库一起移动；若指向项目外，移动后需重新确认路径。包含个人路径的 `.atlas/config.json` 建议在对应项目中忽略；不要未经要求修改其他项目的 Git 配置。

取消项目覆盖可在用户明确要求后移除该项目配置，取消环境覆盖可执行 `unset ATLAS_KB_ROOT`。不要为了切换库删除知识目录。KB 内部的 `<project-or-domain>/` 分区，与这里「每个源码项目选择自己的 KB 根目录」不同。

## Skill 自更新

```sh
# 预检查：访问配置的 Git 远端，但不 fetch、不改 Skill 或知识库
python /path/to/atlas/scripts/atlas_user.py update --check --cwd /absolute/path/to/Project

# 用户明确要求升级后执行
python /path/to/atlas/scripts/atlas_user.py update --cwd /absolute/path/to/Project
```

脚本定位自身真实路径，支持软链接安装。仅支持独立 Git checkout，使用当前分支已配置的 upstream（官方仓库为 `https://github.com/ChongKaKam/Atlas.git`，也支持用户选择的 SSH 地址/fork；不强行切 main 或修改远端）。Agent 执行默认更新前先用 `git remote -v` 核实来源，首次未知来源先让用户确认，因为更新后的 Skill 包含可执行代码。本地远端仅用于隔离测试，不声称对未验证的地址进行了 GitHub 更新。

- 本地已跟踪或未跟踪改动、detached HEAD、无远端跟踪分支、错误 KB 配置都会阻止升级。ZIP 安装需重新下载并单独处理本地修改；脚本不替 ZIP 目录初始化 Git。
- `update --check` 通过 `git ls-remote` 比较版本；`different` 只表示 commit 不同，不承诺可快进。实际升级使用 `git pull --ff-only --no-rebase`，禁用本次 pull 的 hooks 和 autostash。分叉会停止，不 stash/reset/force，不覆盖用户改动；失败的 pull 可能已刷新 Git 的远端引用，但不合并分叉历史。
- KB 与 Skill 不得相互嵌套。仅审计当前解析到的一个 KB，不搜索全磁盘、不把笔记上传、不修改 KB，也不修改全局/项目配置。其他库需分别用 `--kb` 检查。
- 有 KB 时升级前审计；已有 schema error 不阻止 Skill 更新，但必须报告。无法运行审计（例如缺依赖）会阻止 apply。升级后用新代码重新审计，输出前后完整 findings；Agent 对比新增、消失、已有问题，不能将已有错误误称为升级造成。
- 未配置 KB 时允许只升级 Skill，明确标为未检查知识库。升级不要求强制迁移旧约定，不安装依赖。`requirements_changed` 为 true 时提示在原虚拟环境安装新 requirements，再审计。
- `updated-check-failed` / `updated-with-kb-errors` 表示 pull 已完成但检查未通过（是否改变代码以 before/after 为准）；不要声称 pull 没发生，也不要自动回滚。下一步根据缺失依赖或具体兼容性问题处理，任何笔记迁移另取授权。正常的 `unchanged` 表示 pull 后 commit 没变。

更新完成后重新读取新的 SKILL.md 与本次相关引用；必要时开启新会话加载新指令。交付旧/新 commit、KB 路径与来源、依赖变化、审计差异及未执行项。用户只是询问是否有更新时只运行预检查；用户已经要求升级时无需再次索取笼统批准。

## 新功能对比与本地整合

脚本输出 `changes`（文件变更）、`diff_stat`、`audit_diff`（新增/消失/未变诊断）、`local_context`（布局、约定路径、场景 profile 文件名）及 `integration` 后续步骤。检查项的路径/行号变化可能表现为消失+新增，不能直接当作语义错误变化。

Agent 完成升级后：

1. 使用返回的真实 before/after commit 执行 `git diff --no-ext-diff --no-textconv <before> <after> -- SKILL.md references assets scripts`，按变更范围读取新版说明，不只读文件名就声称完成“功能整合”。
2. 说明新增/变化/移除的能力与默认行为，特别是命令参数、布局与审核要求。快进已经整合上游代码，但不等于本地知识规则已经迁移。
3. 读取当前任务选择的本地 profile、根和分区约定，对照新版通用 Capture 模板，组合兼容的增量要求；不修改未选 profile。把场景要求保存在知识库而非 Skill checkout，正常升级保留其原文件。
4. 无冲突的新工作流可直接使用；布局迁移、配置版本变更、场景规则冲突先给具体适配方案。用户确认前不改 KB、不替换扩展文件，shared 仍需具体正文审核。缺依赖时报告并在获准的虚拟环境补齐后重查，不把安装失败当知识错误。
5. 报告“已拉取的代码 / 已核对并生效的工作流 / 待确认的适配”。如果 Skill checkout 有本地编辑或分叉，只报告阻止原因、版本和需对比的文件；可按用户要求进一步 fetch 与准备合并方案，不自动解决冲突或丢弃定制。

旧版管理脚本没有新命令时，可在确认来源、工作区干净及已有升级授权后运行 `git pull --ff-only --no-rebase` 引导升级，再用新版脚本检查。不要在当前未提交的开发目录上强行拉取。

管理命令输出 JSON。退出码 0 表示命令完成（预检查 findings 仍可能有错误）；1 表示 Skill 已更新但 KB 后检查有错误或不可运行；2 表示参数、配置、Git 或操作失败。具体语义兼容性、来源真实性、独立 LLM 工作流不由这些检查证明。
