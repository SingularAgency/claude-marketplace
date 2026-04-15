# qa-architect-agent

An autonomous QA agent for Singular Agency. Analyzes web applications (via repo or URL), generates a structured test plan for human sign-off, executes tests using Playwright headless Chromium, and reports bugs directly to GitHub — all without touching live systems until the plan is approved.

## Install

```
/plugin install qa-architect-agent@singular-agency-marketplace
```

## How It Works

The agent follows a 4-phase workflow, split into three skills:

1. **Plan** — Analyzes the repo (if provided) or the URL structure, then generates a test table (Happy Paths, Edge Cases, Error Handling). Stops and waits for your approval before doing anything else.
2. **Execute** — After approval, sets up Playwright, detects pre-installed Chromium, runs all tests in batches, captures screenshots on failures, and saves results to `/tmp/qa-results/`.
3. **Report** — Reads the results, deduplicates against existing GitHub issues, and opens one issue per unique FAIL with standardized formatting.

## Skills

| Skill | Trigger phrases | What it does |
|-------|----------------|--------------|
| `qa-architect-agent:plan` | "genera el plan de QA", "create a test plan for [URL]", "analyze this app for testing" | Analyzes repo or URL and produces an approvable test case table |
| `qa-architect-agent:execute` | "ejecuta los tests", "run the QA tests", "corre el plan" | Runs the approved plan with Playwright headless and saves results |
| `qa-architect-agent:report` | "reporta los bugs", "abre los issues en GitHub", "report failures" | Opens a deduplicated GitHub issue for each FAIL |

## Usage Example

```
User: genera el plan de QA para https://app.mycompany.com/auth/login
      email: admin@mycompany.com  password: MyPass123

→ [plan skill generates test table with 23 cases]
→ "Confirmo"
→ [execute skill runs all tests, saves screenshots]
→ "reporta los bugs en owner/repo"
→ [report skill opens GitHub issues for each FAIL]
```

## Requirements

- A running web application (URL accessible from the Claude sandbox)
- Login credentials (email + password)
- GitHub MCP configured with a valid token (for the `report` skill)
- Optionally: a GitHub repo URL for Phase 1 static analysis

## Notes

- Credentials are read from the conversation context and passed as environment variables — never hardcoded in scripts.
- Playwright automatically detects pre-installed Chromium at `/opt/pw-browsers/` or `/opt/google/chrome/` to avoid blocked CDN downloads.
- Tests run in batches of 5 to stay within memory and timeout limits.
- The agent never performs destructive DB writes, deletes, or schema changes.
