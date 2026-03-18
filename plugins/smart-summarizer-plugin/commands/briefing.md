---
description: Generate a morning briefing from recent git activity, open TODOs, and recent file changes
---

Generate a concise morning briefing for the current project. Include:

1. **Recent Changes** — summarize git log from the last 24 hours (run `git log --oneline --since="24 hours ago"` to get this)
2. **Open TODOs** — scan the codebase for TODO/FIXME/HACK comments and list the top 5 most relevant
3. **Modified Files** — list files changed in the last 24 hours and a one-line description of what changed in each

Format the output as a clean, scannable briefing a developer can read in under 2 minutes. Lead with the most important or urgent items.
