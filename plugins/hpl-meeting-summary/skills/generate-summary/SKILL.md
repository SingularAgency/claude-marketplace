---
name: generate-summary
description: >
  Use this skill when the user says "summarize my last meeting", "post the meeting summary",
  "generate a call breakdown", "brief the team on the call", "post the Read AI summary to Slack",
  "share the meeting recap", "generate a summary for [client name]", "post the breakdown for [project]",
  or any phrase requesting a structured post-meeting summary from a Read AI call.
metadata:
  version: "0.1.0"
  author: "Singular Agency"
---

# Generate Meeting Summary

Fetch a meeting from Read AI, generate a structured summary, and post it to Slack — with the headline as the parent message and the full breakdown as a thread reply.

---

## Step 0 — First-run check

Read `~/mnt/.claude/.read-ai-summary-config.json` using Bash.

If the file does not exist OR `setup_complete` is not `true`:
→ Tell the user: "It looks like this is your first time using the meeting summary plugin. Let me run the setup first."
→ Run the `setup` skill flow completely before continuing here.

---

## Step 1 — Fetch meetings from Read AI

Call `list_meetings` with:
```
limit: 5
expand: ["summary", "action_items", "key_questions", "topics", "chapter_summaries"]
```

Each meeting returns:
- `id`, `title`, `start_time_ms`, `end_time_ms`
- `participants[]` — name, email, attended boolean
- `owner` — name, email
- `report_url` — direct link to the Read AI report
- `folders[]` — tags like "Sales Strategy", "One-on-One"
- `platform` — meet, zoom, teams
- `summary` — full prose overview
- `chapter_summaries[]` — [{title, description}] per meeting section
- `action_items[]` — follow-up tasks as plain strings
- `key_questions[]` — important questions raised
- `topics[]` — main themes discussed

---

## Step 2 — Select the meeting

If the user named a client or project, find the closest match in the list by title or participant name.

If the user said "last meeting" or nothing specific, use the first item (most recent).

If uncertain (multiple possible matches), show a numbered list of the 5 meetings — title + date formatted as "Mon Mar 23, 3:00 PM" — and ask the user to pick one.

---

## Step 3 — Identify Project Name and Client Name

These two values drive the Slack headline. Derive them as follows:

**Client Name**: The name of the external participant (different email domain from the Singular Agency team). If multiple external participants, use the company name inferred from their email domain (e.g., `viapromeds.com` → `ViaproMeds`). If all participants are internal (singularagency.co), use the meeting title instead.

**Project Name**: Look for a project name in:
1. The meeting `title` (e.g., "HPL Pipeline Review" → project = "HPL")
2. The `folders[]` field (e.g., "Sales Strategy")
3. The meeting `summary` (look for phrases like "building X", "project X", "working on X")

If neither can be confidently inferred, ask the user: "What's the project name for this meeting?" — keep it brief (e.g., "Travelog", "ViaproMeds", "Front Line Roofing").

**Headline format**:
```
ProjectName — ClientName
```
Examples:
- `Travelog — Jamie Sandy`
- `ViaproMeds — Marcelo Gandola`
- `HPL Pipeline — Internal Sync`

---

## Step 4 — Detect technology type and accountable team member

Read `role_assignments` from config. Follow the full detection logic in `references/tech-detection.md`.

Search these meeting fields for keyword matches (case-insensitive):
- `title`, `topics[]`, `summary`, `chapter_summaries[].title`, `chapter_summaries[].description`

Match against each category's `keywords` array in `role_assignments`.

**Result**: a list of matched `user_ids` (may be from multiple categories if meeting covers multiple tech types), and their formatted `<@USER_ID>` strings.

If the user explicitly named someone in their request (e.g., "tag William"), override detection and use that person.

---

## Step 5 — Generate the summary body

Use the meeting data to write a **full, detailed strategic brief**. Follow the format and all rules in `references/output-format.md`. The goal is NOT a quick recap — it is a complete picture that someone who wasn't on the call can read and immediately act on.

