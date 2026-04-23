---
name: configure
description: >
  Use this skill when the user says "configure the meeting summary plugin", "set my default Slack channel",
  "change where summaries are posted", "change the ICP channel", "change where ICP is posted",
  "change the marketing feedback channel", "turn on auto-post", "turn off auto-post",
  "add someone to tag in summaries", "remove a tag", "show my meeting summary settings",
  "update meeting summary preferences", "set my company domain", "change internal domain",
  "who handles airtable leads", "change accountable for [technology]", "assign [name] to [tech type]",
  "update role assignments", "who is responsible for flutterflow", "add a new technology category",
  "reset posted meetings", or any phrase related to managing how, where, and to whom
  meeting analyses are posted.
metadata:
  version: "0.2.0"
  author: "Singular Agency"
---

# Configure HPL Meeting Summary Plugin

Manage all preferences for how and where each analysis is posted. All settings are saved to `~/mnt/Claude/.read-ai-summary-config.json`.

## Full Config Schema

```json
{
  "setup_complete": true,
  "auto_post": true,
  "internal_domain": "singularagency.co",

  "default_channel": "CXXXXXXXX",
  "default_channel_name": "#test-map",

  "summary_channel": "CXXXXXXXX",
  "summary_channel_name": "#test-map",

  "icp_channel": "CXXXXXXXX",
  "icp_channel_name": "#test-map",

  "marketing_channel": "CXXXXXXXX",
  "marketing_channel_name": "#marketing-feedback",

  "mention_users": [],

  "role_assignments": {
    "airtable": {
      "label": "Airtable",
      "user_ids": ["U123"],
      "names": ["William Hernandez"],
      "keywords": ["airtable", "no-code database", "airtable automation"]
    },
    "flutterflow": {
      "label": "FlutterFlow",
      "user_ids": ["U456"],
      "names": ["Fabian"],
      "keywords": ["flutterflow", "flutter", "mobile app"]
    },
    "ai_custom": {
      "label": "AI Custom Integration",
      "user_ids": ["U789"],
      "names": ["Amilkar"],
      "keywords": ["claude", "openai", "gpt", "llm", "ai agent"]
    },
    "fullstack": {
      "label": "FullStack",
      "user_ids": ["U101"],
      "names": ["Charlie"],
      "keywords": ["react", "node", "backend", "web app"]
    }
  },

  "posted_meeting_ids": [],
  "icp_posted_meeting_ids": [],
  "marketing_posted_meeting_ids": [],
  "agent_processed_meeting_ids": []
}
```

---

## Step 1 — Read current config

Read `~/mnt/Claude/.read-ai-summary-config.json` using Bash. Display a clean summary:

```
📋 Current Configuration:

📋 Summary       → #test-map
🎯 ICP           → #test-map
📊 Marketing     → #marketing-feedback
Auto-post        → enabled / disabled
Internal domain  → @singularagency.co

👤 Accountable by Technology:
• Airtable → William Hernandez
• FlutterFlow → Fabian
• AI Custom Integration → Amilkar
• FullStack → Charlie
<any custom categories>

Global tags (all summaries): <none or list>
Meetings tracked: Summary: N | ICP: N | Marketing: N | Agent: N
```

---

## Step 2 — Identify what the user wants to change

Handle each type of change:

---

### A. Set a channel (summary / ICP / marketing / default)

When the user says things like:
- "Change the summary channel to #sales"
- "Move ICP to #qualification"
- "Post marketing feedback to #product"
- "Change my default channel"

Use `slack_search_channels` to find the channel the user named. Show up to 5 matches. Confirm the right one.

Save the appropriate key(s):
- Summary → `summary_channel` + `summary_channel_name` (also update `default_channel` if it was the same)
- ICP → `icp_channel` + `icp_channel_name`
- Marketing → `marketing_channel` + `marketing_channel_name`
- Default → `default_channel` + `default_channel_name`

If the user sets a channel without specifying which analysis, ask: "Should this apply to all three analyses, or just one? (Summary / ICP / Marketing / All)"

---

### B. Toggle auto-post

- "Auto-post on" → `auto_post: true` — analyses post immediately when a meeting is detected
- "Auto-post off" → `auto_post: false` — always shows a preview and waits for confirmation

---

### C. Set internal domain

Save `internal_domain`. Meetings where ALL participants share this domain are skipped as internal.

---

### D. Update accountable for a technology category

- "Who handles Airtable?" → show current assignment
- "Assign William to Airtable" → update `role_assignments.airtable`
- "Add Fabian to FlutterFlow" → append to that category's arrays
- "Remove Amilkar from FullStack" → remove from that category's arrays

Steps:
1. Identify the tech category (airtable / flutterflow / ai_custom / fullstack / custom key)
2. Use `slack_search_users` to look up the person if not a known Slack ID
3. Confirm match (name + email)
4. Update `user_ids` and `names` arrays
5. Confirm: "Done — [TechType] leads will now tag [Name(s)]."

---

### E. Add a new technology category

Ask:
1. Technology name (e.g., "Zapier")
2. Who's accountable — search Slack
3. Detection keywords — suggest defaults, let user edit

Create a new entry under a kebab-case key (e.g., `zapier`):
```json
"zapier": {
  "label": "Zapier",
  "user_ids": ["U..."],
  "names": ["..."],
  "keywords": ["zapier", "zap", "zapier automation"]
}
```

---

### F. Add custom keywords to an existing category

Append to the relevant `keywords` array. Confirm what was added.

---

### G. Add / remove global mention users

`mention_users` — appear in the Summary headline for every meeting.
Use `slack_search_users` to resolve names/handles. Add or remove from the array.

---

### H. Reset posted meeting history

If the user says "reset posted meetings" or "clear history":

Ask which list(s) to clear:
- "Summary history" → `posted_meeting_ids: []`
- "ICP history" → `icp_posted_meeting_ids: []`
- "Marketing history" → `marketing_posted_meeting_ids: []`
- "Agent history" → `agent_processed_meeting_ids: []`
- "All" → clear all four

Warn: "This will let the auto-detect re-process recent meetings it already handled. Are you sure?"

---

### I. Show all current settings

Display the full config in readable format (same as Step 1 output). No changes.

---

## Step 3 — Save updated config

Always read the file first, apply changes, then write back — never overwrite the entire file:

```bash
python3 -c "
import json
path = '~/mnt/Claude/.read-ai-summary-config.json'
with open(path, 'r') as f:
    config = json.load(f)
# Apply targeted changes here
with open(path, 'w') as f:
    json.dump(config, f, indent=2)
"
```

---

## Step 4 — Confirm

Tell the user exactly what changed. Examples:
- "Done — ICP analyses will now post to *#qualification*."
- "Airtable leads will be tagged to *William Hernandez* (<@U123>)."
- "Auto-post is now *enabled*."
- "Cleared ICP and Agent history — those meetings will be re-analysed on the next hourly run."
