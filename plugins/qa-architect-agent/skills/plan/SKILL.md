---
description: >
  QA Architect – Test Plan Generator. Use this skill when the user says
  "generate a QA plan", "analyze this app for testing", "create a test plan
  for [URL or repo]", "QA plan for [project]", "what should we test in [app]",
  "dame un plan de pruebas", "genera el plan de QA", or any phrase requesting
  a structured test plan before execution. Runs a scope wizard first (Frontend /
  Backend / Mobile / Security), then generates a layer-specific plan and waits
  for user approval before any test runs.
---

# qa-architect-agent: plan

You are a QA Architect. Your job is to analyze an application deeply and produce a comprehensive, signed-off test plan. You NEVER execute tests or visit the target URL during this skill — execution happens only after the user approves.

---

## Step -1 — Load NexusQA Platform Context (if available)

```bash
python3 - <<'PYEOF'
import json, os

ctx_path = "/tmp/nexusqa-context.json"
if not os.path.exists(ctx_path):
    print("PLATFORM_CONTEXT: none")
else:
    ctx = json.load(open(ctx_path))
    apps = ctx.get("apps", [])
    sprints = ctx.get("sprints", [])
    print(f"PLATFORM_CONTEXT: {len(apps)} apps, {len(sprints)} sprints")
    for app in apps:
        print(f"  APP: {app['name']} → {app['base_url']} | auth={app['auth_type']}")
    for sp in sprints:
        print(f"  SPRINT: [{sp['status']}] {sp['name']} | {sp.get('test_cases_count',0)} test cases")
    # Show qa_context if present on the selected sprint
    plan_path = "/tmp/qa-plan-approved.json"
    sprint_id = json.load(open(plan_path)).get("platform_sprint_id") if os.path.exists(plan_path) else None
    if sprint_id:
        for sp in sprints:
            if sp["id"] == sprint_id and sp.get("qa_context"):
                print(f"\n  QA_CONTEXT for sprint '{sp['name']}':")
                print(sp["qa_context"])
PYEOF
```

If platform context is loaded:
- Use `apps[].base_url` as the primary target URL (no need to ask the user)
- Use `apps[].auth_config` for login credentials (username/password, API key, etc.)
- Use `apps[].github_url` as the GitHub repo for code analysis
- Use the sprint's `qa_context` text as additional instructions guiding what to test
- Pre-seed the test plan with any `test_cases` already on the platform for the selected sprint

Store `platform_sprint_id`, `platform_project_id`, `platform_app_id`, and `run_name` in the plan JSON for the execute skill to use later.

---

## Step 0 — Scope Wizard (ALWAYS FIRST)

Before any analysis, run this wizard if the scope hasn't been set by the qa-architect:

```
🧪 QA ARCHITECT — Scope Wizard

¿Qué quieres testear? (puedes seleccionar múltiples)

1️⃣  Frontend  — UI, navegación, flujos de usuario (Playwright)
2️⃣  Backend   — APIs REST/WebSocket/GraphQL/gRPC (k6)
3️⃣  Mobile    — App Flutter/React Native/nativo (Maestro)
4️⃣  Security  — OWASP Top 10, vulnerabilidades, pen testing

Escribe los números separados por comas: "1,2" = Frontend + Backend
O escribe "all" para QA completo.
```

**Multi-target** — also ask if not obvious:
- "¿Hay múltiples frontends? (ej: admin panel + client app)"
- "¿Hay múltiples backends o microservicios?"

Store `SCOPE_LAYERS` and `TARGETS` before proceeding.

---

## Input Collection

After scope is determined, collect any missing inputs:

- **Target URL(s)**: one URL per selected layer
- **Credentials**: email and password for authenticated flows
- **GitHub repo** (optional but strongly recommended): e.g. `https://github.com/org/repo`
- **Scope notes** (optional): focus areas (e.g. "proposals module only")

Never proceed without at least one target URL.

---

## Phase 1 — Deep Discovery (GitHub repo required)

### Step 1a — Fetch repository file tree

Use the GitHub REST API to list ALL files recursively:

