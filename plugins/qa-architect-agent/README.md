# qa-architect-agent v0.3.0

Autonomous QA agent for web apps. Analyzes your repo, generates a signed-off test plan, executes Playwright E2E tests with full screenshot evidence per test, produces an HTML dashboard, uploads screenshots to GitHub, and files bugs directly as GitHub issues with inline screenshot evidence.

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| plan | `/qa-architect-agent:plan` | Analyze repo + URL, generate test plan, wait for approval |
| execute | `/qa-architect-agent:execute` | Run approved plan — screenshots for every test + HTML dashboard |
| report | `/qa-architect-agent:report` | Upload screenshots to GitHub repo, file issues with inline evidence |

## Workflow

1. `/qa-architect-agent:plan` — provide URL + GitHub repo + credentials
2. Review test table, confirm or adjust
3. `/qa-architect-agent:execute` — screenshots per test, HTML dashboard
4. `/qa-architect-agent:report` — screenshots uploaded to repo, issues filed with evidence

## What's new in v0.3.0
- Screenshots uploaded to `qa-evidence/YYYY-MM-DD/` in the target repo
- Each GitHub issue includes an inline `![screenshot](url)` embedded in the body
- Existing issues get a new screenshot comment on every re-run

## Requirements
- Chrome/Chromium installed (auto-detected from puppeteer cache or system)
- GitHub Personal Access Token with `repo` scope saved in `~/.singular-agency-plugin-creator.json`

## By [Singular Agency](https://singularagency.co)
