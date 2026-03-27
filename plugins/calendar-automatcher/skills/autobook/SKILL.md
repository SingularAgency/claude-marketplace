---
name: autobook
description: >
  Finds the first available 30-minute slot where PM, PO, and Talent are all free,
  proposes it to the user, and creates the Google Calendar event upon confirmation.
  Supports flexible natural language scheduling: next 48 hours, a specific day,
  next week, this Friday, etc.
  Trigger when the user says: "agendar sync", "agenda la reunión", "busca disponibilidad",
  "busca un espacio", "encuentra un hueco", "agéndanos", "automatcher", "schedule the meeting",
  "find a slot", "book the meeting", "quiero agendar", "lanza el automatcher",
  "busca la próxima semana", "agenda el lunes", "busca el viernes", "quiero agendar el martes",
  "agenda para [día/fecha]", or any variant mentioning scheduling with a day or time reference.
tools:
  - Bash
  - Read
  - gcal_find_meeting_times
  - gcal_list_events
  - gcal_create_event
---

# Calendar Automatcher — Autobook

Find the earliest shared 30-minute availability for the three participants within the requested time window and book it after user confirmation.

## Step 1: Read Configuration

Read `~/.calendar-automatcher-config.json` using Bash:

```bash
cat ~/.calendar-automatcher-config.json
```

If the file does not exist, stop and tell the user:
> "Primero necesito saber quiénes son los participantes. Di **'setup'** para configurar el plugin en 30 segundos."

Parse the following fields:
- `participants.pm`, `participants.po`, `participants.talent` — the three emails
- `timezone` → `America/Guatemala` (UTC-6)
- `working_hours.start` → 8, `working_hours.end` → 17
- `buffer_hours` → 2
- `meeting_duration_minutes` → 30
- `meeting_title` → "Sync Táctica: PM + PO + Talento"

---

## Step 2: Parse the Requested Time Window

Interpret the user's intent to determine the search window. The user may say anything from "ASAP" to "next Tuesday" to "between Monday and Wednesday next week." Be flexible.

### Interpreting natural language (Guatemala time, UTC-6):

| User says | Search window |
|-----------|--------------|
| Nothing specific / "ASAP" / "lo antes posible" | now + 2h → now + 48h |
| "hoy" / "today" | Start of today's remaining working hours → end of today at 17:00 |
| "mañana" / "tomorrow" | 08:00 → 17:00 tomorrow |
| "el lunes" / "next Monday" / a specific weekday | 08:00 → 17:00 on that day |
| "la próxima semana" / "next week" | Monday 08:00 → Friday 17:00 of next week |
| "esta semana" / "this week" | Now (with buffer) → Friday 17:00 of current week |
| "el [día] de [mes]" / a specific date | 08:00 → 17:00 on that date |
| A date range ("entre lunes y miércoles") | Monday 08:00 → Wednesday 17:00 |

When in doubt, ask: "¿Quieres que busque en las próximas 48 horas o tienes una fecha específica en mente?"

Use Bash + Python to resolve the window into ISO 8601 timestamps:

```bash
python3 -c "
from datetime import datetime, timezone, timedelta
import math

utc_offset = timedelta(hours=-6)
tz_gt = timezone(utc_offset)
now = datetime.now(tz_gt)

# --- Replace this section with the resolved window ---
# Example: ASAP mode (default)
buffer = now + timedelta(hours=2)
mins = buffer.minute
rounded_mins = math.ceil(mins / 15) * 15
if rounded_mins == 60:
    buffer = buffer.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
else:
    buffer = buffer.replace(minute=rounded_mins, second=0, microsecond=0)
search_start = buffer
search_end = now + timedelta(hours=48)
# --- End of window resolution ---

print('START:', search_start.isoformat())
print('END:', search_end.isoformat())
print('NOW:', now.strftime('%A %Y-%m-%d %H:%M GT'))
"
```

Adapt the Python logic to compute `search_start` and `search_end` based on the interpreted window. For specific days, set `search_start` to 08:00 of that day and `search_end` to 17:00 of the last day in range.

**Courtesy buffer rule**: Apply the 2-hour buffer only when the search window starts from "now" (ASAP mode). Do not apply it when the user specifies a future day or date — in that case, start from 08:00 of the requested day.

---

## Step 3: Find Available Meeting Times

Use `gcal_find_meeting_times` with:
- Attendee emails: all three from config
- Duration: 30 minutes
- Time range: `search_start` → `search_end`
- Timezone: `America/Guatemala`

If `gcal_find_meeting_times` is unavailable, fall back to `gcal_list_events` for each participant over the window. Then:
1. Merge all busy periods from all three calendars into one sorted list.
2. Collapse overlapping ranges.
3. Walk the merged list to find gaps ≥ 30 minutes.

---

## Step 4: Filter Slots

Apply these filters to all candidate slots:

1. **Working hours**: slot must start at or after 08:00 GT and end at or before 17:00 GT.
2. **Weekdays only**: exclude Saturday and Sunday.
3. **Courtesy buffer**: only when searching from "now" — slot must start at or after `search_start`.

Collect **up to 5 slots** that pass all filters, sorted chronologically. Do not stop at the first one.

If no valid slots exist within the requested window:
> "No encontré ningún espacio libre de 30 minutos [en el período solicitado] dentro del horario laboral (08:00–17:00 GT). ¿Quieres que busque en otro período?"

---

## Step 5: List Options and Ask the User to Choose

Present all found slots as a numbered list:

> 📅 Encontré **[N] horarios disponibles** para los tres:
>
> 1. Lunes 30 de marzo — 09:00 GT
> 2. Lunes 30 de marzo — 14:30 GT
> 3. Martes 31 de marzo — 08:00 GT
> 4. Martes 31 de marzo — 11:00 GT
> 5. Miércoles 1 de abril — 10:00 GT
>
> ¿Cuál prefieres? (responde con el número)

Wait for the user to pick a number. Accept any of: "1", "el primero", "opción 2", "el del martes", etc. Resolve their answer to a specific slot. Do **not** create the event until they confirm a selection.

---

## Step 6: Create the Event

Upon confirmation, call `gcal_create_event` with:
- **title**: `meeting_title` from config
- **start_time**: confirmed slot start in ISO 8601 with UTC-6 offset (e.g., `2026-03-30T09:00:00-06:00`)
- **end_time**: start + 30 minutes
- **attendees**: all three emails
- **description**: "Reunión táctica coordinada automáticamente por Calendar Automatcher."
- **timezone**: `America/Guatemala`

---

## Step 7: Confirm to the User

> ✅ **¡Listo!** La reunión quedó agendada para el [día] a las [hora] GT.
> Se enviaron invitaciones a [pm], [po] y [talent].

Include the calendar link if returned.

---

## Error Handling Reference

| Situation | Response |
|-----------|----------|
| Config file missing | Prompt user to run `setup` first |
| Ambiguous time window | Ask for clarification before searching |
| No free slots in window | Offer to search a different period |
| Calendar API error | Report the error, suggest checking calendar permissions |
| User cancels | "Entendido, no agendé nada. Avísame cuando quieras intentarlo de nuevo." |
