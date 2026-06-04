#!/bin/bash
# ============================================================
# WorkBuddy MCP 一键部署脚本
# 用法: bash setup.sh [--stata-cwd /path/to/project]
# 幂等安全 — 重复运行自动保留已有 GITHUB_TOKEN
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MCP_DIR="$HOME/.workbuddy/mcp"
MCP_JSON="$HOME/.workbuddy/mcp.json"

echo "=========================================="
echo " WorkBuddy MCP 配置部署"
echo "=========================================="
echo ""

# ---- 1. 检测 Python ----
echo "[1/5] 检测 Python 解释器..."

PYTHON_BIN=""
# 优先使用 WorkBuddy 托管版本
if [ -x "$HOME/.workbuddy/binaries/python/versions/3.13.12/bin/python3" ]; then
    PYTHON_BIN="$HOME/.workbuddy/binaries/python/versions/3.13.12/bin/python3"
    echo "  找到 WorkBuddy 托管 Python: $PYTHON_BIN"
elif command -v python3 &>/dev/null; then
    PYTHON_BIN="$(command -v python3)"
    echo "  使用系统 Python: $PYTHON_BIN"
else
    echo "  ⚠️  未找到 python3！github-mcp 将无法运行。"
    PYTHON_BIN="__PYTHON_BIN__"
fi

# ---- 2. 检测二进制目录 ----
echo "[2/5] 检测二进制目录..."

BIN_DIR=""
# 优先使用 ~/.local/bin（pipx/uv tool 默认安装位置）
if [ -d "$HOME/.local/bin" ]; then
    BIN_DIR="$HOME/.local/bin"
elif [ -d "$HOME/.cargo/bin" ]; then
    BIN_DIR="$HOME/.cargo/bin"
else
    BIN_DIR="$HOME/.local/bin"
    mkdir -p "$BIN_DIR"
    echo "  创建 $BIN_DIR"
fi
echo "  二进制目录: $BIN_DIR"

# ---- 3. 复制脚本和文档 ----
echo "[3/6] 复制 MCP 脚本和文档..."

mkdir -p "$MCP_DIR"
cp "$SCRIPT_DIR/scripts/github_reader_mcp.py" "$MCP_DIR/"
cp "$SCRIPT_DIR/scripts/zotero_launcher.py" "$MCP_DIR/"
cp "$SCRIPT_DIR/docs/"*.md "$MCP_DIR/" 2>/dev/null || true
echo "  已复制到 $MCP_DIR"

# ---- 3.5. 安装 zotero-mcp-server（到 managed Python venv） ----
echo "[3.5/6] 安装 zotero-mcp-server..."
if [ "$PYTHON_BIN" != "__PYTHON_BIN__" ]; then
    VENV_DIR="$(dirname "$(dirname "$PYTHON_BIN")")/envs/default"
    if [ ! -f "$VENV_DIR/bin/zotero-mcp" ]; then
        "$PYTHON_BIN" -m venv "$VENV_DIR" 2>/dev/null || true
        "$VENV_DIR/bin/pip" install zotero-mcp-server >/dev/null 2>&1 && \
            echo "  zotero-mcp-server 安装完成" || \
            echo "  ⚠️  zotero-mcp-server 安装失败，请手动安装"
    else
        echo "  zotero-mcp-server 已安装，跳过"
    fi
else
    echo "  ⚠️  未检测到 Python，跳过 zotero 安装"
fi

# ---- 3.6. macOS 代码签名修复 ----
echo "[3.6/6] macOS 代码签名检测..."
if [[ "$(uname)" == "Darwin" ]]; then
    if ! "$PYTHON_BIN" -c "import pydantic_core" 2>/dev/null; then
        echo "  检测到签名冲突，自动修复..."
        codesign --force --deep --sign - "$PYTHON_BIN" 2>/dev/null && \
            echo "  ✓ managed Python 已 ad-hoc 重签" || \
            echo "  ⚠️  自动重签失败（可能需要手动执行）"
    else
        echo "  签名正常，无需修复"
    fi
else
    echo "  非 macOS，跳过"
fi

# ---- 4. 处理 Stata 工作目录 ----
STATA_CWD=""
# 解析 --stata-cwd 参数
for arg in "$@"; do
    if [[ "$arg" == --stata-cwd=* ]]; then
        STATA_CWD="${arg#*=}"
    fi
done

if [ -z "$STATA_CWD" ]; then
    # 未指定则保留占位符，不强制填写（stata-mcp 非必需）
    STATA_CWD="__STATA_CWD__"
    echo "  Stata 工作目录未指定，保留占位符（如需使用 stata-mcp 请手动编辑 mcp.json）"
else
    echo "  Stata 工作目录: $STATA_CWD"
fi

# ---- 5. 保留已有 Token（同步模式安全） ----
GITHUB_TOKEN_VALUE="__GITHUB_TOKEN__"
if [ -f "$MCP_JSON" ]; then
    # 从已有 mcp.json 提取 GITHUB_TOKEN，下次运行不会丢失
    EXISTING_TOKEN=$(python3 -c "
import json, sys
try:
    with open('$MCP_JSON') as f:
        d = json.load(f)
    t = d.get('mcpServers',{}).get('github-mcp',{}).get('env',{}).get('GITHUB_TOKEN','')
    if t and t != '__GITHUB_TOKEN__':
        print(t)
except: pass
" 2>/dev/null)
    if [ -n "$EXISTING_TOKEN" ]; then
        GITHUB_TOKEN_VALUE="$EXISTING_TOKEN"
        echo "  检测到已有 GITHUB_TOKEN，自动保留"
    fi
fi

# ---- 6. 生成 mcp.json ----
echo "[6/6] 生成 mcp.json..."

sed -e "s|__PYTHON_BIN__|$PYTHON_BIN|g" \
    -e "s|__BIN_DIR__|$BIN_DIR|g" \
    -e "s|__MCP_DIR__|$MCP_DIR|g" \
    -e "s|__STATA_CWD__|$STATA_CWD|g" \
    -e "s|__GITHUB_TOKEN__|$GITHUB_TOKEN_VALUE|g" \
    "$SCRIPT_DIR/mcp.template.json" > "$MCP_JSON"

echo "  已生成: $MCP_JSON"

echo ""
echo "=========================================="
echo " 部署完成！还需要手动完成以下步骤："
echo "=========================================="

# 检查是否需要填入 GITHUB_TOKEN
if grep -q "__GITHUB_TOKEN__" "$MCP_JSON"; then
    echo ""
    echo "  ⚠️  请手动填入 GITHUB_TOKEN:"
    echo "     编辑 $MCP_JSON"
    echo "     将 __GITHUB_TOKEN__ 替换为你的 GitHub Personal Access Token"
    echo "     （Token 权限只需 repo → Contents: Read-only）"
fi

echo ""
echo "  📋 检查清单:"
echo "     [✓] zotero-mcp-server — 已自动安装到 managed Python venv"
echo "     [✓] macOS 代码签名 — 已自动检测并修复（如需）"
echo "     [ ] uvx:  uv 工具（如未安装：brew install uv 或 pip install uv）"
echo "     [ ] stata-mcp: uvx 会自动拉取"
echo "     [ ] Zotero 客户端运行中，且开启了本地 API（端口 23119）"
echo ""
echo "  🔧 激活 MCP:"
echo "     打开 WorkBuddy → 连接器管理 → 找到 zotero/github-mcp/stata-mcp → 点击「信任」"
echo ""