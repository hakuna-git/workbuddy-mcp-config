# CHANGELOG

## v2.1.0 (2026-06-01)

### macOS 部署支持

**新增文档：**
- `docs/macos-notes.md` — macOS 代码签名冲突根因分析 + 3 种解决方案
- 更新 `DEPLOY.md` — 新增 macOS 特别说明和故障排查章节
- 更新 `README.md` — 目录结构和注意事项中加入 macOS 文档引用

**新增脚本：**
- `scripts/zotero-mcp-wrapper.sh` — 可复用 wrapper 模板，用 `/bin/bash` 绕过 macOS managed Python 代码签名问题

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