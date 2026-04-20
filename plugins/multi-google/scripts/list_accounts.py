#!/usr/bin/env python3
"""List all configured Google accounts with enabled services."""
import json, os, glob as _g

def _find_data_dir():
    if "MULTI_GOOGLE_HOME" in os.environ:
        d = os.environ["MULTI_GOOGLE_HOME"]; os.makedirs(d, exist_ok=True); return d
    claude_cfg = os.environ.get("CLAUDE_CONFIG_DIR", "")
    if claude_cfg:
        d = os.path.join(os.path.dirname(claude_cfg), ".multi-google")
        os.makedirs(d, exist_ok=True); return d
    session = os.path.basename(os.environ.get("HOME", ""))
    for candidate in _g.glob("/sessions/*/mnt"):
        if session and session in candidate:
            d = os.path.join(candidate, ".multi-google"); os.makedirs(d, exist_ok=True); return d
    for candidate in _g.glob("/sessions/*/mnt"):
        d = os.path.join(candidate, ".multi-google"); os.makedirs(d, exist_ok=True); return d
    return os.path.expanduser("~/.multi-google")

CONFIG_DIR = _find_data_dir()
accounts_dir = os.path.join(CONFIG_DIR, 'accounts')

accounts = {}
if os.path.isdir(accounts_dir):
    for path in sorted(_g.glob(os.path.join(accounts_dir, '*.json'))):
        try:
            with open(path) as f:
                d = json.load(f)
            alias = d.get('alias', os.path.basename(path).replace('.json',''))
            accounts[alias] = {
                'email':    d.get('email', alias),
                'services': d.get('services', []),
            }
        except Exception:
            pass

print(json.dumps(accounts, indent=2, ensure_ascii=False))
