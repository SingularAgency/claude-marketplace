---
name: marketing-feedback
description: >
  Use this skill when the user says "analyze my last meeting for marketing feedback",
  "generate marketing insights", "marketing feedback for [client]",
  "what marketing signals came out of [meeting]", "extract marketing feedback from my last call",
  "run the marketing analysis on [meeting]", "get marketing insights from [client]",
  or any phrase requesting marketing feedback from a Read AI meeting.
  Runs independently from generate-summary and icp-qualification — all three can run on the same meeting.
metadata:
  version: "0.1.0"
  author: "Singular Agency"
---

# Generate Marketing Feedback

Fetch a meeting from Read AI, analyze it as a Senior Product Marketing Strategist, and post structured marketing insights to Slack as a parent headline + one thread reply per insight block.

**Read `references/analysis-guide.md` before starting the analysis.**

---

## Step 0 — First-run check

Read `~/mnt/.read-ai-summary-config.json` using Bash.

If the file does not exist OR `setup_complete` is not `true`:
→ Tell the user: "The HPL meeting plugin hasn't been set up yet. Please run the `setup` skill first."
→ Stop.

---

## Step 1 — Fetch meetings from Read AI

Call `list_meetings` with:
```
limit: 5
expand: ["summary", "action_items", "key_questions", "topics", "chapter_summaries"]
```

---

## Step 2 — Select the meeting

If the user named a client or topic → find the closest match by title or participant name.

If the user said "last meeting" or nothing specific → use the first item (most recent).

If ambiguous → show a numbered list (title + date as "Mon Mar 23, 3:00 PM") and ask the user to pick.

---

## Step 3 — Check meeting has enough data

If `summary` is null or empty:
→ Tell the user: "This meeting's summary isn't ready in Read AI yet — it may still be processing. Try again in a few minutes."
→ Stop.

---

## Step 4 — Identify prospect

Find the external participant (email not matching `internal_domain` from config, default `singularagency.co`).

Extract:
- **Lead/Account name** — external participant's full name
- **Company** — inferred from email domain or named in transcript

If all participants share `internal_domain` → there is no external prospect. Use the meeting title as the identifier and note that no external lead was present.

---

## Step 5 — Analyze for marketing feedback

Follow the full analysis guide in `references/analysis-guide.md`.

Search `summary`, `topics[]`, `chapter_summaries[].description`, `key_questions[]`, `action_items[]` for signals about:
- Brand perception and positioning vs. alternatives
- Messaging clarity or confusion
- Competitor mentions (explicit or implied)
- Content gaps and unanswered questions
- ROI, pricing, and value proposition framing

Generate **1–3 insight blocks**, one per distinct signal. Only generate blocks with genuine marketing signal — do not fabricate insights for meetings with no relevant content.

---

## Step 6 — Choose the Slack channel

Resolve the posting channel from config:

```bash
python3 -c "
import json, os
with open(os.path.expanduser('~/mnt/.read-ai-summary-config.json')) as f:
    c = json.load(f)
ch_id   = c.get('marketing_channel')   or c.get('default_channel')
ch_name = c.get('marketing_channel_name') or c.get('default_channel_name', '#general')
auto    = c.get('auto_post', False)
print('CH_ID='   + str(ch_id))
print('CH_NAME=' + str(ch_name))
print('AUTO='    + str(auto))
"
```

Priority: `marketing_channel` → `default_channel`. If neither is set, ask the user which channel to post to.

If `AUTO=True` AND a channel is available → proceed immediately.

If `AUTO=False` → show the user a preview of all insight blocks and ask: "Ready to post [N] insight(s) to <#channel-name>?" Wait for confirmation.

---

## Step 7 — Post parent headline

Call `slack_send_message`:
- `channel_id`: selected channel
- `text`: `📊 Marketing Insights — [ClientName] · [Meeting Title]`

Capture `ts` from the response.

---

## Step 8 — Post each insight block as a thread reply

For each insight block, call `slack_send_message`:
- `channel_id`: same channel
- `thread_ts`: `ts` from Step 7
- `text`: the formatted insight block (format from `references/analysis-guide.md`)

Each block is its own reply. Do not combine them.

---

## Step 9 — Mark as processed

Append the meeting ID to `marketing_posted_meeting_ids` in config (separate from `posted_meeting_ids` and `icp_posted_meeting_ids`):

```bash
python3 -c "
import json, os
with open(os.path.expanduser('~/mnt/.read-ai-summary-config.json'), 'r') as f:
    config = json.load(f)
config.setdefault('marketing_posted_meeting_ids', []).append('<MEETING_ID>')
with open(os.path.expanduser('~/mnt/.read-ai-summary-config.json'), 'w') as f:
    json.dump(config, f, indent=2)
"
```

Replace `<MEETING_ID>` with the actual meeting `id`.

---

## Step 10 — Confirm to user

Tell the user:

"✅ Posted *[N] marketing insight(s)* for *[ClientName]* to <#channel-name>.

📎 Read AI report: [report_url]"
