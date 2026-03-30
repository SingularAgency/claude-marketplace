# Trustworthiness Report Plugin

Generate evidence-based Trustworthiness Reports for talents by analyzing their participation in Read AI meeting transcripts.

## Overview

This plugin evaluates a named talent across five criteria — Credibility, Reliability, Intimacy, Group Thinking, and English Proficiency — by searching Read AI meeting transcripts from the past month. It produces a self-contained HTML report with scores, evidence-based justifications, and constructive feedback.

## Components

| Component | Name | Purpose |
|-----------|------|---------|
| Skill | `generate-report` | Main workflow: retrieves transcripts, evaluates talent, generates HTML report |

## Setup

This plugin requires the **Read AI MCP** connector to be active. It uses two tools from that connector:

- `list_meetings` — to retrieve meetings within the date window
- `get_meeting_by_id` — to get full transcripts for each meeting

No additional environment variables or configuration are required.

## Usage

Trigger the skill with any of these phrases:

- "Generate a trustworthiness report for [Name]"
- "Evaluate [Name]"
- "Trustworthiness report for [Name]"
- "Assess [Name]'s meeting performance"

The plugin will ask for the talent's name and the report period if not provided.

## Output

Reports are saved to a `Reports/` subfolder in the workspace as self-contained HTML files:

```
Reports/John-Smith-trustworthiness-march-2026.html
```

## Evaluation Criteria

1. **Credibility** — Authority and evidence-backed statements
2. **Reliability** — Follow-through on commitments
3. **Intimacy** — Rapport-building and empathy
4. **Group Thinking** — Collaboration and idea synthesis
5. **English Proficiency** — Grammar, vocabulary, and clarity
