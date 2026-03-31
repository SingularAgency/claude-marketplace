---
name: setup
description: >
  Use this skill when the user says "set up the meeting summary plugin", "first time setup",
  "configure the plugin for the first time", "install Read AI summary", "initialize the plugin",
  or when no config file exists at ~/.read-ai-summary-config.json and the user tries to generate
  a summary for the first time. Also trigger if the user says summaries are not working.
metadata:
  version: "0.1.0"
  author: "Singular Agency"
---

# Setup — Read AI Meeting Summary Plugin

Run this guided setup to verify all integrations are connected and configure where summaries will be posted. Complete every step before allowing the user to use the generate-summary skill.

---

## Step 0 — Connector pre-check (NO API calls yet)

**Before making any tool calls**, check whether the required tools are available in your current session scope. Do this by inspecting your available tools list — do NOT call them yet.

Required tools:
- `list_meetings` → provided by the Read AI connector
- `slack_send_message` → provided by the Slack connector

**If `list_meetings` is NOT in your available tools:**
→ Do not attempt to call it. Do not wait or spin.
→ Immediately show the contents of `references/readai-install-guide.md`.
→ Tell the user:

> "⚠️ The **Read AI** connector isn't connected yet on this computer. Follow the steps above to install it in Cowork, then come back and say *'set up the meeting summary plugin'* to continue."

→ Stop here. Do not proceed to Step 1.

**If `slack_send_message` is NOT in your available tools:**
→ Do not attempt to call it. Do not wait or spin.
→ Immediately show the contents of `references/slack-install-guide.md`.
→ Tell the user:

> "⚠️ The **Slack** connector isn't connected yet on this computer. Follow the steps above to install it in Cowork, then come back and say *'set up the meeting summary plugin'* to continue."

→ Stop here. Do not proceed to Step 1.

**If BOTH tools are available in scope:** tell the user:
> "✅ Both connectors detected. Starting setup..."

Then continue to Step 1.

---

## Step 1 — Verify Read AI connection is working

Now that `list_meetings` is confirmed available, call it with `limit: 1` to verify it actually works.

**If the call returns an authentication error** (unauthorized, invalid token, 401):
→ Tell the user: "Read AI is installed but not authenticated. Go to Cowork → Settings → Plugins & Connectors, disconnect and reconnect Read AI, then try again."
→ Stop here.

**If the call hangs or times out** (no response after a reasonable wait):
→ Tell the user: "Read AI is connected but not responding. Try disconnecting and reconnecting it in Cowork → Settings → Plugins & Connectors, then restart Cowork and try again."
→ Stop here.

**If the call returns data successfully:**
→ Tell the user: "✅ Read AI is connected and responding." and continue to Step 2.

---

## Step 2 — Verify Slack connection is working

`slack_send_message` is already confirmed available from Step 0.
→ Tell the user: "✅ Slack is connected." and continue to Step 3.

---

## Step 3 — Configure default Slack channel

Ask the user: "Which Slack channel should meeting summaries be posted to by default?"

Use `slack_search_channels` with the user's input to find matching channels. Show up to 5 results with their names and descriptions, and ask the user to confirm the right one.

Save the confirmed channel ID and name.

---

## Step 4 — Configure posting behavior

Ask the user: "Should I post summaries automatically when I detect a new client meeting, or always show you a preview first?"

Options:
- **Auto-post**: posts immediately to the default channel, no confirmation needed
- **Preview first**: shows the formatted summary and asks before posting (recommended for new users)

Save the preference as `auto_post: true` or `auto_post: false`.

---

## Step 5 — Ask for internal team domain

Ask the user: "What's your company email domain? This lets me automatically skip internal meetings and only post summaries for client calls."

Example: `singularagency.co`

If the user skips, default to `singularagency.co`.

---

## Step 6 — Assign accountable team members by technology type

Tell the user:

"Now let's set up who gets tagged in summaries based on the type of project. For each technology category, tell me the team member responsible — you can type their name or Slack @handle, and I'll look them up."

Go through each technology one at a time. For each one, ask:

> "Who will be the accountable for **[Technology]** leads?"

