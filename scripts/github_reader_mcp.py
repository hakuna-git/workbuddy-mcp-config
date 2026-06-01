#!/usr/bin/env python3
"""GitHub MCP — read/write via GitHub API. Pure stdlib, zero dependencies.

Read tools: get_file_contents, search_repositories, list_commits, list_branches
Write tools: create_repository, update_repository, create_or_update_file,
              delete_file, batch_commit_files

Uses GITHUB_TOKEN env var for authentication.
"""

import base64
import json
import os
import sys
import urllib.parse
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
    req.add_header("User-Agent", "workbuddy-github-mcp")
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
    rpc = {"jsonrpc": "2.0", "id": request_id, "result": result}
    sys.stdout.write(json.dumps(rpc) + "\n")
    sys.stdout.flush()


def send_error(request_id, code, message):
    """Send JSON-RPC error."""
    rpc = {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}
    sys.stdout.write(json.dumps(rpc) + "\n")
    sys.stdout.flush()


# ====== READ TOOLS ======

def handle_get_file_contents(params):
    """Get file contents from repo (optionally return sha for write ops)."""
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

    if isinstance(data, list):
        files = [{"name": i.get("name"), "type": i.get("type"),
                  "size": i.get("size"), "path": i.get("path")} for i in data]
        return {"type": "directory", "files": files}

    content = data.get("content", "")
    encoding = data.get("encoding", "")
    result = {
        "type": "file",
        "name": data.get("name"),
        "path": data.get("path"),
        "size": data.get("size"),
        "sha": data.get("sha"),
    }
    if encoding == "base64" and content:
        try:
            result["content"] = base64.b64decode(content).decode("utf-8")
        except UnicodeDecodeError:
            result["content"] = f"[Binary file, {data.get('size', 0)} bytes]"
    else:
        result["content"] = content
    return result


def handle_search_repositories(params):
    """Search repos."""
    query = params.get("query", "")
    page = params.get("page", 1)
    per_page = params.get("per_page", 30)

    api_path = f"/search/repositories?q={urllib.parse.quote(query)}&page={page}&per_page={per_page}"
    data, status = gh_api(api_path)
    if status != 200:
        return {"error": data.get("message", str(data))}

    items = [{
        "name": i.get("name"), "full_name": i.get("full_name"),
        "description": i.get("description"), "url": i.get("html_url"),
        "stars": i.get("stargazers_count"), "language": i.get("language"),
        "private": i.get("private"), "owner": i.get("owner", {}).get("login"),
    } for i in data.get("items", [])]
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

    commits = [{
        "sha": c.get("sha", "")[:8],
        "full_sha": c.get("sha"),
        "message": c.get("commit", {}).get("message", "").split("\n")[0],
        "author": c.get("commit", {}).get("author", {}).get("name"),
        "date": c.get("commit", {}).get("author", {}).get("date"),
    } for c in data]
    return {"commits": commits}


def handle_list_branches(params):
    """List branches."""
    owner = params.get("owner", "")
    repo = params.get("repo", "")

    api_path = f"/repos/{owner}/{repo}/branches"
    data, status = gh_api(api_path)
    if status != 200:
        return {"error": data.get("message", str(data))}

    branches = [{
        "name": b.get("name"),
        "sha": b.get("commit", {}).get("sha", "")[:8],
    } for b in data]
    return {"branches": branches}


# ====== WRITE TOOLS ======

def handle_create_repository(params):
    """Create a new GitHub repository."""
    name = params.get("name", "")
    description = params.get("description", "")
    private = params.get("private", True)
    auto_init = params.get("auto_init", False)

    body = {"name": name, "private": private, "auto_init": auto_init}
    if description:
        body["description"] = description

    data, status = gh_api("/user/repos", "POST", body)
    if status not in (200, 201):
        return {"error": data.get("message", str(data)), "status": status}

    return {
        "name": data.get("name"),
        "full_name": data.get("full_name"),
        "url": data.get("html_url"),
        "clone_url": data.get("clone_url"),
        "private": data.get("private"),
        "description": data.get("description"),
    }


def handle_update_repository(params):
    """Update repository settings (visibility, description, etc.)."""
    owner = params.get("owner", "")
    repo = params.get("repo", "")
    body = {}
    for key in ("name", "description", "private", "default_branch"):
        if key in params:
            body[key] = params[key]

    if not body:
        return {"error": "No fields to update"}

    data, status = gh_api(f"/repos/{owner}/{repo}", "PATCH", body)
    if status != 200:
        return {"error": data.get("message", str(data)), "status": status}

    return {
        "name": data.get("name"),
        "full_name": data.get("full_name"),
        "private": data.get("private"),
        "description": data.get("description"),
    }


