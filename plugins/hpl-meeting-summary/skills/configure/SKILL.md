---
name: configure
description: >
  Use this skill when the user says "configure the meeting summary plugin", "set my default Slack channel",
  "change where summaries are posted", "turn on auto-post", "turn off auto-post",
  "add someone to tag in summaries", "remove a tag", "show my meeting summary settings",
  "update meeting summary preferences", "set my company domain", "change internal domain",
  "who handles airtable leads", "change accountable for [technology]", "assign [name] to [tech type]",
  "update role assignments", "who is responsible for flutterflow", "add a new technology category",
  or any phrase related to managing how, where, and to whom Read AI meeting summaries are posted.
metadata:
  version: "0.1.0"
  author: "Singular Agency"
---

# Configure Meeting Summary Plugin

Manage all preferences for how and where meeting summaries are posted. All settings are saved to `~/.read-ai-summary-config.json`.

## Config File Structure

```json
{
  "default_channel": "C0123456789",
  "default_channel_name": "#hpl-general",
  "auto_post": false,
  "internal_domain": "singularagency.co",
  "mention_users": [],
  "posted_meeting_ids": [],
  "role_assignments": {
    "airtable": {
      "label": "Airtable",
      "user_ids": ["U123"],
      "names": ["William Hernandez"],
      "keywords": ["airtable", "no-code database"]
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
  "setup_complete": true
}
```

---

## Step 1 — Read current config

Read `~/.read-ai-summary-config.json` using Bash. Display a clean summary of current settings:

```
📋 Current Configuration:

Channel: #hpl-general
Auto-post: disabled
Internal domain: @singularagency.co

👤 Accountable by Technology:
• Airtable → William Hernandez
• FlutterFlow → Fabian
• AI Custom Integration → Amilkar
• FullStack → Charlie
<any custom categories>

Global tags (all summaries): <none or list of names>
Posted meetings tracked: 12
```

---

## Step 2 — Identify what the user wants to change

Handle each type of change:

---

### A. Set default Slack channel
Use `slack_search_channels` to find the channel the user named. Show up to 5 matches with name and description. Confirm the right one. Save `default_channel` (ID) and `default_channel_name`.

---

### B. Toggle auto-post
- "Auto-post on" / "post automatically" → `auto_post: true`
- "Auto-post off" / "always ask" → `auto_post: false`

Explain:
- **ON**: summaries post immediately when a new client meeting is detected, no confirmation.
- **OFF**: you get a preview and must confirm before posting.

---

### C. Set internal domain
Save `internal_domain`. Meetings where ALL participants share this domain are skipped as internal. Default: `singularagency.co`.

---

### D. Update accountable for a technology category

When the user says things like:
- "Who handles Airtable leads?" → show current assignment, offer to change
- "Assign William to Airtable" → update `role_assignments.airtable`
- "Change FlutterFlow accountable to Fabian" → update `role_assignments.flutterflow`
- "Add Jorge to AI Custom" → append to `role_assignments.ai_custom.user_ids`
- "Remove Amilkar from FullStack" → remove from `role_assignments.fullstack.user_ids`

Steps:
1. Identify the technology category (airtable, flutterflow, ai_custom, fullstack, or a custom key)
2. Use `slack_search_users` to look up the person by name/handle if not already a known Slack ID
3. Confirm the match (name + email)
4. Update `user_ids` and `names` arrays in that category
5. Confirm: "Done — [TechType] leads will now be tagged to [Name(s)]"

---

### E. Add a new technology category

When the user says "add a new technology" or "we also do Zapier / WordPress / etc.":

Ask:
1. "What's the technology name?" (e.g., "Zapier")
2. "Who's accountable for it?" (search Slack for the person)
3. "What keywords should I look for in meetings to detect this type?" (suggest defaults, let user add/remove)

Create a new entry in `role_assignments` under a kebab-case key (e.g., `zapier`):
```json
"zapier": {
  "label": "Zapier",
  "user_ids": ["U..."],
  "names": ["..."],
  "keywords": ["zapier", "zap", "zapier automation", "zapier workflow"]
}
```

---

### F. Add custom keywords to an existing category

When the user says "also detect [keyword] as Airtable" or "add [term] to FlutterFlow detection":

Append the new keyword(s) to the relevant category's `keywords` array.

---

### G. Add global mention users (all summaries)

Use `slack_search_users` to find the users the user named. Add their Slack user IDs to `mention_users`. These appear in the headline message, not the thread.

---

### H. Remove global mention users
Remove the matching user ID from `mention_users`.

---

### I. Clear posted meeting history
If the user says "reset posted meetings" or "re-post all meetings":
- Set `posted_meeting_ids: []`
- Warn: "This will let the auto-detect re-post summaries for all recent meetings it finds. Are you sure?"

---

### J. Show all current settings
Display the full config in a readable format without making changes (same as Step 1 output).

---

## Step 3 — Save updated config

Write the complete updated config back to `~/.read-ai-summary-config.json` using Python (to safely preserve all existing fields):

```bash
python3 -c "
import json
with open('$HOME/.read-ai-summary-config.json', 'r') as f:
    config = json.load(f)
# Apply changes here
with open('$HOME/.read-ai-summary-config.json', 'w') as f:
    json.dump(config, f, indent=2)
"
```

Never overwrite the entire file — always read first and merge changes.

---

## Step 4 — Confirm

Tell the user exactly what changed. Example responses:
- "Done — Airtable leads will now be tagged to *William Hernandez* (<@U123>)."
- "FlutterFlow now has two accountables: *Fabian* and *William*."
- "Added 'zapier' as a new technology category assigned to *Jorge*."
- "Keyword 'bubble.io' added to the FullStack detection list."
