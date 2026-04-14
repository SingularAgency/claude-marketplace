---
name: summarize
description: >
  Use this skill when the user wants a high-level catchup or digest across their Google accounts:
  "catch me up", "what did I miss", "give me a full recap", "morning briefing",
  "resumen del día", "qué pasó mientras estuve afuera", "daily digest",
  "summarize everything", "workspace recap", "resumen de mi workspace",
  "what's on my plate today", "qué tengo hoy", "full recap",
  or any phrase requesting an overview of email, calendar, and Drive activity.
metadata:
  version: "0.6.0"
---

## IMPORTANT: Use VM Bash tool for ALL commands — NO Desktop Commander needed.

## Step 1 — Load accounts

```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/list_accounts.py"
```

If this fails → tell user: "Di 'configurar multi-google' primero."

## Step 2 — Time window

Default: last 7 days email/drive, next 7 days + yesterday for calendar.
Honor user intent: "today" = 1d, "last 3 days" = 3d, etc.

## Step 3 — Fetch per account

**Gmail:**
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gmail.py" <alias> search "newer_than:7d -category:promotions -category:social -category:updates" 30
```

**Calendar:**
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/gcalendar.py" <alias> list 7 1
```

**Drive:**
```bash
MNT=$(ls -d /sessions/*/mnt 2>/dev/null | head -1)
python3 "$MNT/.multi-google/scripts/drive.py" <alias> recent 7 20
```

## Step 4 — Filter and deliver

**Gmail**: Discard automated/promo. Classify: ⚡ Action Required / 💬 Conversations / 👀 FYI.
**Calendar**: Skip declined. Highlight `my_status: needsAction`. Group: Today / Tomorrow / This week.
**Drive**: Surface files modified by others (`modified_by_me: false`).

## Output format

---
## 🗂️ Workspace Recap — [Date Range]

### [alias] — [email]

#### 📬 Gmail
**⚡ Action Required** — [Sender]: [Subject] — [one sentence]
**💬 Conversations** — [Sender]: [Subject] — [one sentence]

#### 📅 Calendar
- [Time] — [Event] ([N] people) [🔗 meet link]
- *(needs RSVP)* [Date] — [Event]

#### 📁 Drive
- **[File]** ([type]) — [person] · [time]
---
