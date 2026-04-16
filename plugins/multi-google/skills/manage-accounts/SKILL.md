---
name: manage-accounts
description: >
  Use this skill when the user says "add a google account", "agregar cuenta de google",
  "connect another google account", "remove a google account", "eliminar cuenta de google",
  "list my google accounts", "qué cuentas tengo conectadas", "show connected accounts",
  "ver mis cuentas", "enable calendar for my work account", "disable drive for personal",
  "update services for an account", "change account permissions",
  or any phrase about adding, removing, listing, or updating Google accounts.
metadata:
  version: "0.9.0"
---

## IMPORTANT: Use VM Bash tool for ALL commands — NO Desktop Commander needed.

## Step 0 — Auto-bootstrap (run FIRST, every time)

Run this single block unconditionally before anything else. It handles fresh sessions and new installs automatically:

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)

# Find the plugin's scripts directory (works regardless of plugin ID)
PLUGIN_SCRIPTS=$(find /sessions/*/mnt/.remote-plugins/*/scripts -name "setup_oauth.py" 2>/dev/null | head -1 | xargs -I{} dirname {})

if [ -z "$PLUGIN_SCRIPTS" ]; then
  echo "ERROR: Plugin scripts not found. Is multi-google installed?"
  exit 1
fi

# Copy scripts to persistent mnt if missing
if [ ! -f "$MNT/.multi-google/scripts/auth.py" ]; then
  echo "First run — copying scripts..."
  mkdir -p "$MNT/.multi-google/scripts" "$MNT/.multi-google/accounts"
  cp "$PLUGIN_SCRIPTS"/*.py "$MNT/.multi-google/scripts/"
fi

# Pre-install Google packages silently (handles pypi.org-blocked networks gracefully)
pip install -q google-auth google-auth-oauthlib google-api-python-client --break-system-packages 2>/dev/null || true

# Generate oauth.json if missing
if [ ! -f "$MNT/.multi-google/oauth.json" ]; then
  echo "Setting up credentials..."
  python3 "$MNT/.multi-google/scripts/setup_oauth.py"
fi

echo "Bootstrap OK."
```

## List accounts

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/list_accounts.py"
```

Show as table: Alias | Email | Services

## Add a new account

1. Ask for **alias** (short name, no spaces, e.g. `work`, `personal`, `dev-singular`).
2. Ask which services: Gmail / Calendar / Drive (can combine).
3. Run Phase 1 — generate auth URL:

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/auth.py" <alias> <service1> [service2] [service3] 2>&1
```

4. Look for `AUTH_URL:` in the output. Show the user the link and tell them:

> "Abre este link en tu navegador e inicia sesión con la cuenta de Google que quieres conectar. Después de aceptar los permisos verás una página de éxito con un botón **'Copy URL'** — haz click en ese botón y pega la URL aquí."

5. Once the user pastes the redirect URL, run Phase 2:

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/auth.py" <alias> --finish "<redirect_url>" 2>&1
```

6. Look for `{"success": true, ...}`. Show detected email and services.

7. Show updated account list:
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/list_accounts.py"
```

## Remove an account

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
rm -f "$MNT/.multi-google/accounts/<alias>.json"
python3 -c "
import json, os, glob
dirs = glob.glob('/sessions/*/mnt/.multi-google')
d = dirs[0] if dirs else os.path.expanduser('~/.multi-google')
f = os.path.join(d, 'accounts.json')
if os.path.exists(f):
    a = json.load(open(f))
    a.pop('<alias>', None)
    json.dump(a, open(f,'w'), indent=2)
    print('Removed.')
else:
    print('No accounts file found.')
"
python3 "$MNT/.multi-google/scripts/list_accounts.py"
```
