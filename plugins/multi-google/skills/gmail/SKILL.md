---
name: gmail
description: >
  Use this skill for any Gmail action across connected accounts: searching emails,
  reading email content, sending new emails, replying, forwarding, archiving, trashing,
  labeling, or marking as read. Triggered by phrases like "search my emails for [topic]",
  "find emails from [person]", "read this email", "send an email to [person]",
  "reply to [name]", "forward this to [email]", "archive this email", "trash this",
  "label this as [label]", "mark as read", "show my unread emails",
  "find all emails about [project]", "buscar emails de [persona]",
  "mandar un email a [persona]", or any request to act on Gmail.
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

### Search emails
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gmail.py" <alias> search "<query>" [max]
```
Query syntax: `from:x@y.com`, `is:unread`, `newer_than:7d`, `subject:x`, `has:attachment`, `in:inbox`

### Read full email
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gmail.py" <alias> read <message_id>
```

### Send new email
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gmail.py" <alias> send "<to>" "<subject>" "<body>"
```
**Always confirm with user before sending — show to, subject, body.**

### Reply
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gmail.py" <alias> reply <message_id> "<body>"
```
**Always confirm before sending.**

### Forward
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gmail.py" <alias> forward <message_id> "<to>" ["<note>"]
```

### Archive / Trash / Label / Mark read
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gmail.py" <alias> archive <message_id>
python3 "$MNT/.multi-google/scripts/gmail.py" <alias> trash <message_id>
python3 "$MNT/.multi-google/scripts/gmail.py" <alias> label <message_id> "<label>"
python3 "$MNT/.multi-google/scripts/gmail.py" <alias> mark_read <message_id>
```

### Labels / Profile
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gmail.py" <alias> labels
python3 "$MNT/.multi-google/scripts/gmail.py" <alias> profile
```

## Guidelines
- Always search first to get IDs before reading or acting
- Always confirm before send/reply/forward
- IDs are ephemeral — search fresh each session
