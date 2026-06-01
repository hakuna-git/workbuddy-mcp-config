# WorkBuddy 新机器 MCP 部署指令

> 把下面的提示词复制给新机器上的 WorkBuddy，它会自动完成部署。
>
> **如果你 fork 了本仓库**，请把下面出现的 `hakuna-git` 替换为你的 GitHub 用户名。

## 前置准备

部署前需先创建 GitHub Personal Access Token（[Settings → Tokens](https://github.com/settings/tokens)），勾选 **`repo`** scope（读写仓库必需）。

## 提示词（复制这段发给 WorkBuddy）

```
请帮我部署 MCP 配置：

1. 克隆仓库:
   git clone https://github.com/hakuna-git/workbuddy-mcp-config.git /tmp/workbuddy-mcp-config

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
| 生成 mcp.json | 🤖 自动 | 占位符替换为本地路径 |
| 填入 GITHUB_TOKEN | ✋ 手动 | Token 不入库，需手动填写 |
| 安装依赖 | 🤖+✋ | WorkBuddy 可执行 brew/pip 安装 |
| 信任 MCP | ✋ 手动 | 需在 WorkBuddy 连接器管理页面点击 |

## 部署后验证

部署完成后，让 WorkBuddy 测试 MCP 连接:

```
请测试 MCP 连接是否正常。先检查 ~/.workbuddy/mcp.json 文件内容，
确认 GITHUB_TOKEN 已填入，然后告诉我哪些 MCP 还需要手动信任。
```

## 部署后维护（修改配置并推送）

github-mcp v2.0 已包含写操作，直接通过 MCP 推送，无需 git push：

```
请帮我把 workbuddy-mcp-config 仓库的这些修改推送到 GitHub:
- README.md: 更新 xxx
仓库: hakuna-git/workbuddy-mcp-config
```

> Fork 用户请将仓库地址替换为 `你的用户名/workbuddy-mcp-config`。