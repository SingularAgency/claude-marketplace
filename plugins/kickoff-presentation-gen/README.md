# Kickoff Presentation Generator

Generate professional client kickoff presentations in Gamma using Singular's standard template, ReadAI meeting context, and strategic OKRs.

## What it does

This plugin automates the kickoff presentation workflow:

1. Asks for the project name and Singular Stories OKR link
2. Searches ReadAI for relevant meetings and extracts project context
3. Crafts strategic, metric-driven OKRs (with your approval before generating)
4. Creates a Gamma presentation following Singular's locked 8-slide template
5. Saves to the "Kickoff Meetings" folder in Gamma

## Components

| Component | Name | Purpose |
|-----------|------|---------|
| Skill | `generate-kickoff` | Full kickoff presentation workflow |
| MCP | Gamma | Create presentations in Gamma |
| MCP | ReadAI | Pull meeting context for project research |

## Setup

### Required connectors

- **Gamma** — connect via Settings > Connectors (search "Gamma")
- **ReadAI** — connect via Settings > Connectors (search "Read AI")

Both must be connected before using the plugin.

### Gamma folder

Create a folder called "Kickoff Meetings" in Gamma to store generated presentations.

## Usage

Say any of these to trigger the skill:

- "Create a kickoff presentation for [project name]"
- "Generate a kickoff deck"
- "Kickoff for [project name]"
- "New kickoff presentation"
- "Prepare kickoff slides for [project name]"

The skill will guide you through the process and ask for your approval on OKRs before generating.

## Template

The presentation follows Singular's locked 8-slide structure:

1. Cover (with Singular logo)
2. Agenda
3. Welcome to Singular (divider)
4. What we are — AI Transformation Partner for SMBs
5. Communication Channels
6. [Project Name] (divider with discussion prompts)
7. OKRs (strategic objectives + Singular Stories link)
8. Next Steps
