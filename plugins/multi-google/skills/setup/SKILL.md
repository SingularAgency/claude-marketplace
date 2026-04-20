---
name: setup
description: >
  Use this skill when the user says "set up multi-google", "configurar el plugin de google",
  "first time setup", "conectar mis cuentas de google", "initialize the google plugin",
  "el plugin no funciona", "setup multi google", or any phrase indicating they want
  to set up or initialize the Multi-Google plugin for the first time.
  Also trigger if any Google service is not working and setup was never completed.
metadata:
  version: "1.0.1"
---

## IMPORTANT: Use VM Bash tool for ALL commands — NO Desktop Commander needed.

## Step 1 — Bootstrap (auto-runs every time)

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
PLUGIN_SCRIPTS=$(find /sessions/*/mnt/.remote-plugins/*/scripts -name "setup_oauth.py" 2>/dev/null | head -1 | xargs -I{} dirname {})

if [ -z "$PLUGIN_SCRIPTS" ]; then
  echo "ERROR: Plugin scripts not found. Is multi-google installed?"
  exit 1
fi

if [ ! -f "$MNT/.multi-google/scripts/auth.py" ]; then
  echo "First run — copying scripts..."
  mkdir -p "$MNT/.multi-google/scripts" "$MNT/.multi-google/accounts"
  cp "$PLUGIN_SCRIPTS"/*.py "$MNT/.multi-google/scripts/"
fi

# Install Google packages silently
pip install -q google-auth google-api-python-client --break-system-packages 2>/dev/null || true

if [ ! -f "$MNT/.multi-google/oauth.json" ]; then
  echo "Setting up credentials..."
  python3 "$MNT/.multi-google/scripts/setup_oauth.py"
fi

echo "Bootstrap OK."
```

## Step 2 — Done! Show onboarding

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
