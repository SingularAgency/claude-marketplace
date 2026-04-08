# Kickoff Presentation Template Structure

This is the locked template for all Singular kickoff presentations. Follow this structure exactly when generating the `inputText` for Gamma.

## Singular Logo

Use this URL for the Singular logo (dark background version, hosted on Gamma CDN):
```
https://cdn.gamma.app/389jz13d9d5tjcf/09f8238075d84ba08b1370e37f2b3db3/original/Logo__Singular_DarkBackground.png
```

## Slide-by-Slide Structure

### SLIDE 1 — COVER
```
Show the Singular logo at the top left.
Logo URL: https://cdn.gamma.app/389jz13d9d5tjcf/09f8238075d84ba08b1370e37f2b3db3/original/Logo__Singular_DarkBackground.png
Title: "Kickoff meeting"
Subtitle: "[PROJECT NAME]"
Dark background with blurry gradient aesthetic.
```

### SLIDE 2 — AGENDA
```
Title: "Agenda"
- **Welcome to Singular**: Introduction to Singular and overview of the team members who will be supporting the project.
- **[PROJECT NAME] Team Introduction**: Introduction of key [PROJECT NAME] stakeholders and a brief overview of expectations, objectives, and desired outcomes for the engagement.
- **Communication & Collaboration**: Alignment on communication channels, working cadence, and definition of primary points of contact to ensure smooth coordination.
- **Next Steps & Project Alignment**: Review of immediate next steps, key milestones, and confirmation of important dates moving forward.
```

### SLIDE 3 — WELCOME TO SINGULAR (divider)
```
Title: "Welcome to Singular"
Include the Singular logo.
Logo URL: https://cdn.gamma.app/389jz13d9d5tjcf/09f8238075d84ba08b1370e37f2b3db3/original/Logo__Singular_DarkBackground.png
Dark background with blurry gradient aesthetic.
```

### SLIDE 4 — WHAT WE ARE (2026)
```
Title: "What we are"
Subtitle: "AI Transformation Partner for SMBs"

Present these capabilities as a clean list:
- AI transformation strategy
- Co-Pilot™, OpenClaw, Omni Model™
- Claude Orchestrator™
- Agentic AI & automation
- Direction, Taste & Speed
- OKR-driven outcomes & ROI
- Partner → transformational

At the bottom, include the model statement:
MODEL: Revenue = outcomes × impact
```

### SLIDE 5 — COMMUNICATION CHANNELS
```
Title: "Communication Channels"
- **Slack**: day to day communication
- **Email**: invoicing and third parties
- **Google Meet**: weekly meetings
```

### SLIDE 6 — [PROJECT NAME] (divider)
```
Title: "[PROJECT NAME]"
Dark background with blurry gradient. Include these discussion prompts:
- Team Presentation
- What success looks like? 3, 6, 12 months?
- Biggest current frustration in operations?
- What are your expectations?
```

### SLIDE 7 — OKRs
```
Title: "OKRs"
Present TWO strategic objectives with their measurable Key Results.

[INSERT APPROVED OKRs HERE]

At the bottom of this slide, add a clickable link:
"View live OKRs in Singular Stories → [SINGULAR STORIES OKR LINK]"
```

### SLIDE 8 — NEXT STEPS
```
Title: "Next Steps"
[INSERT PROJECT-SPECIFIC NEXT STEPS HERE]
```

Next steps should typically include:
- A discovery/deep-dive session with the client's key stakeholder
- Team onboarding to the project's tech environment
- Sprint 1 scope definition and sprint starting date
- Phase 1 milestone alignment and review cadence
- Any client-specific action items from the most recent meeting

## Gamma Generate Parameters

Always use these parameters:
- **format**: `presentation`
- **numCards**: `8`
- **textMode**: `preserve`
- **textOptions**: `{"tone": "professional", "audience": "client stakeholders", "language": "en"}`
- **cardOptions**: `{"dimensions": "16x9"}`
- **imageOptions**: `{"source": "noImages"}`
- **additionalInstructions**: Include instructions about dark professional color scheme, Singular logo on cover and Welcome slides, no stock images, OKR slide visual clarity, and Singular Stories link.

## Gamma Folder

Always save to the "Kickoff Meetings" folder. Use `get_folders` with name "Kickoff" to find the folder ID before generating.
