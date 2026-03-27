---
name: setup
description: >
  Configures the Calendar Automatcher plugin by saving the three participant emails
  (PM, PO, and Talent) for future automatic scheduling.
  Trigger when the user says: "configurar automatcher", "setup del plugin",
  "guardar emails", "configurar participantes", "primera vez", "inicializar plugin",
  "actualizar contactos del sync", or "cambiar participantes".
tools:
  - Bash
  - Read
---

# Calendar Automatcher — Setup

Guide the user through first-time configuration of the three sync participants.

## Steps

### 1. Greet and explain

Tell the user you'll save the three participant emails so they never have to type them again. Future invocations of "agendar sync" will use this config automatically.

### 2. Collect participant emails

Ask the user for each email in a single message (not one at a time):
- **PM**: their own email (suggest as@singularagency.co as default if they confirm)
- **PO**: email of the Product Owner
- **Talento / HR**: email of the Talent team member

### 3. Confirm before saving

Display a summary like:

> **Configuración a guardar:**
> - PM → pm@example.com
> - PO → po@example.com
> - Talento → talent@example.com
> - Horario laboral: 08:00–17:00 (Guatemala, UTC-6)
> - Buffer de cortesía: 2 horas
> - Duración del bloque: 30 minutos
> - Ventana de búsqueda: 48 horas
>
> ¿Confirmas?

Wait for confirmation before writing the file.

### 4. Save configuration

Use Bash to write the config file to `~/.calendar-automatcher-config.json`:

```bash
cat > ~/.calendar-automatcher-config.json << 'EOF'
{
  "participants": {
    "pm": "PM_EMAIL",
    "po": "PO_EMAIL",
    "talent": "TALENT_EMAIL"
  },
  "timezone": "America/Guatemala",
  "working_hours": {
    "start": 8,
    "end": 17
  },
  "buffer_hours": 2,
  "meeting_duration_minutes": 30,
  "search_window_hours": 48,
  "meeting_title": "Sync Táctica: PM + PO + Talento"
}
EOF
```

Replace `PM_EMAIL`, `PO_EMAIL`, and `TALENT_EMAIL` with the actual values provided.

### 5. Confirm success

Tell the user setup is complete and they can now say **"agendar sync"** or **"busca disponibilidad"** at any time to trigger the automatcher.
