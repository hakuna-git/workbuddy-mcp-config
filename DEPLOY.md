# WorkBuddy 新机器 MCP 部署指令

> 把下面的提示词复制给新机器上的 WorkBuddy，它会自动完成部署。
>
> **第一步：** [Fork 本仓库](https://github.com/hakuna-git/workbuddy-mcp-config/fork)，然后把提示词中的 `你的用户名/workbuddy-mcp-config` 换成你的 fork 地址。

## 前置准备

部署前需先创建 GitHub Personal Access Token（[Settings → Tokens](https://github.com/settings/tokens)），勾选 **`repo`** scope（读写仓库必需）。

## 提示词（复制这段发给 WorkBuddy）

```
请帮我部署 MCP 配置：

1. 克隆仓库（请替换为你的 fork 地址）:
   git clone https://github.com/你的用户名/workbuddy-mcp-config.git /tmp/workbuddy-mcp-config

2. 运行部署脚本（将 /path/to/your/project 换成你的实际项目目录）:
   cd /tmp/workbuddy-mcp-config && bash setup.sh --stata-cwd=/path/to/your/project

3. 完成后告诉我:
   - 生成的文件路径
   - 哪些占位符已自动填充
   - 哪些步骤需要我手动完成（如填入 GITHUB_TOKEN、安装依赖、信任 MCP）

4. 然后引导我逐项完成手动步骤（填入 GITHUB_TOKEN、安装依赖、信任 MCP）。
   Token 填入后 github-mcp 即获得写权限，后续直接用 MCP 推送。
```

## WorkBuddy 会做什么

| 步骤 | 自动化程度 | 说明 |
|------|-----------|------|
| 克隆仓库 | 🤖 自动 | 从 GitHub 拉取模板 |
| 检测 Python | 🤖 自动 | 优先 WorkBuddy 托管版，回退系统版 |
| 检测二进制目录 | 🤖 自动 | `~/.local/bin` 或自建 |
| 复制脚本和文档 | 🤖 自动 | 到 `~/.workbuddy/mcp/` |
| 保留已有 Token | 🔒 自动 | 重复运行不会丢失 GITHUB_TOKEN |
| 生成 mcp.json | 🤖 自动 | 占位符替换为本地路径，新增 MCP 自动合并 |
| 填入 GITHUB_TOKEN | ✋ 手动 | 首次部署需手动填写（后续同步自动保留） |
| 安装依赖 | 🤖+✋ | WorkBuddy 可执行 brew/pip 安装 |
| 信任 MCP | ✋ 手动 | 需在 WorkBuddy 连接器管理页面点击 |

## 部署后验证

部署完成后，让 WorkBuddy 测试 MCP 连接:

```
请测试 MCP 连接是否正常。先检查 ~/.workbuddy/mcp.json 文件内容，
确认 GITHUB_TOKEN 已填入，然后告诉我哪些 MCP 还需要手动信任。
```

## 同步新配置

仓库有更新（新增 MCP、升级脚本等）时，重新运行 setup.sh 即可同步。
脚本会**自动保留已有的 GITHUB_TOKEN**，不会丢失：

```
我的 workbuddy-mcp-config 仓库有更新，请帮我同步：
1. 克隆最新版本到 /tmp
   git clone https://github.com/你的用户名/workbuddy-mcp-config.git /tmp/workbuddy-mcp-config-sync
2. 运行部署脚本同步
   cd /tmp/workbuddy-mcp-config-sync && bash setup.sh --stata-cwd=/path/to/your/project
3. 告诉我新增了哪些内容，以及是否需要重新信任 MCP
```

## 推送修改

github-mcp v2.0 已包含写操作，直接通过 MCP 推送，无需 git push：

```
请帮我把 workbuddy-mcp-config 仓库的这些修改推送到 GitHub:
- README.md: 更新 xxx
仓库: 你的用户名/workbuddy-mcp-config
```