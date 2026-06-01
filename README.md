# WorkBuddy MCP 配置仓库

跨机器共享的 MCP 配置模板，一键部署到新机器。

## 目录结构

```
mcp-config/
├── mcp.template.json          # MCP 配置模板（用占位符替代路径/Token）
├── setup.sh                   # 一键部署脚本
├── scripts/                   # 自建 MCP 脚本
│   └── github_reader_mcp.py   # GitHub 读写 MCP v2.0（9 tools，纯标准库）
├── docs/                      # 各 MCP 配置文档
│   ├── stata_config.md
│   └── zotero_config.md
├── .gitignore
└── README.md
```

## 快速开始（新机器）

### 方式一：Fork 后部署（推荐）

1. Fork 本仓库到自己的 GitHub 账号
2. 在新机器上打开 WorkBuddy，将 [DEPLOY.md](./DEPLOY.md) 中的提示词复制给它
3. 把提示词里的仓库地址换为 `你的用户名/workbuddy-mcp-config`
4. WorkBuddy 会自动克隆、部署、引导你填入 Token 和信任 MCP

### 方式二：直接克隆（不自定义）

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
| `__STATA_CWD__` | Stata 工作目录 | `--stata-cwd` 参数，未指定则保留占位符 |
| `__GITHUB_TOKEN__` | GitHub Token | **手动填入**（不入库） |

### Token 权限要求

github-mcp v2.0 包含读写操作，Token 需在 [GitHub Settings → Personal Access Tokens](https://github.com/settings/tokens) 创建时勾选：

| Scope | 用途 | 必需 |
|-------|------|------|
| `repo` | 读写仓库内容、创建仓库 | ✅ 必需 |

> `public_repo` 仅能操作公开仓库，推荐直接开 `repo` 全量。

## 自定义维护

Fork 后如需调整配置：

1. 按需修改 `mcp.template.json`（增减 MCP、调整参数）
2. 通过 MCP 推送修改到你的 fork
3. 其他机器 `git pull` 即可同步

**跨平台：** 脚本通过 `brew` 安装依赖，非 macOS 用户手动 `pip install uv zotero-mcp-server` 即可。

## 工作流

```mermaid
graph LR
    A[Fork 仓库] --> B[clone]
    B --> C[setup.sh]
    C --> D[生成 mcp.json]
    D --> E[手动填 Token]
    E --> F[信任 MCP]
    F --> G[MCP 推送修改]
```

## 注意事项

- **mcp.template.json 不可直接使用** — 必须通过 setup.sh 生成
- **GITHUB_TOKEN 永不入库** — 已在 .gitignore 中排除含 Token 的文件
- 部署后 github-mcp 即拥有读写权限，直接通过 MCP 推送，无需手动 git push
- 自建 MCP 脚本（`scripts/`）直接复制到 `~/.workbuddy/mcp/`
- 每次修改 MCP 配置后提交此仓库，新机器 pull 即可同步