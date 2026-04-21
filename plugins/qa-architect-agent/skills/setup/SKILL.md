---
description: >
  NexusQA Platform Setup — connects the qa-architect-agent plugin to the
  NexusQA tracking platform. Use when: "configurar nexusqa", "setup nexusqa",
  "conectar la plataforma", "agregar api key", "inicializar el plugin",
  "primera vez", "setup qa platform", "connect to qa platform",
  or any phrase indicating first-time setup or re-configuration of the
  NexusQA integration.
---

# qa-architect-agent: setup

You are setting up the connection between the qa-architect-agent plugin and the NexusQA platform at **https://qa.singular-innovation.com**.

---

## Step 1 — Check current config

```bash
python3 - <<'EOF'
import json, os
cfg = os.path.expanduser("~/.nexusqa-config.json")
if os.path.exists(cfg):
    d = json.load(open(cfg))
    key = d.get("api_key", "")
    print(f"EXISTING_CONFIG: true")
    print(f"  platform_url : {d.get('platform_url', '')}")
    print(f"  api_key      : {key[:8]}{'...' if key else ''}")
    print(f"  configured_at: {d.get('configured_at', 'unknown')}")
else:
    print("EXISTING_CONFIG: false")
EOF
```

If a config already exists, ask the user:
> "Ya hay una API key configurada (`nqa_xxxxxxxx...`). ¿Quieres reemplazarla o mantenerla?"

If they want to keep it, show a connection test (Step 3) and exit. Otherwise continue.

---

## Step 2 — Ask for API key

Tell the user:

> Para conectarte a NexusQA necesito tu **API key**.
> 
> Podés generarla en: **https://qa.singular-innovation.com** → Settings → API Keys → New Key
> 
> La clave tiene el formato `nqa_xxxxxxxxxxxxxxxxxxxxxxxx`
> 
> Por favor pegala aquí:

Wait for the user to paste the key. Validate that it:
- Starts with `nqa_`
- Has length > 10

If invalid, say: "Esa clave no parece válida — debe empezar con `nqa_`. Intentá de nuevo."

---

## Step 3 — Test connection

```bash
API_KEY="<key_from_user>"
PLATFORM_URL="https://qa.singular-innovation.com"

curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -H "Authorization: Bearer $API_KEY" \
  "$PLATFORM_URL/api/v1/agent/projects"
```

Parse the response:
- **HTTP 200** + JSON with `data` array → connection successful ✅
- **HTTP 401** → "La API key no es válida o fue revocada."
- **HTTP 403** → "La API key no tiene permisos suficientes."
- **Other / timeout** → "No se pudo conectar a la plataforma. Verificá tu conexión."

Show the list of accessible projects:
```
✅ Conexión exitosa

Proyectos accesibles con esta key:
  • Nombre del Proyecto 1 (id: abc123)
  • Nombre del Proyecto 2 (id: def456)
```

---

## Step 4 — Save config

```bash
python3 - <<'EOF'
import json, os
from datetime import datetime

config = {
    "platform_url": "https://qa.singular-innovation.com",
    "api_key": "<API_KEY>",
    "configured_at": datetime.now().isoformat(),
}

cfg_path = os.path.expanduser("~/.nexusqa-config.json")
json.dump(config, open(cfg_path, "w"), indent=2)
os.chmod(cfg_path, 0o600)  # owner-only permissions
print(f"Config saved to {cfg_path}")
EOF
```

---

## Step 5 — Confirm and guide next steps

Tell the user:

> 🎉 **Setup completo**
> 
> Tu API key de NexusQA quedó guardada. A partir de ahora, cuando uses el qa-architect-agent:
> 
> 1. Detecta automáticamente tu config y te muestra los proyectos accesibles
> 2. Crea un sprint + test run en la plataforma antes de ejecutar
> 3. Reporta cada resultado en tiempo real — podés ver el progreso en **https://qa.singular-innovation.com**
> 4. Al terminar, el run queda marcado como `completed` con todos los resultados
> 
> **Para empezar:** simplemente decí `"quiero testear el proyecto [nombre]"` o `"run QA on [URL]"`.
> 
> Si querés cambiar la API key en el futuro, ejecutá `qa-architect-agent:setup` de nuevo.
