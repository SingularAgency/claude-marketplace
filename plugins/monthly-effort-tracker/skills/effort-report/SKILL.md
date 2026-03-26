---
description: Generates a monthly effort breakdown table by project based on Google Calendar meetings. Triggered by phrases like "genera mi reporte de esfuerzo", "cuánto tiempo dediqué a cada proyecto este mes", "tabla de esfuerzo del mes", "effort report", "distribución de esfuerzo por proyecto", "breakdown de reuniones por proyecto", "cuántas reuniones tuve por cliente este mes".
---

Generate a monthly effort breakdown report for the user based on their Google Calendar meetings.

## Step 1 — Ask for the target month

Ask the user which month and year they want to analyze (e.g., "marzo 2026", "febrero 2026"). Accept natural language like "este mes", "el mes pasado", "last month", or a specific month name.

Resolve relative references using today's date. For "este mes" use the current month; for "el mes pasado" use the previous month.

## Step 2 — Fetch calendar events

Use `gcal_list_events` with:
- `timeMin`: first day of the target month at 00:00:00
- `timeMax`: last day of the target month at 23:59:59
- `timeZone`: America/New_York (or infer from context if known)
- `maxResults`: 250

If the response includes a `nextPageToken`, fetch subsequent pages until all events are retrieved.

## Step 3 — Filter events

Keep only events that meet ALL of these criteria:
- `allDay` is false
- `myResponseStatus` is NOT "declined"
- The event is meeting-like and not clearly administrative/internal (project mapping and new-project detection both happen in Step 4 — do NOT filter by project keyword here)

Exclude events that are clearly internal/administrative, such as: PO meetings, Accountability, Healthscore review, Plugins Workshop, personal appointments, birthday events, or generic syncs with no project name.

## Step 4 — Map events to projects

For each event, attempt to match its title against known project keywords (case-insensitive). Use the following mapping logic:

- "Lunch Bunch" → Lunch Bunch
- "ProDriven" or "Pro Driven" → ProDriven
- "VITL" → VITL
- "Housing Research" → Housing Research
- "Perry Construction" → Perry Construction
- "Velvet Verify", "Velvel Verify", "Claudia Raymond Velvet", "Velvet Onboarding", "Velvet Alignment" → Velvet Verify
- "Leadership SOP", "Leader SOPs", "LeaderShip SOP", "Leadership Sync" → Leadership SOP
- "Search Me" → Search Me
- "Bloomer Health" or "Blommer Health" → Bloomer Health
- "Manifestasia" → Manifestasia
- "Pfabes" → Pfabes
- "Fed Up" → Fed Up
- "Control" (only if followed by a client name or "Stand Up") → Control
- "FiFutures" → FiFutures

**Detecting new projects:** For events that don't match any known keyword, check if the title follows a pattern suggesting a project meeting (e.g., contains "X Singular", "Interna", "Internal", "Sync", "Client Review", "Demo", "Onboarding", "Kick Off", "Sprint Planning"). If so, extract the likely project name from the title and add it as a new project marked with ⭐. Events that match neither a known project nor a meeting-like pattern are silently discarded.

## Step 5 — Count and calculate

Count the number of meetings per project. Calculate the percentage as `(project_meetings / total_meetings) * 100`, rounded to the nearest whole number.

## Step 6 — Display the table in chat

Show the results as a markdown table with these columns:

| Proyecto | # Reuniones | Esfuerzo calculado |
|---|---|---|
| ... | ... | ...% |

Sort by number of meetings descending. Show the total row at the bottom. Mark new projects (not in the standard list) with ⭐.

## Step 7 — Generate the Excel file

Create an `.xlsx` file at `/sessions/.../mnt/outputs/esfuerzo_<mes>_<año>.xlsx` using openpyxl with the following structure:

**Columns:**
- A: Proyecto
- B: # Reuniones (blue font — hardcoded input)
- C: % porcentaje de esfuerzo estimado (blank — for the user to fill manually)
- D: Esfuerzo calculado según numero de reuniones (formula: `=IF(B{total_row}=0,0,B{row}/B{total_row})`, format as `0%`)

**Formatting:**
- Header row: dark blue fill (`1F4E79`), white bold Arial font, centered, wrapped text
- Total row: light blue fill (`D6E4F0`), bold font
- New projects (⭐): light yellow fill (`FFF2CC`), italic font
- All cells: thin gray border, Arial 10pt
- Column widths: A=24, B=14, C=26, D=30
- Freeze top row

Add a note below the table: `* Proyectos nuevos detectados en <mes> <año>`

After saving, open the file with `openpyxl` in `data_only=False` mode and verify that column D contains formulas (not hardcoded values) as a basic correctness check.

## Step 8 — Share the file

Provide a `computer://` link to the generated file and a one-line summary:

> Aquí está tu reporte de esfuerzo de [mes]: [N] reuniones totales en [X] proyectos. [Y] proyectos nuevos detectados ⭐.