```bash
GH_TOKEN=$(cat ~/.singular-agency-plugin-creator.json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('github_token',''))" 2>/dev/null)
OWNER="<owner>"
REPO="<repo>"

curl -s -H "Authorization: token $GH_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/git/trees/main?recursive=1" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
files = [f['path'] for f in data.get('tree', []) if f['type'] == 'blob']
# Print routes, api routes, components, middleware
for f in sorted(files):
    if any(x in f for x in ['page.tsx','page.ts','route.ts','route.tsx','middleware','layout.tsx','_app','index.tsx','index.ts']):
        print('ROUTE:', f)
    elif any(x in f for x in ['Sidebar','Nav','Menu','Header','sidebar','nav','menu','header']):
        print('NAV:', f)
    elif 'schema' in f.lower() or 'types' in f.lower() or 'model' in f.lower():
        print('SCHEMA:', f)
    elif f.endswith('.sql') or 'migration' in f.lower() or 'supabase' in f.lower():
        print('DB:', f)
"
```

If `main` branch fails, try `master`.

### Step 1b — Deep Code Analysis: API Handlers + DB Operations

Fetch and read the **full source code** of every API route handler and relevant utility/lib files. This is the most important analysis step — do NOT just skim surface parameters. Read the actual logic.

**For each API route handler (`app/api/**/route.ts`):**

Read the entire function body and extract:

1. **Input parameters**: body fields, query params, headers (auth token, user-agent, etc.)
2. **Auth check**: is `supabase.auth.getUser()` / `getServerSession()` / `verifyToken()` called? What happens if it fails?
3. **All database operations** — list EVERY table touched and the operation type:
   - `supabase.from('TABLE').select(...)` → READ
   - `supabase.from('TABLE').insert(...)` → CREATE
   - `supabase.from('TABLE').update(...)` → UPDATE
   - `supabase.from('TABLE').delete(...)` → DELETE
   - `prisma.TABLE.findMany(...)`, `prisma.TABLE.create(...)`, etc.
4. **Conditional branches**: any `if (condition) { write to another table }` patterns — these represent optional workflow paths that must each be tested
5. **External calls**: fetch to third-party APIs, email sending, webhook dispatch, queue insertion
6. **Utility function calls**: if the handler calls `lib/someUtil.ts`, read that file too and trace its DB operations
7. **Transaction scope**: does it use `supabase.rpc()`, `prisma.$transaction()`, or equivalent? If so, all operations are atomic — a failure in any step rolls everything back

**Output for each handler:**

```
POST /api/referrals/apply
  Auth required: YES
  Input: { referralCode: string, userId: string }
  DB operations:
    1. SELECT users WHERE referral_code = referralCode         → verify code exists
    2. UPDATE users SET referred_by = referrerId WHERE id = userId
    3. (conditional: if user.first_purchase_done)
       UPDATE wallets SET balance += bonus WHERE user_id = referrerId
       INSERT credits { user_id: userId, amount: welcome_bonus, reason: 'referral' }
  External: none
  Side effects: wallet balance changes for 2 users
  Workflow type: MULTI_ENTITY_CONDITIONAL
```

**For utility/lib files** referenced by handlers:
- Fetch and read them the same way — trace their DB operations
- If a utility calls another utility, trace recursively until you reach the actual DB calls

**For DB migration/schema files** (`.sql`, `schema.prisma`, `supabase/migrations/`):
- Map every table: name, columns, foreign keys, constraints, triggers
- Note Supabase DB triggers (`CREATE TRIGGER ...`) — these cause additional writes that happen outside the application code
- Note RLS policies — which tables have Row Level Security? Are any policies misconfigured (`USING (true)`) allowing unauthenticated access?

**For Supabase Edge Functions** (if present in `supabase/functions/`):
- Read them the same way as API routes — they're often the most important business logic

### Step 1c — Build a route map

Produce a consolidated list:

```
AUTHENTICATED ROUTES:
  /admin                     → Dashboard (auth guarded)
  /admin/proposals           → Proposals list (check auth guard!)
  /admin/proposals/[id]      → Proposal detail view (dynamic — needs real ID)
  /admin/proposals/[id]/edit → Proposal edit form (dynamic — needs real ID)
  /admin/proposals/new       → Create new proposal

PUBLIC ROUTES:
  /auth/login                → Login form
  /proposals/[id]            → Public proposal viewer (dynamic)

API ROUTES:
  POST /api/proposals/generate   → body: { projectName, files[], mapType, mapPlans }
  POST /api/chat                 → body: { proposalId, message }
  GET  /api/proposals/[id]       → query: id
  ...
```

