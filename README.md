# WorkBuddy MCP 配置仓库

跨机器共享的 MCP 配置模板，一键部署到新机器。

## 目录结构

```
mcp-config/
├── mcp.template.json          # MCP 配置模板（用占位符替代路径/Token）
├── setup.sh                   # 一键部署脚本
├── scripts/                   # 自建 MCP 脚本
│   └── github_reader_mcp.py   # GitHub 文件读取/搜索 MCP（纯标准库，零依赖）
├── docs/                      # 各 MCP 配置文档
│   ├── stata_config.md
│   └── zotero_config.md
├── .gitignore
└── README.md
```

## 快速开始（新机器）

### 方式一：让 WorkBuddy 帮你部署（推荐）

在新机器上打开 WorkBuddy，复制 [DEPLOY.md](./DEPLOY.md) 中的提示词发给它，WorkBuddy 会自动克隆仓库、运行脚本、引导你完成手动步骤。

### 方式二：手动部署

```bash
# 1. 克隆仓库
git clone https://github.com/hakuna-git/workbuddy-mcp-config.git && cd workbuddy-mcp-config

# 2. 运行部署脚本
bash setup.sh

# 3. 手动填入 GITHUB_TOKEN
vim ~/.workbuddy/mcp.json

# 4. 安装依赖
brew install uv          # stata-mcp 需要 uvx
pip install zotero-mcp-server
```

## 当前包含的 MCP

| MCP | 类型 | 说明 |
|-----|------|------|
| zotero | 本地 | Zotero 文献管理，需 Zotero 客户端运行 |
| stata-mcp | uvx | Stata 统计分析，通过 uvx 自动拉取 |
| github-mcp | 自建 | GitHub 读写（9 tools: 读文件/搜仓库/列提交&分支/创建&修改仓库/增删文件/批量提交） |
| connector-proxy | HTTP | 聚合代理（默认禁用） |

## 占位符说明

| 占位符 | 含义 | setup.sh 如何填充 |
|--------|------|-------------------|
| `__PYTHON_BIN__` | Python 3 路径 | 优先 WorkBuddy 托管版，回退系统版 |
| `__BIN_DIR__` | 二进制目录 | 检测 `~/.local/bin` → `~/.cargo/bin` |
| `__MCP_DIR__` | MCP 脚本目录 | 固定为 `~/.workbuddy/mcp/` |
| `__STATA_CWD__` | Stata 工作目录 | `--stata-cwd` 参数或当前 pwd |
| `__GITHUB_TOKEN__` | GitHub Token | **手动填入**（不入库） |

## 工作流

```mermaid
graph LR
    A[clone 仓库] --> B[setup.sh]
    B --> C[自动检测路径]
    C --> D[替换占位符]
    D --> E[生成 mcp.json]
    E --> F[手动填 Token]
    F --> G[WorkBuddy 信任 MCP]
```

## 注意事项

- **mcp.template.json 不可直接使用** — 必须通过 setup.sh 生成
- **GITHUB_TOKEN 永不入库** — 已在 .gitignore 中排除含 Token 的文件
- 克隆无需认证（公开仓库），但 **push 需要 Token** — WorkBuddy 会读取 `~/.workbuddy/mcp.json` 中的 Token 来认证，见 [DEPLOY.md](./DEPLOY.md)
- 自建 MCP 脚本（`scripts/`）直接复制到 `~/.workbuddy/mcp/`
- 每次修改 MCP 配置后提交此仓库，新机器 pull 即可同步
