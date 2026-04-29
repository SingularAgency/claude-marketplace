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

### `repo-documentator`
> Developer tools · v0.4.0

Autonomously documents a GitHub repository and opens a pull request with **non-technical, PM-friendly** business docs. One file per module with a flow diagram, plain-English capabilities, business rules with origin, and a Mermaid **user-journey map per actor**. Cross-module workflows ship with two diagrams: a business view (for stakeholders) and a technical sequence (for engineers). After the initial run, `document-refresh` provides **cursor-based incremental updates** — only modules whose paths changed get re-derived.

| Capability | Type | What it does |
|---|---|---|
| `document-init` | Skill | Clones a repo (or accepts a local path), detects modules, maps connections, writes the full `docs/` tree, and opens a PR |
| `document-refresh` | Skill | Reads the cursor in `docs/.business-docs-state.json`, processes only what changed since, advances the cursor, and opens a PR |
| `document-module` | Skill | Regenerates a single module's doc from the code |
| `document-workflow` | Skill | Traces a workflow from an entry point and writes a 2-diagram workflow file |
| `document-connections` | Skill | Regenerates the inter-module connection map |
| `module-detector` | Agent | Proposes a split into bounded contexts (DDD) |
| `connection-analyst` | Agent | Maps explicit + subtle inter-module connections (gold for handoffs) |

**Requirements:** A GitHub PAT with `repo` scope (or `gh` CLI authenticated) so the plugin can clone and open PRs.

**Install:**
```shell
/plugin install repo-documentator@singular-agency-marketplace
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