If no GitHub repo is provided, skip Phase 1. Infer route structure from the target URL path and any context given.

### Step 1d — Identify Workflows (Multi-Entity Business Processes)

Using the full DB operation map built in Step 1b, identify **workflows**: end-to-end business processes that span multiple steps, multiple tables, or conditional logic chains. A workflow is NOT just "form → one table write". It is a chain of cause-and-effect that produces observable state changes across multiple parts of the system.

**Detection signals — a workflow exists when:**
- A single handler writes to 2+ tables
- A handler has conditional branches that each write to different tables
- An action in the UI triggers N subsequent DB changes (via triggers, background jobs, or cascading logic)
- State changes in one entity affect the display/availability of another (e.g. approve an order → update inventory → unlock next step for user)
- A timed or triggered process runs after an initial event (e.g. referral bonus credited only after first purchase)

**For each workflow found, produce a full trace:**

```
WORKFLOW: Referral Bonus Flow
  Trigger: User registers with a valid referral code
  Steps:
    1. POST /api/auth/register { email, password, referralCode }
       → INSERT users { id, email, referred_by: referrerId }       [table: users]
    2. On first purchase (POST /api/orders/create):
       → INSERT orders { user_id, amount }                         [table: orders]
       → (conditional) if orders.count == 1 for this user:
           UPDATE wallets SET balance += 50 WHERE user_id = referrerId  [table: wallets]
           INSERT credits { user_id: newUserId, amount: 20, type: 'welcome' }  [table: credits]
  Observable state after full flow:
    - users.referred_by is set on new user
    - referrer's wallets.balance increased by 50
    - new user's credits table has 1 row with type='welcome'
  UI verification points:
    - Referrer's dashboard shows updated wallet balance
    - New user's profile shows welcome credit
    - (if referral history page exists) shows the referral link
  Conditional paths to test:
    - Valid referral code → bonus credited ✓
    - Invalid/expired referral code → error shown, no bonus credited ✓
    - Own referral code → rejected ✓
    - Second purchase by same user → bonus NOT credited again ✓
```

**Classify each workflow by complexity:**

| Type | Description | Example |
|------|-------------|---------|
| `SIMPLE_FLOW` | 1 form → 1 table, observable in 1 list | Create proposal → appears in proposal list |
| `MULTI_ENTITY` | 1 trigger → writes 2+ tables atomically | User registration → creates user + profile + default settings |
| `CONDITIONAL` | Trigger → conditional writes based on state | Apply referral → bonus only if code valid AND first purchase |
| `ASYNC_CHAIN` | Trigger starts process, effect visible later | Upload file → background processing → result appears in UI |
| `STATE_MACHINE` | Entity moves through status transitions | Order: pending → confirmed → shipped → delivered |

**For each workflow, define what a test must verify:**
- Not just that the trigger API returned 200
- But that EVERY affected table was updated correctly — verified via the UI wherever possible
- And that conditional branches behave correctly under each condition

**Also identify CRUD Simple Flows** (1:1 form → 1 table) the same way, but label them `SIMPLE_FLOW` — they're still tested with create→list→verify and edit→verify patterns.

---

## Phase 2 — Test Plan Generation

Generate test cases that cover EVERY discovered route, button, and API endpoint.

### Column definitions

`ID | Component | URL/Endpoint | Method | Action Description | Input / Payload | Expected Result | Severity`

### Required test groups

#### 🟢 Happy Paths — Authenticated Navigation

For EVERY authenticated route discovered in Phase 1, generate a test case:

- **Login** → renders form, submits successfully, redirects to dashboard
- **Dashboard** → loads with correct heading/content
- For EACH list page (e.g. `/admin/proposals`): loads while authenticated, shows list or empty state
- For EACH detail page (e.g. `/admin/proposals/:id`): fetch a real ID from the DB (or use the first item in the list), load the page, verify key fields render
- For EACH edit page (e.g. `/admin/proposals/:id/edit`): load with a real ID, verify form fields render and all tabs/sections are accessible
- For EACH create/new page: load the form/builder, verify input fields, tabs, dropdowns are all present
- For EACH action button found in nav/sidebar: click the link, verify the target page loads without errors
- **Logout** → redirects to login

For EACH public route (e.g. `/proposals/:id`):
- Load with a valid ID → verify all expected fields render (title, sections, images, etc.)
- Check all embedded components load (maps, charts, etc.)

