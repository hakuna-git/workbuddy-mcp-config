# WorkBuddy 新机器 MCP 部署指令

> 把下面的提示词复制给新机器上的 WorkBuddy，它会自动完成部署。

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

4. 然后引导我逐项完成手动步骤，包括：
   - 填入 GITHUB_TOKEN 后，配置 git remote 以支持后续 push:
     "读取 ~/.workbuddy/mcp.json 中的 GITHUB_TOKEN，然后用它配置 /tmp/workbuddy-mcp-config 的 git remote，让我以后能直接 git push"
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

部署完成后，git remote 是纯 HTTPS 不带凭据的，直接 push 会失败。
让 WorkBuddy 帮你推送，它会读取 mcp.json 里的 Token：

```
请帮我把 workbuddy-mcp-config 仓库的修改推送到 GitHub。
读取 ~/.workbuddy/mcp.json 中的 GITHUB_TOKEN，用它做 git push 认证。
仓库路径: /tmp/workbuddy-mcp-config
```
