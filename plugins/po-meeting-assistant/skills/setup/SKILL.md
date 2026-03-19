---
name: setup
description: >
  Use this skill when the user says "configurar el asistente", "setup", "iniciar el asistente",
  "instalar el plugin", "primera vez", "cómo empiezo", "ayuda con la configuración",
  or any phrase indicating they want to set up or initialize the PO Meeting Assistant for the first time.
  Also trigger if the user says briefings are not working and setup was never completed.
metadata:
  version: "0.2.0"
---

# Setup Skill — PO Meeting Assistant

Guide the PO step by step through the complete initial setup. Complete each phase before moving to the next. Keep all language plain and non-technical. Never mention tables, databases, or SQL to the user.

## Phase 0: Welcome

> "Vamos a configurar tu asistente de reuniones. Una vez listo, voy a consultar tus correos, mensajes de Slack y transcripciones cada vez que tengas una reunión próxima — sin guardar nada, todo en tiempo real. 5 pasos, ninguno toma más de 5 minutos."

## Phase 1: Connect the Connectors

Present each connector ONE AT A TIME. Wait for confirmation before continuing.

---

**Paso 1 de 4 — Slack**
> "Primero necesito conectarme a Slack para leer los canales de tus clientes y enviarte el briefing por mensaje directo."

Use `suggest_connectors` with UUID: `597f662f-36de-437e-836e-5a81013cbfbe`

✅ Wait for confirmation.

---

**Paso 2 de 4 — Google Calendar**
> "Ahora conectá tu Google Calendar. Lo necesito para saber cuándo tenés reuniones y activar el briefing automático."

Use `suggest_connectors` with UUID: `5de23dc2-0fa3-47f7-9332-68e60d14b84e`

✅ Wait for confirmation.

---

**Paso 3 de 4 — Supabase (configuración del asistente)**
> "Necesito un lugar donde guardar tu configuración: qué clientes tenés, qué canales monitorear, tus preferencias. No guardamos mensajes ni emails — solo la configuración."

Load and follow `references/supabase-setup-guide.md`.

✅ Wait for confirmation.

---

**Paso 4 de 4 — Read.ai**
> "Por último, conectamos Read.ai para que pueda consultar las transcripciones de tus reuniones cuando armes un briefing."

Load and follow `references/readai-setup-guide.md`.

✅ Wait for confirmation.

---

**Gmail** — verify silently:
Call `gmail_get_profile`. If it works, confirm to user: "✅ Gmail ya está conectado." If it fails, use `suggest_connectors` with Gmail UUID: `a02abd88-a6c4-4c27-a35a-25de5c2a6a93`

---

## Phase 2: Initialize the Database

> "Ahora preparo tu configuración. Esto es automático."

Execute the SQL from `references/database-schema.sql` via Supabase MCP. Run all statements in order. On any failure, show the error and stop.

> "✅ Configuración lista."

## Phase 3: Create Your Profile

Ask these questions conversationally:

1. **Nombre**: "¿Cuál es tu nombre?"
   → Used to generate `po_id` (slug: `nombre-apellido` lowercase)

2. **Lead time**: "¿Cuántos minutos antes de una reunión querés recibir el briefing?" *(Recomendado: 10)*

3. **Ventana de tiempo**: "¿Cuántos días de historial querés que consulte cuando preparo un briefing? Por ejemplo: 7 días significa que reviso la última semana de emails, Slack y transcripciones. Más días = más contexto pero también más tiempo para preparar el briefing." *(Recomendado: 14)*

4. **Slack**: "¿Cuál es tu usuario de Slack? (con @ adelante, ej: @amilkar)"

Insert into `po_preferences`:
```sql
INSERT INTO po_preferences (po_id, display_name, notification_slack_user_id, briefing_lead_minutes, time_window_days)
VALUES ('[slug]', '[name]', '[slack_user]', [lead_minutes], [window_days])
ON CONFLICT (po_id) DO UPDATE SET
  display_name               = EXCLUDED.display_name,
  notification_slack_user_id = EXCLUDED.notification_slack_user_id,
  briefing_lead_minutes      = EXCLUDED.briefing_lead_minutes,
  time_window_days           = EXCLUDED.time_window_days,
  updated_at                 = now();
```

## Phase 4: Configure Your First Client

> "Ahora configuremos tu primer cliente. Necesito saber de dónde sacar información cuando tengas una reunión con ellos."

Load and follow `references/client-configuration-guide.md`.

## Phase 5: Set Up the Automatic Briefing Task

> "Último paso: programo la tarea que te avisa antes de cada reunión."

Create ONE scheduled task using the schedule skill:
- **Name**: `po-briefing-check-[po_id]`
- **Prompt**: `Ejecuta el skill generate-briefing en modo automático para el PO [po_id].`
- **Interval**: every 5 minutes

> "Esta tarea se ejecuta cada 5 minutos pero es muy liviana — solo revisa si hay una reunión próxima. Si no hay nada, termina en segundos."

## Phase 6: Completion

> "🎉 ¡Todo listo!
>
> Lo que va a pasar de ahora en más:
> - Cada 5 minutos reviso tu calendario silenciosamente
> - Cuando detecte una reunión con un cliente en los próximos [lead_minutes] minutos, voy a consultar tus últimos [window_days] días de emails, Slack y transcripciones de ese cliente
> - Te mando el resumen por Slack antes de entrar
>
> Podés pedir un briefing en cualquier momento diciéndome: **'dame el brief de [cliente]'**"
