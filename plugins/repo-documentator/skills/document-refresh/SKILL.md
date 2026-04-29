---
name: document-refresh
description: >
  Incremental documentation update. Reads the cursor stored by document-init in
  docs/.business-docs-state.json, computes git log <cursor>..HEAD, identifies which
  modules and workflows have changed, regenerates only those, advances the cursor,
  and opens a pull request. No user questions. Use when the user says "refresh the
  docs", "update the documentation", "what changed since the last doc", "rerun the
  doc generation", or after a sprint of code changes.
metadata:
  version: "0.4.0"
  author: "Singular Innovation"
---

# document-refresh

Incremental, cursor-based documentation update. Picks up exactly where the last `document-init` (or `document-refresh`) left off, processes only what changed in the code since then, and opens a PR with the updates.

## Core principles

- **Cursor-based, not heuristic.** The state file `docs/.business-docs-state.json` carries an exact commit SHA. We compute `git log <cursor>..HEAD` to find the diff. No guessing from `last-reviewed` dates.
- **Only regenerate what changed.** If nothing in `lib/billing/` changed, `modules/billing.md` is left alone — including its `last-reviewed` date.
- **Diff-merge.** User-edited content (sections without `auto-detected: true`) is preserved. Only auto-detected sections get rewritten.
- **No user questions.** Drift is reported, refresh is applied, PR is opened.

## Pre-conditions
- `docs/.business-docs-state.json` exists (the repo was initialized with `document-init`).
- The current branch matches `state.repo.default_branch`. (If not, refuse — tell the user to switch branch.)
- The `cursor` commit still exists in the repo (else fall back — see Failure modes).

## Flow

### Step 1: load the state file
Read `docs/.business-docs-state.json`. Validate `schema_version`. If missing, stop with: "No state file found. Run `document-init` first."

If `plugin_version` in the state is older than the running plugin and the schema has incompatibilities, run a versioned migration. If migration fails, stop and tell the user to re-init.

### Step 2: compute what changed
```bash
CURSOR=$(jq -r .last_run.commit_sha docs/.business-docs-state.json)
HEAD=$(git rev-parse HEAD)
if [ "$CURSOR" = "$HEAD" ]; then
  # Nothing changed since last analysis. Tell the user, exit cleanly.
  exit 0
fi
git log --name-only --pretty=format:"=== %h %s" "$CURSOR..HEAD" > /tmp/changes.txt
```

If the cursor doesn't exist (force-push, rebase), see Failure modes.

### Step 3: classify changed files
For each changed file, determine which module(s) it belongs to by matching against `state.modules[].paths`. A single file may map to multiple modules (e.g. a shared schema). Track:
- **Modules affected**: union of all matched modules
- **Workflows affected**: any workflow whose `entry_points` overlap with changed files
- **Connection map invalidations**: any cross-module edge that involves a changed file → trigger `document-connections`
- **Unmapped files**: changes that don't fit any known module — could be new module candidates. List them in the drift report for review (don't auto-create modules in refresh; that's `document-init`'s job).
- **New migrations** (`scripts/*.sql` or equivalent): always trigger refresh of the module(s) that own the migration.

### Step 4: write a drift report (visible)
Write `docs/_DRIFT_REPORT.md` summarizing:

```markdown
# Drift report — <today>

## Cursor
- Previous: `<old-sha>` (<date> — "<old subject>")
- Current:  `<new-sha>` (<date> — "<new subject>")
- Range:    <N> commits, <M> files changed

## What's being refreshed
### Modules (<count>)
- `test-runs` — 12 files changed (path:`lib/test-runs/`, etc.)
- `repo-analysis` — 4 files changed
- ...

### Workflows (<count>)
- `agent-driven-test-run` — entry point changed (`app/api/v1/agent/auth/route.ts`)
- ...

### Connections
- Re-running `connection-analyst` because cross-module edges may have shifted.

## What's NOT being refreshed
### Modules untouched (<count>)
- `metrics` — no changes in scope
- `evidence` — no changes in scope

### Unmapped changes (review needed)
- `lib/realtime/` — 3 files changed but no module owns these paths.
  Possibly a new module — consider running `document-init` for this directory or extending an existing module's `paths`.
- `.github/workflows/ci.yml` — CI config; not a business module.

## Stale flags
Files with `last-reviewed` > 90 days that the cursor didn't touch:
- `modules/sprints.md` (last-reviewed 142 days ago)
  Status flag bumped to `stale`. No content rewrite.
```

