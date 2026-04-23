---
name: auto-detect
description: >
  This skill runs automatically on a schedule every hour to detect new completed
  client meetings from Read AI and trigger the meeting-analyst agent for each one.
  The agent runs all three analyses (Summary, ICP Qualification, Marketing Feedback)
  and posts each independently to Slack. This skill should NOT be triggered manually —
  it is called exclusively by the scheduled task.
metadata:
  version: "0.2.0"
  author: "Singular Agency"
---

# Auto-Detect New Client Meetings

This skill runs silently on a schedule. It detects newly completed client meetings in Read AI, filters out internal-only calls and already-processed ones, then delegates each new meeting to the `meeting-analyst` agent which handles all three analyses.

Do NOT announce or explain what you're doing. Only speak if a meeting is processed or a critical error occurs.

---

## Step 1 — Load config

Read `~/mnt/.read-ai-summary-config.json` using Bash.

Extract:
- `setup_complete` — must be `true` to proceed
- `auto_post` — must be `true` to proceed
- `internal_domain` — default `singularagency.co`
- `agent_processed_meeting_ids` — meetings already handled by the agent
- `default_channel` — must exist

**If any of these conditions fail** → exit silently. Do nothing.

---

## Step 2 — Fetch recent meetings

Call `list_meetings` with:
```
limit: 10
start_datetime_gte: <1 hour ago in ISO 8601>
expand: ["summary", "action_items", "key_questions", "topics", "chapter_summaries"]
```

Compute "1 hour ago" via Bash:
```bash
date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%SZ'
```

---

## Step 3 — Filter: skip internal-only meetings

For each meeting, check `participants[]`. A meeting is **internal** if ALL participants share `internal_domain`. Skip internal meetings silently.

---

## Step 4 — Filter: skip already-processed meetings

For each remaining meeting:

**Layer 1 — Check `agent_processed_meeting_ids`** (fast path):
If `meeting.id` is present → skip silently.

**Layer 2 — Search Slack** (catch meetings processed by individual skills or manual runs):
If not in the list, search Slack for prior posts.

Infer `ClientName` from the external participant's name or email domain.

Call `slack_search_public_and_private` with: `"Call Breakdown" "[ClientName]"`
Also try: `"ICP Qualification" "[ClientName]"`

If either search returns a match referencing this client → write `meeting.id` to `agent_processed_meeting_ids` and skip.

---

## Step 5 — Check meeting has enough data

Only process meetings with a non-empty `summary`. If `summary` is null or empty → skip silently and retry next cycle.

---

## Step 6 — Delegate to meeting-analyst agent

For each valid new meeting, pass the meeting data to the `meeting-analyst` agent defined in `agents/meeting-analyst.md`.

Provide the agent with:
- `meeting_id` — the meeting's `id` field
- All expanded meeting data already fetched (pass through — do not re-fetch)

The agent handles:
1. Strategic Summary → post to Slack
2. ICP Qualification (including web research) → post to Slack
3. Marketing Feedback → post to Slack
4. Updating all tracking fields in config

---

## Step 7 — Exit

If no new meetings were found or processed → exit silently.

If a meeting was processed → confirm briefly:
"✅ Full analysis posted for *ProjectName — ClientName*: Summary, ICP, and Marketing Feedback."

If an error occurred → log briefly:
"⚠️ Error processing *[title]*: [short message]. Will retry next cycle."
