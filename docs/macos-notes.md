# macOS 部署注意事项

> 本仓库的 `setup.sh` 在 Linux 上可直接运行，macOS 上有额外的代码签名问题需要处理。

## 核心问题：macOS 代码签名冲突

WorkBuddy 托管的 Python (`~/.workbuddy/binaries/python/versions/*/bin/python3`) 有特定的 Team ID 代码签名，而 `pip install` 安装的预编译 `.so` 扩展（如 pydantic_core、numpy 等）来自其他签名团队。macOS 的安全策略拒绝不同 Team ID 的代码在同一进程中加载。

### 典型错误

```
ImportError: dlopen(...pydantic_core/_pydantic_core.cpython-313-darwin.so, 0x0002):
  code signature ... not valid for use in process:
  mapping process and mapped file (non-platform) have different Team IDs
```

```
MCP error -32000: Connection closed
```

```
spawn /Users/.../zotero-mcp ENOENT
```

## 解决方案（按推荐顺序）

### 方案 1：Bash Wrapper（推荐 ✓）

用 Apple 原生签名的 `/bin/bash` 作为启动入口，再 `exec` 到 Python：

**1) 创建 wrapper 脚本**

```bash
cat > ~/.workbuddy/mcp/zotero-mcp-wrapper.sh << 'EOF'
#!/bin/bash
export ZOTERO_LOCAL=true
export ZOTERO_LOCAL_PORT=23119
export ZOTERO_READ_ONLY=true
exec /path/to/venv/bin/zotero-mcp serve --transport stdio
EOF
chmod +x ~/.workbuddy/mcp/zotero-mcp-wrapper.sh
```

**2) 修改 mcp.json**

```json
"zotero": {
  "command": "/bin/bash",
  "args": ["/Users/xxx/.workbuddy/mcp/zotero-mcp-wrapper.sh"],
  "disabled": false
}
```

### 方案 2：Ad-hoc 重签 Python

如果必须直接使用 managed Python，需要重签：

```bash
# 重签 Python 二进制（去掉 Team ID，改为 ad-hoc 签名）
codesign --force --deep --sign - /path/to/managed/python3

# 重签问题扩展
codesign --force --sign - /path/to/venv/lib/**/pydantic_core/*.so
```

⚠️ 注意：`--remove-signature` 会导致 "Trying to load an unsigned library" 错误，必须用 `--sign -` 做 ad-hoc 重签。

### 方案 3：使用系统 Python

如果系统 Python 版本够新（≥3.10），可以用系统 Python 创建独立 venv 安装 zotero-mcp-server。但 macOS 自带 Python 3.9 太旧，需要额外安装 Homebrew Python。

## 其他 macOS 注意事项

- **软链接**：WorkBuddy 的 MCP spawner 不跟随软链接，必须使用真实路径
- **uv tool install**：会被 WorkBuddy 沙箱拦截，改用 pip + venv
- **brew formula**：`brew install zotero-mcp` 可能不存在，直接用 pip

## 部署验证

```bash
# 测试 zotero-mcp 能否启动
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
  | /path/to/venv/bin/zotero-mcp serve --transport stdio

# 期望输出包含 "serverInfo":{"name":"Zotero"...}
```
