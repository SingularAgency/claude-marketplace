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
    "smart-summarizer-plugin@singular-agency-marketplace": true
  }
}
```

## Contributing a plugin

1. Create your plugin under `plugins/<your-plugin-name>/`
2. Add a `.claude-plugin/plugin.json` manifest
3. Add your skills, agents, or commands
4. Open a PR — once merged, the marketplace updates automatically for all users

See [Claude Code plugin docs](https://code.claude.com/docs/en/plugins) for the full authoring guide.
