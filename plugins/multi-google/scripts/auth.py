#!/usr/bin/env python3
"""
Google OAuth2 authentication for multi-google plugin.
Works without Desktop Commander — runs entirely from the Cowork VM.

Usage:
  Phase 1 — Start auth:
    python3 auth.py <alias> <service1> [service2...]
    → Prints AUTH_URL:<url> and saves pending state

  Phase 2 — Finish auth (after user pastes redirect URL):
    python3 auth.py <alias> --finish <code_or_redirect_url>
    → Exchanges code for token and saves credentials
"""
import sys as _sys, os as _os, glob as _glob

# Auto-add local site-packages (for DC/WSL2 environments)
for _sp in _glob.glob(_os.path.expanduser('~/.local/lib/python3*/site-packages')):
    if _sp not in _sys.path:
        _sys.path.insert(0, _sp)

import json, os, sys, tempfile, glob, urllib.parse

def _find_data_dir():
    """Find or create the persistent data directory.
    Checks Cowork mnt folder first (no DC needed), then WSL2 home fallback."""
    if 'MULTI_GOOGLE_HOME' in os.environ:
        d = os.environ['MULTI_GOOGLE_HOME']
        os.makedirs(d, exist_ok=True)
        return d
    # Cowork mnt folder — persists on user's machine across sessions
    existing = glob.glob('/sessions/*/mnt/.multi-google')
    if existing:
        return existing[0]
    mnts = glob.glob('/sessions/*/mnt')
    if mnts:
        d = os.path.join(mnts[0], '.multi-google')
        os.makedirs(d, exist_ok=True)
        return d
    # Fallback: WSL2/Desktop Commander home
    return os.path.expanduser('~/.multi-google')

CONFIG_DIR = _find_data_dir()

SCOPES_MAP = {
    "gmail":    ["https://www.googleapis.com/auth/gmail.modify",
                 "https://www.googleapis.com/auth/gmail.send"],
    "calendar": ["https://www.googleapis.com/auth/calendar"],
    "drive":    ["https://www.googleapis.com/auth/drive"],
}

def _load_oauth():
    path = os.path.join(CONFIG_DIR, 'oauth.json')
    if not os.path.exists(path):
        print(json.dumps({"error": f"OAuth credentials not found at {path}. Run setup first."}))
        sys.exit(1)
    with open(path) as f:
        return json.load(f)

def phase1_start(alias, services):
    """Generate the OAuth URL and save pending state."""
    scopes = ["openid", "https://www.googleapis.com/auth/userinfo.email"]
    for svc in services:
        scopes.extend(SCOPES_MAP.get(svc, []))

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print(json.dumps({"error": "Run: pip install google-auth google-auth-oauthlib google-api-python-client"}))
        sys.exit(1)

    creds_data = _load_oauth()
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(creds_data, tmp); tmp.close()

    flow = InstalledAppFlow.from_client_secrets_file(tmp.name, scopes=scopes)
    os.unlink(tmp.name)

    flow.redirect_uri = "http://localhost"
    auth_url, state = flow.authorization_url(prompt='consent', access_type='offline')

    # Save state so phase2 can complete the exchange
    pending = {
        "alias": alias,
        "services": services,
        "scopes": scopes,
        "redirect_uri": "http://localhost",
        "state": state,
        "code_verifier": getattr(flow, 'code_verifier', None)
    }
    pending_path = os.path.join(CONFIG_DIR, f'pending_auth_{alias}.json')
    with open(pending_path, 'w') as f:
        json.dump(pending, f)

    print(f"AUTH_URL:{auth_url}", flush=True)

def phase2_finish(alias, code_or_url):
    """Exchange the auth code for a token and save credentials."""
    # Support pasting the full redirect URL or just the code
    if code_or_url.startswith('http'):
        params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(code_or_url).query))
        code = params.get('code')
        if not code:
            print(json.dumps({"error": "No 'code' parameter found in the URL. Did you paste the full redirect URL?"}))
            sys.exit(1)
    else:
        code = code_or_url

    pending_path = os.path.join(CONFIG_DIR, f'pending_auth_{alias}.json')
    if not os.path.exists(pending_path):
        print(json.dumps({"error": f"No pending auth found for '{alias}'. Run auth.py {alias} <services> first."}))
        sys.exit(1)

    with open(pending_path) as f:
        pending = json.load(f)

    services = pending['services']
    scopes   = pending['scopes']

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        print(json.dumps({"error": "Run: pip install google-auth google-auth-oauthlib google-api-python-client"}))
        sys.exit(1)

    creds_data = _load_oauth()
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(creds_data, tmp); tmp.close()

    flow = InstalledAppFlow.from_client_secrets_file(tmp.name, scopes=scopes)
    os.unlink(tmp.name)

    flow.redirect_uri = pending['redirect_uri']
    if pending.get('code_verifier'):
        flow.code_verifier = pending['code_verifier']

    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    flow.fetch_token(code=code)
    creds = flow.credentials

    # Get email from Google
    try:
        svc = build('oauth2', 'v2', credentials=creds)
        email = svc.userinfo().get().execute().get('email', alias + '@unknown')
    except Exception:
        email = alias + '@unknown'

    # Save token
    accounts_dir = os.path.join(CONFIG_DIR, 'accounts')
    os.makedirs(accounts_dir, exist_ok=True)
    with open(os.path.join(accounts_dir, f'{alias}.json'), 'w') as f:
        f.write(creds.to_json())

    # Update accounts registry
    accounts_file = os.path.join(CONFIG_DIR, 'accounts.json')
    accounts = {}
    if os.path.exists(accounts_file):
        with open(accounts_file) as f:
            accounts = json.load(f)
    accounts[alias] = {'email': email, 'services': services}
    with open(accounts_file, 'w') as f:
        json.dump(accounts, f, indent=2)

    # Clean up pending state
    os.remove(pending_path)

    print(json.dumps({"success": True, "alias": alias, "email": email, "services": services}), flush=True)

# --- Main ---
if len(sys.argv) < 2:
    print(json.dumps({"error": "Usage: auth.py <alias> <service1> [service2...] OR auth.py <alias> --finish <code_or_url>"}))
    sys.exit(1)

alias = sys.argv[1]

if '--finish' in sys.argv:
    idx = sys.argv.index('--finish')
    if idx + 1 >= len(sys.argv):
        print(json.dumps({"error": "--finish requires a code or redirect URL"}))
        sys.exit(1)
    phase2_finish(alias, sys.argv[idx + 1])
else:
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: auth.py <alias> <service1> [service2...]"}))
        sys.exit(1)
    phase1_start(alias, sys.argv[2:])
