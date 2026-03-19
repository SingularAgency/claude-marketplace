# Singular Agency — Claude Code Plugin Marketplace

Official plugin marketplace for the Singular Agency team. This repository distributes Claude Code plugins across all team members via the marketplace system.

## Add this marketplace

```shell
/plugin marketplace add SingularAgency/claude-marketplace
```

## Available plugins

### `smart-summarizer-plugin`
> Productivity · v1.0.0

Adds three capabilities to Claude Code:

| Capability | Type | What it does |
|---|---|---|
| `/summarize` | Skill | Summarizes selected text, a file, or recent changes into a structured briefing |
| `/briefing` | Command | Generates a morning briefing from git activity, TODOs, and recent file changes |
| `summarizer-agent` | Agent | Autonomous agent that reads any file/folder and writes a `SUMMARY.md` report |

**Install:**
```shell
/plugin install smart-summarizer-plugin@singular-agency-marketplace
```

---

### `meeting-message-drafter`
> Productivity · v1.0.0

Fetches meeting transcripts from Airtable and drafts any message, follow-up, or summary — for clients or the internal team — based on what was actually discussed.

| Capability | Type | What it does |
|---|---|---|
| `meeting-message-drafter` | Skill | Reads a meeting transcript from Airtable and drafts a message for any recipient based on the user's intent |

**Requirements:** Airtable MCP connector must be enabled.

**Install:**
```shell
/plugin install meeting-message-drafter@singular-agency-marketplace
```

---

### `daily-executive-briefing`
> Productivity · v1.0.0

Pulls live data from Google Calendar, Gmail, Slack, and Airtable, analyzes it through a senior PM lens, and delivers a prioritized, action-oriented daily briefing — with draft responses included.

| Capability | Type | What it does |
|---|---|---|
| `daily-executive-briefing` | Skill | Aggregates signals from Calendar, Gmail, Slack, and Airtable to generate a structured executive briefing with urgent items, high-value actions, follow-ups, and strategic alerts |

**Requirements:** Google Calendar, Gmail, Slack, and Airtable MCP connectors must be enabled.

**Install:**
```shell
/plugin install daily-executive-briefing@singular-agency-marketplace
```

---

## Auto-enable for the team

Add this to your project's `.claude/settings.json` to automatically register the marketplace and enable plugins for all team members:

```json
{
  "extraKnownMarketplaces": {
    "singular-agency-marketplace": {
      "source": {
        "source": "github",
        "repo": "SingularAgency/claude-marketplace"
      }
    }
  },
  "enabledPlugins": {
    "smart-summarizer-plugin@singular-agency-marketplace": true,
    "meeting-message-drafter@singular-agency-marketplace": true,
    "daily-executive-briefing@singular-agency-marketplace": true
  }
}
```

## Contributing a plugin

1. Create your plugin under `plugins/<your-plugin-name>/`
2. Add a `.claude-plugin/plugin.json` manifest
3. Add your skills, agents, or commands
4. Open a PR — once merged, the marketplace updates automatically for all users

See [Claude Code plugin docs](https://code.claude.com/docs/en/plugins) for the full authoring guide.