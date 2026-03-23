---
name: configure
description: >
  Use this skill when the user says "agregar cliente", "nuevo cliente", "configurar cliente",
  "agregar canal", "agregar canal global", "cambiar canales de [cliente]",
  "editar cliente", "borrar cliente", "cambiar cuántos minutos antes", "cambiar ventana de tiempo",
  "cambiar a [N] días de historial", "actualizar mis preferencias", "ver mis clientes",
  "listar clientes", "¿qué clientes tengo configurados?", "¿qué canales estoy monitoreando?",
  or any phrase related to managing the assistant's configuration.
metadata:
  version: "0.2.0"
---

# Configure Skill

Handle all configuration management via natural language. The user never touches the database.

## Identify the PO

```sql
SELECT po_id, display_name FROM po_preferences;
```

If multiple, ask: "¿Sos [name1] o [name2]?"

---

## Operations

### LIST — Show current configuration

```sql
SELECT client_id, display_name, email_domains, calendar_keywords
FROM clients WHERE po_id = '[po_id]' ORDER BY display_name;

SELECT channel_name, client_id, scope, priority
FROM slack_channels WHERE po_id = '[po_id]' ORDER BY scope, priority;

SELECT briefing_lead_minutes, time_window_days, notification_slack_user_id
FROM po_preferences WHERE po_id = '[po_id]';
```

Present as a friendly summary:
> "Tu configuración actual:
> - ⏱ Briefing **[N] minutos** antes de cada reunión
> - 📅 Consulto los últimos **[N] días** de historial
> - 👤 Te notifico en Slack como **[user]**
>
> Clientes configurados:
> - **Acme Inc**: @acme.com · #proyecto-acme · keywords: ACME
> - **Bancolombia**: @bancolombia.com · #banca-ops
>
> Canales globales: #alertas-prod, #dev-general"

---

### ADD CLIENT

Trigger: "agregar cliente [nombre]", "nuevo cliente"

Follow `references/add-client-guide.md`.

---

### EDIT CLIENT

Trigger: "cambiar los canales de [cliente]", "agregar dominio [x] a [cliente]"

Ask which field to change, then:

```sql
UPDATE clients
SET
  email_domains     = ARRAY[/* new domains */],     -- only if changing
  calendar_keywords = ARRAY[/* new keywords */],    -- only if changing
  display_name      = '[name]'                      -- only if changing
WHERE po_id = '[po_id]' AND client_id = '[client_id]';
```

---

### DELETE CLIENT

Trigger: "borrar cliente [nombre]", "ya no trabajo con [cliente]"

Always confirm:
> "¿Confirmás que querés borrar **[display_name]**? Se eliminan también sus canales configurados."

```sql
DELETE FROM slack_channels WHERE po_id = '[po_id]' AND client_id = '[client_id]';
DELETE FROM clients WHERE po_id = '[po_id]' AND client_id = '[client_id]';
```

---

### ADD CHANNEL

Trigger: "agregar el canal [nombre]", "monitorear [canal]"

Ask if unclear:
- "¿Este canal es de un cliente específico o es un canal general del equipo?"
- If client: "¿Para cuál cliente?"
- "¿Prioridad alta, normal o baja?"

Resolve channel ID via Slack MCP if only name given.

```sql
INSERT INTO slack_channels (po_id, channel_id, channel_name, client_id, scope, priority)
VALUES ('[po_id]', '[channel_id]', '[channel_name]', '[client_id_or_null]', '[scope]', [priority])
ON CONFLICT (po_id, channel_id) DO UPDATE SET
  client_id = EXCLUDED.client_id,
  scope     = EXCLUDED.scope,
  priority  = EXCLUDED.priority;
```

---

### REMOVE CHANNEL

Trigger: "sacar el canal [nombre]", "dejar de monitorear [canal]"

```sql
DELETE FROM slack_channels
WHERE po_id = '[po_id]' AND channel_name = '[channel_name]';
```

---

### UPDATE PREFERENCES

Trigger: "cambiar a [N] minutos antes", "quiero [N] días de historial", "cambiar mi usuario de Slack"

```sql
UPDATE po_preferences
SET
  briefing_lead_minutes      = [N],            -- only if changing
  time_window_days           = [N],            -- only if changing
  notification_slack_user_id = '[slack_user]', -- only if changing
  updated_at                 = now()
WHERE po_id = '[po_id]';
```

**On `time_window_days` change**, explain the tradeoff:
> "Listo. Con [N] días voy a revisar [N] días hacia atrás en emails, Slack y transcripciones cada vez que preparo un briefing. Más días = más contexto, pero el briefing puede tardar unos segundos más en prepararse."

---

## Always confirm after any change

Show the updated value. Build confidence for non-technical users who can't verify the DB themselves.
