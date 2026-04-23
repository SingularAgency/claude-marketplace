# hpl-meeting-summary

Post-meeting analysis suite for Singular Innovation. After every client call, the `meeting-analyst` agent runs three independent analyses from a single Read AI session and posts each as a separate Slack thread.

## Architecture

```
hpl-meeting-summary/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── meeting-analyst.md     ← orchestrator: runs all 3 analyses
└── skills/
    ├── auto-detect/            ← scheduled: detects new meetings → delegates to agent
    ├── generate-summary/       ← manual: strategic call breakdown
    ├── icp-qualification/      ← manual: Singular Innovation ICP analysis
    ├── marketing-feedback/     ← manual: positioning & messaging insights
    ├── configure/              ← manage channel routing & role assignments
    └── setup/                  ← first-time setup
```

## What gets posted after every meeting

| Output | Slack format | Channel config key |
|--------|-------------|-------------------|
| 📋 Strategic Summary | Headline + full call breakdown thread | `summary_channel` → `default_channel` |
| 🎯 ICP Qualification | Headline + cohort report thread | `icp_channel` → `default_channel` |
| 📊 Marketing Feedback | Headline + 1–3 insight blocks as thread replies | `marketing_channel` → `default_channel` |

## Skills

| Skill | How to trigger | What it does |
|-------|---------------|--------------|
| `auto-detect` | Scheduled task (every 5–10 min) | Detects new meetings, delegates to agent |
| `generate-summary` | "summarize my last meeting" | Strategic call breakdown, manual |
| `icp-qualification` | "run ICP analysis for [client]" | Full ICP qualification, manual |
| `marketing-feedback` | "marketing feedback for [client]" | Positioning & messaging insights, manual |
| `configure` | "configure the plugin" | Channel routing, role assignments, tags |
| `setup` | "set up the plugin" | First-time setup |

## Config

All settings live in `~/mnt/.claude/.read-ai-summary-config.json`. Key fields:

```json
{
  "setup_complete": true,
  "auto_post": true,
  "internal_domain": "singularagency.co",
  "default_channel": "CXXXXXXXX",
  "summary_channel": "CXXXXXXXX",
  "icp_channel": "CXXXXXXXX",
  "marketing_channel": "CXXXXXXXX",
  "mention_users": [],
  "role_assignments": {},
  "agent_processed_meeting_ids": [],
  "posted_meeting_ids": [],
  "icp_posted_meeting_ids": [],
  "marketing_posted_meeting_ids": []
}
```

The four `*_channel` keys are optional — all fall back to `default_channel`. Set them to route each output to a dedicated Slack channel (e.g. `#sales-briefings`, `#sales-qualification`, `#marketing-insights`).

## Prerequisites

- Read AI connector active
- Slack connector active
- Run `hpl-meeting-summary:setup` on first use

## Scheduled task

Create a scheduled task pointing to `hpl-meeting-summary:auto-detect` every hour. Use the `schedule` skill to set this up.
