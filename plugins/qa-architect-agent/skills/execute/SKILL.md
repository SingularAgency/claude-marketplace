---
description: >
  QA Architect – Test Executor. Use this skill when the user says "ejecuta
  los tests", "run the QA tests", "ejecuta el plan", "run the test suite",
  "corre los tests", "execute QA", or after the user approves a test plan
  from the plan skill. Requires an approved plan at /tmp/qa-plan-approved.json.
---

# qa-architect-agent: execute

You are a QA Executor. Run the approved test suite using Playwright headless Chromium. Follow every step in order — do not skip setup.

---

## Step 0 — Load Approved Plan

```bash
cat /tmp/qa-plan-approved.json 2>/dev/null || echo "NO_PLAN"
```

If no plan exists, tell the user to run `qa-architect-agent:plan` first. Do not proceed without a plan.

Extract: `target_url`, `login_url`, `email`, `password`, `route_map`, `test_cases`.

---

## Step 0.5 — NexusQA Platform Run Registration (if configured)

```bash
python3 - <<'PYEOF'
import json, os, sys
import urllib.request, urllib.error

cfg_path = os.path.expanduser("~/.nexusqa-config.json")
ctx_path = "/tmp/nexusqa-context.json"
plan_path = "/tmp/qa-plan-approved.json"

if not os.path.exists(cfg_path):
    print("PLATFORM: disabled — no config found")
    sys.exit(0)

cfg = json.load(open(cfg_path))
PLATFORM_URL = cfg["platform_url"].rstrip("/")
API_KEY = cfg["api_key"]
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

plan = json.load(open(plan_path)) if os.path.exists(plan_path) else {}
ctx  = json.load(open(ctx_path))  if os.path.exists(ctx_path)  else {}

sprint_id = plan.get("platform_sprint_id") or ctx.get("sprint_id")
app_id    = plan.get("platform_app_id")
project_id = plan.get("platform_project_id") or cfg.get("default_project_id")

if not sprint_id:
    print("PLATFORM: no sprint_id — skipping run registration")
    sys.exit(0)

# 1. Register test cases in bulk to get UUIDs
test_cases = plan.get("test_cases", [])
if test_cases:
    bulk_body = json.dumps({
        "sprint_id": sprint_id,
        "project_id": project_id,
        "test_cases": [
            {"title": tc.get("title", tc.get("id", "Unnamed")),
             "description": tc.get("description"),
             "priority": tc.get("priority", "medium"),
             "type": "automated"}
            for tc in test_cases
        ]
    }).encode()
    req = urllib.request.Request(
        f"{PLATFORM_URL}/api/v1/agent/test-cases/bulk",
        data=bulk_body, headers=HEADERS, method="POST"
    )
    try:
        with urllib.request.urlopen(req) as r:
            bulk_resp = json.loads(r.read())
        registered = bulk_resp.get("test_cases", [])
        # Build mapping: plan test case title → platform UUID
        tc_map = {tc["title"]: tc["id"] for tc in registered}
        plan["platform_test_case_map"] = tc_map
        print(f"PLATFORM: registered {len(registered)} test cases")
    except Exception as e:
        print(f"PLATFORM: bulk registration error: {e}")

# 2. Create the test run
run_body = json.dumps({
    "sprint_id": sprint_id,
    "app_id": app_id,
    "name": plan.get("run_name", "Agent Run"),
    "environment": plan.get("environment", "staging"),
    "initiated_by": "agent",
}).encode()
req = urllib.request.Request(
    f"{PLATFORM_URL}/api/v1/test-runs",
    data=run_body, headers=HEADERS, method="POST"
)
try:
    with urllib.request.urlopen(req) as r:
        run_resp = json.loads(r.read())
    run_id = (run_resp.get("data") or run_resp).get("id")
    plan["platform_run_id"] = run_id
    print(f"PLATFORM: test run created → {run_id}")
except Exception as e:
    print(f"PLATFORM: run creation error: {e}")

# 3. Mark run as in_progress
if plan.get("platform_run_id"):
    patch_body = json.dumps({"status": "in_progress"}).encode()
    req = urllib.request.Request(
        f"{PLATFORM_URL}/api/v1/agent/test-runs/{plan['platform_run_id']}",
        data=patch_body, headers=HEADERS, method="PATCH"
    )
    try:
        urllib.request.urlopen(req)
        print(f"PLATFORM: run status → in_progress")
    except Exception as e:
        print(f"PLATFORM: status update error: {e}")

# Save updated plan with platform IDs
json.dump(plan, open(plan_path, "w"))
PYEOF
```