**Extract the maximum detail available from each field:**
- `summary` — use this for the "Who They Are" and "Context & Current State" sections. Do not paraphrase lazily — pull out all the specific details, tools, systems, and context mentioned.
- `topics[]` — map these to the "Pain Points" and "What Was Discussed" sections.
- `chapter_summaries[]` — use each chapter as a "What Was Discussed" bullet. Write 1–2 sentences per chapter, not just the title.
- `action_items[]` — use verbatim or lightly cleaned up for the Action Items section. Always include the assignee name.
- `key_questions[]` — use for the "Key Questions Raised" section.

**Mandatory for client calls:**
- Fill in EVERY section of the Full Format — do not skip or merge sections.
- Write at least 3 pain points with operational context for each.
- Include direct quotes from the client if they appear in `summary` or `chapter_summaries`.
- Write a clear "Strategic Read" with an honest assessment and recommendation.
- Make action items and timelines specific — include names, dates, and deliverables.

Prepend the tags at the very top of the thread body (only if a match was found):

```
<@USER_ID> <@USER_ID2>

📋 *Call Breakdown — ClientName*
...rest of summary...
```

If multiple tech types matched, list all tags together on one line:
```
<@U_WILLIAM> <@U_FABIAN>
```

The summary body will be posted as a **thread reply** — NOT the main message.

---

## Step 6 — Choose the Slack channel

Resolve the posting channel from config. Use this Python snippet to determine the channel:

```bash
python3 -c "
import json, os
with open(os.path.expanduser('~/mnt/.claude/.read-ai-summary-config.json')) as f:
    c = json.load(f)
ch_id   = c.get('summary_channel')   or c.get('default_channel')
ch_name = c.get('summary_channel_name') or c.get('default_channel_name', '#general')
auto    = c.get('auto_post', False)
print('CH_ID='   + str(ch_id))
print('CH_NAME=' + str(ch_name))
print('AUTO='    + str(auto))
"
```

Priority: `summary_channel` → `default_channel`. If neither is set, ask the user which channel to post to.

- If `AUTO=True` AND channel is known → post immediately without asking.
- If `AUTO=False` → show a preview of both the headline and the summary body (including the accountable tag), confirm the channel, then post.

To confirm: "I'll post this to <#channel-name>. Ready?" Wait for user confirmation unless `auto_post` is on.

---

## Step 7 — Post the parent message to Slack

Call `slack_send_message` with:
- `channel_id`: the selected channel ID
- `text`: the headline only — **`ProjectName — ClientName`**

Capture the `ts` (timestamp) from the response. You will need it for the thread reply.

If `mention_users` is set in config (global tags), prepend them to the headline:
```
<@USER_ID> <@USER_ID2> | ProjectName — ClientName
```

Note: accountable team members (from role_assignments) are tagged in the thread, NOT the headline.

---

## Step 8 — Post the full summary as a thread reply

Call `slack_send_message` again with:
- `channel_id`: same channel
- `thread_ts`: the `ts` value captured in Step 7
- `text`: the full formatted summary body including the accountable line at the top

This creates a thread under the headline message. The channel feed stays clean — just showing `ProjectName — ClientName` — while the full breakdown and the tagged accountable are in the thread.

---

## Step 9 — Update posted meeting IDs (prevent duplicates)

After both Slack messages are successfully posted, add the meeting ID to `posted_meeting_ids` in the config so the auto-detect scheduled task doesn't post it again.

```bash
python3 -c "
import json, os
with open(os.path.expanduser('~/mnt/.claude/.read-ai-summary-config.json'), 'r') as f:
    config = json.load(f)
config.setdefault('posted_meeting_ids', []).append('<MEETING_ID>')
with open(os.path.expanduser('~/mnt/.claude/.read-ai-summary-config.json'), 'w') as f:
    json.dump(config, f, indent=2)
"
```

Replace `<MEETING_ID>` with the actual `id` field from the meeting data.

---

## Step 10 — Confirm and share links

After both posts succeed, tell the user:

"✅ Posted to <#channel-name>
- Headline: *ProjectName — ClientName*
- Full breakdown + accountable tag in the thread

📎 Read AI report: [report_url]"
