# OKR Story Drafter

Generate OKR-aligned user stories with responsible parties from meeting transcripts — automatically pulled from Read.ai.

## What it does

Given a meeting from Read.ai and a set of OKR objectives and key results, this plugin:

1. Asks you which meeting to use as reference (by name/client and date)
2. Asks you for your Objective and Key Results
3. Fetches the meeting transcript from Read.ai
4. Generates structured user stories grouped by Epic
5. Maps each story to its relevant Key Result(s)
6. Assigns responsible team members based on what was discussed

## Components

| Component | Name | Purpose |
|---|---|---|
| Skill | `okr-story-drafter` | Main skill — guides the full flow from meeting to user stories |

## Requirements

- **Read.ai** must be connected as an MCP tool (provides `list_meetings` and `get_meeting_by_id`)

## How to trigger

Say something like:
- "Genera las user stories de la reunión de [cliente] de ayer basadas en mis OKRs"
- "OKR story drafter"
- "Crea historias de usuario del sprint con responsable para cada uno"
- "Draft user stories from today's meeting mapped to our key results"

The skill will ask you two questions and then generate everything automatically.

## Output

A structured Markdown document saved to your outputs folder containing:
- OKR summary table
- User stories grouped by Epic (each with acceptance criteria, responsible parties, and KR mapping)
- Responsibility summary table
- Pending sprint tasks

You can also request the output as a `.docx` file or a Slack message after generation.

## Author

Singular Agency — built with Cowork