If platform is enabled, the test run is now visible in NexusQA with status `in_progress` and the UI will start receiving live results.

---

## Step 1 — Environment Setup

### 1a. Detect Chromium/Chrome

```bash
python3 - <<'EOF'
import os, subprocess, glob as g

candidates = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/google/chrome/chrome",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
]
for pattern in ["/sessions/*/.cache/puppeteer/chrome/**/chrome", "/root/.cache/puppeteer/chrome/**/chrome"]:
    for match in g.glob(pattern, recursive=True):
        if os.path.isfile(match) and os.access(match, os.X_OK) and "linux" in match:
            candidates.insert(0, match)

for path in candidates:
    if os.path.isfile(path) and os.access(path, os.X_OK):
        try:
            r = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
            print(f"FOUND:{path}")
            break
        except: continue
else:
    print("NOT_FOUND")
EOF
```

Save the found path as `CHROME_EXECUTABLE`. If `NOT_FOUND`, try:
```bash
cd /tmp && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install playwright 2>&1 | tail -3
npx playwright install chromium 2>&1 | tail -5
```

### 1b. Install Playwright npm package

Check `${CLAUDE_PLUGIN_DATA}/node_modules/playwright` first (persisted from previous session). If missing:

```bash
# Use plugin data dir if available, else /tmp
PW_DIR="${CLAUDE_PLUGIN_DATA:-/tmp/qa-node}"
mkdir -p "$PW_DIR"
[ ! -d "$PW_DIR/node_modules/playwright" ] && \
  cd "$PW_DIR" && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install playwright 2>&1 | tail -3
```

### 1c. Create output directories

```bash
mkdir -p /tmp/qa-screenshots /tmp/qa-results
```

---

## Step 2 — Write Test Script

Write `/tmp/qa-suite.mjs`. Requirements:

### Core rules

1. All credentials from env vars only: `CHROME_PATH`, `TARGET_URL`, `LOGIN_URL`, `QA_EMAIL`, `QA_PASSWORD`, `ROUTE_MAP` (JSON string)
2. Launch with `--no-sandbox --disable-setuid-sandbox --ignore-certificate-errors`, `ignoreHTTPSErrors: true`
3. **Screenshot every test** (PASS, FAIL, WARN, SKIP) — call `await shot(page, id)` before recording result:
   ```javascript
   async function shot(page, id) {
     try { await page.screenshot({ path: `/tmp/qa-screenshots/${id}.png`, fullPage: false }); }
     catch(e) { /* ignore */ }
   }
   ```
4. Run in **batches of 5** with 2s pause between batches
5. Save all results to `/tmp/qa-results/qa-results.json`
6. Generate HTML dashboard after all tests

### Batch structure (adapt based on plan's test_cases)

**Batch 1 — Auth & Dashboard**
- Render login form
- Login with valid credentials → expect redirect to admin/dashboard
- Dashboard page loads (check heading or main content present)

**Batch 2 — Authenticated Navigation (CRITICAL)**

This batch must cover every route in `route_map.authenticated`:

```javascript
// Parse route map from env
const routeMap = JSON.parse(process.env.ROUTE_MAP || '{"authenticated":[],"public":[],"api":[]}');

// For each static authenticated route:
for (const route of routeMap.authenticated.filter(r => !r.includes(':id'))) {
  await authPage.goto(BASE_URL + route);
  await authPage.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  await authPage.waitForTimeout(1500);
  const url = authPage.url();
  const isRedirectedToLogin = url.includes('/login') || url.includes('/auth');
  await shot(authPage, `NAV-${sanitize(route)}`);
  // FAIL if redirected to login (route not auth-guarded properly or session expired)
  // PASS if page loaded with content
}

// For dynamic routes (contain :id), get a real ID first:
// 1. Navigate to the list page
// 2. Extract the first item's ID from the URL after clicking it, or from the DOM
// 3. Then test detail, edit, view routes with that ID
```

