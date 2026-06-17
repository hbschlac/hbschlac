---
name: debug-escalation
description: >
  Stops fix-churn cycles before they waste hours. Activates when the same
  bug has been attempted 3+ times, when fixes keep getting reverted, or when
  a debugging session exceeds 30 minutes without progress. Provides structured
  escalation from symptom-chasing to root-cause analysis.
---

# debug-escalation

Stops fix-churn cycles. When the same bug has been attempted multiple times or a
debugging session stalls, this skill forces a step back from symptom-chasing to
root-cause analysis.

**Relationship to code-builder:** code-builder's debug loop (Step 4c) handles normal
debugging. debug-escalation activates when the debug loop itself is failing — when
you've hit the 5-hypothesis limit, or when the same area has been fixed and broken
3+ times.

---

## Activation

Triggers when ANY of these are true:

**Fix-churn triggers:**
- 3+ fix commits in the same file area within a session
- A fix was reverted or overwritten within 30 minutes
- code-builder's debug loop hit its 5-hypothesis limit
- User says "this keeps breaking" / "we've been going in circles" / "nothing works"
- Git log shows 3+ consecutive "fix:" commits to the same file

**Production incident triggers:**
- "It's broken in prod" / "users are reporting X" / "this was working yesterday"
- External dependency returning errors (503, 403, timeouts) that the app doesn't handle
- Monitoring shows failures / quota burn / cascading errors
- Feature works locally but fails in production (or vice versa)

> **debug-escalation activated** — [fix-churn detected in {area} | production incident: {symptom}]. Switching to root-cause analysis.

---

## Step 0: Production Incident Response (skip if fix-churn)

When the trigger is a production incident (not fix-churn), follow this before Step 1.

### 0A. Triage

1. **Blast radius:** How many users/features are affected? Is this total outage or degraded?
2. **Recency:** When did this start? Check deploy history — was anything shipped recently?
3. **Dependency check:** Probe external services directly before assuming your code is broken.

```bash
# Check recent deploys
git log --oneline -10 --since="24 hours ago"
# Probe external dependency (example)
curl -sI https://external-api.example.com | head -5
```

### 0B. Incident investigation order

1. **External dependencies first.** Most "sudden" production failures are upstream outages, not code bugs. Probe every external service the failing feature touches.
2. **Deployment state.** Is the running code the same as what's on main? Check deploy logs, not just git.
3. **Data/state corruption.** Check KV, database, cache for stale or invalid state. Real example: kindle-schlacter-me traced a download failure to archive.org returning 503/403 by probing the URL directly and checking KV delivery history.
4. **Recent changes.** `git log --oneline -10 -- {affected-files}` — did a recent change introduce a fragile assumption?

### 0C. Build the resilient fix

Production incidents expose fragile assumptions. The fix should not just restore service — it should prevent recurrence:

| Pattern | When to use |
|---|---|
| **Cross-source fallback** | Primary data source can go down. Try primary with timeout, fall back through alternatives in priority order. |
| **Dead-resource fast-fail** | External resource hangs indefinitely. Detect zero-progress + zero-speed for N seconds → abort early. |
| **Quota-after-success** | Rate-limited operation. Don't charge quota until the operation actually succeeds. |
| **Parallel fan-out** | Multiple sources queried sequentially. Query all in parallel with per-source timeout. |
| **Negative caching** | API returns "not found" repeatedly. Cache the miss with TTL to avoid hammering. |

After the fix, proceed to Step 5 to write the root-cause report.

---

## Cross-Skill Routing (when to escalate here)

Other skills handle initial debugging. debug-escalation takes over when they've failed:

| Coming from | Escalation trigger | debug-escalation starts at |
|---|---|---|
| **code-builder debug loop** | Hit 5-hypothesis limit, or same area fixed 3+ times | Step 2 (audit the churn) |
| **vercel-ship** | Build failure fix attempted 2+ times, or runtime error not in the debugging table | Step 1 (stop writing code) — the build/deploy context is config, not just code |
| **vercel-ship + external dep** | 500 error traced to upstream API, not Vercel config | Step 0 (production incident) — vercel-ship handles config, debug-escalation handles resilience |
| **Scheduled routine** | Health check found failures; routine can't diagnose root cause | Step 0 (production incident) with notification — don't silently log findings |

