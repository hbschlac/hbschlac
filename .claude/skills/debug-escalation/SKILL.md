---
name: debug-escalation
description: >
  Stops the "try a fix, commit, repeat 10 times" cycle. Forces root-cause
  analysis before writing code. Max 3 hypothesis cycles, then structured
  escalation. Checks across ALL branches for prior failed approaches.
  Integrates with code-builder (takes over on fix churn) and session-safety
  (considers concurrent session conflicts as a hypothesis category).
---

# debug-escalation

Stops the cycle of "try a fix, commit, try another fix, commit, repeat 10 times." Forces root-cause analysis before writing code when a bug has resisted multiple fix attempts.

## Activation

Triggers when ANY of these are true:
- The same file or function has been fixed 3+ times in recent `git log`
- The user says anything like: "this still doesn't work", "tried that already", "same error", "it broke again", "still broken"
- The current error message or symptom matches a recently committed fix (i.e., a regression)
- There are 3+ consecutive commits with "fix" in the message touching the same area

Also triggers proactively: if code-builder or any other skill is about to write a fix for an area with recent fix churn, this skill takes over.

## The Protocol

### Step 1: Stop and Read

Do NOT write any code yet. Instead:

1. Read the relevant code thoroughly — not just the error line, but the full function, its callers, and its dependencies.
2. Read the last 3-5 diffs that touched this area (`git log -p -5 -- {file}`).
3. Read any error messages, stack traces, or browser console output.

### Step 2: Hypothesize

Form a single-sentence hypothesis about the ROOT CAUSE (not the symptom):

```
debug-escalation: hypothesis — {one sentence}
```

Print this and wait for user confirmation. If the user says "no" or provides more context, form a new hypothesis.

**Root cause vs symptom examples:**
- Symptom: "popup doesn't close" / Root cause: "window.close() is blocked by browser when opener reference is null because reload() cleared it"
- Symptom: "API returns 500" / Root cause: "trust proxy not set in Vercel serverless, so Express reads 127.0.0.1 instead of client IP, rate limiter blocks everything"
- Symptom: "image shows 1x1 pixel" / Root cause: "migration fetched blob URL without auth token, got HTML error page, saved that as image"

### Step 3: Prove It

Write a minimal diagnostic that proves or disproves the hypothesis. This is NOT the fix — it's verification.

Options (pick the lightest one that works):
- Add a single console.log / print statement at the suspected root cause
- Write a failing test that reproduces the bug
- Run a curl command that demonstrates the API behavior
- Check a specific value in the database/KV/config

### Step 4: Fix (only after proof)

Now write the fix targeting the proven root cause. The fix should:
- Address the root cause, not paper over the symptom
- Not revert to an approach that already failed (check the git log)
- Include a guard or test that prevents regression

### Step 5: Verify

After the fix:
- Run the same diagnostic from Step 3 to confirm the root cause is addressed
- Check for side effects in related functionality
- If the project has tests, run them

## Escalation Limits

- **3 hypothesis cycles max.** If 3 hypotheses are wrong, stop and provide structured output:
  ```
  debug-escalation: exhausted after 3 cycles.
  Ruled out:
  1. {hypothesis 1} — disproved by {evidence}
  2. {hypothesis 2} — disproved by {evidence}
  3. {hypothesis 3} — disproved by {evidence}
  Remaining unknowns: {what would help narrow it down}
  Suggested next steps: {specific questions or data the user could provide}
  ```
  This structured format gives the user actionable next steps instead of a generic "I need more context."
- **Never repeat a failed approach.** Before writing any fix, grep the recent git log for similar changes. If a similar fix was already tried and committed, it didn't work — try something different.
- **Check across sessions.** Run `git log --all --oneline --grep="fix" -- {file}` (note `--all`) to catch fixes attempted on OTHER branches too. The Groundhog Day pattern applies to debugging: a fix tried and abandoned on branch A shouldn't be re-tried on branch B.

## Anti-Patterns This Skill Prevents

| Anti-pattern | What happens instead |
|-------------|---------------------|
| "Try this fix" without understanding the bug | Hypothesis + proof before any code |
| Same fix attempted with minor variations | Check git log, don't repeat failed approaches |
| Fixing symptoms (add null check) instead of causes (fix the data flow) | Root-cause framing required |
| 10 commits in a row all saying "fix" | Max 3 cycles, then escalate to user |
| Language confusion (Python idioms in JS) | Step 1 forces reading the actual codebase before writing |

## Pre-Step 0: Failed Approach Check (mandatory)

Before forming ANY hypothesis, run:
```bash
git log --all --oneline -20 -- {file}
git log --all --oneline --grep="fix" -- {file}
```

Scan the output for prior fix attempts. List them explicitly:
```
Prior attempts found:
- {sha} {date}: {what was tried}
- {sha} {date}: {what was tried}
These approaches are OFF LIMITS.
```

This prevents the iOS Shortcut pattern (v3 through v13 trying variations of the same wrong approach).

## Environment-Awareness Hypotheses

Consider these root causes that are invisible in the code:

- **Session conflicts:** Was this file modified by a concurrent session? (`git log --all -5 -- {file}`)
- **Vercel vs local divergence:** Does the bug only happen in deployment? Check for env vars, case-sensitive imports, or API routes that differ between `next dev` and Vercel's serverless runtime
- **Stale dependencies:** Was `node_modules` or `.next` cache built from an older state? Try `rm -rf .next && npm run build`

## Integration with code-builder

When code-builder detects fix churn (3+ recent fixes in the same area), it hands off to debug-escalation mode instead of generating parallel drafts. Parallel drafts of a misunderstood bug just produce 5 wrong answers.

## Integration with session-safety

If Step 1 reading reveals the file was recently modified by a different session, consider "concurrent session conflict" as a hypothesis category. Files restored via `git reflog` or commits with "restore:" prefixes are strong signals.