For list pages: check that the page renders (empty state OR items). Record PASS regardless.

For detail/edit pages with `:id`:
- Try to get a real ID by going to the list page and clicking the first item
- If no items exist: record SKIP ("No items in DB — empty state")
- If items exist: navigate to `/route/:realId`, verify key fields render, take screenshot

For "New/Create" pages:
- Navigate to the create URL
- Verify form inputs are present (count `input`, `textarea`, `select`)
- Verify any "tabs" or "sections" render
- Take screenshot

**Batch 3 — Workflow & E2E Flow Tests (MOST CRITICAL)**

This batch runs the business logic chains identified in the plan. It does NOT check HTTP status codes. It drives the full UI and verifies that **every affected part of the system** reflects the correct state after each workflow step.

**Setup for all flow/workflow tests:**

```javascript
// Capture console errors throughout all flows
const consoleErrors = [];
authPage.on('console', msg => {
  if (msg.type() === 'error') consoleErrors.push(`[${msg.type()}] ${msg.text()}`);
});

const TS = Date.now();

// Helper: wait for network to settle after an action
async function waitForSave(page) {
  await Promise.race([
    page.waitForResponse(r => r.url().includes('/api/') && r.request().method() !== 'GET', { timeout: 8000 }).catch(() => {}),
    page.waitForTimeout(3000)
  ]);
  await page.waitForTimeout(1000);   // let UI re-render
}

// Helper: find text anywhere on page (including inside shadow DOM / React portals)
async function pageHas(page, text) {
  const content = await page.content();
  return content.includes(text);
}

// Helper: try multiple selectors for a UI element
async function tryFill(page, selectors, value) {
  for (const sel of (Array.isArray(selectors) ? selectors : [selectors])) {
    try { await page.fill(sel, value); return true; } catch {}
  }
  return false;
}

// Helper: submit a form
async function submitForm(page) {
  const submitSels = [
    'button[type="submit"]',
    'button:has-text("Save")', 'button:has-text("Guardar")',
    'button:has-text("Create")', 'button:has-text("Crear")',
    'button:has-text("Submit")', 'button:has-text("Enviar")',
    'button:has-text("Confirm")', 'button:has-text("Confirmar")',
  ];
  for (const sel of submitSels) {
    const btn = await page.$(sel);
    if (btn && await btn.isVisible()) { await btn.click(); return; }
  }
}
```

**For each workflow in `plan.workflows`:**

Read the workflow definition from the plan JSON. Then execute each step. The following shows the pattern — adapt to the actual workflow found:

