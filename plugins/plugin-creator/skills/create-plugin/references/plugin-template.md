# Plugin Template Reference

Complete worked example of a well-structured plugin for the Singular Agency marketplace.

---

## Example: `meeting-prep-plugin`

### `.claude-plugin/plugin.json`

```json
{
  "name": "meeting-prep-plugin",
  "version": "0.1.0",
  "description": "Prepares concise meeting briefs from calendar events, recent Slack threads, and open action items.",
  "author": {
    "name": "Singular Agency",
    "email": "as@singularagency.co"
  },
  "repository": "https://github.com/SingularAgency/claude-marketplace",
  "license": "MIT",
  "keywords": ["meetings", "productivity", "briefing"]
}
```

### `skills/meeting-brief/SKILL.md`

```markdown
---
description: Generates a concise pre-meeting brief for an upcoming meeting. Triggered by phrases like "prepare for my meeting", "meeting brief", "what do I need to know before my call", "prep for standup", "brief me on my next meeting".
---

Generate a pre-meeting brief for the upcoming meeting the user describes.

Ask the user for:
- Meeting name or topic (if not provided)
- Attendees (optional)
- Any context files or threads to include

Then produce a brief with this structure:

## Meeting: <Name>
**When**: <time if known>
**Attendees**: <list>

### Context
<2-3 sentences on what this meeting is about and why it matters>

### Key Points to Cover
<bullet list of 3-5 agenda items or discussion points>

### Open Questions
<any unresolved items that should be addressed>

### Suggested Outcome
<what a successful meeting looks like>

Keep the brief under one page. Be direct and actionable.
```

### `README.md`

```markdown
# Meeting Prep Plugin

Generates a concise pre-meeting brief from context you provide — attendees, topics, and any relevant files or threads.

## Install

/plugin install meeting-prep-plugin@singular-agency-marketplace

## Skills

| Skill | Trigger | What it does |
|-------|---------|--------------|
| /meeting-brief | "prep for my meeting", "meeting brief" | Generates a structured pre-meeting brief |
```

---

## Rules to follow when writing new plugins

- Plugin name must be kebab-case (lowercase, hyphens only)
- SKILL.md description must include 3–5 specific trigger phrases users would actually say
- SKILL.md body is instructions for Claude, not docs for the user — use imperative style
- Keep SKILL.md under 2,000 words; put detailed content in `references/` subdirectory
- README must include the install command with the marketplace name
- Every plugin must have exactly one `.claude-plugin/plugin.json`
