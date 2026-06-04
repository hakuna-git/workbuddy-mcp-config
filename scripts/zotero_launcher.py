#!/usr/bin/env python3
"""zotero-mcp launcher — sets env vars, auto-heals macOS code signing, launches.

Design: WorkBuddy spawns managed Python → runs this launcher → exec into zotero-mcp.
Same pattern as github_reader_mcp.py — no bash wrappers, no symlinks.
"""

import os
import sys
import subprocess

# 0. macOS code signing self-heal
#    WorkBuddy re-downloads managed Python on updates, overwriting the ad-hoc signature
#    needed for pip-installed native extensions (pydantic_core etc).
#    This check auto-detects and re-signs if necessary.
PYTHON_BIN = "/Users/qiuyangqian/.workbuddy/binaries/python/versions/3.13.12/bin/python3"
try:
    subprocess.run(
        [PYTHON_BIN, "-c", "import pydantic_core"],
        capture_output=True, timeout=5, check=True,
    )
except Exception:
    subprocess.run(
        ["codesign", "--force", "--deep", "--sign", "-", PYTHON_BIN],
        capture_output=True, timeout=10,
    )

# 1. Environment variables for Zotero local API mode
os.environ.setdefault("ZOTERO_LOCAL", "true")       # Use Zotero desktop client
os.environ.setdefault("ZOTERO_LOCAL_PORT", "23119")  # Default local API port
os.environ.setdefault("ZOTERO_READ_ONLY", "true")    # Read-only mode (safer)

# 2. Launch zotero-mcp with stdio transport
ZOTERO_BIN = "/Users/qiuyangqian/.workbuddy/binaries/python/envs/default/bin/zotero-mcp"
os.execv(ZOTERO_BIN, [ZOTERO_BIN, "serve", "--transport", "stdio"])