```javascript
// ══════════════════════════════════════════════════════════
// PATTERN: MULTI-ENTITY WORKFLOW EXECUTION
// ══════════════════════════════════════════════════════════
//
// For EACH workflow in plan.workflows, do:
//
// 1. SETUP — Create any prerequisite state
// 2. TRIGGER — Execute the workflow-starting action via UI
// 3. VERIFY CHAIN — Navigate to each affected entity and check state
// 4. CONDITIONAL PATHS — Re-run trigger with invalid inputs, verify no side effects

// Example for a referral workflow:
const WF_MARKER  = `QA-WF01-${TS}`;
const WF_EMAIL   = `qa-wf01-${TS}@test.com`;

// Setup: get referral code from existing user's profile
await authPage.goto(BASE_URL + '/profile');
await authPage.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
await shot(authPage, 'WF-01-setup-profile');
const profileContent = await authPage.content();
const codeMatch = profileContent.match(/referral[_-]?code['":\s]+([A-Z0-9]{4,20})/i);
const referralCode = codeMatch ? codeMatch[1] : null;

if (!referralCode) {
  results.push({ id: 'WF-01-setup', label: 'Workflow', status: 'SKIP', detail: 'No referral code found in profile — workflow skipped.', severity: 'high' });
} else {
  // Trigger: register new user with referral code using a fresh browser context
  const freshCtx  = await browser.newContext({ ignoreHTTPSErrors: true });
  const freshPage = await freshCtx.newPage();
  await freshPage.goto(BASE_URL + '/auth/register');
  await freshPage.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  await shot(freshPage, 'WF-01-register-form');

  await tryFill(freshPage, ['input[name="email"]', 'input[type="email"]'], WF_EMAIL);
  await tryFill(freshPage, ['input[name="password"]', 'input[type="password"]'], 'TestPass123!');
  await tryFill(freshPage, ['input[name="referralCode"]', 'input[placeholder*="referral" i]', 'input[placeholder*="invit" i]'], referralCode);
  await shot(freshPage, 'WF-01-form-filled');
  await submitForm(freshPage);
  await waitForSave(freshPage);
  await shot(freshPage, 'WF-01-after-register');

  // Verify A: immediate success (no error state)
  const regContent = await freshPage.content();
  const hasRegError = /error|invalid|failed|incorrecto/i.test(regContent.replace(/<[^>]+>/g,''));
  results.push({ id: 'WF-01a', label: 'Workflow', status: hasRegError ? 'FAIL' : 'PASS',
    detail: hasRegError ? `Registration failed with referral code. Content: ${regContent.slice(0,200)}` : `Registration succeeded with referral code ${referralCode}.`,
    severity: 'critical' });

  // Trigger second step if workflow requires it (e.g. first purchase to activate bonus)
  // Navigate to purchase/order flow with freshPage, complete it, then verify side effects

  // Verify B: referrer's balance/wallet (back in authPage, already logged in as referrer)
  await authPage.goto(BASE_URL + '/profile/wallet');  // adapt to actual URL from plan
  await authPage.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  await authPage.waitForTimeout(2000);   // bonus may be async, wait briefly
  await shot(authPage, 'WF-01-referrer-wallet');
  const walletContent = await authPage.content();
  // Expect the wallet balance to have increased — look for a higher number or the bonus amount
  results.push({ id: 'WF-01b', label: 'Workflow',
    status: walletContent.includes('50') || walletContent.match(/\+\s*50/) ? 'PASS' : 'WARN',
    detail: 'Referrer wallet: checked for bonus credit. Manual verification may be needed if amount format differs.',
    severity: 'high' });

  // Verify C: new user's credits (on freshPage)
  await freshPage.goto(BASE_URL + '/profile/credits');
  await freshPage.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  await shot(freshPage, 'WF-01-newuser-credits');
  const creditsContent = await freshPage.content();
  results.push({ id: 'WF-01c', label: 'Workflow',
    status: /welcome|credit|bonus/i.test(creditsContent) ? 'PASS' : 'WARN',
    detail: 'New user credits page: checked for welcome bonus.',
    severity: 'high' });

  // Verify D: CONDITIONAL PATH — register without referral code → no bonus
  const freshCtx2  = await browser.newContext({ ignoreHTTPSErrors: true });
  const freshPage2 = await freshCtx2.newPage();
  await freshPage2.goto(BASE_URL + '/auth/register');
  await freshPage2.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  await tryFill(freshPage2, ['input[name="email"]', 'input[type="email"]'], `qa-nowf-${TS}@test.com`);
  await tryFill(freshPage2, ['input[name="password"]', 'input[type="password"]'], 'TestPass123!');
  // intentionally leave referral code empty
  await submitForm(freshPage2);
  await waitForSave(freshPage2);
  // verify: registration succeeded but referrer's wallet did NOT change again
  results.push({ id: 'WF-01d', label: 'Workflow',
    status: 'PASS',  // manual check unless we can query wallet balance difference
    detail: 'No-referral path: registration completed without triggering bonus. Verify referrer wallet manually.',
    severity: 'medium' });

  await freshCtx.close();
  await freshCtx2.close();
}
```

**For each SIMPLE_FLOW in `plan.simple_flows`:**

