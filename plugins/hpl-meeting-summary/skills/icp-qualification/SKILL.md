---
name: icp-qualification
description: >
  Use this skill when the user says "run ICP analysis for [client]", "qualify [client]",
  "ICP qualification for [meeting]", "analyze the fit for [client]", "should we pursue [client]",
  "run the qualification on [client]", "ICP check for [client]", "what cohort is [client]",
  "is [client] ICP?", "score [client]", "dar el ICP de [cliente]", "analizar el fit de [cliente]",
  or any phrase requesting a B2B ICP qualification analysis from a Read AI meeting.
  Runs independently from generate-summary — both can run on the same meeting.
metadata:
  version: "0.1.0"
  author: "Singular Agency"
---

# Generate ICP Qualification Analysis

Fetch a meeting from Read AI, extract prospect signals, research the company and person, run the full Singular Innovation ICP framework, and post the qualification report to Slack as a standalone thread — completely independently from the meeting summary.

**Read `references/icp-framework.md` before executing any analysis steps. Do not skip it.**

---

## Step 0 — First-run check

Read `~/mnt/.read-ai-summary-config.json` using Bash.

If the file does not exist OR `setup_complete` is not `true`:
→ Tell the user: "The HPL meeting plugin hasn't been set up yet. Please run the `setup` skill first, then come back here."
→ Stop.

---

## Step 1 — Fetch meetings from Read AI

Call `list_meetings` with:
```
limit: 5
expand: ["summary", "action_items", "key_questions", "topics", "chapter_summaries"]
```

Fields available per meeting: `id`, `title`, `start_time_ms`, `end_time_ms`, `participants[]` (name, email, attended), `owner`, `report_url`, `summary`, `chapter_summaries[]`, `action_items[]`, `key_questions[]`, `topics[]`.

---

## Step 2 — Select the meeting

If the user named a client or project → find the closest match by title or participant name.

If the user said "last meeting" or nothing specific → use the first item (most recent).

If multiple possible matches → show a numbered list (title + date as "Mon Mar 23, 3:00 PM") and ask the user to pick.

---

## Step 3 — Identify the prospect

Find the external participant: the one whose email domain is NOT `singularagency.co` (or the `internal_domain` from config).

If multiple external participants: pick the most senior or most active one based on the transcript. List all external participants found.

Extract:
- **Prospect name** — from `participants[]`
- **Prospect email** — for domain inference
- **Company name** — from email domain (e.g. `acme.com` → Acme) or named in transcript
- **Company domain** — for web research

If ALL participants share `internal_domain` → tell the user "This is an internal meeting — no external prospect to qualify." and stop.

---

## Step 4 — Extract signals from transcript

Search `summary`, `topics[]`, `chapter_summaries[].description`, `action_items[]`, and `key_questions[]`. Build this extraction table before researching anything:

| Field | Extracted value or [Not detected] |
|-------|----------------------------------|
| Prospect name | |
| Company name | |
| Prospect role/title | |
| Pain points (all named) | |
| Budget signals | |
| Urgency / timeline signals | |
| Tools / platforms named | |
| AI readiness signals | |
| Decision authority signals | |
| Direct quotes (verbatim) | |

Mark anything absent from the transcript as `[Not detected]`. Do not fabricate.

---

## Step 5 — Research the company

Run at minimum 2 web searches:

1. `"[CompanyName]" site:[domain] OR "[CompanyName]" company employees industry`
2. `"[CompanyName]" funding OR hiring OR growth OR automation OR SaaS`

Find: official website, industry, employee count, revenue signals, tech maturity, growth signals, operational complexity. If the company has no web presence, note it explicitly — it is a risk flag.

---

## Step 6 — Research the person

Run at minimum 2 web searches:

1. `"[ProspectName]" "[CompanyName]" LinkedIn`
2. `"[ProspectName]" "[CompanyName]" site:linkedin.com OR founder OR CEO OR director`