**Key distinction:** vercel-ship owns "the deploy broke" (config, types, env vars). debug-escalation owns "the deploy works but the feature doesn't" (logic, state, external deps, resilience). If vercel-ship's debugging table doesn't cover the symptom, escalate here.

---

## Step 1: Stop writing code

Do NOT write any code. The instinct to "try one more thing" is exactly the problem.

---

## Step 2: Audit the churn

```bash
git log --oneline -20 -- {files}
git log --all --oneline --grep="fix\|revert\|undo" -- {files}
```

Build the failure timeline:
```
Attempt 1: {what was tried} → {what happened}
Attempt 2: {what was tried} → {what happened}
Attempt 3: {what was tried} → {what happened}
```

What do these attempts have in common? What assumption do they all share?

---

## Step 3: Challenge the shared assumption

Every churn cycle has a shared assumption that's wrong. Common ones:

| Assumed | Actually |
|---|---|
| "The bug is in this function" | The bug is in the caller or the data |
| "This is a code bug" | This is a configuration/environment issue |
| "The error message is accurate" | The error is a downstream symptom of an upstream cause |
| "This worked before, so the change broke it" | It was already broken, the change just exposed it |
| "The fix is in the same layer as the symptom" | The fix is in a different layer (DB, infra, auth, env) |

State the shared assumption explicitly. Then ask: what if this assumption is wrong?

---

## Step 4: Expand the investigation radius

Read code you haven't read yet:
1. **Callers** of the broken function (not just the function itself)
2. **Configuration** files (env vars, vercel.json, next.config, package.json scripts)
3. **Recent changes to adjacent files** that weren't part of the "fix" attempts
4. **The deployment/runtime environment** — does this only break in prod? Only in CI?

```bash
git log --oneline -10 -- $(dirname {file})
git diff HEAD~10..HEAD -- $(dirname {file})
```

### Environment-specific investigation