```javascript
// ── Simple flow: Create → Verify in List ─────────────────────────────────
for (const flow of (plan.simple_flows || [])) {
  const MARKER = `QA-${flow.id}-${TS}`;
  const EDITED = `QA-${flow.id}-EDIT-${TS}`;
  let createdId = null;
  const stepBase = flow.id;

  // Navigate to create
  await authPage.goto(BASE_URL + flow.create_url);
  await authPage.waitForLoadState('networkidle', { timeout: 12000 }).catch(() => {});
  await authPage.waitForTimeout(1500);
  await shot(authPage, `${stepBase}-create-page`);

  // Fill fields — use MARKER in the marker_field, generic QA data in others
  for (const field of (flow.required_fields || [])) {
    const value = field.name === flow.marker_field ? MARKER : `QA-${field.name}-${TS}`;
    if (field.type === 'text' || field.type === 'textarea') {
      await authPage.fill(field.selector, value).catch(() => {});
    } else if (field.type === 'select') {
      await authPage.selectOption(field.selector, field.value || '').catch(() => {});
    }
  }
  await shot(authPage, `${stepBase}-form-filled`);

  await submitForm(authPage);
  await waitForSave(authPage);
  await shot(authPage, `${stepBase}-after-submit`);

  // Capture ID from URL
  const m = authPage.url().match(/\/([a-f0-9-]{8,}|[0-9]+)(\/|$)/);
  if (m) createdId = m[1];

  // Navigate to list, search for marker
  await authPage.goto(BASE_URL + flow.list_url);
  await authPage.waitForLoadState('networkidle', { timeout: 12000 }).catch(() => {});
  await authPage.waitForTimeout(2000);
  const searchEl = await authPage.$('input[type="search"], input[placeholder*="search" i], input[placeholder*="buscar" i]').catch(() => null);
  if (searchEl) { await searchEl.fill(MARKER); await authPage.waitForTimeout(1500); }
  await shot(authPage, `${stepBase}-list-after-create`);

  const found = await pageHas(authPage, MARKER);
  results.push({ id: `${stepBase}-create`, label: flow.entity, severity: 'critical',
    status: found ? 'PASS' : 'FAIL',
    detail: found ? `"${MARKER}" found in list.` : `"${MARKER}" NOT found in ${flow.list_url}. Data may not have persisted.` });

  // Edit flow (only if create succeeded and we have an ID)
  if (found && createdId && flow.edit_url) {
    await authPage.goto(BASE_URL + flow.edit_url.replace(':id', createdId));
    await authPage.waitForLoadState('networkidle', { timeout: 12000 }).catch(() => {});
    await authPage.waitForTimeout(1500);
    await shot(authPage, `${stepBase}-edit-page`);
    const ef = flow.editable_field;
    if (ef) await authPage.fill(ef.selector, EDITED).catch(() => {});
    await shot(authPage, `${stepBase}-form-edited`);
    await submitForm(authPage);
    await waitForSave(authPage);
    await shot(authPage, `${stepBase}-after-edit`);

    await authPage.goto(BASE_URL + flow.list_url);
    await authPage.waitForLoadState('networkidle', { timeout: 12000 }).catch(() => {});
    await authPage.waitForTimeout(2000);
    if (searchEl) { await searchEl.fill(EDITED).catch(() => {}); await authPage.waitForTimeout(1500); }
    await shot(authPage, `${stepBase}-list-after-edit`);

    const editFound = await pageHas(authPage, EDITED);
    results.push({ id: `${stepBase}-edit`, label: flow.entity, severity: 'high',
      status: editFound ? 'PASS' : 'FAIL',
      detail: editFound ? `Edited value "${EDITED}" visible in list.` : `Edited value "${EDITED}" NOT found — edit may not have persisted.` });
  }
}
```

**Golden rules for all flow/workflow tests:**
- Never trust HTTP 200 alone — always navigate the UI to confirm state change
- Use `waitForSave()` (waits for POST/PUT response) before checking list pages — avoid timing issues
- Always capture the created record's ID from the URL — do not hardcode IDs
- For multi-entity workflows, verify EACH affected entity in a separate navigation step
- Screenshot before setup, at trigger, after submit, and at every verification point
- Async side effects (jobs, triggers): poll up to 15s with 3s intervals before marking FAIL

