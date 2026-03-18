# Email Weekly Recap

Fetches your Gmail inbox from the past 7 days, filters out all automated, promotional, and notification emails, and delivers a clean digest showing only real human conversations — grouped by whether they need your attention or not.

## Install

```
/plugin install email-weekly-recap@singular-agency-marketplace
```

## Requirements

- Gmail MCP connector must be enabled in your Cowork session.

## Skills

| Skill | Trigger phrases | What it does |
|-------|----------------|--------------|
| /weekly-recap | "recap my emails", "summarize my inbox", "what emails did I get this week", "email digest", "catch me up on my emails" | Fetches last 7 days of Gmail, filters noise, and delivers a grouped digest of real conversations |

## How it works

1. Pulls up to 50 emails from the past 7 days via Gmail MCP
2. Filters out anything automated: noreply senders, notification subjects, newsletters, receipts, alerts, OTPs, etc.
3. Groups remaining emails into: **Action Required**, **Conversations**, and **FYI**
4. Delivers a clean inline summary — one sentence per email, with ⚡ flags for anything needing a reply
