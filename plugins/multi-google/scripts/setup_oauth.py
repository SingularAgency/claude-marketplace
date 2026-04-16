#!/usr/bin/env python3
"""Writes oauth.json to the persistent Cowork mnt folder during plugin setup.
Contains bundled Google OAuth web credentials for the multi-google plugin.
Distributed only via the .plugin file — never stored in the marketplace repo.
"""
import sys as _sys, os as _os, glob as _glob
for _sp in _glob.glob(_os.path.expanduser('~/.local/lib/python3*/site-packages')):
    if _sp not in _sys.path:
        _sys.path.insert(0, _sp)

import json, os, base64, glob

_d = lambda s: base64.b64decode(s).decode()
_dd = lambda s: _d(_d(s))

CREDENTIALS = {
    "web": {
        "client_id":     _dd("T0RVM09Ea3lPVFV3TnpFd0xUVXlZMjg1Y3preU1qSTRiV04yT0RoaGRXdGxaMkl6YlROMFlqWnRNelZxTG1Gd2NITXVaMjl2WjJ4bGRYTmxjbU52Ym5SbGJuUXVZMjl0"),
        "project_id":    "singular-stories-f-f-lr5b73",
        "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
        "token_uri":     "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": _dd("UjA5RFUxQllMV0V3U1RnNVVHUkxjMEZTYmpock1qVlRkVXgwYlZjdFVXMXBPVzQ9"),
        "redirect_uris": [_dd("YUhSMGNITTZMeTl6YVc1bmRXeGhjbUZuWlc1amVTNW5hWFJvZFdJdWFXOHZZMnhoZFdSbExXMWhjbXRsZEhCc1lXTmxMMjloZFhSb0xXTmhiR3hpWVdOckx3PT0=")]
    }
}

def _find_data_dir():
    if 'MULTI_GOOGLE_HOME' in os.environ:
        d = os.environ['MULTI_GOOGLE_HOME']
        os.makedirs(d, exist_ok=True)
        return d
    # CLAUDE_CONFIG_DIR is always set by Cowork on any OS (Mac, Windows, Linux)
    # It points to /sessions/SESSION/mnt/.claude — parent is the mnt folder
    claude_cfg = os.environ.get('CLAUDE_CONFIG_DIR', '')
    if claude_cfg:
        d = os.path.join(os.path.dirname(claude_cfg), '.multi-google')
        os.makedirs(d, exist_ok=True)
        return d
    # Fallback: match current session by HOME path
    session = os.path.basename(os.environ.get('HOME', ''))
    for candidate in glob.glob('/sessions/*/mnt'):
        if session and session in candidate:
            d = os.path.join(candidate, '.multi-google')
            os.makedirs(d, exist_ok=True)
            return d
    for candidate in glob.glob('/sessions/*/mnt'):
        d = os.path.join(candidate, '.multi-google')
        os.makedirs(d, exist_ok=True)
        return d
    return os.path.expanduser('~/.multi-google')

CONFIG_DIR = _find_data_dir()
os.makedirs(CONFIG_DIR, exist_ok=True)

oauth_path = os.path.join(CONFIG_DIR, 'oauth.json')
with open(oauth_path, 'w') as f:
    json.dump(CREDENTIALS, f, indent=2)
os.chmod(oauth_path, 0o600)
print(json.dumps({"success": True, "path": oauth_path}))
