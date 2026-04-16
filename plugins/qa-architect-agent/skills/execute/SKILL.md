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
// 3. VERIFY CHAIN — Navigate to eac