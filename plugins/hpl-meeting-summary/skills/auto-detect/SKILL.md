---
name: auto-detect
description: >
  This skill runs automatically on a schedule every hour to detect new completed
  client meetings from Read AI and trigger the meeting-analyst agent for each one.
  The agent runs all three analyses (Summary, ICP Qualification, Marketing Feedback)
  and posts each independently to Slack. This skill should NOT be triggered manually —
  it is called exclusively by the scheduled task.
metadata:
  version: "0.3.0"
  author: "Singular Agency"
---

# Auto-Detect New Client Meetings

Runs silently on a schedule. Detects newly completed client meetings, applies a multi-layer deduplication check to guarantee no meeting is posted more than once across any analysis, then delegates to the `meeting-analyst` agent.

Do NOT announce or explain what you're doing. Only speak if a meeting is processed or a critical error occurs.

---

## Step 1 — Concurrency lock (prevent overlapping runs)

Before doing anything else, check for a lock file:

```bash
python3 -c "
import os, time
lock = os.path.expanduser('~/.hpl-meeting-analyst.lock')
if os.path.exists(lock):
    age = time.time() - os.path.getmtime(lock)
    # Stale lock (older than 90 min) — remove and proceed
    if age > 5400:
        os.remove(lock)
        print('STALE_LOCK_REMOVED')
    else:
        print('LOCKED')
else:
    # Acquire lock
    open(lock, 'w').write(str(os.getpid()))
    print('ACQUIRED')
"
```

- `LOCKED` → exit silently. Another run is in progress.
- `STALE_LOCK_REMOVED` or `ACQUIRED` → continue.

The lock is released at the very end of Step 7, regardless of outcome.

---

## Step 2 — Load config

Read `~/mnt/.claude/.read-ai-summary-config.json` using Bash.

Extract:
- `setup_complete` — must be `true`
- `auto_post` — must be `true`
- `internal_domain` — default `singularagency.co`
- `default_channel` — must exist
- All four tracking arrays:
  - `agent_processed_meeting_ids`
  - `posted_meeting_ids`
  - `icp_posted_meeting_ids`
  - `marketing_posted_meeting_ids`

**If `setup_complete` is not `true`, `auto_post` is not `true`, or no channel is set** → release lock and exit silently.

---

## Step 3 — Fetch recent meetings

Call `list_meetings` with:
```
limit: 10
start_datetime_gte: <1 hour ago in ISO 8601>
expand: ["summary", "action_items", "key_questions", "topics", "chapter_summaries"]
```

Compute "1 hour ago":
```bash
date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%SZ'
```

---

## Step 4 — Filter: skip internal-only meetings

For each meeting, check `participants[]`. If ALL participants share `internal_domain` → skip silently.

---

## Step 5 — Multi-layer deduplication per meeting

For each remaining (external) meeting, run this dedup sequence. A meeting advances to the agent only if it passes all layers.

### Layer 1 — Local tracking (fast, no network)

```bash
python3 -c "
import json, os, sys
meeting_id = sys.argv[1]
path = os.path.expanduser('~/mnt/.claude/.read-ai-summary-config.json')
with open(path) as f:
    c = json.load(f)

agent_done  = meeting_id in c.get('agent_processed_meeting_ids', [])
summary_done = meeting_id in c.get('posted_meeting_ids', [])
icp_done    = meeting_id in c.get('icp_posted_meeting_ids', [])
mktg_done   = meeting_id in c.get('marketing_posted_meeting_ids', [])
all_done    = summary_done and icp_done and mktg_done

print(f'AGENT={agent_done}')
print(f'SUMMARY={summary_done}')
print(f'ICP={icp_done}')
print(f'MARKETING={mktg_done}')
print(f'ALL_DONE={all_done}')
" '<MEETING_ID>'
```

**Decision table:**

| Condition | Action |
|-----------|--------|
| `AGENT=True` | Skip meeting entirely — agent already ran all three |
| `ALL_DONE=True` | All three individual analyses already posted (manual runs). Write to `agent_processed_meeting_ids` and skip |
| `SUMMARY=True AND ICP=True AND MARKETING=True` | Same as above |
| Any combination of partial completion | Pass to agent — agent will skip the already-done analyses and only run the missing ones |
| All `False` | Genuinely new meeting — continue to Layer 2 |

### Layer 2 — Slack search (catch posts made outside this plugin)

Only run if the meeting was NOT found in any local tracking field (all False from Layer 1).

Infer `ClientName` and `MeetingDate` (format: "Mon Apr 14") from meeting data.

Run two searches:
```
slack_search_public_and_private: "Call Breakdown" "[ClientName]"
slack_search_public_and_private: "ICP Qualification" "[ClientName]"
```

For each result: check if the message timestamp falls within ±24 hours of `meeting.start_time_ms`. A name match alone is not enough — it must be temporally plausible for this specific meeting.

**If a match is found for ALL three analyses** → mark as fully processed: write to `agent_processed_meeting_ids` and skip.

**If a match is found for SOME analyses** → write those meeting IDs to the relevant individual tracking fields, then pass to agent (agent will skip the already-posted ones).

**If no matches** → pass to agent as genuinely new.

### Layer 3 — Summary presence check

Only process meetings with a non-empty `summary` field. If `summary` is null or empty → skip silently. Read AI hasn't finished processing yet; it will be retried on the next hourly run.

---

## Step 6 — Delegate to meeting-analyst agent

For each meeting that passed all dedup layers, pass to the `meeting-analyst` agent with:
- `meeting_id`
- All expanded meeting data (pass through — do not re-fetch)
- The per-analysis completion flags from Layer 1 so the agent knows which analyses to skip

The agent handles running whichever analyses are still pending and writes all tracking fields immediately after each successful post.

---

## Step 7 — Release lock and exit

Always release the lock at the end, regardless of outcome:

```bash
python3 -c "
import os
lock = os.path.expanduser('~/.hpl-meeting-analyst.lock')
if os.path.exists(lock):
    os.remove(lock)
"
```

If no new meetings were found or processed → exit silently.

If meetings were processed → confirm briefly:
"✅ Full analysis posted for *[N] meeting(s)*."

If an error occurred → log briefly and release lock:
"⚠️ Error during auto-detect: [short message]. Lock released."
