---
name: calendar
description: >
  Use this skill for any Google Calendar action: viewing upcoming events, searching events,
  creating new events, updating or deleting existing events, RSVPing to invitations,
  finding free time slots, or listing calendars. Triggered by phrases like:
  "what's on my calendar", "qué tengo en el calendario", "show my schedule",
  "create a meeting with [person]", "agendar una reunión con [persona]",
  "schedule [event] on [date]", "what do I have tomorrow", "cancel [meeting]",
  "accept the [meeting] invite", "decline the [event]", "when am I free on [day]",
  "find a slot for a 30 min meeting", "update [meeting] time", "what meetings do I have this week",
  or any request to view, create, modify, or respond to calendar events.
metadata:
  version: "0.6.0"
---

## IMPORTANT: Use Desktop Commander for ALL commands

ALL commands MUST run via Desktop Commander (`mcp__Desktop_Commander__start_process` with `shell: "bash"`). Do NOT use the VM Bash tool. The config and scripts live in the WSL2 environment.

## Step 1 — Verify config (via Desktop Commander)

```bash
python3 -c "import json,os; print(json.load(open(os.path.expanduser('~/.multi-google/config.json')))['scripts_dir'])"
```

If this fails → tell user: "Di 'configurar multi-google' primero."

If no account specified, list accounts:
```bash
python3 ~/.multi-google/scripts/list_accounts.py
```

## Commands (all via Desktop Commander)

### List upcoming events
```bash
python3 ~/.multi-google/scripts/gcalendar.py <alias> list [days_ahead] [days_behind]
```
Default: next 7 days + yesterday. Fields: `id, title, start, end, location, attendees, organizer, my_status, meet_link, is_all_day, recurring`

### Search events
```bash
python3 ~/.multi-google/scripts/gcalendar.py <alias> search "<query>"
```

### Get event
```bash
python3 ~/.multi-google/scripts/gcalendar.py <alias> get <event_id>
```

### Create event
```bash
python3 ~/.multi-google/scripts/gcalendar.py <alias> create "<title>" "<start_iso>" "<end_iso>" ["<attendees_csv>"] ["<description>"] ["<location>"]
```
Date format: `2026-04-01T14:00:00`. Confirm with user before creating.

### Update event
```bash
python3 ~/.multi-google/scripts/gcalendar.py <alias> update <event_id> ["<title>"] ["<start_iso>"] ["<end_iso>"] ["<description>"] ["<location>"]
```
Use `""` for fields you don't want to change. Confirm before updating.

### Delete event
```bash
python3 ~/.multi-google/scripts/gcalendar.py <alias> delete <event_id>
```
Confirm before deleting.

### RSVP
```bash
python3 ~/.multi-google/scripts/gcalendar.py <alias> rsvp <event_id> <accept|decline|tentative>
```

### Find free slots
```bash
python3 ~/.multi-google/scripts/gcalendar.py <alias> free_slots <date_iso> [duration_minutes]
```

### List calendars
```bash
python3 ~/.multi-google/scripts/gcalendar.py <alias> calendars
```

## Guidelines
- For pending invites: use `list` and filter `my_status: needsAction`
- For "find a time": use `free_slots`, then offer options
- Always show `meet_link` when present
- Confirm before creating, updating, or deleting events