### Step 5: regenerate affected modules
For each affected module, run the same logic as `document-module` (read code, regenerate Capabilities, Data Model, Connections, Business Rules, Actors, User journey maps). Diff-merge against existing user edits.

Update each module's `last-reviewed` to today.

### Step 6: regenerate affected workflows
For each affected workflow, run the logic of `document-workflow` (re-trace from entry points, refresh Business view + Technical sequence + Happy path + Edge cases). Diff-merge.

### Step 7: refresh connections (if needed)
If any cross-module file changed, invoke `connection-analyst` and refresh `docs/connections.md` plus the `Connections` section of each affected module.

### Step 8: handle structural drift
- **New module** detected (unmapped files cluster in a new directory) → flag in the drift report. Do NOT auto-create. The user runs `document-init` if they want it added.
- **Removed module** (all paths deleted) → move `modules/<slug>.md` to `docs/_archive/` with a frontmatter note (`status: archived, archived_at: <today>, archived_in_commit: <sha>`). Don't delete.
- **Path moved** (file renamed) → update `state.modules[].paths` and the module's frontmatter `paths:` field; no content rewrite needed if the renamed file's content is the same.

### Step 9: lint Mermaid
Same as `document-init`:
1. No parens inside `|...|` edge labels in flowcharts.
2. No colons inside step text in `journey` diagrams.

### Step 10: update the state file
Move the cursor forward:
- `last_run.skill = "document-refresh"`
- `last_run.commit_sha = HEAD`
- `last_run.ran_at = <now>`
- For each module that was actually regenerated → bump `last_regenerated_commit` to HEAD.
- Modules that were checked but didn't need a refresh → leave their `last_regenerated_commit` alone.
- Same for workflows.

### Step 11: update the visible cursor line
Update the cursor line at the top of `docs/_AUTOGENERATED.md`:

> **Analyzed up to commit `<new-short-sha>` (`<new-date>` — "<new-subject>") on branch `<branch>`.**

### Step 12: open the pull request
Follow `${CLAUDE_PLUGIN_ROOT}/skills/document-init/references/pr-flow.md`. In short:
1. `git checkout -b business-docs/refresh-<YYYYMMDD-HHMM>`
2. `git add docs/`
3. Commit: `docs: refresh — <N> modules, <M> workflows, cursor advanced to <new-short-sha>`
4. `git push -u origin <branch>`
5. `gh pr create` with body = `docs/_DRIFT_REPORT.md`.

If no commits accumulated (clean refresh, but cursor advanced) → still open the PR with just the state file update so the cursor moves forward. Empty content refreshes are fine — they prove the docs are current.

If absolutely nothing to commit (cursor was already at HEAD) → skip the PR and tell the user the docs are already up-to-date.

If no credentials, fall back to local-only and print manual push/PR steps.

### Step 13: report
Print to the user:
- **PR URL** (or "no drift detected") or local path + manual steps
- Cursor advancement: `<old-sha>` → `<new-sha>`
- Modules refreshed (count + names)
- Workflows refreshed (count + names)
- Unmapped changes flagged for review (count)
- Stale flags applied (count)

## Failure modes

### Cursor commit no longer exists in repo
Force-push or rebase has removed the cursor. `git log <cursor>..HEAD` fails.
**Behavior:** Warn the user. Fall back to a path-based diff (compare `state.modules[].paths` against the current file tree). Regenerate any module whose paths changed structurally. Reset the cursor to current HEAD. Note in the drift report that history was rewritten.

### Current branch ≠ `state.repo.default_branch`
**Behavior:** Refuse to run. Tell the user to switch branch or update the state file's branch field manually if they intentionally changed branches.

### `state.plugin_version` is older than running plugin and migration is needed
**Behavior:** Run versioned migration. If incompatible, stop and ask user to re-init.

### Missing state file
**Behavior:** Stop with a clear error: "No state file found at `docs/.business-docs-state.json`. The repo wasn't initialized — run `document-init` first."

## Rules

- **No user questions** except on real configuration mismatches (branch, missing state).
- **Don't touch user-edited content** (frontmatter without `auto-detected: true`).
- **Don't delete historical docs.** Archived modules go to `_archive/` with a note.
- **Always advance the cursor** when the run completes successfully — even for empty refreshes, the cursor must move so the next run uses the right baseline.
- **Always open a PR** when there's anything to commit.
- **Lint Mermaid** before writing.
- Operate in English by default.
