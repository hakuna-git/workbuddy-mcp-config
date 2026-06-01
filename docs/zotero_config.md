# Zotero MCP 配置说明

## 安装

```bash
# 方式一：pip 安装
pip install zotero-mcp-server

# 方式二：通过 Zotero 插件
# 在 Zotero 中安装 "Better BibTeX" 插件后，
# 确保 Zotero 客户端运行并开启本地 API
```

## mcp.json 片段

```json
"zotero": {
  "command": "__BIN_DIR__/zotero-mcp",
  "args": ["serve"],
  "env": {
    "ZOTERO_LOCAL": "true",
    "ZOTERO_LOCAL_PORT": "23119",
    "ZOTERO_READ_ONLY": "true"
  }
}
```

## 前置条件

| 条件 | 说明 |
|------|------|
| Zotero 客户端 | 需要安装并运行 |
| 本地 API | Zotero → 首选项 → 高级 → 允许本地 API（默认端口 23119） |
| zotero-mcp 二进制 | 安装在 `__BIN_DIR__` 下 |

## 环境变量说明

| 变量 | 值 | 说明 |
|------|-----|------|
| `ZOTERO_LOCAL` | `"true"` | 使用本地 Zotero API（不通过云端） |
| `ZOTERO_LOCAL_PORT` | `"23119"` | Zotero 本地 API 端口 |
| `ZOTERO_READ_ONLY` | `"true"` | 只读模式，防止误修改文献库 |
