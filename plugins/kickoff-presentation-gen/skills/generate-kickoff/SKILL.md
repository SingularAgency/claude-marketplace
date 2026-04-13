---
name: generate-kickoff
description: >
  Generate a client kickoff presentation in Gamma following Singular's standard template.
  Use when the user says "create a kickoff presentation", "generate a kickoff deck",
  "kickoff for [project name]", "new kickoff presentation", "prepare kickoff slides",
  or any request to build a client kickoff deck for a new project.
metadata:
  version: "0.1.0"
  author: "Singular Agency"
---

# Generate Kickoff Presentation

Create a professional client kickoff presentation in Gamma using Singular's locked template, populated with project context from ReadAI meetings and strategic OKRs.

## Prerequisites

Ensure both **Gamma** and **ReadAI** MCP connectors are active. If either is missing, prompt the user to connect them via Settings > Connectors before proceeding.

## Workflow

### Step 1: Gather Project Information

Use AskUserQuestion to collect:

1. **Project name** — the client/project name (used for titles and meeting search)
2. **Singular Stories OKR link** — the URL to the project's OKR section in Singular Stories
3. **Any additional context** — anything the user wants to emphasize (e.g., specific goals, constraints, focus areas)

### Step 2: Research Project Context via ReadAI

Search ReadAI for meetings related to the project:

1. Use `list_meetings` to search recent meetings. Page through results until meetings matching the project name are found.
2. For each relevant meeting, use `get_meeting_by_id` with expand fields: `summary`, `chapter_summaries`, `action_items`, `key_questions`, `topics`.
3. Extract and synthesize:
   - **Client background** — who is the client, what do they do, what is their domain
   - **Product/project vision** — what are they building or transforming
   - **Phased roadmap** — what phases were discussed (stabilization, growth, monetization, etc.)
   - **Technical stack** — technologies, platforms, integrations mentioned
   - **Key stakeholders** — names, roles, emails of client contacts
   - **Priorities and constraints** — timeline, budget, competitive urgency
   - **Action items and next steps** — from the most recent meeting

If no meetings are found, ask the user to provide context directly or share meeting titles to search for.

### Step 3: Craft Strategic OKRs

This is the most important part. Act as a **strategist and expert consultant**, not a project manager.

Read `references/okr-guidelines.md` for detailed OKR crafting rules.

Key principles:
- OKRs must be **strategic**, not product/feature-oriented
- Focus on **business outcomes**: market validation, competitive positioning, investment readiness, risk reduction
- Every KR must have a **trackable metric** — percentages, rates, counts, scores, or zero-target thresholds
- Frame objectives around **why** we're building, not **what** we're building
- Align with Singular's positioning as an AI Transformation Partner (see `references/singular-positioning.md`)

Generate **2 strategic objectives**, each with **3 measurable key results**.

Present the OKRs to the user and get explicit approval before generating the presentation. Iterate if the user wants changes.

### Step 4: Generate in Gamma

Use the Gamma `generate` tool with the following parameters:

- **format**: `presentation`
- **numCards**: `8`
- **textMode**: `preserve`
- **textOptions**: `{"tone": "professional", "audience": "client stakeholders", "language": "en"}`
- **cardOptions**: `{"dimensions": "16x9"}`
- **imageOptions**: `{"source": "noImages"}`

Read `references/template-structure.md` for the exact slide-by-slide content structure. The `inputText` must follow that template precisely, substituting the project name, OKRs, and next steps.

Always save to the "Kickoff Meetings" Gamma folder. Use `get_folders` with name "Kickoff Meetings" to find the folder ID.

Include in `additionalInstructions`:
- Dark, professional color scheme with subtle gradient accents
- The Singular logo must appear on cover and Welcome slides (CDN URL in template reference)
- No stock images — text and logo only
- OKR slide must be visually clear with two distinct objectives
- Include the Singular Stories link at the bottom of the OKR slide

### Step 5: Deliver and Review

1. Share the Gamma URL with the user
2. Note that they may want to fine-tune the theme in Gamma's editor to match the exact dark gradient aesthetic
3. Confirm the Singular logo appears correctly (if not, instruct user to add it manually from the template)
4. Ask if any content adjustments are needed

## Important Notes

- Never skip the OKR approval step — always present OKRs to the user before generating
- If the user provides feedback on OKRs, iterate until they approve
- The presentation structure is locked — do not add or remove slides from the template
- Always include the Singular Stories OKR link on the OKR slide
