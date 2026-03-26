# Monthly Effort Tracker

Analyzes your Google Calendar meetings for any month and generates a project effort breakdown — both as a chat table and a downloadable Excel file. Automatically detects new projects that weren't in previous months.

## Install

```bash
/plugin install monthly-effort-tracker@singular-agency-marketplace
```

## Skills

| Skill | Trigger phrases | What it does |
|-------|----------------|--------------|
| /effort-report | "genera mi reporte de esfuerzo", "tabla de esfuerzo del mes", "cuántas reuniones tuve por proyecto", "effort report", "distribución de reuniones" | Counts meetings per project for a chosen month and outputs a table + Excel file with effort percentages |

## How it works

1. Asks which month to analyze
2. Pulls all calendar events via Google Calendar
3. Maps each meeting to its project using keyword matching
4. Detects new projects automatically (marked with ⭐)
5. Displays the breakdown in chat and generates an `.xlsx` file ready to download

## Requirements

- Google Calendar MCP connected
- Excel skill available (for `.xlsx` generation)