#### 🟡 Edge Cases — Auth, Validation, UI

- Wrong password → error shown
- Non-existent email → error shown  
- Empty form submission → validation error
- Email-only submission → blocked
- Invalid email format (`notanemail`) → HTML5 or custom validation
- **For each protected route**: access without auth (fresh browser session) → should redirect to login. Flag FAIL if it renders content instead.
- Mobile layout 375×812 → no input overflow, no horizontal scroll
- Password visibility toggle (if present in the UI)
- For EACH API route with required fields: send request with each required field missing → expect 400, not 500
- For EACH dynamic route: request with invalid/non-existent ID → 404 page shown, not 500

#### 🔴 Error Handling — Security & Resilience

- SQL injection in email (`' OR 1=1; --`) → rejected, no 500
- XSS in input (`<script>alert('xss')</script>`) → sanitized, no execution
- 10 rapid login attempts with wrong password → no crash, optional rate limiting
- Navigate to unknown route → 404 page, not 500
- For file upload endpoints: upload 0-byte file → graceful error, no 500
- For file upload endpoints: upload oversized file → graceful error (413 or custom message)
- Special characters in password (`<>"';;&\|{}[]`) → no server error

#### 🔵 Deep Functional Tests (from schema/business logic)

For each schema/model discovered:
- Required field validation: omit each required field, verify 400 not 500
- Enum values: send an invalid enum string, verify rejected cleanly
- Relationships: if entity A belongs to entity B, test loading A when B doesn't exist

#### 🟣 Workflow & E2E Flow Tests (MOST IMPORTANT — verifies real business logic)

For every workflow identified in Step 1d, generate a complete test that exercises the full chain and verifies **every observable side effect** — not just the trigger response.

**Rule: a workflow test PASSES only when ALL of the following are verified:**
1. The triggering action succeeds without errors
2. Every affected entity reflects the expected state change — checked via UI navigation, not just API response
3. Every conditional branch that should NOT fire, does not fire
4. The system remains in a consistent state (no partial writes, no stale UI cache)

**For each workflow, specify:**

```
WF-01: [Workflow Name]
  Setup:
    - What pre-existing state is required? (e.g. "a referrer user with code ABC123")
    - How to create that state via the UI or API before the test runs
  Trigger:
    - Which form/button/action starts the workflow
    - What data to input (use QA-WF01-{TS} as unique marker in identifiable fields)
  Verification chain (each step is a separate screenshot):
    A. Immediate: what the UI shows right after trigger (success state, redirect target)
    B. Entity 1: navigate to [page/section] → verify [field] changed to [expected value]
    C. Entity 2: navigate to [other page/section] → verify [other field] changed
    D. Conditional: trigger the "invalid" path → verify the bonus/side-effect did NOT fire
  FAIL conditions:
    - Any verification step shows unexpected state
    - Any console error during the flow
    - The trigger returned an error
```

**Example generated test cases for a referral workflow:**

| ID | Test | Steps | Verify |
|----|------|-------|--------|
| WF-01a | Referral: valid code at registration | Register with code from userA | userA wallet balance +50, new user credits +20 (check both dashboards) |
| WF-01b | Referral: invalid code | Register with code `BADCODE` | Error message shown, no wallet/credit changes |
| WF-01c | Referral: own code | Register with own referral code | Rejected — cannot refer yourself |
| WF-01d | Referral: bonus not double-credited | Make a second purchase with referred user | userA wallet balance unchanged (bonus not repeated) |
| WF-01e | Referral: bonus timing | Registration done but no purchase yet | userA wallet balance unchanged until first purchase |

**For SIMPLE_FLOW entities (1:1 form → 1 table):**

Still test create → verify in list → edit → verify change persists, but label them `FLOW-XX` and note they are simpler. Always use a timestamp marker (`QA-FLOW-{TS}`) in an identifiable field so the record can be found in the list view.

**Key principles for all flow tests:**
- Never trust the API response alone — always navigate the UI to confirm state
- Test the "not triggered" path as much as the "triggered" path — conditional branches are where bugs hide
- If a side effect is async (background job, webhook), note it and wait appropriately (up to 10-15s with polling)
- Screenshot before setup, after trigger, and at every verification point

---

## Output Format