| Environment | What to check first |
|---|---|
| **Vercel serverless** | Missing env vars, trust proxy, middleware order, `fs` usage, body parser conflict |
| **GitHub Actions** | Secrets not passed to reusable workflows, `working-directory` wrong, Ubuntu version changed, network timeouts |
| **Docker/containers** | Port mapping, volume mounts, env var injection, DNS resolution inside container |
| **Python venv** | Wrong Python version, venv not activated in CI, `pip install -e` vs `pip install` |
| **Cron/scheduled** | UTC vs local timezone, job overlap (previous run still going), empty-input path |
| **Web session (Claude Code)** | Missing deps (hook didn't run), no network access, ephemeral filesystem, sandbox scope |

---

## Step 5: Write the root-cause report

Before writing any fix, write a 3-sentence root-cause report:

```
ROOT CAUSE: {one sentence explaining the actual cause}
EVIDENCE: {what proves this, not what suggests it}
FIX: {what specifically needs to change}
```

If you can't write this with confidence, you don't understand the bug yet. Go back to Step 4.

---

## Step 6: Fix with guardrails

1. The fix must be different from all prior attempts
2. Write a regression test BEFORE the fix (test must fail first)
3. The fix must target the root cause from Step 5, not a symptom
4. After fixing, verify ALL prior symptoms are resolved (not just the latest one)

---

## Escalation to human

If after completing Steps 1-5 you still can't identify the root cause:

```
STUCK: I've exhausted debugging for {area}.

Ruled out:
- {approach 1}: {why it failed}
- {approach 2}: {why it failed}

Still unknown:
- {specific question that would unblock}

Suggested next steps:
- {what data or access would help}
```

This is a valid outcome. Not every bug is solvable in one session.

---

## Performance Escalation (not a bug — it's slow)

When the problem isn't "broken" but "too slow," the fix-churn cycle still applies — sessions often iterate on micro-optimizations without profiling first.

### Step P1: Measure before optimizing

```bash
# For API endpoints: measure wall-clock time
time curl -s https://your-api/endpoint > /dev/null

# For Node.js: add timing around suspects
console.time('section-name');
// ... code ...
console.timeEnd('section-name');
```

### Step P2: Identify the bottleneck category

| Category | Symptom | Fix direction |
|---|---|---|
| **Sequential I/O** | N serial `await fetch()` calls, each taking 1-5s | Parallelize with `Promise.allSettled()` |
| **Single slow dependency** | One external call takes 10s+ | Add timeout + fallback, or cache |
| **Cold start** | First request slow, subsequent fast | Move initialization out of handler, reduce bundle |
| **Unnecessary work** | Processing data that's already cached or unchanged | Add caching layer, skip no-op |
| **N+1 queries** | One DB query per item in a list | Batch or join |

### Step P3: Fix the bottleneck, benchmark the fix

1. Fix the #1 bottleneck only. Don't optimize multiple things at once.
2. Re-measure with the same method as Step P1.
3. Report before/after numbers in the commit message or PR body.
4. If improvement is <2x, the bottleneck may be elsewhere — go back to P1.

Evidence: kindle-connector PR#1 — profiling revealed sequential indexer queries (not slow indexers), parallelization gave 10x improvement (30s→3s).

---

## Proactive Monitoring Setup (prevent incidents before they happen)

debug-escalation is reactive by default. This section covers what to configure BEFORE incidents so you catch them early instead of discovering them when users report "it's broken."

### What to monitor per deployment type

| Deploy target | Monitoring | Setup |
|---|---|---|
| **Vercel** | Runtime logs + deploy notifications | Vercel dashboard → Notifications → deploy failures to Slack/email. Check `mcp__Vercel__get_runtime_logs` in web sessions. |
| **k8s** | Pod health + resource usage | `kubectl top pods`, liveness/readiness probes, alerting on CrashLoopBackOff |
| **GitHub Actions** | Workflow failure notifications | Repository → Settings → Notifications → workflow runs. Or: `mcp__github__actions_list` in web sessions. |
| **External APIs** | Uptime + response time | Periodic health check (cron job or GHA scheduled workflow) that probes each external dependency and alerts on failure |

### Minimum viable monitoring for any project

1. **Deploy failure alerts.** Vercel/GHA send emails by default — make sure they're going to an inbox you check.
2. **External dependency health check.** A scheduled job (GHA cron or Vercel cron) that pings external APIs and records status. This is how you catch "archive.org is down" BEFORE users report download failures.
3. **Error budget tracking.** After a production incident, add a regression check: a test or health probe that would have caught the specific failure mode.

### Health check pattern (GHA cron)

```yaml
name: Health Check
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - run: |
          for url in "https://your-app.vercel.app/api/health" "https://external-api.example.com"; do
            status=$(curl -sI -o /dev/null -w "%{http_code}" --max-time 10 "$url")
            if [ "$status" -lt 200 ] || [ "$status" -ge 400 ]; then
              echo "ALERT: $url returned $status"
              exit 1
            fi
          done
```

Evidence: kindle-schlacter-me PR#2 was triggered by an archive.org outage discovered reactively. A 6-hour health check on archive.org endpoints would have caught it hours earlier.

## Claude Code Web Session Debugging

Debugging in web sessions has unique constraints. Before applying general debug patterns, account for:

| Constraint | Impact | Workaround |
|---|---|---|
| **Ephemeral filesystem** | Can't persist debugging artifacts between sessions. Breakpoints, test fixtures, custom scripts — gone on restart. | Commit debug helpers to the repo. Write reproduction steps in CLAUDE.md, not just "it's broken." |
| **No browser access** | Can't visually inspect UI, open devtools, or see console output in a real browser. | Use `curl` for API testing. For UI issues, describe what the user should test and ask them to report back. Use `WebFetch` for SSR-rendered pages. |
| **MCP tool failures** | GitHub/Vercel MCP tools can timeout, return stale data, or silently fail. | Always verify MCP tool results. If `mcp__github__pull_request_read` returns an error, try `mcp__github__list_pull_requests` as a fallback. Don't build on assumed state. |
| **No long-running processes** | Can't run a dev server and then test against it in separate steps. | Run server + test in a single command: `timeout 10 bash -c 'npm run dev & sleep 5 && curl localhost:3000/api/health'`. Or use build-time checks (`tsc --noEmit`, `next build`). |
| **Context window limits** | Long debug sessions exhaust context. Earlier findings get compressed. | Write the root-cause report (Step 5) EARLY — don't wait until the end. Commit findings as you go. |
| **Network policy** | Outbound requests may be blocked depending on environment config. | Check if the request works with `curl -sI` before assuming code is broken. Network errors in web sessions are often policy, not code. |

---

## Pipeline Hardening (not a bug — it's fragile)

When multiple symptoms point to the same pipeline (e.g., search → download → validate → send), the problem isn't any single bug — it's an unhardened pipeline. Fix-churn on individual symptoms wastes time. Step back and audit the whole pipeline.

### Trigger

Activate when:
- 3+ bug reports or fixes in the same session target different steps of the same pipeline
- A fix for step N exposes a new failure in step N+1
- The same user journey has been "fixed" multiple times but keeps breaking differently
- code-builder's rapid shipping mode flags 5+ PRs targeting the same pipeline (automatic handoff)

**Detecting the 5-PR threshold:** At the start of each PR in a rapid shipping session, count recent commits to the pipeline:
```bash
git log --oneline --since="7 days ago" -- {pipeline-directory} | wc -l
```
If >=5, this section activates automatically. Don't wait for code-builder to hand off — both skills can check.

### Step PH1: Map the pipeline

List every step from input to output:
```
Step 1: {input} → Step 2: {transform} → Step 3: {validate} → Step 4: {output} → Step 5: {confirm}
```

### Step PH2: Audit each step

For each step, ask:
| Question | If yes |
|---|---|
| Can the input be malformed? | Add input validation |
| Can it timeout? | Add timeout + fallback |
| Can it succeed silently with bad data? | Add output validation |
| Does the user see failures? | Add visible error state |
| Is there a manual fallback? | Add escape hatch |

### Step PH3: Prioritize by blast radius

Fix the step that causes the most user-visible damage first. Usually: the point of no return (the step where you can't undo — e.g., sending an email, writing to DB).

Evidence: kindle-schlacter-me PRs #6-#20 — 15 PRs fixing the same download→validate→send pipeline. A pipeline audit upfront would have caught format compliance (#7), content integrity (#17), delivery confirmation (#18), and fallback sources (#11) in 3-4 comprehensive PRs.

---

## Rapid Production Iteration (healthy, not churn)

Not every rapid iteration cycle is fix-churn. When shipping to real users and getting immediate feedback, rapid iteration is the RIGHT approach. The key difference from fix-churn:

| Fix-churn (bad) | Rapid iteration (good) |
|---|---|
| Same symptom, different fixes | Different symptoms, each fixed once |
| No new information between attempts | User feedback or logs provide new info |
| Fixes contradict each other | Each fix builds on the previous |
| No validation between fixes | Each fix is validated before moving on |

### When to stay in rapid iteration (not escalate to debug-escalation):
- Each PR addresses a DIFFERENT failure mode
- You have evidence (logs, user feedback, screenshots) for each issue
- Fixes don't regress previous fixes
- The pipeline is getting measurably more robust

### When rapid iteration has become fix-churn (escalate):
- You're re-fixing something you already fixed
- The same symptom returns after your fix
- You don't have new evidence for the current attempt

---

## Invisible Downstream Failures

The hardest production bugs are ones where your system reports success but the downstream system silently drops the payload. No error, no callback, no signal — the user just says "it didn't work."

### Trigger

- "It says sent/delivered/complete but nothing happened on the other end"
- External system provides no error callback or delivery receipt
- Multiple users report the same "it worked but didn't work" pattern
- Your logs show 200 OK but the expected result never materializes

### Investigation pattern

1. **Confirm the downstream system actually received the payload.** Email providers: check delivery logs. APIs: check the third-party dashboard. File systems: verify the file arrived and was processed.
2. **Reproduce with a known-good payload.** If a manually-constructed input works, the bug is in your payload generation, not the delivery.
3. **Diff a working payload vs. a failing one.** Often a single field, header, or formatting difference causes silent rejection.
4. **Build progressive validation before the point of no return.** Since the downstream system won't tell you what's wrong, validate everything you can before sending.

### Progressive validation checklist

When a downstream system silently rejects payloads, add validation layers. This applies to ANY silent-rejection scenario — file delivery, API payloads, email content, payment submissions:

| Layer | What to check | File delivery example | API/email example |
|---|---|---|---|
| 1. Format compliance | Does the payload meet the spec? | zip structure, mimetype encoding | content-type header, required fields, payload size limits |
| 2. Content integrity | Is this real content, not a stub? | file size, page count, structure | not an error page, not empty, not a rate-limit response |
| 3. Structural validity | Is it well-formed internally? | no broken references, parseable | valid JSON/XML, no circular refs, required nested objects present |
| 4. Feature isolation | Can optional enhancements break it? | AI summary corrupts EPUB | enrichment metadata exceeds field length limits |
| 5. Deliverability | Undocumented receiving-system rules? | Amazon silently rejects certain EPUBs | spam filter triggers, attachment restrictions, character encoding |

**Key insight:** Each layer was discovered empirically across kindle-schlacter-me PRs #7, #8, #9, #14, #15, #17 — six PRs targeting the same pipeline. A single upfront validation audit would have identified most of these in 2-3 PRs. This pattern generalizes to any system that returns 200 OK but silently drops your payload.

**Triggering a validation audit proactively:** When building ANY feature that sends data to an external system with no error callback, walk through all 5 layers BEFORE shipping. See code-builder's "File validation audit" in Rapid Shipping Mode.

---

## Client-State Debugging (UI stuck, state lost, stale display)

Browser-specific state bugs require different debugging than server-side issues. The server returns 200 OK, the database is correct, but the user sees something wrong.

### Trigger

- "The button is stuck on [state]" / "It says Sending but it's already done"
- "It worked but the UI didn't update"
- "I refreshed and lost my progress/status"
- Server logs show success but user reports failure

### Investigation pattern

1. **Confirm the server state is correct.** Hit the API directly (curl, browser devtools Network tab). If the server returns the right data, the bug is client-side.
2. **Check state persistence.** Is the status stored in React state only? React state dies on: page reload, tab switch (iOS background kill), navigation away and back, PWA restart. If the status should survive these, it needs server-side storage (DB/KV) with client-side reconciliation on mount.
3. **Check for lost HTTP responses.** The server completed, the client sent the request, but the response never arrived (network blip, iOS background kill during fetch, timeout). The client shows "in progress" forever because it never got the completion signal. Fix: poll for status after long operations, don't rely on the response. (kindle-schlacter-me PR#18)
4. **Check for stale closures.** React effects capturing stale state is the #1 cause of "the UI shows old data." If a `useEffect` or callback references state that was set before the current render, it's stale. Fix: dependency arrays, refs, or reducer patterns.
5. **Check optimistic UI reconciliation.** If the UI optimistically shows a new state but the server hasn't confirmed, what happens when the server disagrees or doesn't respond? The UI must reconcile back to server truth.

### Client-state bug patterns

| Symptom | Likely cause | Fix |
|---|---|---|
| Stuck "Sending/Loading" forever | Lost HTTP response — client waiting for a callback that will never come | Poll for server-side status on timeout |
| Status disappears on reload | State stored in React state, not persisted | Persist to server (KV/DB) and reconcile on mount |
| Stale data after action | Server updated but client cache is stale | Invalidate relevant queries/cache after mutation |
| UI flickers between states | Optimistic update + server response race condition | Use server state as source of truth after confirmation |
| Action works once, fails on retry | Event handler bound to stale closure | Check dependency arrays, use refs for latest values |

Evidence: kindle-schlacter-me PR#13 (download status lost on reload — React state not persisted), PR#18 (stuck "Sending" — HTTP response lost, no polling fallback). Both required client-state debugging, not server-side debugging.

---

## When to Abandon vs. Keep Debugging

**Abandon the current approach when:**
- 3+ fundamentally different hypotheses have been tested and disproven
- The fix requires access/permissions you don't have (production DB, third-party dashboard)
- The bug is in a dependency and you can't patch it locally
- The cost of the workaround is lower than the cost of the fix

**Keep debugging when:**
- You have untested hypotheses that are fundamentally different from prior attempts
- The bug is a regression (it worked before, something specific changed)
- You haven't yet read the callers/configuration/adjacent files (Step 4 incomplete)

---

## Changelog

- **2026-06-17 — v12: Cross-skill routing, generalized invisible failures, pipeline audit automation**
  - ADDED: Cross-skill routing table — clear handoff protocol from code-builder, vercel-ship, and scheduled routines with specific entry points
  - CHANGED: Progressive validation checklist generalized beyond EPUB/file delivery to include API payloads, email content, payment submissions — with parallel examples for each layer
  - ADDED: Pipeline hardening trigger now includes automatic 5-PR threshold detection via git log, connecting to code-builder's rapid shipping mode rule
  - Evidence: Cross-skill overlap between vercel-ship (500 errors) and debug-escalation (resilience patterns) had no clear handoff — sessions would apply config fixes when the problem was architectural. Progressive validation was EPUB-specific but the pattern applies to any silent-rejection system.
- **2026-06-15 — v11: Client-state debugging**
  - ADDED: Client-state debugging section — investigation pattern for browser-specific state bugs where the server is correct but the UI is wrong
  - ADDED: Client-state bug patterns table (stuck loading, state lost on reload, stale data, flickering, stale closures)
  - Evidence: kindle-schlacter-me PR#13 (download status lost on reload — React state not persisted to server), PR#18 (stuck "Sending" — HTTP response lost during fetch, no polling fallback). Both required client-side debugging, not server-side — debug-escalation had no patterns for this.
- **2026-06-14 — v10: Invisible downstream failures**
  - ADDED: Invisible downstream failures section — investigation pattern and progressive validation checklist for when a system reports success but the downstream system silently drops the payload
  - Evidence: kindle-schlacter-me PRs #7, #8, #9, #14, #15, #17 — six PRs targeting silent Amazon rejection of EPUBs. Each discovered a new validation layer empirically (format compliance → content integrity → structural validity → feature isolation → deliverability). The downstream system (Amazon Kindle) provided zero error feedback.
- **2026-06-13 — v9: Pipeline hardening, rapid iteration vs. churn**
  - ADDED: Pipeline hardening section — when 3+ symptoms point to the same pipeline, audit all steps instead of fixing one at a time (map→audit→prioritize by blast radius)
  - ADDED: Rapid production iteration section — distinguishes healthy rapid iteration (different symptoms, new evidence) from fix-churn (same symptom, no new info), with clear escalation criteria
  - Evidence: kindle-schlacter-me PRs #6-#20 — 15 PRs on the same pipeline in one day. Productive but would have been faster with upfront pipeline audit. debug-escalation lacked the positive-pattern counterpart to fix-churn.
- **2026-06-12 — v8: Claude Code web session debugging**
  - ADDED: Web session debugging table — ephemeral filesystem, no browser access, MCP tool failures, no long-running processes, context limits, network policy constraints
  - Evidence: debugging patterns assumed persistent environments and browser access; web sessions have neither
- **2026-06-11 — v7: Proactive monitoring setup**
  - ADDED: Proactive monitoring section (deploy alerts, external dep health checks, error budgets)
  - ADDED: Health check GHA cron pattern for external dependency monitoring
  - ADDED: Per-deployment monitoring table (Vercel, k8s, GHA, external APIs)
  - Evidence: kindle-schlacter-me archive.org outage was discovered reactively; health check would have caught it hours earlier
- **2026-06-09 — v6: Performance escalation**
  - ADDED: Performance escalation section (measure→categorize→fix→benchmark cycle)
  - ADDED: Bottleneck category table (sequential I/O, single slow dep, cold start, N+1)
  - Evidence: kindle-connector PR#1 (30s→3s from profiling + parallelization, not micro-optimization)
- **2026-06-08 — v5: Production incident response protocol**
  - ADDED: Production incident triggers (external dep failures, "broken in prod", cascading errors)
  - ADDED: Step 0 — Production incident response (triage, external dep probing, data/state check)
  - ADDED: Resilient fix patterns table (cross-source fallback, dead-resource fast-fail, quota-after-success, parallel fan-out, negative caching)
  - Evidence: kindle-schlacter-me PR#2 (archive.org outage → cascading download failures → quota burn), kindle-connector PR#2 (dead-torrent fast-fail)
- **2026-06-05 — v4: Environment-specific debugging, abandon vs. continue framework**
  - ADDED: Environment-specific investigation table (Vercel, GHA, Docker, Python, cron, web session)
  - ADDED: "When to Abandon vs. Keep Debugging" decision framework
- **2026-05-29 — v3: Integrated with code-builder debug loop, added shared assumption patterns**
  - Added: explicit relationship to code-builder's debug loop
  - Added: "shared assumption" patterns table
  - Added: expanded investigation radius step
  - Added: regression test requirement before fix
  - Consolidated from GpVa7 (v2) + 358hG audit findings
- **2026-05-17 — v2: initial version on GpVa7 branch**
