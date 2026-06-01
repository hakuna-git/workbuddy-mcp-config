# Stata MCP 配置说明

## mcp.json 片段（使用占位符）

```json
"stata-mcp": {
  "command": "__BIN_DIR__/uvx",
  "args": ["stata-mcp"],
  "env": {
    "STATA_MCP__CWD": "__STATA_CWD__"
  }
}
```

> 运行 `setup.sh --stata-cwd /path/to/project` 会自动替换占位符。

## 配置项说明

| 配置项 | 占位符 | 说明 |
|--------|--------|------|
| `command` | `__BIN_DIR__/uvx` | uvx 二进制路径，setup.sh 自动检测 |
| `args` | `["stata-mcp"]` | 指定运行 stata-mcp 包（uvx 自动拉取） |
| `STATA_MCP__CWD` | `__STATA_CWD__` | Stata 工作目录，限定文件操作范围 |

## 安装依赖

```bash
# 安装 uv（包含 uvx）
brew install uv
# 或
pip install uv
```

## 激活步骤

1. 运行 `bash setup.sh`
2. 编辑 `~/.workbuddy/mcp.json` 确认路径正确
3. 打开 WorkBuddy 连接器管理
4. 找到 stata-mcp，点击「信任」
5. 告诉 WorkBuddy 测试连接
