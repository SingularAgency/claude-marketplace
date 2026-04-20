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
  version: "1.0.1"
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
pip install -q google-auth google-api-python-client --break-system-packages 2>/dev/null || true

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

Run the wizard — ask each question and wait for the answer before moving to the next step. Never skip or assume.

**Step 1 — Alias**
Ask: *"¿Qué nombre le ponés a esta cuenta? (ej: work, personal, empresa)"*
Wait for answer. Alias must be one word, no spaces.

**Step 2 — Services wizard**
Use the `AskUserQuestion` tool with `multiSelect: true` and these exact options:

```json
{
  "question": "¿Qué servicios querés conectar para la cuenta \"[alias]\"?",
  "header": "Servicios",
  "multiSelect": true,
  "options": [
    { "label": "📬 Gmail",    "description": "Leer, enviar y gestionar emails" },
    { "label": "📅 Calendar", "description": "Ver y crear eventos del calendario" },
    { "label": "📁 Drive",    "description": "Buscar y leer archivos en Drive" }
  ]
}
```

Map selected labels to service names: `📬 Gmail` → `gmail`, `📅 Calendar` → `calendar`, `📁 Drive` → `drive`.

**Step 3 — Confirm**
Show a summary and ask for confirmation before generating the URL:

> *"Voy a conectar la cuenta **[alias]** con acceso a: [servicios]. ¿Confirmás?"*

**Step 4 — Generate auth URL**

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/auth.py" <alias> <service1> [service2] [service3] 2>&1
```

Look for `AUTH_URL:` in the output. Show the user the link and say:

> "Abrí este link en tu navegador e iniciá sesión con la cuenta de Google que querés conectar. Después de aceptar los permisos vas a ver una página de éxito con un botón **'Copy URL'** — hacé click en ese botón y pegá la URL aquí."

**Step 5 — Finish auth**

Once the user pastes the redirect URL:

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/auth.py" <alias> --finish "<redirect_url>" 2>&1
```

Look for `{"success": true, ...}`. Show detected email and connected services.

**Step 6 — Show updated account list**
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/list_accounts.py"
```

## Remove an account

Ask for confirmation before removing. Then:

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
rm -f "$MNT/.multi-google/accounts/<alias>.json"
echo "Account <alias> removed."
python3 "$MNT/.multi-google/scripts/list_accounts.py"
```
