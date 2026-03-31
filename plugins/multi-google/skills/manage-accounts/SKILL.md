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
  version: "0.6.0"
---

## IMPORTANT: Use Desktop Commander for ALL commands

ALL commands MUST run via Desktop Commander (`mcp__Desktop_Commander__start_process` with `shell: "bash"`). Do NOT use the VM Bash tool.

## List accounts (via Desktop Commander)

```bash
python3 ~/.multi-google/scripts/list_accounts.py
```

Show as table: Alias | Email | Services

## Add a new account

1. Ask for **alias** (short name, no spaces, e.g. `work`, `personal`, `dev-singular`).
2. Ask which services: Gmail / Calendar / Drive (can combine).
3. Run auth via Desktop Commander:

```bash
python3 ~/.multi-google/scripts/auth.py <alias> <service1> [service2] [service3] 2>&1
```

> **Note:** No email needed — it's detected automatically from Google after sign-in.

4. Look for `AUTH_URL:` in the output. Copy the full URL after `AUTH_URL:` and tell the user:
   > "Abre este link en tu navegador, inicia sesión con la cuenta de Google que quieres conectar y acepta los permisos. El tab se cerrará automáticamente cuando termine."

5. Wait for user to confirm they saw the "Connected to Claude!" page (or tab closed). Then check:
```bash
cat ~/.multi-google/accounts.json
```
Look for `"success": true` in the process output or verify the alias appears in accounts.json.

6. Show updated account list.

## Remove an account (via Desktop Commander)

```bash
rm -f ~/.multi-google/accounts/<alias>.json
python3 -c "
import json,os
f=os.path.expanduser('~/.multi-google/accounts.json')
a=json.load(open(f)); a.pop('<alias>',None)
json.dump(a,open(f,'w'),indent=2); print('Removed.')
"
python3 ~/.multi-google/scripts/list_accounts.py
```
