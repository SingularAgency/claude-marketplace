#!/usr/bin/env python3
# Auto-add user local site-packages so Google packages are found in any env
import sys as _sys, os as _os, glob as _glob
for _sp in _glob.glob(_os.path.expanduser('~/.local/lib/python3*/site-packages')):
    if _sp not in _sys.path:
        _sys.path.insert(0, _sp)

import json, os, sys, tempfile, urllib.parse
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

CONFIG_DIR = os.path.expanduser('~/.multi-google')

# Credentials are loaded from ~/.multi-google/oauth.json (written by setup).
# The .plugin distribution includes a pre-configured oauth.json so users never
# need to create a Google Cloud project. For marketplace source installs,
# run the setup skill to configure credentials.
def _load_credentials():
    oauth_path = os.path.join(CONFIG_DIR, 'oauth.json')
    if os.path.exists(oauth_path):
        with open(oauth_path) as f:
            return json.load(f)
    # Fallback: inline credentials (populated by setup or .plugin distribution)
    raise FileNotFoundError(
        f"OAuth credentials not found at {oauth_path}. "
        "Run 'configurar multi-google' to set up."
    )

SCOPES_MAP = {
    "gmail":    ["https://www.googleapis.com/auth/gmail.modify",
                 "https://www.googleapis.com/auth/gmail.send"],
    "calendar": ["https://www.googleapis.com/auth/calendar"],
    "drive":    ["https://www.googleapis.com/auth/drive"],
}

SUCCESS_PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Connected to Claude</title>
<style>body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#f9f9f9}.card{background:white;border-radius:16px;padding:48px 56px;box-shadow:0 4px 24px rgba(0,0,0,.08);text-align:center;max-width:420px}.icon{font-size:48px;margin-bottom:16px}h1{color:#1a1a1a;font-size:22px;margin:0 0 8px}p{color:#666;font-size:15px;margin:0 0 24px;line-height:1.5}.badge{background:#f0faf0;color:#2d7a2d;border-radius:8px;padding:8px 16px;font-size:13px;display:inline-block}</style></head>
<body><div class="card"><div class="icon">&#x2705;</div><h1>Connected to Claude!</h1><p>Your Google account has been linked.<br>This tab will close automatically.</p><div class="badge">&#x1F512; SERVICES_PLACEHOLDER</div></div>
<script>setTimeout(function(){window.close();},2000);</script></body></html>"""

if len(sys.argv) < 3:
    print(json.dumps({"error": "Usage: auth.py <alias> <service1> [service2...]"}))
    sys.exit(1)

alias    = sys.argv[1]
services = sys.argv[2:]

scopes = ["openid", "https://www.googleapis.com/auth/userinfo.email"]
for svc in services:
    scopes.extend(SCOPES_MAP.get(svc, []))

print(f"Starting auth for {alias} ({', '.join(services)})", flush=True)

try:
    creds_data = _load_credentials()
except FileNotFoundError as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)

tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
json.dump(creds_data, tmp)
tmp.close()

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print(json.dumps({"error": "Run: pip install google-auth google-auth-oauthlib google-api-python-client"}))
    sys.exit(1)

flow = InstalledAppFlow.from_client_secrets_file(tmp.name, scopes=scopes)
os.unlink(tmp.name)

_auth_code = [None]

class SilentHandler(WSGIRequestHandler):
    def log_message(self, fmt, *args): pass

class CallbackApp:
    def __call__(self, environ, start_response):
        params = dict(urllib.parse.parse_qsl(environ.get('QUERY_STRING', '')))
        _auth_code[0] = params.get('code')
        page = SUCCESS_PAGE.replace('SERVICES_PLACEHOLDER', ' · '.join(s.capitalize() for s in services))
        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
                                  ('Content-Length', str(len(page.encode())))])
        return [page.encode()]

server = WSGIServer(('localhost', 0), SilentHandler)
server.set_app(CallbackApp())
port = server.server_address[1]

flow.redirect_uri = f"http://localhost:{port}/"
auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
print(f"AUTH_URL:{auth_url}", flush=True)

server.handle_request()
server.server_close()

if not _auth_code[0]:
    print(json.dumps({"error": "No auth code received"}))
    sys.exit(1)

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
flow.fetch_token(code=_auth_code[0])
creds = flow.credentials

try:
    oauth2_service = build('oauth2', 'v2', credentials=creds)
    user_info = oauth2_service.userinfo().get().execute()
    email = user_info.get('email', alias + '@unknown')
except Exception:
    email = alias + '@unknown'

accounts_dir = os.path.join(CONFIG_DIR, 'accounts')
os.makedirs(accounts_dir, exist_ok=True)
with open(os.path.join(accounts_dir, f'{alias}.json'), 'w') as f:
    f.write(creds.to_json())

accounts_file = os.path.join(CONFIG_DIR, 'accounts.json')
accounts = {}
if os.path.exists(accounts_file):
    with open(accounts_file) as f:
        accounts = json.load(f)
accounts[alias] = {'email': email, 'services': services}
with open(accounts_file, 'w') as f:
    json.dump(accounts, f, indent=2)

print(json.dumps({"success": True, "alias": alias, "email": email, "services": services}), flush=True)
