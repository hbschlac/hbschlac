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
- 3+ fix commits in the same file area within a session
- A fix was reverted or overwritten within 30 minutes
- code-builder's debug loop hit its 5-hypothesis limit
- User says "this keeps breaking" / "we've been going in circles" / "nothing works"
- Git log shows 3+ consecutive "fix:" commits to the same file

> **debug-escalation activated** — fix-churn detected in {area}. Switching from symptom-chasing to root-cause analysis.

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
