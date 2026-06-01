#!/usr/bin/env python3
"""Minimal GitHub MCP reader - pure stdlib, zero dependencies.

Reads files, searches repos, lists commits via GitHub API.
Uses GITHUB_TOKEN env var for authentication.
"""

import json
import os
import sys
import urllib.request
import urllib.error


GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
BASE_URL = "https://api.github.com"


def gh_api(path, method="GET", data=None):
    """Call GitHub API."""
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "workbuddy-github-reader")
    if data:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode()), resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return {"error": str(e), "body": body, "status": e.code}, e.code


def send_response(request_id, result):
    """Send JSON-RPC response."""
    rpc = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result,
    }
    sys.stdout.write(json.dumps(rpc) + "\n")
    sys.stdout.flush()


def send_error(request_id, code, message):
    """Send JSON-RPC error."""
    rpc = {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }
    sys.stdout.write(json.dumps(rpc) + "\n")
    sys.stdout.flush()


def handle_get_file_contents(params):
    """Get file contents from repo."""
    owner = params.get("owner", "")
    repo = params.get("repo", "")
    path = params.get("path", "")
    branch = params.get("branch")

    api_path = f"/repos/{owner}/{repo}/contents/{path}"
    if branch:
        api_path += f"?ref={branch}"

    data, status = gh_api(api_path)
    if status != 200:
        return {"error": data.get("message", str(data)), "status": status}

    # Handle directory listing
    if isinstance(data, list):
        files = []
        for item in data:
            files.append({
                "name": item.get("name"),
                "type": item.get("type"),
                "size": item.get("size"),
                "path": item.get("path"),
            })
        return {"type": "directory", "files": files}

    # Handle single file
    content = data.get("content", "")
    encoding = data.get("encoding", "")
    if encoding == "base64" and content:
        import base64
        try:
            decoded = base64.b64decode(content).decode("utf-8")
        except UnicodeDecodeError:
            decoded = f"[Binary file, {data.get('size', 0)} bytes]"
        return {
            "type": "file",
            "name": data.get("name"),
            "path": data.get("path"),
            "size": data.get("size"),
            "content": decoded,
        }
    return {"type": "file", "name": data.get("name"), "content": content}


def handle_search_repositories(params):
    """Search repos."""
    query = params.get("query", "")
    page = params.get("page", 1)
    per_page = params.get("per_page", 30)

    api_path = f"/search/repositories?q={urllib.parse.quote(query)}&page={page}&per_page={per_page}"
    data, status = gh_api(api_path)
    if status != 200:
        return {"error": data.get("message", str(data))}

    items = []
    for item in data.get("items", []):
        items.append({
            "name": item.get("name"),
            "full_name": item.get("full_name"),
            "description": item.get("description"),
            "url": item.get("html_url"),
            "stars": item.get("stargazers_count"),
            "language": item.get("language"),
            "private": item.get("private"),
            "owner": item.get("owner", {}).get("login"),
        })
    return {"total": data.get("total_count", 0), "items": items}


def handle_list_commits(params):
    """List commits."""
    owner = params.get("owner", "")
    repo = params.get("repo", "")
    sha = params.get("sha", "")
    page = params.get("page", 1)
    per_page = params.get("per_page", 30)

    api_path = f"/repos/{owner}/{repo}/commits"
    params_list = []
    if sha:
        params_list.append(f"sha={sha}")
    params_list.append(f"page={page}")
    params_list.append(f"per_page={per_page}")
    if params_list:
        api_path += "?" + "&".join(params_list)

    data, status = gh_api(api_path)
    if status != 200:
        return {"error": data.get("message", str(data))}

    commits = []
    for c in data:
        commits.append({
            "sha": c.get("sha", "")[:8],
            "message": c.get("commit", {}).get("message", "").split("\n")[0],
            "author": c.get("commit", {}).get("author", {}).get("name"),
            "date": c.get("commit", {}).get("author", {}).get("date"),
        })
    return {"commits": commits}


def handle_list_branches(params):
    """List branches."""
    owner = params.get("owner", "")
    repo = params.get("repo", "")

    api_path = f"/repos/{owner}/{repo}/branches"
    data, status = gh_api(api_path)
    if status != 200:
        return {"error": data.get("message", str(data))}

    branches = []
    for b in data:
        branches.append({
            "name": b.get("name"),
            "sha": b.get("commit", {}).get("sha", "")[:8],
        })
    return {"branches": branches}


# Tool handlers
TOOLS = {
    "get_file_contents": {
        "handler": handle_get_file_contents,
        "schema": {
            "type": "object",
            "required": ["owner", "repo", "path"],
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "path": {"type": "string"},
                "branch": {"type": "string"},
            },
        },
    },
    "search_repositories": {
        "handler": handle_search_repositories,
        "schema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string"},
                "page": {"type": "integer", "default": 1},
                "per_page": {"type": "integer", "default": 30},
            },
        },
    },
    "list_commits": {
        "handler": handle_list_commits,
        "schema": {
            "type": "object",
            "required": ["owner", "repo"],
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "sha": {"type": "string"},
                "page": {"type": "integer", "default": 1},
                "per_page": {"type": "integer", "default": 30},
            },
        },
    },
    "list_branches": {
        "handler": handle_list_branches,
        "schema": {
            "type": "object",
            "required": ["owner", "repo"],
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
            },
        },
    },
}


def handle_initialize(request_id, params):
    """Handle initialize request."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {},
        },
        "serverInfo": {
            "name": "github-reader-mcp",
            "version": "1.0.0",
        },
    }


def handle_tools_list(request_id, params):
    """List available tools."""
    tools = []
    for name, info in TOOLS.items():
        tools.append({
            "name": name,
            "description": info.get("description", f"GitHub {name}"),
            "inputSchema": info["schema"],
        })
    return {"tools": tools}


def handle_tools_call(request_id, params):
    """Call a tool."""
    tool_name = params.get("name", "")
    tool_args = params.get("arguments", {})

    if tool_name not in TOOLS:
        send_error(request_id, -32601, f"Tool not found: {tool_name}")
        return

    try:
        result = TOOLS[tool_name]["handler"](tool_args)
        return {
            "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}],
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {e}"}],
            "isError": True,
        }


def main():
    """Main MCP stdio loop."""
    for line in sys.stdin:
        try:
            rpc = json.loads(line.strip())
        except json.JSONDecodeError:
            continue

        request_id = rpc.get("id")
        method = rpc.get("method", "")
        params = rpc.get("params", {})

        if method == "initialize":
            result = handle_initialize(request_id, params)
            send_response(request_id, result)
        elif method == "notifications/initialized":
            pass  # No response needed
        elif method == "tools/list":
            result = handle_tools_list(request_id, params)
            send_response(request_id, result)
        elif method == "tools/call":
            result = handle_tools_call(request_id, params)
            send_response(request_id, result)
        else:
            send_error(request_id, -32601, f"Method not found: {method}")


if __name__ == "__main__":
    main()
