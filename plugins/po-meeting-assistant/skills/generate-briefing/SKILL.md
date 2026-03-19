---
name: generate-briefing
description: >
  Use this skill when the user says "dame el brief de [cliente]", "prepárame para la reunión",
  "brief de [nombre]", "qué hay pendiente con [cliente]", "resumen antes de la reunión",
  "qué tengo que saber antes de hablar con [cliente]", or any phrase requesting
  a pre-meeting summary. Also triggered automatically every 5 minutes by the scheduled task.
metadata:
  version: "0.2.0"
---

# Generate Briefing Skill

Query all data sources fresh via MCP using the configured time window. No stored messages, no embeddings — everything consulted in real time at briefing moment.

## Mode Detection

- **Automatic**: Triggered by scheduled task → check calendar first, bail early if no meeting
- **Manual**: User requested a briefing → skip calendar check, go straight to data fetching

---

## AUTOMATIC MODE — Calendar Check First (Cheap Path)

### Step A: Working hours check

Before doing anything else, verify the current time is within the active window.

Guatemala time = UTC-6 (no daylight saving time, ever).

Convert current UTC time to Guatemala time: `guatemala_time = now() AT TIME ZONE 'America/Guatemala'`

Active window: **7:50 AM to 5:00 PM Guatemala time (Monday–Friday)**.

```
guatemala_hour   = extract(hour   from now() AT TIME ZONE 'America/Guatemala')
guatemala_minute = extract(minute from now() AT TIME ZONE 'America/Guatemala')
guatemala_dow    = extract(dow    from now() AT TIME ZONE 'America/Guatemala')
-- dow: 0=Sunday, 1=Monday ... 5=Friday, 6=Saturday

time_as_minutes = guatemala_hour * 60 + guatemala_minute
start_minutes   = 7 * 60 + 50   -- 470
end_minutes     = 17 * 60        -- 1020

if guatemala_dow IN (0, 6) → weekend, stop
if time_as_minutes < start_minutes → too early, stop
if time_as_minutes >= end_minutes  → after hours, stop
```

If outside window → stop immediately. Cost: ~100 tokens total.

### Step B: Load PO config

```sql
SELECT po_id, notification_slack_user_id, briefing_lead_minutes, time_window_days
FROM po_preferences
LIMIT 10;
```

If multiple rows exist, identify the right PO from task context.

### Step C: Calendar check

Use Google Calendar MCP `list_events`:
```
time_min = now()
time_max = now() + 60 minutes
```

If **no events** → stop. Done. (~300 tokens total)

### Step D: Match event to client

For each event, query:
```sql
SELECT client_id, display_name
FROM clients
WHERE po_id = '[po_id]'
  AND '[event_title]' ILIKE ANY(
    SELECT '%' || unnest(calendar_keywords) || '%'
  );
```

If **no client matched** → stop.

### Step E: Check lead time window

```
minutes_until = event_start - now()
```

- If `minutes_until > briefing_lead_minutes` → too early, stop
- If `minutes_until < 1` → meeting already started, stop
- If within window → proceed to briefing generation

### Step F: Anti-duplicate check

Key the check on the **calendar event ID + client_id**, not just the client_id.
This prevents blocking a second meeting with the same client later in the day,
while still deduplicating multiple runs within the same 10-minute lead window.

Build the dedup key:
```
briefing_key = '[client_id]__[calendar_event_id]'
```

Google Calendar returns a unique `id` per event (and per occurrence for recurring events).
Extract it from the `list_events` response.

```sql
SELECT updated_at FROM po_preferences
WHERE po_id = '[po_id]'
  AND (metadata->>'last_briefing_key') = '[briefing_key]'
  AND (metadata->>'last_briefing_sent_at')::timestamptz > now() - INTERVAL '20 minutes';
```

If found → skip. Already notified for this specific event occurrence.

Update the flag after sending:
```sql
UPDATE po_preferences
SET metadata = metadata
  || jsonb_build_object(
       'last_briefing_key',     '[briefing_key]',
       'last_briefing_sent_at', now()::text
     ),
  updated_at = now()
WHERE po_id = '[po_id]';
```

---

## BRIEFING GENERATION

### Step 1: Load client config

```sql
SELECT c.client_id, c.display_name, c.email_domains, c.calendar_keywords,
       p.notification_slack_user_id, p.time_window_days
FROM clients c
JOIN po_preferences p ON c.po_id = p.po_id
WHERE c.po_id = '[po_id]' AND c.client_id = '[client_id]';
```

Compute `since_date = now() - INTERVAL '[time_window_days] days'`

### Step 2: Load channel list

```sql
SELECT channel_id, channel_name, scope, priority
FROM slack_channels
WHERE po_id = '[po_id]'
  AND (client_id = '[client_id]' OR scope IN ('global', 'team'))
ORDER BY priority ASC;
```

### Step 3: Fetch data from all sources in parallel

Execute all three fetches. Each is bounded by `time_window_days`.

**3a. Gmail**
For each domain in `email_domains`, call `gmail_search_messages`:
```
query: "(from:*@[domain] OR to:*@[domain]) after:[since_date_YYYY/MM/DD]"
max_results: 10
```
For each result, call `gmail_read_thread` to get the content. Strip signatures, quoted replies, legal footers.

**3b. Slack**
For each channel in the channel list, call Slack MCP `slack_get_channel_history` or equivalent:
```
channel: [channel_id]
oldest:  [since_date as unix timestamp]
limit:   50
```
Filter out messages under 15 words, bot messages, pure emoji reactions.

**3c. Read.ai / Fireflies**
Search for transcripts since `since_date` that include participants from `email_domains`.

Transcript correlation logic (apply in order, stop at first match):
1. **Participant match** → transcript has attendee with email domain in `email_domains` → associate to this client
2. **Title match** → meeting title contains one of `calendar_keywords` → associate to this client
3. **No match** → skip transcript (belongs to another client or is unrelated)

For internal meetings (no client participants, title doesn't match): skip — they don't belong to this client's briefing context. They'll be relevant if the PO runs a briefing for whatever client the meeting was about.

### Step 4: Synthesize

Feed all fetched content to the synthesis prompt. See `references/briefing-format.md` for exact instructions and output template.

Synthesis questions:
1. ¿Qué está pendiente o sin resolver de este cliente?
2. ¿Hubo algún problema, bloqueo o cancelación reciente?
3. ¿Qué pidió el cliente por email en la última semana?
4. ¿Qué discutió el equipo en los canales de Slack?
5. ¿Hay algo en los canales globales (alertas, incidentes) que pueda afectar esta reunión?

If a source returned no data, omit that section silently — don't say "no encontré nada en Slack".

### Step 5: Deliver

**Manual request** → respond in chat with formatted briefing.

**Automatic** → send Slack DM via Slack MCP to `notification_slack_user_id`. Then update the anti-duplicate flag using the same `briefing_key` from Step F:

```sql
UPDATE po_preferences
SET metadata = metadata
  || jsonb_build_object(
       'last_briefing_key',     '[client_id]__[calendar_event_id]',
       'last_briefing_sent_at', now()::text
     ),
  updated_at = now()
WHERE po_id = '[po_id]';
```
