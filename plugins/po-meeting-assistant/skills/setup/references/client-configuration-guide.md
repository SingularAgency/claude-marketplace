# Client Configuration Guide

Use this when guiding the user to configure their first (or any subsequent) client.

## What to ask the user

Ask these questions conversationally, not as a form. One at a time if the user seems uncertain.

1. **Nombre del cliente** — "¿Cómo se llama el cliente?"
   → Used as `display_name` and to generate `client_id` (lowercase slug, no spaces)

2. **Dominio de email** — "¿Cuál es el dominio de su email corporativo? Por ejemplo, si te escriben desde juan@acme.com, el dominio es `acme.com`. Pueden ser varios."
   → Stored as `email_domains[]`

3. **Palabras clave del calendario** — "¿Cómo aparece este cliente en el título de tus reuniones del calendario? Por ejemplo: 'ACME', 'Acme Inc', 'Weekly Acme'. Pueden ser varias."
   → Stored as `calendar_keywords[]`

4. **Canales de Slack del cliente** — "¿En qué canales de Slack hablás de este cliente? Podés decirme los nombres (#proyecto-acme) y yo busco el ID."
   → For each channel name provided, use Slack MCP to resolve the channel ID, then insert into `slack_channels` with `scope = 'client'`

5. **Canales globales** (ask only once during first setup) — "¿Hay canales internos de tu equipo que sean siempre relevantes para cualquier reunión? Por ejemplo #alertas-prod, #dev-general, #arquitectura."
   → Insert these into `slack_channels` with `scope = 'global'`, `client_id = NULL`

## SQL to execute after collecting data

```sql
-- Insert client
INSERT INTO clients (po_id, client_id, display_name, email_domains, calendar_keywords)
VALUES (
  '[po_id]',
  '[slug]',        -- e.g. 'acme'
  '[display_name]', -- e.g. 'Acme Inc'
  ARRAY['[domain1]', '[domain2]'],
  ARRAY['[keyword1]', '[keyword2]']
)
ON CONFLICT (po_id, client_id) DO UPDATE SET
  display_name     = EXCLUDED.display_name,
  email_domains    = EXCLUDED.email_domains,
  calendar_keywords = EXCLUDED.calendar_keywords;

-- Insert client Slack channels
INSERT INTO slack_channels (po_id, channel_id, channel_name, client_id, scope, priority)
VALUES
  ('[po_id]', '[channel_id]', '[channel_name]', '[client_id]', 'client', 2)
ON CONFLICT (po_id, channel_id) DO NOTHING;

-- Insert global Slack channels (if provided)
INSERT INTO slack_channels (po_id, channel_id, channel_name, client_id, scope, priority)
VALUES
  ('[po_id]', '[channel_id]', '[channel_name]', NULL, 'global', 1)
ON CONFLICT (po_id, channel_id) DO NOTHING;

-- Initialize sync state for this client
INSERT INTO sync_state (po_id, source_type, client_id, last_synced_at)
VALUES
  ('[po_id]', 'slack',      '[client_id]', now() - INTERVAL '7 days'),
  ('[po_id]', 'email',      '[client_id]', now() - INTERVAL '7 days'),
  ('[po_id]', 'transcript', '[client_id]', now() - INTERVAL '7 days')
ON CONFLICT DO NOTHING;
```

## After inserting

Confirm to the user:
> "✅ Cliente **[display_name]** configurado. Voy a monitorear:
> - Emails desde: [domains]
> - Canales de Slack: [channel names]
> - Reuniones que incluyan: [keywords] en el título del evento"
