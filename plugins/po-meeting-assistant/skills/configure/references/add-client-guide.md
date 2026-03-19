# Add Client Guide

Follow this sequence when a user wants to add a new client.

## Questions to ask (conversationally, one at a time)

1. **"¿Cómo se llama el cliente?"**
   → `display_name` = answer as-is (e.g. "Bancolombia")
   → `client_id`    = slugify: lowercase, spaces → hyphens (e.g. "bancolombia")

2. **"¿Cuál es el dominio de su email corporativo? Por ejemplo, si te escriben desde juan@acme.com, el dominio es `acme.com`. Si tienen varios dominios, decímelos todos."**
   → `email_domains[]`

3. **"¿Cómo aparece este cliente en el título de tus reuniones del calendario? Puede ser el nombre completo, una sigla, o una combinación. Ejemplo: 'ACME', 'Acme Inc', 'Weekly Acme'."**
   → `calendar_keywords[]`

4. **"¿En qué canales de Slack hablás de este cliente? Podés decirme los nombres con el # adelante."**
   → For each channel name: resolve ID using Slack MCP → `slack_channels` with `scope = 'client'`
   → Ask priority: "¿Alguno de estos canales es más importante que los otros, o todos igual?"

5. **"¿Hay algún canal global del equipo que todavía no hayas configurado?"** (only ask if `slack_channels` with `scope IN ('global','team')` returns 0 rows for this PO)
   → If yes: add them with `scope = 'global'` or `scope = 'team'`

## SQL to run after collecting all data

```sql
-- 1. Insert the client
INSERT INTO clients (po_id, client_id, display_name, email_domains, calendar_keywords)
VALUES (
  '[po_id]',
  '[client_id]',
  '[display_name]',
  ARRAY[/* domains */],
  ARRAY[/* keywords */]
)
ON CONFLICT (po_id, client_id) DO UPDATE SET
  display_name      = EXCLUDED.display_name,
  email_domains     = EXCLUDED.email_domains,
  calendar_keywords = EXCLUDED.calendar_keywords;

-- 2. Insert client Slack channels
INSERT INTO slack_channels (po_id, channel_id, channel_name, client_id, scope, priority)
VALUES /* one row per channel */
ON CONFLICT (po_id, channel_id) DO NOTHING;

-- 3. Initialize sync state (start from 7 days ago to get recent history)
INSERT INTO sync_state (po_id, source_type, client_id, last_synced_at)
VALUES
  ('[po_id]', 'slack',      '[client_id]', now() - INTERVAL '7 days'),
  ('[po_id]', 'email',      '[client_id]', now() - INTERVAL '7 days'),
  ('[po_id]', 'transcript', '[client_id]', now() - INTERVAL '7 days')
ON CONFLICT DO NOTHING;
```

## Confirmation message to show user

> "✅ **[display_name]** agregado correctamente. Voy a monitorear:
> - 📧 Emails desde/hacia: [domains joined with ', ']
> - 💬 Canales de Slack: [channel_names joined with ', ']
> - 📅 Reuniones con: [keywords joined with ', '] en el título
>
> ¿Querés que haga una sincronización inicial ahora para traer los últimos 7 días de contexto?"

If user says yes → trigger sync-memory skill with scope = '[client_id]'
