---
name: setup
description: >
  Use this skill when the user says "set up multi-google", "configurar el plugin de google",
  "first time setup", "conectar mis cuentas de google", "initialize the google plugin",
  "el plugin no funciona", "setup multi google", or any phrase indicating they want
  to set up or initialize the Multi-Google plugin for the first time.
  Also trigger if any Google service is not working and setup was never completed.
metadata:
  version: "0.6.0"
---

## IMPORTANT: Use VM Bash tool for ALL commands — NO Desktop Commander needed.

## Step 1 — Install Google packages (VM Bash)

```bash
pip install google-auth google-auth-oauthlib google-api-python-client -q 2>&1 | tail -3
python3 -c "from google_auth_oauthlib.flow import InstalledAppFlow; print('OK')"
```

## Step 2 — Copy scripts to persistent folder (VM Bash)

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
mkdir -p "$MNT/.multi-google/scripts" "$MNT/.multi-google/accounts"

PLUGIN_SCRIPTS=$(find /sessions -path "*/remote-plugins/plugin_011*/scripts" 2>/dev/null | head -1)
if [ -z "$PLUGIN_SCRIPTS" ]; then
  echo "ERROR: Plugin scripts not found. Is the plugin installed in Claude Desktop?"
else
  cp "$PLUGIN_SCRIPTS"/*.py "$MNT/.multi-google/scripts/"
  echo "Scripts copied to $MNT/.multi-google/scripts/"
  ls "$MNT/.multi-google/scripts/"
fi
```

## Step 3 — Google OAuth credentials

Check if credentials exist:
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 -c "import os; p='$MNT/.multi-google/oauth.json'; print('EXISTS' if os.path.exists(p) else 'MISSING')"
```

**If EXISTS → skip to Step 4.**

**If MISSING → show the user:**

> Para conectar tus cuentas de Google necesitas crear credenciales en Google Cloud. Solo toma 2 minutos:
>
> 1. Ve a **[console.cloud.google.com](https://console.cloud.google.com)** e inicia sesión
> 2. Crea un proyecto nuevo (cualquier nombre, ej. `claude-google-plugin`)
> 3. Ve a **APIs y servicios → Biblioteca** y habilita:
>    - **Gmail API**, **Google Calendar API**, **Google Drive API**, **Google OAuth2 API**
> 4. Ve a **APIs y servicios → Credenciales → Crear credenciales → ID de cliente de OAuth**
>    - Tipo: **Aplicación de escritorio** · Nombre: `claude-multi-google`
> 5. Descarga el JSON (botón ⬇️) y pega todo su contenido aquí

Once the user pastes the JSON, save it:
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 -c "
import json, os
raw = r'''PASTE_JSON_HERE'''
data = json.loads(raw)
path = '$MNT/.multi-google/oauth.json'
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
os.chmod(path, 0o600)
print('Credentials saved.')
"
```

Replace `PASTE_JSON_HERE` with the JSON the user pasted.

## Step 4 — Done! Show onboarding

---

🎉 **Multi-Google está listo!**

Conecta tu primera cuenta diciéndome:
> "Agregar cuenta de Google"

---

Una vez conectada, aquí algunos ejemplos:

**📬 Gmail** — *"Muéstrame mis emails sin leer"* · *"Busca emails de [persona]"* · *"Respóndele a [persona] que..."*

**📅 Calendar** — *"Qué tengo esta semana?"* · *"Crea una reunión con [persona] el [día]"* · *"Acepta la invitación de [evento]"*

**📁 Drive** — *"Cuál es el archivo más reciente?"* · *"Busca el doc sobre [tema]"* · *"Comparte [archivo] con [email]"*

**🗂️ Recap** — *"Ponme al día con lo de esta semana"*

---
