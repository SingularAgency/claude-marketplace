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
  version: "0.9.0"
---

## IMPORTANT: Use VM Bash tool for ALL commands — NO Desktop Commander needed.

## Step 0 — Auto-bootstrap (run FIRST, every time)

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
PLUGIN_SCRIPTS=$(find /sessions/*/mnt/.remote-plugins/*/scripts -name "setup_oauth.py" 2>/dev/null | head -1 | xargs -I{} dirname {})

if [ ! -f "$MNT/.multi-google/scripts/auth.py" ]; then
  mkdir -p "$MNT/.multi-google/scripts" "$MNT/.multi-google/accounts"
  cp "$PLUGIN_SCRIPTS"/*.py "$MNT/.multi-google/scripts/"
fi

# Pre-install Google packages silently (handles pypi.org-blocked networks gracefully)
pip install -q google-auth google-auth-oauthlib google-api-python-client --break-system-packages 2>/dev/null || true

if [ ! -f "$MNT/.multi-google/oauth.json" ]; then
  python3 "$MNT/.multi-google/scripts/setup_oauth.py"
fi
```

If no accounts exist after bootstrap → tell user: "Primero agrega una cuenta. Di 'agregar cuenta de Google'."

## Step 1 — Verify accounts

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/list_accounts.py"
```

If no account specified and multiple exist, ask which one to use. With a single account, use it automatically.

## Commands

### List upcoming events
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gcalendar.py" <alias> list [days_ahead] [days_behind]
```
Default: next 7 days + yesterday. Fields: `id, title, start, end, location, attendees, organizer, my_status, meet_link, is_all_day, recurring`

### Search events
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gcalendar.py" <alias> search "<query>"
```

### Get event
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gcalendar.py" <alias> get <event_id>
```

### Create event
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gcalendar.py" <alias> create "<title>" "<start_iso>" "<end_iso>" ["<attendees_csv>"] ["<description>"] ["<location>"]
```
Date format: `2026-04-01T14:00:00`. Confirm with user before creating.

### Update event
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gcalendar.py" <alias> update <event_id> ["<title>"] ["<start_iso>"] ["<end_iso>"] ["<description>"] ["<location>"]
```
Use `""` for fields you don't want to change. Confirm before updating.

### Delete event
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gcalendar.py" <alias> delete <event_id>
```
Confirm before deleting.

### RSVP
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gcalendar.py" <alias> rsvp <event_id> <accept|decline|tentative>
```

### Find free slots
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gcalendar.py" <alias> free_slots <date_iso> [duration_minutes]
```

### List calendars
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gcalendar.py" <alias> calendars
```

## Guidelines
- For pending invites: use `list` and filter `my_status: needsAction`
- For "find a time": use `free_slots`, then offer options
- Always show `meet_link` when present
- Confirm before creating, updating, or deleting events
