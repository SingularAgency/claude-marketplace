#!/usr/bin/env python3
"""
Writes oauth.json to the persistent Cowork mnt folder during plugin setup.

Contains only the OAuth client_id (public) and the exchange_url (Cloud Function proxy).
No client_secret is stored anywhere in the plugin — the secret lives server-side.
"""
import sys as _sys, os as _os, glob as _glob
for _sp in _glob.glob(_os.path.expanduser('~/.local/lib/python3*/site-packages')):
    if _sp not in _sys.path:
        _sys.path.insert(0, _sp)

import json, os, glob

# ── Public OAuth config (no secrets here) ─────────────────────────────────────
# client_id identifies the OAuth app — it appears in public URLs and is not sensitive.
# client_secret is handled entirely by the Cloud Function proxy.
CLIENT_ID    = "849295070710-5yco5cj94ky4228mcv88aukelgb3m35j.apps.googleusercontent.com"
EXCHANGE_URL = "REPLACE_WITH_YOUR_CLOUD_FUNCTION_URL"   # e.g. https://us-central1-PROJECT.cloudfunctions.net/google-oauth-exchange


def _find_data_dir():
    if 'MULTI_GOOGLE_HOME' in os.environ:
        d = os.environ['MULTI_GOOGLE_HOME']
        os.makedirs(d, exist_ok=True)
        return d
    # CLAUDE_CONFIG_DIR is always set by Cowork on any OS (Mac, Windows, Linux)
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
os.makedirs(os.path.join(CONFIG_DIR, 'accounts'), exist_ok=True)

oauth_path = os.path.join(CONFIG_DIR, 'oauth.json')
with open(oauth_path, 'w') as f:
    json.dump({
        "client_id":    CLIENT_ID,
        "exchange_url": EXCHANGE_URL,
    }, f, indent=2)
os.chmod(oauth_path, 0o600)
print(json.dumps({"success": True, "path": oauth_path}))
