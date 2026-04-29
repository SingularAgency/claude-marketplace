---
audience: PMs, stakeholders, new devs, support
last-reviewed: {{DATE}}
status: draft
owner: {{OWNER}}
---

# {{PROJECT_NAME}}

## What this is, in one sentence
{{ELEVATOR_PITCH}}

## Business problem it solves
{{BUSINESS_PROBLEM}}

## Who it serves
{{PRIMARY_USERS}}

## Module map

```mermaid
{{MODULE_MAP_DIAGRAM}}
```

| Module | Business responsibility | Owner |
|---|---|---|
{{MODULE_TABLE}}

## Critical workflows

The most important end-to-end processes (cross several modules):

{{WORKFLOW_LIST}}

## How to navigate this documentation

- **Understand the business** → start here and in `glossary.md`
- **Understand a module** → `modules/<name>/purpose.md`
- **Understand a process** → `workflows/<name>.md`
- **Understand how everything connects** → `connections.md`
- **Understand a historical decision** → `decisions/`

## What's NOT here

This documentation **does not describe how the code works** (the AI reads that directly from the repo). It describes the **business why**, the **real workflows** (including human steps), and **decisions**.
