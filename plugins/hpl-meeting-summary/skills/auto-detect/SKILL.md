---
name: auto-detect
description: >
  This skill runs automatically on a schedule every 5 minutes to detect new completed client meetings
  from Read AI and post their summaries to Slack. It should NOT be triggered manually by the user —
  it is called exclusively by the scheduled task. It filters out internal meetings (same company domain),
  skips already-posted meetings, and prevents duplicates by tracking posted meeting IDs.
metadata:
  version: "0.1.0"
  author: "Singular Agency"
---

# Auto-Detect New Client Meetings

This skill runs silently on a schedule. It checks Read AI for newly completed meetings, filters to client-only calls, avoids duplicates, and posts summaries automatically. Do NOT announce or explain what you're doing — just execute the steps and only speak if a summary is actually posted or a critical error occurs.

---

## Step 1 — Load config

Read `~/.read-ai-summary-config.json` using Bash.

Extract:
- `default_channel` — where to post
- `auto_post` — if false, skip posting silently (user prefers manual triggering)
- `internal_domain` — e.g. `singularagency.co` (default if not set)
- `posted_meeting_ids` — array of meeting IDs already posted (deduplication list)
- `setup_complete` — if not true, do nothing and exit silently

**If `setup_complete` is not true, or `default_channel` is not set, or `auto_post` is false**: exit silently. Do not post anything, do not say anything to the user.

---

## Step 2 — Fetch recent meetings

Call `list_meetings` with:
```
limit: 10
start_datetime_gte: <2 hours ago in ISO 8601>
expand: ["summary", "action_items", "key_questions", "topics", "chapter_summaries"]
```

To compute "2 hours ago": use `date -u -d '2 hours ago' '+%Y-%m-%dT%H:%M:%SZ'` via Bash.

---

## Step 3 — Filter: skip internal-only meetings

For each meeting in the response, examine `participants[]`.

**A meeting is "internal"** if ALL participants have an email ending in the `internal_domain` from config (e.g., all end in `@singularagency.co`).

**A meeting is a "client meeting"** if at least ONE participant has a different email domain.

Skip all internal meetings silently. Only continue with client meetings.

---

## Step 4 — Filter: skip already-posted meetings

For each remaining meeting, check if `meeting.id` exists in `posted_meeting_ids` from config.

If it does → skip silently.
If it does not → this is a new, unposted client meeting. Continue to Step 5.

---

## Step 5 — Check meeting is complete enough to summarize

Only post summaries for meetings that have a non-empty `summary` field. A meeting that just ended may not have been processed by Read AI yet.

If `summary` is null or empty string → skip this meeting silently for now. It will be retried on the next 5-minute cycle.

---

## Step 6 — Generate summary and post to Slack

For each valid new meeting:

**6a. Identify Project Name and Client Name**

- **Client Name**: The name of the external participant (different domain). If multiple external participants, use the company name inferred from their email domain (e.g., `viapromeds.com` → `ViaproMeds`). Use the participant's full name if only one external person.
- **Project Name**: Infer from the meeting `title` or `folders[]`. If ambiguous, use the external company name.

**Headline**: `ProjectName — ClientName`

**6b. Detect technology type and accountable team member**

Read `role_assignments` from config. Search the meeting's `title`, `topics[]`, `summary`, and `chapter_summaries[]` for keyword matches against each category's `keywords` array (case-insensitive).

Collect all matching `user_ids` across matched categories. If multiple tech types match, include all accountables with their category label.

**6c. Generate summary body**

Compose the full breakdown using the meeting data. Use the client meeting format:

```
<@USER_ID> <@USER_ID2>

📋 *Call Breakdown — [ClientName]*

[One concise paragraph: who the client is, what they're building or doing, what they need, key constraints or context.]

*Core Direction:*
• [Key topic 1 — from topics[] or summary]
• [Key topic 2]
• [Key topic 3]

*What Was Discussed:*
• [Chapter title]: [1-sentence recap — from chapter_summaries[]]
• [Chapter title]: [1-sentence recap]
• [Chapter title]: [1-sentence recap]

🔴 *Action Items*
• [Assignee first name]: [task — from action_items[]]
• [Assignee first name]: [task]

🔴 *Next Steps / Timeline*
• [Any date-specific follow-up inferred from action_items or summary]

🔗 Full report: [report_url]
```

If no tech type matched, omit the tag line entirely.

**6c. Post parent message (headline)**

Call `slack_send_message`:
- `channel_id`: `default_channel` from config
- `text`: the headline — `ProjectName — ClientName`

If `mention_users` is non-empty, prepend: `<@USER_ID> | ProjectName — ClientName`

Capture `ts` from the response.

**6d. Post summary as thread reply**

Call `slack_send_message`:
- `channel_id`: same channel
- `thread_ts`: the `ts` from step 6c
- `text`: the full summary body

---

## Step 7 — Update posted meeting IDs (prevent duplicates)

After successfully posting both messages, add `meeting.id` to the `posted_meeting_ids` array in config.

Read the current config, append the new ID, and write back:

```bash
python3 -c "
import json, sys
with open('$HOME/.read-ai-summary-config.json', 'r') as f:
    config = json.load(f)
config.setdefault('posted_meeting_ids', []).append('<MEETING_ID>')
with open('$HOME/.read-ai-summary-config.json', 'w') as f:
    json.dump(config, f, indent=2)
"
```

Replace `<MEETING_ID>` with the actual meeting ID string.

---

## Step 8 — Silent exit or brief confirmation

If no new meetings were found or posted: exit silently. Do not say anything to the user.

If a summary was posted: tell the user briefly:
"📋 Posted a summary for *ProjectName — ClientName* to <#channel-name>. Check the thread for the full breakdown."

If posting failed (Slack error, Read AI error): log the error briefly without alarming the user:
"⚠️ Tried to post the meeting summary for *[title]* but hit an error: [short error]. I'll retry next cycle."