def handle_create_or_update_file(params):
    """Create or update a single file via Contents API.

    For UPDATES, you MUST provide `sha` (get it from get_file_contents first).
    For NEW files, omit `sha`.
    """
    owner = params.get("owner", "")
    repo = params.get("repo", "")
    path = params.get("path", "")
    content = params.get("content", "")
    message = params.get("message", f"Update {path}")
    branch = params.get("branch", "main")
    sha = params.get("sha")

    body = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "branch": branch,
    }
    if sha:
        body["sha"] = sha

    data, status = gh_api(f"/repos/{owner}/{repo}/contents/{path}", "PUT", body)
    if status not in (200, 201):
        return {"error": data.get("message", str(data)), "status": status}

    return {
        "path": data.get("content", {}).get("path", path),
        "url": data.get("content", {}).get("html_url"),
        "commit_sha": data.get("commit", {}).get("sha", "")[:8],
        "message": message,
    }


def handle_delete_file(params):
    """Delete a file via Contents API. Requires sha from get_file_contents."""
    owner = params.get("owner", "")
    repo = params.get("repo", "")
    path = params.get("path", "")
    message = params.get("message", f"Delete {path}")
    branch = params.get("branch", "main")
    sha = params.get("sha", "")

    if not sha:
        return {"error": "sha is required — call get_file_contents first"}

    body = {"message": message, "sha": sha, "branch": branch}
    data, status = gh_api(f"/repos/{owner}/{repo}/contents/{path}", "DELETE", body)
    if status != 200:
        return {"error": data.get("message", str(data)), "status": status}

    return {"path": path, "deleted": True, "commit_sha": data.get("commit", {}).get("sha", "")[:8]}


def handle_batch_commit_files(params):
    """Commit multiple files in a single commit via Git Data API.

    files: [{"path": "relative/path", "content": "file content"}, ...]
    message: commit message
    owner, repo, branch: standard
    """
    owner = params.get("owner", "")
    repo = params.get("repo", "")
    branch = params.get("branch", "main")
    message = params.get("message", "Batch commit")
    files = params.get("files", [])

    if not files:
        return {"error": "No files provided"}

    # Step 1: Get latest commit on branch
    ref_data, ref_status = gh_api(f"/repos/{owner}/{repo}/git/ref/heads/{branch}")
    if ref_status != 200:
        return {"error": f"Cannot get branch ref: {ref_data.get('message', ref_status)}"}
    base_commit_sha = ref_data["object"]["sha"]

    # Step 2: Get base tree
    commit_data, _ = gh_api(f"/repos/{owner}/{repo}/git/commits/{base_commit_sha}")
    base_tree_sha = commit_data["tree"]["sha"]

    # Step 3: Create blobs for each file
    tree_items = []
    for f in files:
        blob_data, blob_status = gh_api(
            f"/repos/{owner}/{repo}/git/blobs",
            "POST",
            {"content": f["content"], "encoding": "utf-8"},
        )
        if blob_status not in (200, 201):
            return {"error": f"Failed to create blob for {f['path']}: {blob_data.get('message')}"}
        tree_items.append({
            "path": f["path"],
            "mode": "100644",
            "type": "blob",
            "sha": blob_data["sha"],
        })

    # Step 4: Create new tree
    tree_data, tree_status = gh_api(
        f"/repos/{owner}/{repo}/git/trees",
        "POST",
        {"base_tree": base_tree_sha, "tree": tree_items},
    )
    if tree_status not in (200, 201):
        return {"error": f"Failed to create tree: {tree_data.get('message')}"}
    new_tree_sha = tree_data["sha"]

    # Step 5: Create commit
    commit_payload = {
        "message": message,
        "tree": new_tree_sha,
        "parents": [base_commit_sha],
    }
    new_commit, commit_status = gh_api(
        f"/repos/{owner}/{repo}/git/commits", "POST", commit_payload
    )
    if commit_status not in (200, 201):
        return {"error": f"Failed to create commit: {new_commit.get('message')}"}

    # Step 6: Update branch ref
    ref_patch, ref_patch_status = gh_api(
        f"/repos/{owner}/{repo}/git/refs/heads/{branch}",
        "PATCH",
        {"sha": new_commit["sha"], "force": False},
    )
    if ref_patch_status != 200:
        return {"error": f"Failed to update ref: {ref_patch.get('message')}"}

    return {
        "commit_sha": new_commit["sha"][:8],
        "full_sha": new_commit["sha"],
        "files_committed": len(files),
        "paths": [f["path"] for f in files],
        "message": message,
    }