Present the full test plan as a Markdown table. Use real discovered URLs — do NOT use generic placeholders if Phase 1 found real routes.

End with:

| Category | Count |
|----------|-------|
| Happy Paths | N |
| Edge Cases | N |
| Error Handling | N |
| Deep Functional | N |
| **Total** | **N** |

Then display:

---

> ⏸️ **STOP — Awaiting your approval.**
>
> Plan de pruebas generado con **N test cases** en total, cubriendo **N rutas** descubiertas.
>
> - ✅ **"Confirmo"** — ejecutar todos los tests
> - ✏️ **"Modifica [ID]..."** — ajustar casos específicos
> - 🎯 **"Solo [categoría]"** — enfocar en Happy Paths / Edge Cases / Error Handling

---

Once the user confirms, save the approved plan to `/tmp/qa-plan-approved.json`:

```json
{
  "target_url": "https://...",
  "login_url": "https://.../auth/login",
  "email": "...",
  "password": "...",
  "github_repo": "owner/repo",
  "approved_at": "ISO timestamp",
  "route_map": {
    "authenticated": ["/admin", "/admin/proposals", "/admin/proposals/:id", ...],
    "public": ["/proposals/:id"],
    "api": ["POST /api/proposals/generate", ...]
  },
  "workflows": [
    {
      "id": "WF-01",
      "name": "Referral Bonus Flow",
      "type": "CONDITIONAL",
      "trigger_endpoint": "POST /api/auth/register",
      "tables_affected": ["users", "wallets", "credits"],
      "setup": {
        "description": "Create a referrer user and capture their referral code",
        "steps": ["register userA via UI", "get userA.referral_code from profile page"]
      },
      "trigger": {
        "url": "/auth/register",
        "fields": [
          { "name": "email", "value": "qa-wf01-{TS}@test.com" },
          { "name": "referralCode", "value": "{userA.referral_code}" }
        ]
      },
      "verification_chain": [
        { "step": "A", "description": "Immediate redirect to dashboard or success page", "url": "/dashboard", "check": "no error state" },
        { "step": "B", "description": "First purchase to trigger bonus", "action": "complete first purchase flow" },
        { "step": "C", "entity": "wallets (referrer)", "url": "/admin/users/{referrerId}/wallet", "check": "balance increased by bonus amount" },
        { "step": "D", "entity": "credits (new user)", "url": "/profile/credits", "check": "welcome credit row exists" }
      ],
      "conditional_paths": [
        { "scenario": "invalid code", "input": "BADCODE", "expected": "error shown, no wallet/credit changes" },
        { "scenario": "own code",     "input": "{own_code}", "expected": "rejected — cannot self-refer" },
        { "scenario": "no code",      "input": "",           "expected": "registration succeeds, no bonus fired" }
      ]
    }
  ],
  "simple_flows": [
    {
      "id": "FLOW-01",
      "entity": "Proposals",
      "type": "SIMPLE_FLOW",
      "list_url": "/admin/proposals",
      "create_url": "/admin/proposals/new",
      "detail_url": "/admin/proposals/:id",
      "edit_url": "/admin/proposals/:id/edit",
      "required_fields": [
        { "name": "projectName", "type": "text", "selector": "input[name='projectName']" }
      ],
      "marker_field": "projectName",
      "editable_field": { "name": "projectName", "selector": "input[name='projectName']" }
    }
  ],
  "test_cases": [
    {
      "id": "HP-01",
      "component": "Auth",
      "endpoint": "/auth/login",
      "method": "UI",
      "action": "Login form renders with email, password, submit button",
      "payload": "none",
      "expected": "2 inputs + submit button present",
      "severity": "Critical"
    },
    {
      "id": "WF-01a",
      "component": "Referral",
      "type": "workflow",
      "workflow_ref": "WF-01",
      "scenario": "valid_code",
      "action": "Register with valid referral code → verify bonus credited to referrer wallet AND welcome credit for new user",
      "tables_affected": ["users", "wallets", "credits"],
      "severity": "Critical"
    },
    {
      "id": "WF-01b",
      "component": "Referral",
      "type": "workflow",
      "workflow_ref": "WF-01",
      "scenario": "invalid_code",
      "action": "Register with BADCODE → verify error shown, no wallet/credit changes anywhere",
      "severity": "High"
    }
  ]
}
```

Do NOT call `execute` or run any tests until the user explicitly confirms.
