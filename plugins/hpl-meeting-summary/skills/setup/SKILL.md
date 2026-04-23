---
name: setup
description: >
  Use this skill when the user says "set up the meeting summary plugin", "first time setup",
  "configure the plugin for the first time", "initialize the plugin",
  or when no config file exists at ~/mnt/.read-ai-summary-config.json and the user tries to
  run any analysis for the first time. Also trigger if the plugin says it is not working.
metadata:
  version: "0.2.0"
  author: "Singular Agency"
---

# Setup — HPL Meeting Summary Plugin

Guided first-time setup. Verifies both MCP connections, configures channel routing for all three analyses, assigns accountable team members, and creates the hourly scheduled task. Complete every step before allowing the user to use any skill or the agent.

---

## Step 1 — Check Read AI MCP connection

Call `list_meetings` with `limit: 1`.

- **Tool not found / unknown tool** → show `references/readai-install-guide.md` and stop. Tell the user to come back after installing.
- **Auth error** → tell the user to add their Read AI API key in Cowork plugin settings.
- **Success** → "✅ Read AI is connected." Continue.

---

## Step 2 — Check Slack MCP connection

Check whether `slack_send_message` is available.

- **Not available** → show `references/slack-install-guide.md` and stop.
- **Available** → "✅ Slack is connected." Continue.

---

## Step 3 — Configure channel routing

The plugin posts three independent analyses to Slack. Each can go to a different channel.

Tell the user:

> "Let's configure where each analysis gets posted. I'll suggest defaults — just confirm or give me a different channel name."

Ask about each in order, searching Slack for the channel if the user provides a name:

**3a. Summary channel** (Strategic call breakdown)
- Suggested default: `#test-map`
- Ask: "Where should the *Strategic Summary* be posted? (default: #test-map)"
- Use `slack_search_channels` to find the channel ID. Confirm with the user.

**3b. ICP channel** (Qualification analysis)
- Suggested default: `#test-map` (same channel as summary — ICP posts right after)
- Ask: "Where should the *ICP Qualification* be posted? (default: #test-map, same as summary)"
- If the user confirms `#test-map`, reuse the ID from 3a — no need to re-search.

**3c. Marketing Feedback channel**
- Suggested default: `#marketing-feedback`
- Ask: "Where should *Marketing Feedback* be posted? (default: #marketing-feedback)"
- Use `slack_search_channels` to find the channel ID. Confirm.

**3d. Fallback / default channel**
- Set `default_channel` to the Summary channel ID (used as fallback if any specific channel is not set).

Save all four: `default_channel`, `summary_channel`, `icp_channel`, `marketing_channel`.

---

## Step 4 — Configure posting behaviour

Ask: "Should analyses post automatically when I detect a new client meeting, or always show a preview first?"

- **Auto-post**: posts immediately, no confirmation. Recommended for scheduled runs.
- **Preview first**: shows the output and asks before posting.

Save as `auto_post: true` or `auto_post: false`.

---

## Step 5 — Internal team domain

Ask: "What's your company email domain? I'll use it to skip internal-only meetings."

Default: `singularagency.co`. If the user skips, use the default.

---

## Step 6 — Assign accountable team members by technology type

Tell the user:

> "Now let's set up who gets tagged in the Summary thread based on the project type. Tell me the team member responsible for each — I'll look them up in Slack."

Go through each one at a time. Use `slack_search_users` to resolve each name/handle. Confirm match (name + email). Accept multiple people per category as an array.

1. **Airtable** — no-code database, Airtable automations
2. **FlutterFlow** — mobile apps, Flutter development
3. **AI Custom Integration** — Claude, OpenAI, GPT, LLM workflows, AI automation
4. **FullStack** — React, Node.js, backend APIs, web apps

After the four defaults, ask: "Any other tech categories to add? Format: 'Zapier — @name'. Say 'done' when finished."

---

## Step 7 — Write config file

Write the full config to `~/mnt/.read-ai-summary-config.json`:

```bash
python3 -c "
import json, os
config = {
  'setup_complete': True,
  'auto_post': <true|false>,
  'internal_domain': '<domain.com>',
  'default_channel': '<SUMMARY_CHANNEL_ID>',
  'default_channel_name': '<#channel-name>',
  'summary_channel': '<SUMMARY_CHANNEL_ID>',
  'summary_channel_name': '<#channel-name>',
  'icp_channel': '<ICP_CHANNEL_ID>',
  'icp_channel_name': '<#channel-name>',
  'marketing_channel': '<MARKETING_CHANNEL_ID>',
  'marketing_channel_name': '<#channel-name>',
  'mention_users': [],
  'role_assignments': {
    'airtable': {
      'label': 'Airtable',
      'user_ids': ['<SLACK_USER_ID>'],
      'names': ['<Full Name>'],
      'keywords': ['airtable', 'no-code database', 'airtable automation']
    },
    'flutterflow': {
      'label': 'FlutterFlow',
      'user_ids': ['<SLACK_USER_ID>'],
      'names': ['<Full Name>'],
      'keywords': ['flutterflow', 'flutter', 'flutter flow', 'mobile app']
    },
    'ai_custom': {
      'label': 'AI Custom Integration',
      'user_ids': ['<SLACK_USER_ID>'],
      'names': ['<Full Name>'],
      'keywords': ['claude', 'openai', 'gpt', 'llm', 'ai agent', 'ai automation', 'custom ai', 'langchain', 'cowork']
    },
    'fullstack': {
      'label': 'FullStack',
      'user_ids': ['<SLACK_USER_ID>'],
      'names': ['<Full Name>'],
      'keywords': ['react', 'node', 'nodejs', 'backend', 'frontend', 'web app', 'api', 'fullstack', 'full-stack']
    }
  },
  'posted_meeting_ids': [],
  'icp_posted_meeting_ids': [],
  'marketing_posted_meeting_ids': [],
  'agent_processed_meeting_ids': []
}
path = os.path.expanduser('~/mnt/.read-ai-summary-config.json')
with open(path, 'w') as f:
    json.dump(config, f, indent=2)
print('Config written.')
"
```

Replace all placeholders with the actual values collected in Steps 3–6. Include any custom tech categories added in Step 6.

---

## Step 8 — Create the hourly scheduled task

Use `create_scheduled_task` to set up the automatic detection loop:

```
name: "HPL Meeting Auto-Detect"
prompt: "Run the hpl-meeting-summary auto-detect skill to check for new completed client meetings from the last hour and run the full analysis (Summary, ICP, Marketing Feedback) for each one."
schedule: "0 * * * *"
```

This runs every hour. The skill scans the past hour for new client meetings and delegates each to the `meeting-analyst` agent.

---

## Step 9 — Confirm setup complete

Tell the user:

"🎉 You're all set! Here's your configuration:

📋 **Summary** → <#summary-channel>
🎯 **ICP Qualification** → <#icp-channel>
📊 **Marketing Feedback** → <#marketing-channel>

**Auto-post:** <enabled / disabled>
**Internal domain:** @<domain.com>
**Auto-detection:** running every hour

**Accountable by project type:**
• Airtable → <Name(s)>
• FlutterFlow → <Name(s)>
• AI Custom Integration → <Name(s)>
• FullStack → <Name(s)>
<any custom categories>

After each client meeting, I'll automatically run all three analyses and post them in order. To run any analysis manually, use:
👉 *'Summarize my last meeting'*
👉 *'Run ICP analysis for [client]'*
👉 *'Marketing feedback for [client]'*

To update settings, say *'Configure the meeting summary plugin'*."