# ====== TOOL REGISTRY ======

TOOLS = {
    "get_file_contents": {
        "handler": handle_get_file_contents,
        "description": "Get file/directory contents from a GitHub repository. "
                       "Returns file content, metadata, and sha (needed for write ops).",
        "schema": {
            "type": "object",
            "required": ["owner", "repo", "path"],
            "properties": {
                "owner": {"type": "string", "description": "Repo owner (user or org)"},
                "repo": {"type": "string", "description": "Repository name"},
                "path": {"type": "string", "description": "File path within the repo"},
                "branch": {"type": "string", "description": "Branch name (default: default branch)"},
            },
        },
    },
    "search_repositories": {
        "handler": handle_search_repositories,
        "description": "Search GitHub repositories by keyword.",
        "schema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "page": {"type": "integer", "default": 1},
                "per_page": {"type": "integer", "default": 30},
            },
        },
    },
    "list_commits": {
        "handler": handle_list_commits,
        "description": "List commits in a repository.",
        "schema": {
            "type": "object",
            "required": ["owner", "repo"],
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "sha": {"type": "string", "description": "Branch or commit SHA"},
                "page": {"type": "integer", "default": 1},
                "per_page": {"type": "integer", "default": 30},
            },
        },
    },
    "list_branches": {
        "handler": handle_list_branches,
        "description": "List branches in a repository.",
        "schema": {
            "type": "object",
            "required": ["owner", "repo"],
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
            },
        },
    },
    "create_repository": {
        "handler": handle_create_repository,
        "description": "Create a new GitHub repository.",
        "schema": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string", "description": "Repository name"},
                "description": {"type": "string", "description": "Repository description"},
                "private": {"type": "boolean", "default": True},
                "auto_init": {"type": "boolean", "default": False},
            },
        },
    },
    "update_repository": {
        "handler": handle_update_repository,
        "description": "Update repository settings (name, description, visibility).",
        "schema": {
            "type": "object",
            "required": ["owner", "repo"],
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "name": {"type": "string", "description": "New repo name"},
                "description": {"type": "string"},
                "private": {"type": "boolean", "description": "true=private, false=public"},
                "default_branch": {"type": "string"},
            },
        },
    },
    "create_or_update_file": {
        "handler": handle_create_or_update_file,
        "description": "Create or update a single file. For updates, provide sha "
                       "(get it from get_file_contents). For new files, omit sha.",
        "schema": {
            "type": "object",
            "required": ["owner", "repo", "path", "content", "message"],
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "path": {"type": "string", "description": "File path within the repo"},
                "content": {"type": "string", "description": "New file content"},
                "message": {"type": "string", "description": "Commit message"},
                "branch": {"type": "string", "default": "main"},
                "sha": {"type": "string", "description": "File blob SHA (required for updates)"},
            },
        },
    },
    "delete_file": {
        "handler": handle_delete_file,
        "description": "Delete a file. Requires sha from get_file_contents.",
        "schema": {
            "type": "object",
            "required": ["owner", "repo", "path", "sha", "message"],
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "path": {"type": "string"},
                "sha": {"type": "string", "description": "File blob SHA from get_file_contents"},
                "message": {"type": "string", "description": "Commit message"},
                "branch": {"type": "string", "default": "main"},
            },
        },
    },
    "batch_commit_files": {
        "handler": handle_batch_commit_files,
        "description": "Commit multiple files in a single commit. Best for pushing "
                       "several files at once. Files format: [{path, content}, ...]",
        "schema": {
            "type": "object",
            "required": ["owner", "repo", "files", "message"],
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "branch": {"type": "string", "default": "main"},
                "files": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"},
                        },
                        "required": ["path", "content"],
                    },
                    "description": "Array of {path, content} objects",
                },
                "message": {"type": "string", "description": "Commit message"},
            },
        },
    },
}


# ====== MCP HANDLERS ======

def handle_initialize(request_id, params):
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "github-mcp", "version": "2.0.0"},
    }


def handle_tools_list(request_id, params):
    tools = [{
        "name": name,
        "description": info["description"],
        "inputSchema": info["schema"],
    } for name, info in TOOLS.items()]
    return {"tools": tools}


def handle_tools_call(request_id, params):
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
            pass
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
