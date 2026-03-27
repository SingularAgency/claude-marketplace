---
name: generate-report
description: >
  Generate a Trustworthiness Report for a talent based on Read AI meeting transcripts.
  Use when the user asks to "generate a trustworthiness report", "evaluate a talent",
  "trustworthiness report for [name]", "talent evaluation for [name]",
  "review [name]'s performance in meetings", "assess [name]", or any request
  to score or evaluate a team member's meeting behavior using Read AI data.
metadata:
  version: "0.1.0"
---

# Trustworthiness Report Generator

Generate an evidence-based Trustworthiness Report for a named talent by analyzing their participation across Read AI meeting transcripts from the past month.

## Required Inputs

Before starting, collect two pieces of information from the user. Use AskUserQuestion if either is missing:

1. **Talent full name** — the person to evaluate
2. **Report month/year** — defaults to the current month if not specified

## Step 1: Retrieve Meetings from Read AI

Calculate a date window of exactly one month back from the current date. Use the Read AI MCP tools to pull meetings within that window.

1. Call `list_meetings` to get all meetings from the past 30 days.
2. For each meeting returned, call `get_meeting_by_id` to retrieve the full transcript.
3. Search each transcript for the talent's name — check speaker labels, participant lists, and raw transcript text. Use case-insensitive matching and try common name variants (e.g., first name only, full name, nickname if known).
4. Collect all meetings where the talent appears. Track the total count.

**If fewer than 3 transcripts are found**, flag this in the report as "Insufficient Data" and note the exact count. Still evaluate what is available, but add a warning banner to the HTML output.

## Step 2: Evaluate Across 5 Criteria

Score each criterion on a scale of **1–10** (10 = Excellent, 1 = Poor). Base every score strictly on evidence found in the transcripts. Do not infer or assume behavior not documented in the transcripts.

Read the detailed scoring rubric in `references/scoring-rubric.md` before assigning scores.

### Criteria

1. **Credibility** — Does the talent speak with authority and back up statements with data, examples, or domain expertise?
2. **Reliability** — Does the talent follow through on commitments? Look for patterns: did they report completing tasks they previously committed to? Are there mentions of missed deadlines or incomplete work?
3. **Intimacy** — Does the talent build rapport and show empathy? Look for personal check-ins, supportive language, active listening cues, and relationship-building behavior.
4. **Group Thinking** — Does the talent collaborate effectively? Do they build on others' ideas, ask clarifying questions, facilitate discussion, and contribute to group problem-solving?
5. **English Proficiency** — Evaluate grammar, vocabulary range, clarity of expression, and ability to articulate complex ideas. Note any recurring patterns (e.g., filler words, unclear phrasing).

For each criterion, write a 2–3 sentence justification that cites the specific meeting(s) where the evidence was found. Use the meeting title or date as the citation.

## Step 3: Write Overall Feedback

Write one paragraph (3–5 sentences) of overall feedback that:

- Highlights the talent's strongest area
- Identifies one or two specific, actionable areas for improvement
- Gives a constructive suggestion for how to improve
- Maintains a professional, encouraging tone

## Step 4: Generate the HTML Report

Read the HTML template from `references/html-template.md` and populate it with the evaluation data.

Use the clean, minimal design specified in the template. The report must be fully self-contained (all CSS inline in a `<style>` block, no external dependencies).

### File naming convention

Save the file as: `[TalentName]-trustworthiness-[Month]-[Year].html`

- Replace spaces in the talent name with hyphens
- Month should be the full month name in lowercase (e.g., `march`)
- Year is 4 digits

Example: `John-Smith-trustworthiness-march-2026.html`

### Save location

Create a `Reports/` subfolder in the user's workspace if it does not already exist, and save the HTML file there. Present the file link to the user when done.

## Important Rules

- **Evidence only**: Every score must be backed by transcript evidence. Never fabricate or assume.
- **One month window**: Only analyze meetings from the past 30 days relative to the request date.
- **Insufficient data warning**: If fewer than 3 transcripts mention the talent, add a visible warning banner in the report.
- **Professional tone**: The report should be constructive and encouraging, never punitive.
- **Self-contained HTML**: No external CSS/JS dependencies. Everything inline.