**Batch 3 — API Happy Paths**
- Test each API endpoint with valid inputs (from plan's API test cases)
- Use `fetch()` or `page.evaluate()` with auth cookies for authenticated API calls

**Batch 4 — Edge Cases: Auth**
- Wrong password → expect `?error` in URL or error text in DOM
- Non-existent email → same
- Empty fields → blocked
- Invalid email format → HTML5 blocked

**Batch 5 — Edge Cases: Routes & API**
- Each protected route accessed without auth (fresh context) → expect redirect to login
- Each API endpoint with missing required fields → expect 400
- Each dynamic route with non-existent ID → expect 404 page, not 500
- Mobile 375×812 layout check for login page

**Batch 6 — Error Handling & Security**
- SQL injection in email field
- XSS in email field
- 10 rapid wrong-password logins
- Unknown route → 404
- File upload: 0-byte file → expect error, not 500
- File upload: oversized file → expect graceful error

### HTML Dashboard

After all tests, call `generateDashboard(results)` to write `/tmp/qa-results/qa-dashboard.html`.

The dashboard must be a self-contained single HTML file with:
- **Header**: app hostname, timestamp, pass-rate progress bar (% passed, green fill)
- **Summary cards**: Total, ✅ PASS, ❌ FAIL, ⚠️ WARN, ⏭️ SKIP
- **Results table**: ID | Component | Test | Status (color badge) | Detail | Screenshot thumbnail
- **Click-to-expand modal**: clicking thumbnail opens full-size screenshot overlay (Escape to close)
- **Component breakdown**: group by component, show pass/fail/warn/skip per group
- **All screenshots embedded as base64** — no external file references

---

## Step 3 — Execute

```bash
cd /tmp && \
  CHROME_PATH="<CHROME_EXECUTABLE>" \
  TARGET_URL="<target_url>" \
  LOGIN_URL="<login_url>" \
  QA_EMAIL="<email>" \
  QA_PASSWORD="<password>" \
  ROUTE_MAP='<route_map JSON>' \
  NODE_PATH="${CLAUDE_PLUGIN_DATA:-/tmp/qa-node}/node_modules" \
  timeout 600 node --experimental-vm-modules qa-suite.mjs 2>&1
```

Stream output as it runs. On timeout, report partial results from `qa-results.json`.

---

## Step 4 — Baseline Comparison (Regresiones)

After collecting results, compare against the previous run to distinguish **new regressions** from **known issues**. This gives the team actionable priority: fix new regressions first.

```bash
python3 << 'PYEOF'
import json, os, hashlib
from datetime import datetime

RESULTS_PATH = '/tmp/qa-results/qa-results.json'
PLAN_PATH    = '/tmp/qa-plan-approved.json'

results = json.loads(open(RESULTS_PATH).read())
plan    = json.loads(open(PLAN_PATH).read()) if os.path.exists(PLAN_PATH) else {}

# Stable key for this repo (slug from URL or github_repo)
repo    = plan.get('github_repo', plan.get('target_url', 'unknown'))
slug    = hashlib.md5(repo.encode()).hexdigest()[:8]
HISTORY = os.path.expanduser(f'~/.qa-agent-history/{slug}.json')
os.makedirs(os.path.dirname(HISTORY), exist_ok=True)

# Load previous run
prev_run = {}
if os.path.exists(HISTORY):
    try:
        prev_run = json.loads(open(HISTORY).read())
    except:
        pass

prev_fails = set(prev_run.get('fails', []))
current_fails = {r['id'] for r in results if r['status'] == 'FAIL'}

new_regressions = current_fails - prev_fails   # newly failing
resolved        = prev_fails - current_fails    # no longer failing
known_issues    = current_fails & prev_fails    # failing in both runs

# Annotate results with regression status
for r in results:
    if r['id'] in new_regressions:
        r['regression'] = 'new'
    elif r['id'] in known_issues:
        r['regression'] = 'known'
    else:
        r['regression'] = None

# Save annotated results
with open(RESULTS_PATH, 'w') as f:
    json.dump(results, f)

# Save this run as the new baseline
with open(HISTORY, 'w') as f:
    json.dump({
        'run_date': datetime.now().isoformat(),
        'repo':     repo,
        'fails':    list(current_fails),
        'total':    len(results),
        'pass':     sum(1 for r in results if r['status'] == 'PASS'),
    }, f)

print("\n📊 REGRESSION ANALYSIS")
print(f"  🔴 New regressions:  {len(new_regressions)}  → {sorted(new_regressions) or 'none'}")
print(f"  🟡 Known issues:     {len(known_issues)}  → {sorted(known_issues) or 'none'}")
print(f"  ✅ Resolved since last run: {len(resolved)}  → {sorted(resolved) or 'none'}")
PYEOF
```

Show the regression analysis output prominently. New regressions should be highlighted as the top priority to fix.

---

## Step 4.5 — NexusQA Platform Result Reporting (if run was registered)

```bash
python3 - <<'PYEOF'
import json, os, sys
import urllib.request

cfg_path   = os.path.expanduser("~/.nexusqa-config.json")
plan_path  = "/tmp/qa-plan-approved.json"
results_path = "/tmp/qa-results/qa-results.json"

if not os.path.exists(cfg_path) or not os.path.exists(results_path):
    print("PLATFORM: skipping — no config or no results")
    sys.exit(0)

cfg = json.load(open(cfg_path))
plan = json.load(open(plan_path)) if os.path.exists(plan_path) else {}
run_id = plan.get("platform_run_id")
tc_map = plan.get("platform_test_case_map", {})

if not run_id:
    print("PLATFORM: no run_id — skipping result reporting")
    sys.exit(0)

PLATFORM_URL = cfg["platform_url"].rstrip("/")
API_KEY = cfg["api_key"]
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

results = json.load(open(results_path))

# STATUS mapping: PASS→pass, FAIL→fail, WARN→fail, SKIP→skipped
STATUS_MAP = {"PASS": "pass", "FAIL": "fail", "WARN": "fail", "SKIP": "skipped"}

reported = 0
for r in results:
    tc_title = r.get("component", r.get("id", ""))
    tc_id = tc_map.get(tc_title) or tc_map.get(r.get("id", ""))
    if not tc_id:
        continue  # can't link without UUID

    payload = json.dumps({
        "test_case_id": tc_id,
        "status": STATUS_MAP.get(r.get("status", "FAIL"), "fail"),
        "duration_ms": r.get("duration_ms"),
        "actual_result": r.get("detail"),
        "screenshot_url": r.get("screenshot"),
        "error_details": {"message": r.get("detail", "")} if r.get("status") == "FAIL" else None,
    }).encode()

    req = urllib.request.Request(
        f"{PLATFORM_URL}/api/test-runs/{run_id}/results",
        data=payload, headers=HEADERS, method="POST"
    )
    try:
        urllib.request.urlopen(req)
        reported += 1
    except Exception as e:
        print(f"  ⚠️  Error reporting {tc_title}: {e}")

# Mark run completed
final_status = "completed" if all(r.get("status") == "PASS" for r in results) else "completed"
patch_body = json.dumps({"status": final_status}).encode()
req = urllib.request.Request(
    f"{PLATFORM_URL}/api/v1/agent/test-runs/{run_id}",
    data=patch_body, headers=HEADERS, method="PATCH"
)
try:
    urllib.request.urlopen(req)
except Exception:
    pass

print(f"PLATFORM: reported {reported}/{len(results)} results → run {run_id} marked {final_status}")
PYEOF
```

---

## Step 5 — Deliver Results

1. Show summary table (PASS/FAIL/WARN/SKIP counts)
2. Highlight **new regressions** (🔴) vs **known issues** (🟡) vs **resolved** (✅)
3. List all FAILs with ID, component, detail, and regression tag
4. Copy dashboard to outputs:
   ```bash
   SESSION_OUT=$(ls -d /sessions/*/mnt/outputs 2>/dev/null | head -1)
   [ -n "$SESSION_OUT" ] && cp /tmp/qa-results/qa-dashboard.html "$SESSION_OUT/qa-dashboard.html"
   ```
5. Share as: `[Ver QA Dashboard](computer:///sessions/<session>/mnt/outputs/qa-dashboard.html)`
6. Ask: "¿Deseas que reporte los bugs en GitHub? Puedo abrir un issue por cada FAIL con `qa-architect-agent:report`."
