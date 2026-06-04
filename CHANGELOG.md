# CHANGELOG

## v2.2.0 (2026-06-04)

### zotero 部署重构 — 告别代码签名坑

**核心修复：** zotero-mcp 不再依赖 `$BIN_DIR/zotero-mcp` 软链接，改用与 github-mcp 一致的 `managed Python + launcher` 模式。

**变更：**
- `mcp.template.json`: zotero `command` 改为 `__PYTHON_BIN__`，`args` 改为 `__MCP_DIR__/zotero_launcher.py`
- 新增 `scripts/zotero_launcher.py` — 启动器，内置 macOS 签名自修复 + 环境变量设置
- **弃用** `scripts/zotero-mcp-wrapper.sh` — bash wrapper 在 WorkBuddy 沙箱下反而不稳定
- `setup.sh` 新增自动安装 zotero-mcp-server + macOS 签名检测修复

**效果：** 新 Mac 上 `bash setup.sh` 一键跑完，只需手动填 GITHUB_TOKEN + 信任 MCP。

## v2.1.0 (2026-06-01)

### 长文档推送支持

`batch_commit_files` / `create_or_update_file` 要求文件内容嵌入 MCP JSON 消息，长文档（>100 行）容易触发消息体大小限制。

**新增工具：**
- `push_file_from_path` — 指定本地文件路径，脚本自行读取并推送（内容不经过 MCP 消息）
- `batch_commit_from_paths` — 同上，批量版本

**设计要点：**
- MCP 只传 `local_path`（字符串），不传文件内容
- 自动检测 sha，已存在的文件走更新逻辑
- 纯标准库，零依赖

### macOS 部署支持

**新增文档：**
- `docs/macos-notes.md` — macOS 代码签名冲突根因分析 + 3 种解决方案
- 更新 `DEPLOY.md` — 新增 macOS 特别说明和故障排查章节
- 更新 `README.md` — 目录结构和注意事项中加入 macOS 文档引用

**新增脚本：**
- `scripts/zotero-mcp-wrapper.sh` — 可复用 wrapper 模板（v2.2.0 已弃用）

## v2.0.0 (2026-06-01)

### github-mcp upgrade: read-only → read/write

**新增写工具：**
- `create_repository` — 创建 GitHub 仓库
- `update_repository` — 修改仓库设置
- `create_or_update_file` — 单文件增改
- `delete_file` — 删除文件
- `batch_commit_files` — 批量提交多文件

**已有工具增强：**
- `get_file_contents` 新增返回 `sha` 字段，供写操作使用
- 服务器名从 `github-reader-mcp` 更名为 `github-mcp`

## v1.0.0 (2026-05-31)

### 初始版本

- `get_file_contents` — 读取 GitHub 文件/目录
- `search_repositories` — 搜索仓库
- `list_commits` — 列出提交记录
- `list_branches` — 列出分支
- 模板化部署：`mcp.template.json` + `setup.sh`
- 纯标准库，零依赖