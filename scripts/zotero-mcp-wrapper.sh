#!/bin/bash
# ============================================================
# zotero-mcp macOS Wrapper
# 用途：解决 managed Python 的代码签名问题
# 用法：将此文件的路径填入 mcp.json 的 args，command 设为 /bin/bash
#
# mcp.json 配置示例：
#   "zotero": {
#     "command": "/bin/bash",
#     "args": ["/path/to/zotero-mcp-wrapper.sh"],
#     "disabled": false
#   }
# ============================================================

# 根据你的环境修改以下路径
ZOTERO_MCP_BIN="/Users/qiuyangqian/.workbuddy/binaries/python/envs/default/bin/zotero-mcp"
# 或：ZOTERO_MCP_BIN="$HOME/.local/bin/zotero-mcp"

# Zotero 本地模式环境变量
export ZOTERO_LOCAL=true
export ZOTERO_LOCAL_PORT=23119
export ZOTERO_READ_ONLY=true

# 启动 zotero-mcp
exec "$ZOTERO_MCP_BIN" serve --transport stdio
