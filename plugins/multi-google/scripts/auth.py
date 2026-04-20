#!/usr/bin/env python3
"""
Google OAuth2 authentication for multi-google plugin.
Uses PKCE + Cloud Function proxy — zero secrets bundled in the plugin.

Phase 1 — Start auth:
  python3 auth.py <alias> <service1> [service2...]
  → Prints AUTH_URL and saves pending state (code_verifier)

Phase 2 — Finish auth (after user pastes redirect URL):
  python3 auth.py <alias> --finish <code_or_redirect_url>
  → Calls Cloud Function proxy to exchange code, saves credentials
"""
import sys as _sys, os as _os, glob as _glob

# Auto-add local site-packages (for environments where packages are installed per-user)
for _sp in _glob.glob(_os.path.expanduser('~/.local/lib/python3*/site-packages')):
    if _sp not in _sys.path:
        _sys.path.insert(0, _sp)

import base64, datetime, glob, hashlib, json, os, secrets, subprocess, sys, urllib.parse, urllib.request


# ── Package bootstrap ──────────────────────────────────────────────────────────

def _ensure_google_packages():
    """Auto-install Google API packages if missing. Fails silently if pypi.org is blocked."""
    try:
        import google.auth, googleapiclient
        return
    except ImportError:
        pass
    try:
        subprocess.call(
            [sys.executable, '-m', 'pip', 'install', '-q',
             'google-auth', 'google-api-python-client',
             '--break-system-packages'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=60,
        )
    except Exception:
        pass
    for sp in glob.glob(os.path.expanduser('~/.local/lib/python3*/site-packages')):
        if sp not in sys.path:
            sys.path.insert(0, sp)

_ensure_google_packages()


# ── Constants ──────────────────────────────────────────────────────────────────

REDIRECT_URI = "https://singularagency.github.io/claude-marketplace/oauth-callback/"

SCOPES_MAP = {
    "gmail":    ["https://www.googleapis.com/auth/gmail.modify",
                 "https://www.googleapis.com/auth/gmail.send"],
    "calendar": ["https://www.googleapis.com/auth/calendar"],
    "drive":    ["https://www.googleapis.com/auth/drive"],
}


# ── Data directory ─────────────────────────────────────────────────────────────

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


# ── OAuth config ───────────────────────────────────────────────────────────────

def _load_oauth():
    path = os.path.join(CONFIG_DIR, 'oauth.json')
    if not os.path.exists(path):
        print(json.dumps({"error": f"OAuth config not found at {path}. Run setup first."}))
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


# ── PKCE ───────────────────────────────────────────────────────────────────────

def _generate_pkce():
    """Generate a PKCE code_verifier and S256 code_challenge."""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode()
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()
    return code_verifier, code_challenge


# ── Proxy calls ────────────────────────────────────────────────────────────────

def _proxy_post(exchange_url, payload):
    """POST JSON to the Cloud Function proxy, return parsed response."""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        exchange_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())
    except Exception as exc:
        return {"error": "proxy_unreachable", "error_description": str(exc)}


def _exchange_via_proxy(exchange_url, code, code_verifier):
    return _proxy_post(exchange_url, {
        "action": "exchange",
        "code": code,
        "code_verifier": code_verifier,
        "redirect_uri": REDIRECT_URI,
    })


def _refresh_via_proxy(exchange_url, refresh_token):
    return _proxy_post(exchange_url, {
        "action": "refresh",
        "refresh_token": refresh_token,
    })


# ── Credential management ──────────────────────────────────────────────────────

def _get_credentials(alias):
    """Load stored credentials, refreshing via proxy if the access token is expired."""
    creds_path = os.path.join(CONFIG_DIR, 'accounts', f'{alias}.json')
    if not os.path.exists(creds_path):
        print(json.dumps({"error": f"Account '{alias}' not found. Add it first."}))
        sys.exit(1)

    with open(creds_path) as f:
        data = json.load(f)

    oauth = _load_oauth()
    exchange_url = oauth.get('exchange_url')

    # Check expiry with a 5-minute safety buffer
    expiry_str = data.get('expiry')
    is_expired = True
    if expiry_str:
        try:
            expiry = datetime.datetime.fromisoformat(expiry_str)
            is_expired = datetime.datetime.utcnow() > (expiry - datetime.timedelta(minutes=5))
        except ValueError:
            pass

    if is_expired and data.get('refresh_token') and exchange_url:
        result = _refresh_via_proxy(exchange_url, data['refresh_token'])
        if 'access_token' in result:
            data['token'] = result['access_token']
            if 'refresh_token' in result:
                data['refresh_token'] = result['refresh_token']
            if 'expires_in' in result:
                new_expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=result['expires_in'])
                data['expiry'] = new_expiry.isoformat()
            with open(creds_path, 'w') as f:
                json.dump(data, f, indent=2)

    try:
        from google.oauth2.credentials import Credentials
    except ImportError:
        print(json.dumps({"error": "Run: pip install google-auth google-api-python-client"}))
        sys.exit(1)

    # Build Credentials with a far-future expiry so google-auth won't auto-refresh
    # (we handle refresh ourselves above via the proxy)
    creds = Credentials(
        token=data.get('token'),
        refresh_token=data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=oauth.get('client_id'),
        client_secret=None,   # no secret in the plugin
        scopes=data.get('scopes'),
    )
    # Mark token as fresh to suppress auto-refresh attempts
    creds.expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    return creds