Find: current title, seniority, tenure, decision-making authority, background type. If no professional profile is found, note it explicitly — it is a risk flag.

---

## Step 7 — Cross-validate

Compare transcript signals vs. research:
- Does their claimed role match what research shows?
- Does the company size match the budget/urgency signals expressed?
- Did they overstate authority or maturity?

If research contradicts the transcript → trust research.

---

## Step 8 — Run the ICP analysis

Using the full framework in `references/icp-framework.md`, determine:

**A. ICP Fit** — High / Medium / Low / Not ICP
- High: SMB/mid-market with operational complexity + strong budget signals + clear AI opportunity
- Medium: fits but one major signal weak or missing
- Low: partial fit, key criteria not met
- Not ICP: wrong size, wrong profile, no evidence of budget or strategic need

**B. Cohort** — Wolf / Golden Retriever / Labradoodle / Beagle / Chihuahua
Default to the LOWER cohort when signals are ambiguous. Refer to cohort definitions in `references/icp-framework.md`.

**C. Decision Role** — Decision Maker / Champion (No Authority) / Non-Decision Role
Verify with research — never assume authority from title alone.

**D. Buy Intent** — High / Medium / Low

**E. Timing** — Now / 3–6 months / 6–18 months / Unknown

---

## Step 9 — Generate the report

Compose the full qualification report using the EXACT output format in `references/icp-framework.md`. Requirements:
- Every section filled — no skipping, no merging
- Minimum 4 key signals in the WHY section (mix of transcript + research)
- Minimum 2 specific risks
- Recommended Next Step is a single unambiguous directive
- Confidence note lists exactly what was detected vs. missing

The report posts as a **thread reply** — the parent message is the headline only.

---

## Step 10 — Choose the Slack channel

Resolve the posting channel from config:

```bash
python3 -c "
import json, os
with open(os.path.expanduser('~/mnt/.read-ai-summary-config.json')) as f:
    c = json.load(f)
ch_id   = c.get('icp_channel')   or c.get('default_channel')
ch_name = c.get('icp_channel_name') or c.get('default_channel_name', '#general')
auto    = c.get('auto_post', False)
print('CH_ID='   + str(ch_id))
print('CH_NAME=' + str(ch_name))
print('AUTO='    + str(auto))
"
```

Priority: `icp_channel` → `default_channel`. If neither is set, ask the user which channel to post to.

If `AUTO=True` AND channel is known → post immediately without asking.
If `AUTO=False` → show a preview of the headline + report and confirm before posting.

---

## Step 11 — Post the parent headline

Call `slack_send_message`:
- `channel_id`: selected channel
- `text`: `🎯 ICP — [ProjectName] — [ClientName]`

Where `ProjectName` is inferred from the meeting title or folders (same logic as `generate-summary`). Capture `ts` from the response.

---

## Step 12 — Post the full report as a thread reply

Call `slack_send_message`:
- `channel_id`: same channel
- `thread_ts`: `ts` from Step 11
- `text`: the full formatted qualification report from Step 9

---

## Step 13 — Mark as ICP-processed

After both posts succeed, append the meeting ID to `icp_posted_meeting_ids` in config (separate from `posted_meeting_ids` — do NOT touch that field):

```bash
python3 -c "
import json, os
with open(os.path.expanduser('~/mnt/.read-ai-summary-config.json'), 'r') as f:
    config = json.load(f)
config.setdefault('icp_posted_meeting_ids', []).append('<MEETING_ID>')
with open(os.path.expanduser('~/mnt/.read-ai-summary-config.json'), 'w') as f:
    json.dump(config, f, indent=2)
"
```

Replace `<MEETING_ID>` with the actual meeting `id`.

---

## Step 14 — Confirm to user

Tell the user:

"✅ ICP analysis posted to <#channel-name>
- Headline: *🎯 ICP — ProjectName — ClientName*
- Full qualification report in the thread

📎 Read AI report: [report_url]"
