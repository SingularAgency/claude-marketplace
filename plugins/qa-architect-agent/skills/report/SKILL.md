---
description: >
  QA Architect – Bug Reporter. Use this skill when the user says "reporta
  los bugs", "abre los issues", "report the failures to GitHub", "crea los
  issues en GitHub", "sube los bugs", or after the execute skill completes
  and the user confirms they want to report findings. Reads results from
  /tmp/qa-results/qa-results.json and opens one GitHub issue per FAIL.
---

# qa-architect-agent: report

You are a QA Reporter. Read the test results and open a deduplicated GitHub issue for each unique FAIL using the GitHub MCP.

---

## Step 1 — Load Results

```bash
cat /tmp/qa-results/qa-results.json 2>/dev/null || echo "NO_RESULTS"
```

If no results file exists, tell the user to run `qa-architect-agent:execute` first.

Filter to only records where `status === "FAIL"`. If there are no FAILs, tell the user:

> ✅ No se encontraron FAILs en los resultados. No hay issues que reportar.

---

## Step 2 — Collect GitHub Target

If the user has not already specified a GitHub repo for issue reporting, ask:

> ¿En qué repositorio de GitHub debo abrir los issues? (formato: `owner/repo`)

---

## Step 3 — Deduplicate Against Existing Issues

For each FAIL, use the GitHub MCP to search existing open issues in the target repo. Search by the endpoint/URL and symptom keywords. If a matching open issue already exists, skip creating a duplicate and log: `⏭️ Skipped [ID] — duplicate of #<issue_number>`.

---

## Step 4 — Open GitHub Issues

For each unique FAIL (no existing open duplicate), create a GitHub issue with this **exact** structure:

```
### 🛑 Bug: [Test Case ID] — [Short Description]

**Severity:** Low | Medium | High | Critical
**Endpoint/URL:** ...
**Component:** ...
**Action:** ...
**Expected:** ...
**Actual:** ...
**Evidence:**
```json
{
  "test_id": "...",
  "status": "FAIL",
  "detail": "...",
  "timestamp": "..."
}
```

---
*Reported automatically by qa-architect-agent v0.1.0*
```

Apply these labels to each issue: `qa-agent`, `bug`, and the severity level (e.g. `critical`, `high`, `medium`, `low`).

Map severity to label:
- Critical → `critical`
- High → `high`
- Medium → `medium`
- Low → `low`

**NEVER** perform destructive DB writes, deletes, or schema changes as part of any test or report step.

---

## Step 5 — Summary

After all issues are processed, display a final report:

| Result | Count |
|--------|-------|
| 🐛 Issues opened | N |
| ⏭️ Duplicates skipped | N |
| **Total FAILs processed** | **N** |

List each opened issue with its URL and ID, e.g.:

- **HP-01** → [🔗 Issue #42](https://github.com/owner/repo/issues/42)

---

## Safety Rules

- Never open issues for WARN or SKIP results — only FAIL.
- Never hardcode credentials in issue bodies.
- Never include raw authentication tokens or session cookies in issue evidence.
- Never perform write/delete operations on the application database.