# ── Service builders (imported by gmail.py / drive.py / gcalendar.py) ─────────

def _build_service(name, version, alias):
    creds = _get_credentials(alias)
    try:
        from googleapiclient.discovery import build
    except ImportError:
        print(json.dumps({"error": "Run: pip install google-api-python-client"}))
        sys.exit(1)
    return build(name, version, credentials=creds)

def get_gmail_service(alias):    return _build_service('gmail',    'v1', alias)
def get_calendar_service(alias): return _build_service('calendar', 'v3', alias)
def get_drive_service(alias):    return _build_service('drive',    'v3', alias)


# ── Phase 1 — Start OAuth ──────────────────────────────────────────────────────

def phase1_start(alias, services):
    scopes = list(dict.fromkeys(
        scope for svc in services for scope in SCOPES_MAP.get(svc, [])
    ))

    oauth = _load_oauth()
    code_verifier, code_challenge = _generate_pkce()

    params = {
        'client_id':             oauth['client_id'],
        'redirect_uri':          REDIRECT_URI,
        'response_type':         'code',
        'scope':                 ' '.join(scopes),
        'code_challenge':        code_challenge,
        'code_challenge_method': 'S256',
        'access_type':           'offline',
        'prompt':                'consent',
        'state':                 alias,
    }
    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params)

    # Persist code_verifier so phase 2 can use it
    pending = {
        'alias':         alias,
        'services':      services,
        'scopes':        scopes,
        'code_verifier': code_verifier,
    }
    with open(os.path.join(CONFIG_DIR, f'pending_{alias}.json'), 'w') as f:
        json.dump(pending, f)

    print(f"AUTH_URL:{auth_url}")


# ── Phase 2 — Finish OAuth ─────────────────────────────────────────────────────

def phase2_finish(alias, code_or_url):
    pending_path = os.path.join(CONFIG_DIR, f'pending_{alias}.json')
    if not os.path.exists(pending_path):
        print(json.dumps({"error": f"No pending auth for '{alias}'. Run phase 1 first."}))
        sys.exit(1)

    with open(pending_path) as f:
        pending = json.load(f)

    # Accept either a bare code or the full redirect URL
    code = code_or_url
    if code_or_url.startswith('http'):
        parsed = urllib.parse.urlparse(code_or_url)
        params = urllib.parse.parse_qs(parsed.query)
        code = params.get('code', [None])[0]
        if not code:
            print(json.dumps({"error": "No 'code' parameter found in the URL."}))
            sys.exit(1)

    oauth = _load_oauth()
    exchange_url = oauth.get('exchange_url')
    if not exchange_url:
        print(json.dumps({"error": "No exchange_url in oauth.json. Re-run setup."}))
        sys.exit(1)

    token_data = _exchange_via_proxy(exchange_url, code, pending['code_verifier'])

    if 'error' in token_data:
        print(json.dumps({
            "error":       token_data.get('error'),
            "description": token_data.get('error_description'),
        }))
        sys.exit(1)

    # Fetch email via userinfo endpoint
    access_token = token_data['access_token']
    email = alias
    try:
        req = urllib.request.Request(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            email = json.loads(resp.read()).get('email', alias)
    except Exception:
        pass

    # Calculate token expiry
    expires_in = token_data.get('expires_in', 3600)
    expiry = (datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)).isoformat()

    # Save credentials
    accounts_dir = os.path.join(CONFIG_DIR, 'accounts')
    os.makedirs(accounts_dir, exist_ok=True)
    creds_data = {
        'alias':         alias,
        'email':         email,
        'token':         access_token,
        'refresh_token': token_data.get('refresh_token'),
        'expiry':        expiry,
        'scopes':        pending['scopes'],
        'services':      pending['services'],
    }
    with open(os.path.join(accounts_dir, f'{alias}.json'), 'w') as f:
        json.dump(creds_data, f, indent=2)

    os.remove(pending_path)

    print(json.dumps({
        "success":  True,
        "alias":    alias,
        "email":    email,
        "services": pending['services'],
    }))


# ── CLI entry point ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"error": "Usage: auth.py <alias> [services...] | auth.py <alias> --finish <url>"}))
        sys.exit(1)

    alias = args[0]

    if '--finish' in args:
        idx = args.index('--finish')
        phase2_finish(alias, args[idx + 1])
    else:
        services = args[1:] if len(args) > 1 else ['gmail', 'calendar', 'drive']
        phase1_start(alias, services)
