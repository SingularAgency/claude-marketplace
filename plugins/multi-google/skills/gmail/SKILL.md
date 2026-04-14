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
  version: "0.6.0"
---

## IMPORTANT: Use VM Bash tool for ALL commands — NO Desktop Commander needed.

## Step 1 — Verify setup

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/list_accounts.py"
```

If this fails → tell user: "Necesitas configurar el plugin primero. Di 'configurar multi-google'."

If no account specified and multiple exist, ask which one to use. With a single account, use it automatically.

## Commands

### Search emails
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gmail.py" <alias> search "<query>" [max]
```
Query syntax: `from:x@y.com`, `is:unread`, `newer_than:7d`, `subject:x`, `has:attachment`, `in:inbox`

Returns: `{id, from, to, subject, date, snippet, labels}`

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
