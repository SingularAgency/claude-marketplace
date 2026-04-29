---
module: {{MODULE_NAME}}
audience: PMs, stakeholders, new devs
last-reviewed: {{DATE}}
status: draft
auto-detected: true
owner: "{{OWNER}}"
paths: {{PATHS}}
---

# {{MODULE_NAME_HUMAN}} Module

## Purpose

{{PURPOSE_PARAGRAPHS}}

> 2-3 paragraphs in plain language. What this module is for, why it exists, what business problem it solves. Pull from existing PRD / product docs where they exist. NOT a one-liner.

## Module flow

How users typically interact with this module:

```mermaid
flowchart LR
    {{MODULE_FLOW_DIAGRAM}}

    classDef person fill:#cce5ff,stroke:#0066cc,color:#003366
    classDef warn fill:#fff3cd,stroke:#ff9900,color:#664d03
    classDef good fill:#d4edda,stroke:#28a745,color:#155724
    classDef neutral fill:#e9ecef,stroke:#6c757d,color:#212529
```

> Convention: `:::person` for human actors (blue), `:::good` for positive outcomes (green), `:::warn` for cautionary states (amber), `:::neutral` for terminal-but-not-bad states (grey).
> **No parentheses inside `|...|` edge labels** — Mermaid parses `(` as a node-shape delimiter and the diagram breaks. Use em-dashes: `|Manual — QA Engineer|`.

## Capabilities

{{CAPABILITIES_LIST}}

> Plain-English bullets describing **what users can DO**, not how the code does it. NO file paths, NO line numbers, NO endpoints, NO SQL. Use plain verbs (Create, Edit, Filter, Promote, Run, Attach, Configure…).

## Data Model

{{DATA_MODEL_TABLES}}

> This section IS allowed to be technical. Tables, columns, types, FKs, constraints, indexes. Cite the migration that introduced each table.

## Connections (this module ↔ others)

{{CONNECTIONS_SUBSET}}

> A specific subset relevant to this module — what it consumes, what it exposes, what events it publishes/subscribes. Cite path:line. Don't say "see global"; pull the relevant content inline.

## Business Rules

{{BUSINESS_RULES_LIST}}

> Each rule = one short paragraph with: rule statement (in policy language, not code), Owner (auto-filled from git first-commit author with caveat to verify with team), Origin (commit reference). **NO `Implementation:` line, NO `Revisable:` line, NO `Exceptions:` line** — these are 100% human-only context. Add inline if and when the team fills them.

## Actors

{{ACTORS_LIST}}

> - **Human actors:** infer real roles from route patterns, role checks, UI affordances. Don't say `{{TBD}}`. Cite specific role-check evidence.
> - **External systems:** be specific (Supabase tables, AI providers, GitHub, Slack, etc.).
> - **Other modules:** which call into this one, which it calls.

## User journey maps

How each actor experiences this module, step by step. Satisfaction scores (0-5) reflect typical pain or delight at each step.

{{USER_JOURNEYS}}

> One Mermaid `journey` diagram per real actor of the module (read the Actors section above to identify them).
> Format per actor:
>
> ```
> ### <Actor name> — <one-line goal>
>
> ```mermaid
> journey
>     title <Actor>: <what they're trying to do>
>     section <Phase 1>
>       <Step description>: <0-5>: <Actor>
>       <Step description>: <0-5>: <Actor>
>     section <Phase 2>
>       <Step description>: <0-5>: <Actor>
> ```
>
> (Optional 1-2 sentence note on a key pain or delight point)
> ```
>
> Rules:
> - Each diagram has 2-4 sections with 2-4 steps each.
> - Steps in plain English from the actor's perspective. NO endpoints, NO file paths, NO database mentions.
> - Realistic satisfaction (5=delight, 1=real friction). Mix scores. All-5s is unrealistic.
> - Same exact actor name across all rows of one diagram.
> - **No colons inside step text** — Mermaid splits step lines on `:`. Use em-dashes inside step text.

## Related workflows

End-to-end flows this module participates in. Diagrams, happy paths, and edge cases live in the `workflows/` folder — this module just lists which flows touch it.

{{RELATED_WORKFLOWS_LINKS}}

> Each link = `[`workflows/<flow>.md`](../workflows/<flow>.md) — <one-line role>`. NO duplication of the workflow diagrams here.
