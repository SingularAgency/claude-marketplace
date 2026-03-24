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

Apply **two layers** of duplicate detection for each remaining meeting:

**Layer 1 — Check local config (fast path):**
Check if `meeting.id` exists in `posted_meeting_ids` from config.
If it does → skip silently. Do not proceed to Layer 2.

**Layer 2 — Search Slack channel for existing summaries (catches manually posted summaries):**
If the meeting ID is NOT in `posted_meeting_ids`, it may still have been posted manually by a team member. Before posting, search Slack to verify.

First, infer `ClientName` from participants: the external participant's company name (anyone with a domain different from `internal_domain`). If only one external person, use their full name. If multiple, infer from their email domain (e.g., `viapromeds.com` → `ViaproMeds`).

Call `slack_search_public_and_private` with:
```
"Call Breakdown" "[ClientName]"
```

Also try a second search with the meeting title:
```
"[MeetingTitle]"
```

**Evaluate results:**
- If any message contains `"Call Breakdown"` and references the client name → treat as already posted.
- Immediately add `meeting.id` to `posted_meeting_ids` in config (same write-back as Step 7) so it won't be rechecked next cycle.
- Skip silently.

**If no matching message is found** → this is a genuinely new, unposted client meeting. Continue to Step 5.

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

Compose a **full, detailed strategic brief** using the meeting data. This is NOT a quick recap — it must give someone who wasn't on the call a complete picture. Extract the maximum detail from all available fields: `summary`, `topics[]`, `chapter_summaries[]`, `action_items[]`, and `key_questions[]`.

Use this format:

```
<@USER_ID> <@USER_ID2>

📋 *Call Breakdown — [ClientName]*

*Who They Are*
[2–4 sentences: who the client is, what their business does, their role, their technical sophistication, and relevant context about where they are in their journey. Be specific.]

*Context & Current State*
[2–4 sentences: what tools or systems they currently use, what their workflow looks like today, and what is NOT working. Name specific tools and platforms.]

*Pain Points*
[Number each pain point. Include a direct quote if available, plus 1–2 sentences on the operational impact. Minimum 3 pain points.]

1. [Pain point title]
"[Direct quote if available]"
[Operational impact]

2. [Pain point title]
"[Direct quote if available]"
[Operational impact]

3. [Pain point title]
[Explanation]

*What Was Discussed*
[One full sentence per chapter/topic — not just titles. Capture what was actually said, decided, or explored.]

• [Topic]: [What was covered and what was decided or left open]
• [Topic]: [What was covered and what was decided or left open]

*Key Questions Raised*
[Open questions, blockers, or unresolved items that still need answers.]

• [Question or blocker]

*Options / Directions Considered*
[Only include if multiple approaches or scopes were discussed.]

Option A — [Name]: [What it is, why it works, any risk]
Option B — [Name]: [What it is, why it works, any risk]

*Strategic Read*
[1–3 sentences: honest read on this client — urgency, fit, what will win them, what could lose them. Make a clear recommendation.]

🔴 *Action Items*
• [Assignee first name]: [specific task — no vague items]
• [Assignee first name]: [specific task with deadline if mentioned]

🔴 *Next Steps / Timeline*
• [Specific date or event]: [what happens, what is due]
• [Specific date or event]: [follow-up or milestone]

🔗 Full report: [report_url]
```

If no tech type matched, omit the tag line at the top. Never write just one paragraph — all sections are required for client calls.

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
