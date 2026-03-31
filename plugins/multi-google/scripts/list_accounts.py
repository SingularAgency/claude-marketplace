#!/usr/bin/env python3
"""List all configured Google accounts with enabled services."""
import json, os

CONFIG_DIR = os.path.expanduser('~/.multi-google')
try:
    with open(os.path.join(CONFIG_DIR, 'accounts.json')) as f:
        print(json.dumps(json.load(f), indent=2, ensure_ascii=False))
except (FileNotFoundError, json.JSONDecodeError):
    print('{}')
