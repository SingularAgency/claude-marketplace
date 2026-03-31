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

## Step 0 — Check Desktop Commander dependency

**Desktop Commander is required** for this plugin. It allows Claude to run commands in your local environment (WSL2/terminal) where the Google scripts live.

Check if Desktop Commander is available by attempting to use `mcp__Desktop_Commander__start_process`. If it IS available, proceed to Step 1.

**If Desktop Commander is NOT available** (tool not found or not connected), show this wizard:

---

⚠️ **Desktop Commander requerido**

Este plugin necesita **Desktop Commander** para funcionar — es una extensión que le permite a Claude ejecutar comandos directamente en tu computadora.

**Cómo instalarlo:**

1. Abre Claude Desktop
2. Ve a **Settings → Extensions** (o **Configuración → Extensiones**)
3. Busca **"Desktop Commander"** e instálalo
4. Reinicia Claude Desktop
5. Vuelve a este chat y di **"configurar multi-google"** para continuar

> Si ya lo tienes instalado pero aparece este mensaje, asegúrate de que Desktop Commander esté **habilitado** en Settings → Extensions.

---

Stop here and do NOT proceed until the user confirms Desktop Commander is installed and active.

---

## Step 1 — Check Python (via Desktop Commander)

Run via `mcp__Desktop_Commander__start_process` with `shell: "bash"`:

```bash
python3 --version
```

If Python is not found or version < 3.8, tell user:
> "Necesitas Python 3.8 o superior. Descárgalo desde python.org e instálalo, luego di 'configurar multi-google' de nuevo."

Stop if Python is missing.

## Step 2 — Install Google packages (via Desktop Commander)

```bash
python3 -m pip install google-auth google-auth-oauthlib google-api-python-client -q 2>&1 | tail -3
```

If pip is missing:
```bash
curl -sS https://bootstrap.pypa.io/get-pip.py | python3
```
Then retry the install.

Verify:
```bash
python3 -c "from google_auth_oauthlib.flow import InstalledAppFlow; print('OK')"
```

## Step 3 — Copy scripts to WSL2 native filesystem (via Desktop Commander)

```bash
mkdir -p ~/.multi-google/scripts ~/.multi-google/accounts

PLUGIN_SCRIPTS=$(find /mnt/c/Users -path "*/remote-plugins/plugin_011*/scripts" 2>/dev/null | head -1)
if [ -z "$PLUGIN_SCRIPTS" ]; then
  echo "ERROR: Plugin scripts not found. Is the plugin installed?"
else
  cp "$PLUGIN_SCRIPTS"/*.py ~/.multi-google/scripts/
  echo "Scripts copied:" && ls ~/.multi-google/scripts/
fi
```

Write config:
```bash
echo "{\"scripts_dir\": \"$HOME/.multi-google/scripts\"}" > ~/.multi-google/config.json
```

## Step 4 — Google OAuth credentials

Check if credentials already exist:
```bash
python3 -c "import os; p=os.path.expanduser('~/.multi-google/oauth.json'); print('EXISTS' if os.path.exists(p) else 'MISSING')"
```

**If EXISTS → skip to Step 5.**

**If MISSING → show this to the user:**

> Para conectar tus cuentas de Google necesitas crear credenciales de OAuth en Google Cloud. Solo toma 2 minutos:
>
> 1. Ve a **[console.cloud.google.com](https://console.cloud.google.com)** e inicia sesión
> 2. Crea un proyecto nuevo (cualquier nombre, ej. `mi-claude-plugin`)
> 3. En el menú izquierdo → **APIs y servicios → Biblioteca** — habilita:
>    - **Gmail API**
>    - **Google Calendar API**
>    - **Google Drive API**
>    - **Google OAuth2 API**
> 4. Ve a **APIs y servicios → Credenciales → Crear credenciales → ID de cliente de OAuth**
>    - Tipo de aplicación: **Aplicación de escritorio**
>    - Nombre: `claude-multi-google`
> 5. Descarga el JSON (botón ⬇️ junto a tu credencial recién creada)
> 6. Abre el archivo y **pega todo su contenido aquí**

Once the user pastes the JSON, save it via Desktop Commander:

```bash
python3 -c "
import json, os
raw = r'''PASTE_JSON_HERE'''
data = json.loads(raw)
path = os.path.expanduser('~/.multi-google/oauth.json')
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
os.chmod(path, 0o600)
print('Credentials saved to', path)
"
```

Replace `PASTE_JSON_HERE` with the exact JSON the user pasted, then run.

## Step 5 — Done! Show onboarding to user

Once setup completes successfully, show this welcome message **exactly as formatted below**:

---

🎉 **Multi-Google está listo!**

Conecta tu primera cuenta diciéndome:
> "Agregar cuenta de Google"

---

Una vez que tengas una cuenta conectada, aquí van algunos ejemplos de lo que puedes hacer:

**📬 Gmail**
- *"Muéstrame mis emails sin leer"*
- *"Busca emails de [persona] de esta semana"*
- *"Lee el último email de [remitente]"*
- *"Respóndele a [persona] que..."*
- *"Manda un email a [dirección] con asunto [X] diciendo [Y]"*

**📅 Google Calendar**
- *"Qué tengo en el calendario esta semana?"*
- *"Crea una reunión con [persona] el [día] a las [hora]"*
- *"Acepta la invitación de [evento]"*
- *"Cuándo estoy libre el [día] para una reunión de 30 minutos?"*

**📁 Google Drive**
- *"Cuál es el archivo más reciente en mi Drive?"*
- *"Busca el documento sobre [tema]"*
- *"Comparte [archivo] con [email]"*
- *"Qué cambios hubo en mi Drive esta semana?"*

**🗂️ Recap completo**
- *"Dame un resumen de todo lo que pasó hoy"*
- *"Ponme al día con lo de esta semana"*

**👥 Multi-cuenta**
> Si tienes varias cuentas de Google (ej. trabajo + personal), puedes conectar todas. Yo sé cuál usar según el contexto, o puedes especificar: *"Busca en mi cuenta de trabajo..."*

---
