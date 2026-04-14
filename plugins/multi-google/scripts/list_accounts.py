#!/usr/bin/env python3
"""List all configured Google accounts with enabled services."""
import json, os

import glob as _g2

def _find_data_dir():
    if "MULTI_GOOGLE_HOME" in os.environ:
        d = os.environ["MULTI_GOOGLE_HOME"]; os.makedirs(d, exist_ok=True); return d
    ex = _g2.glob("/sessions/*/mnt/.multi-google")
    if ex: return ex[0]
    mnts = _g2.glob("/sessions/*/mnt")
    if mnts:
        d = os.path.join(mnts[0], ".multi-google"); os.makedirs(d, exist_ok=True); return d
    return os.path.expanduser("~/.multi-google")

CONFIG_DIR = _find_data_dir()
try:
    with open(os.path.join(CONFIG_DIR, 'accounts.json')) as f:
        print(json.dumps(json.load(f), indent=2, ensure_ascii=False))
except (FileNotFoundError, json.JSONDecodeError):
    print('{}')
