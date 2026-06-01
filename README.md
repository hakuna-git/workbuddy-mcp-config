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
| `__STATA_CWD__` | Stata 工作目录 | `--stata-cwd` 参数，未指定则保留占位符 |
| `__GITHUB_TOKEN__` | GitHub Token | **手动填入**（不入库） |

### Token 权限要求

github-mcp v2.0 包含读写操作，Token 需在 [GitHub Settings → Personal Access Tokens](https://github.com/settings/tokens) 创建时勾选：

| Scope | 用途 | 必需 |
|-------|------|------|
| `repo` | 读写仓库内容、创建仓库 | ✅ 必需 |

> `public_repo` 仅能操作公开仓库，推荐直接开 `repo` 全量。

## 第三方使用

如果你的团队/同行也想用这套配置：

**直接克隆即用：**
```bash
git clone https://github.com/hakuna-git/workbuddy-mcp-config.git
bash setup.sh --stata-cwd=/your/project
# 填入自己的 GITHUB_TOKEN，信任 MCP 即可
```
脚本自动检测 Python / 二进制目录，兼容任意 macOS。

**如需自定义并自行维护：**
1. Fork 本仓库到自己的账号
2. 将 `DEPLOY.md` 和 `README.md` 中的仓库地址替换为你的 fork 地址
3. 按需修改 `mcp.template.json`（增减 MCP、调整配置）
4. 通过 MCP 推送你的修改

**跨平台：** 脚本依赖 `brew` 安装依赖，非 macOS 用户手动安装 `uv` 和 `zotero-mcp-server` 即可。

## 工作流

```mermaid
graph LR
    A[clone 仓库] --> B[setup.sh]
    B --> C[自动检测路径]
    C --> D[替换占位符]
    D --> E[生成 mcp.json]
    E --> F[手动填 Token]
    F --> G[WorkBuddy 信任 MCP]
    G --> H[MCP 推送修改]
```

## 注意事项

- **mcp.template.json 不可直接使用** — 必须通过 setup.sh 生成
- **GITHUB_TOKEN 永不入库** — 已在 .gitignore 中排除含 Token 的文件
- 部署后 github-mcp 即拥有读写权限，直接通过 MCP 推送，无需手动 git push
- 自建 MCP 脚本（`scripts/`）直接复制到 `~/.workbuddy/mcp/`
- 每次修改 MCP 配置后提交此仓库，新机器 pull 即可同步