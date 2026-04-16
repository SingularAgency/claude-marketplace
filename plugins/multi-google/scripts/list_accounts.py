#!/usr/bin/env python3
"""List all configured Google accounts with enabled services."""
import json, os

import glob as _g2

def _find_data_dir():
    if "MULTI_GOOGLE_HOME" in os.environ:
        d = os.environ["MULTI_GOOGLE_HOME"]; os.makedirs(d, exist_ok=True); return d
    # CLAUDE_CONFIG_DIR is always set by Cowork on any OS (Mac, Windows, Linux)
    # It points to /sessions/SESSION/mnt/.claude — parent is the mnt folder
    claude_cfg = os.environ.get("CLAUDE_CONFIG_DIR", "")
    if claude_cfg:
        d = os.path.join(os.path.dirname(claude_cfg), ".multi-google")
        os.makedirs(d, exist_ok=True); return d
    # Fallback: match current session by HOME path
    import glob as _gf
    session = os.path.basename(os.environ.get("HOME", ""))
    for candidate in _gf.glob("/sessions/*/mnt"):
        if session and session in candidate:
            d = os.path.join(candidate, ".multi-google"); os.makedirs(d, exist_ok=True); return d
    for candidate in _gf.glob("/sessions/*/mnt"):
        d = os.path.join(candidate, ".multi-google"); os.makedirs(d, exist_ok=True); return d
    return os.path.expanduser("~/.multi-google")

CONFIG_DIR = _find_data_dir()
try:
    with open(os.path.join(CONFIG_DIR, 'accounts.json')) as f:
        print(json.dumps(json.load(f), indent=2, ensure_ascii=False))
except (FileNotFoundError, json.JSONDecodeError):
    print('{}')
