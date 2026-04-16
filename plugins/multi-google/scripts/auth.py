#!/usr/bin/env python3
"""
Google OAuth2 authentication for multi-google plugin.
Works without Desktop Commander — runs entirely from the Cowork VM.

Supports both "web" and "installed" OAuth client types.

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

import json, os, sys, tempfile, glob, urllib.parse, subprocess

def _ensure_google_packages():
    """Auto-install Google API packages if missing. Fails silently if pypi.org is blocked."""
    try:
        import google.auth, google_auth_oauthlib, googleapiclient
        return  # already installed
    except ImportError:
        pass

    # Attempt silent install — do NOT print, do NOT ask user, do NOT raise
    try:
        subprocess.call(
            [sys.executable, '-m', 'pip', 'install', '-q',
             'google-auth', 'google-auth-oauthlib', 'google-api-python-client',
             '--break-system-packages'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=60
        )
    except Exception:
        pass  # network blocked, timeout, etc. — will surface as ImportError below

    # Re-add site-packages so freshly installed packages are visible
    import glob as _g
    for sp in _g.glob(os.path.expanduser('~/.local/lib/python3*/site-packages')):
        if sp not in sys.path:
            sys.path.insert(0, sp)

_ensure_google_packages()

REDIRECT_URI = "https://singularagency.github.io/claude-marketplace/oauth-callback/"

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

def _make_flow(creds_data, scopes):
    """Create a Flow that works with both 'web' and 'installed' credential types."""
    try:
        from google_auth_oauthlib.flow import Flow, InstalledAppFlow
    except ImportError:
        print(json.dumps({"error": "Run: pip install google-auth google-auth-oauthlib google-api-python-client"}))
        sys.exit(1)

    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(creds_data, tmp); tmp.close()

    cred_type = list(creds_data.keys())[0]  # "web" or "installed"
    if cred_type == "web":
        flow = Flow.from_client_secrets_file(tmp.name, scopes=scopes)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(tmp.name, scopes=scopes)

    os.unlink(tmp.name)
    return flow

def phase1_start(alias, services):
    """Generate the OAuth URL and save pending state."""
    scopes = ["openid", "https://www.googleapis.com/auth/userinfo.email"]
    for svc in services:
        scopes.extend(SCOPES_MAP.get(svc, []))

    creds_data = _load_oauth()
    flow = _make_flow(creds_data, scopes)
    flow.redirect_uri = REDIRECT_URI
    auth_url, state = flow.authorization_url(prompt='consent', access_type='offline')

    # Save state so phase2 can complete the exchange
    pending = {
        "alias": alias,
        "services": services,
        "scopes": scopes,
        "redirect_uri": REDIRECT_URI,
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
        from googleapiclient.discovery import build
    except ImportError:
        print(json.dumps({"error": "Run: pip install google-auth google-auth-oauthlib google-api-python-client"}))
        sys.exit(1)

    creds_data = _load_oauth()
    flow = _make_flow(creds_data, scopes)
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
