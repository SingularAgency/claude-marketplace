---
name: okr-story-drafter
description: >
  Use this skill when the user wants to generate user stories from a meeting transcript mapped to OKR objectives and key results.
  Trigger phrases include: "genera user stories", "crea historias de usuario", "okr story drafter",
  "user stories de la reunión", "basado en la reunión genera historias", "stories del sprint",
  "historias con responsable", "genera el backlog desde la reunión", "draft user stories from meeting".
  Also trigger when the user mentions a meeting name alongside OKRs or key results.
metadata:
  version: "0.1.0"
  author: "Singular Agency"
---

## OKR Story Drafter

Generate structured, OKR-aligned user stories with responsible parties from a meeting transcript retrieved from Read.ai.

### Step 1: Ask for the meeting reference

Use AskUserQuestion to ask the user which meeting to use as the reference. Ask for:
- The name or client of the meeting (e.g., "Pfabes", "FiFutures", "Velvet")
- The date of the meeting (e.g., "hoy", "ayer", a specific date, or "la más reciente")

Present this as a single question so the user can answer both at once. Example prompt:
> "¿De qué reunión quieres generar las user stories? Dime el nombre del proyecto/cliente y si fue hoy, ayer, u otra fecha."

### Step 2: Ask for the Objective and Key Results

Use AskUserQuestion to collect the OKR data. Ask the user to provide:
- The **Objective** (the high-level goal)
- The **Key Results** (KR1, KR2, KR3... — as many as they have)

Suggest they paste them directly. Example prompt:
> "Ahora dime el Objetivo y los Key Results que quieres usar para mapear las historias. Puedes copiarlos tal como los tienes."

Parse the user's free text to extract:
- `objective`: the main objective statement
- `key_results`: array of KR strings with their descriptions

### Step 3: Find the meeting in Read.ai

Use `list_meetings` from Read.ai to search for the meeting:
- For "hoy" → use today's date range `YYYY-MM-DDT00:00:00Z` to `YYYY-MM-DDT23:59:59Z`
- For "ayer" → use yesterday's date range
- For specific dates → compute the range accordingly
- If no date given → search the last 7 days

Filter results to find the meeting whose title matches the name or client the user mentioned.

If multiple matches are found, use AskUserQuestion to let the user pick which one.
If no match is found, expand the search to the last 14 days and try again.

### Step 4: Fetch the transcript

Use `get_meeting_by_id` with:
```yaml
expand: ["transcript", "action_items", "summary"]
```

Use `transcript` as the primary source for story generation.
Use `action_items` to identify pending tasks and map them to stories.
Use `summary` as context if the transcript is very long.

### Step 5: Generate User Stories

Analyze the transcript and generate user stories following the format in `references/user-story-format.md`.

For each story:
1. Identify a clear user need or feature discussed in the meeting
2. Write it in standard user story format: *"Como [rol], quiero [acción], para que [beneficio]"* (or in English if the user prefers)
3. Define acceptance criteria based on what was discussed
4. Assign responsible team members based on who was mentioned for each task
5. Map it to the most relevant Key Result(s) from the OKRs provided

**Grouping**: Organize stories into Epics based on thematic groupings from the meeting (e.g., "Chat & Safety", "Service History", "Quality Assurance", "Discovery & Onboarding").

**Responsible parties**: Extract participant names from the transcript. If a person is mentioned as owner of a task, assign them. If multiple people are involved, list all with their specific sub-responsibilities (Backend, Frontend, Design, QA).

**KR mapping**: For each story, determine which Key Result it most directly contributes to. A story may contribute to multiple KRs — list the primary and secondary ones.

### Step 6: Output the user stories

Present the user stories in a well-structured markdown document saved to the outputs folder.

The document must include:
- Header with project name, meeting date, and sprint context
- OKR summary table (Objective + all Key Results)
- Stories grouped by Epic
- For each story: title, user story statement, acceptance criteria, responsible parties (with role), KR mapping
- A closing summary table: Responsible → Stories → Role

After presenting the output, offer to:
- Export it as a `.docx` file
- Post a summary to Slack
- Create the stories in a project management tool if connected

### Error handling

- If the meeting transcript is not yet available in Read.ai, inform the user and suggest they try again in a few minutes
- If the transcript is available but very sparse, use the summary and action_items instead
- If the user's OKR text is ambiguous, extract the best interpretation and confirm with the user before generating stories
- If no participants are mentioned for a task, mark the responsible as "Por definir"
