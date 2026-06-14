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

When a downstream system silently rejects payloads, add validation layers iteratively:

| Layer | What to check | Evidence |
|---|---|---|
| 1. Format compliance | Does the file meet the spec? (zip structure, required entries, encoding) | kindle-schlacter-me PR#7: EPUB mimetype DEFLATED instead of STORED |
| 2. Content integrity | Is the content real? (not a stub, not a placeholder, not an error page) | PR#8: rate-limited HTML page sent as "EPUB"; PR#17: fake torrent stubs |
| 3. Structural validity | Is the content well-formed? (no broken references, no empty sections) | PR#15: broken spines, DRM'd files, missing content documents |
| 4. Feature isolation | Can optional features break the core payload? | PR#9, #14: AI summary embed corrupted the EPUB; gated off |
| 5. Deliverability | Will the receiving system's specific rules accept this? | PR#16: honest copy since Amazon provides no receipt |

**Key insight:** Each layer was discovered empirically when a book "sent" but never arrived. Six PRs (#7, #8, #9, #14, #15, #17) targeted the same silent-rejection pipeline. A single upfront validation audit would have identified most of these in 2-3 PRs.

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