Technologies to assign (ask in this order):

1. **Airtable** — e.g., no-code database, Airtable automations, Airtable integrations
2. **FlutterFlow** — e.g., mobile apps, Flutter development, FlutterFlow builds
3. **AI Custom Integration** — e.g., Claude agents, OpenAI, GPT, LLM workflows, AI automation
4. **FullStack** — e.g., React, Node.js, backend APIs, web apps, custom dev

For each answer:
- Use `slack_search_users` to find the person by name or handle
- Show the match (name + email) and confirm with the user
- If the user types a Slack ID directly (format: `U` followed by alphanumerics), use it as-is without searching
- If the user says "skip" or "same as previous", handle accordingly
- If a single category has multiple accountables (e.g., "William and Fabian"), collect both user IDs as an array

After all 4 are assigned, ask:

> "Do you have any other technology categories to add? For example: 'Zapier — @name' or 'WordPress — @name'. Say 'done' when finished."

Accept freeform additions until the user says "done" or "no".

---

## Step 7 — Write config file

Write the complete config to `~/.read-ai-summary-config.json`:

```bash
cat > ~/.read-ai-summary-config.json << 'EOF'
{
  "default_channel": "<CHANNEL_ID>",
  "default_channel_name": "<#channel-name>",
  "auto_post": <true|false>,
  "internal_domain": "<domain.com>",
  "mention_users": [],
  "posted_meeting_ids": [],
  "role_assignments": {
    "airtable": {
      "label": "Airtable",
      "user_ids": ["<SLACK_USER_ID>"],
      "names": ["<Full Name>"],
      "keywords": ["airtable", "no-code database", "airtable automation"]
    },
    "flutterflow": {
      "label": "FlutterFlow",
      "user_ids": ["<SLACK_USER_ID>"],
      "names": ["<Full Name>"],
      "keywords": ["flutterflow", "flutter", "flutter flow", "mobile app"]
    },
    "ai_custom": {
      "label": "AI Custom Integration",
      "user_ids": ["<SLACK_USER_ID>"],
      "names": ["<Full Name>"],
      "keywords": ["claude", "openai", "gpt", "llm", "ai agent", "ai automation", "custom ai", "ai integration", "langchain", "cowork"]
    },
    "fullstack": {
      "label": "FullStack",
      "user_ids": ["<SLACK_USER_ID>"],
      "names": ["<Full Name>"],
      "keywords": ["react", "node", "nodejs", "backend", "frontend", "web app", "api", "fullstack", "full-stack", "full stack"]
    }
  },
  "setup_complete": true
}
EOF
```

Replace all placeholder values with the actual user answers. If a category has multiple accountables, include all user IDs in the array. Include any additional custom categories the user added, following the same schema.

---

## Step 8 — Create the scheduled task

Use the `create_scheduled_task` tool to set up the 5-minute auto-detection loop:

```
name: "Read AI Meeting Auto-Detect"
prompt: "Run the auto-detect skill to check for new completed client meetings from Read AI and post their summaries to Slack."
schedule: "*/5 * * * *"
```

This creates a background task that checks for new client meetings every 5 minutes. It will silently skip internal meetings, skip meetings already posted, and skip meetings whose Read AI summary isn't ready yet.

---

## Step 9 — Confirm setup complete

Tell the user:

"🎉 You're all set! Here's your configuration:

- **Channel**: <#channel-name>
- **Auto-post**: <enabled/disabled>
- **Internal domain**: @<domain.com> (internal-only meetings will be skipped)
- **Auto-detection**: running every 5 minutes in the background

**Accountable by project type:**
- Airtable → <Name(s)>
- FlutterFlow → <Name(s)>
- AI Custom Integration → <Name(s)>
- FullStack → <Name(s)>
<any custom categories>

When a new client meeting comes in, I'll detect the project type, tag the right person in the Slack thread, and post the full breakdown automatically.

To post a summary manually anytime, say:
👉 *'Summarize my last meeting'*
👉 *'Post the call breakdown for [client name]'*

To update assignments or settings, say *'Configure the meeting summary plugin'*."
