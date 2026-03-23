# Read AI Meeting Summary

Automatically generate structured call breakdowns from Read AI and post them to Slack — with client context, core direction, action items, and next steps. Designed for the Singular Agency sales and delivery workflow.

## What it does

After every meeting, trigger this plugin to:

1. Pull the meeting data from Read AI (summary, topics, chapter breakdown, action items, key questions)
2. Generate a structured Slack post tailored to the meeting type (sales call, internal sync, or one-on-one)
3. Post it to your configured Slack channel

The output format mirrors Tyler's manual call breakdown style — giving anyone on the team instant context without having to read the full transcript.

## Skills

### `generate-summary`
Fetches your most recent Read AI meeting (or one you specify by client/title), generates the formatted summary, and posts it to Slack.

**Trigger phrases:**
- "Summarize my last meeting"
- "Post the meeting summary to Slack"
- "Generate a call breakdown for [client name]"
- "Share the recap from the Travelog call"

### `configure`
Manage your posting preferences — default Slack channel, auto-post behavior, and who gets @-mentioned.

**Trigger phrases:**
- "Set my default channel to #hpl-general"
- "Turn on auto-post"
- "Tag Tyler in all meeting summaries"
- "Show my meeting summary settings"

## Setup

No environment variables required — this plugin uses your already-connected Read AI and Slack integrations.

**First-time setup (optional but recommended):**

Tell Claude: *"Configure the meeting summary plugin"* to set your default Slack channel and auto-post preference. Without configuration, you'll be asked to confirm the channel each time.

## Output formats

The plugin generates three formats based on meeting type:

| Meeting Type | Format |
|---|---|
| External client / sales call | Full breakdown (context, direction, action items, next steps) |
| Internal team sync (3+ people) | Compact recap (decisions, action items, blockers) |
| One-on-one | Minimal (decisions + action items only) |

## Configuration file

Settings are stored at `~/.read-ai-summary-config.json`:

```json
{
  "default_channel": "C0123456789",
  "default_channel_name": "#hpl-general",
  "auto_post": false,
  "mention_users": []
}
```

## Requirements

- Read AI MCP connected (provides `list_meetings`, `get_meeting_by_id`)
- Slack MCP connected (provides `slack_send_message`, `slack_search_channels`)
