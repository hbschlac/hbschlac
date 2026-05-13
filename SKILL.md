# code-builder v3

## Overview

**code-builder** is a Claude agent skill that improves code quality through three execution modes:

1. **Single pass** — one implementation, fast, for obvious fixes
2. **Parallel (N=3–5)** — isolated drafts scored against a 100-point rubric, winner merged
3. **Debug loop** — systematic hypothesis-test-learn cycle for integration failures

The core hypothesis: single-pass output leaves performance on the table. Parallel attempts with objective evaluation raise the floor. And when the problem is iterative debugging, a structured debug loop prevents spirals.

---

## Activation

**Auto-triggers whenever Hannah is writing, changing, or fixing code.** Explicit signals: `/code-builder`, "build this," "fix this bug," "add a feature." Implicit: working in a git repo while describing a coding task, sharing error messages or stack traces, working in known project repositories.

**Do NOT activate for:** pure code reading, research, writing prose (unless editing user-facing copy in code files), design, planning, or meta-tasks like "what are my TODOs?"

**Default rule:** when uncertain, activate. A single-pass run costs negligible resources; missing an actual dev task is worse.

**Conflict declaration:** If `mcp-contributor` is active (guiding a PR to the MCP org), code-builder defers to its workflow for code changes. code-builder handles only code tasks that mcp-contributor doesn't claim.

---

## Required Announcement

Before any work begins, print this one-line banner:

> **code-builder activated** — [parallel, N drafts | single pass | debug loop]. [reason.]

Example: `code-builder activated — parallel, 5 drafts. New feature; multiple architectures viable.`
Example: `code-builder activated — debug loop. iOS shortcut failing against API; need systematic isolation.`

**Single-pass suppression:** If this is the 3rd+ consecutive single-pass activation in the same session, suppress the banner. Print only on mode escalation or first activation.

Hannah can override with "actually, 5x this" or "actually, just fix it" or "actually, debug this" to flip modes.

---

## Step 1 — Pre-flight Check

**Before writing any code**, scan the task against known failure patterns. This runs in ALL modes.

### 1A. Claude Process Failures

| Check | Action if triggered |
|---|---|
| Task touches `process.env.*` or env vars? | Validate + trim at read-site. Check for `NEXT_PUBLIC_` exposure. |
| Task adds a `useEffect`? | Must return cleanup function if it subscribes, starts timer, or sets state. |
| Task uses floating UI (tooltip, dropdown, popover)? | Check for scroll/overflow parent — use `position: fixed` + portal, not `absolute`. |
| Task destructures API/KV response? | Guard nullable response before destructuring. Render `<EmptyState />` or early-return. |
| Task could duplicate an existing utility? | `grep -r` for similar helpers before writing new ones. |
| Task adds conditional logic around a hook? | Verify Rules of Hooks: no conditional calls, no hooks in callbacks/effects. |

### 1B. Deployment & Integration

| Check | Action if triggered |
|---|---|
| Deploying to Vercel? | Verify: no `fs` access in serverless, correct entry point, `trust proxy` if behind proxy. |
| Task changes auth/OAuth flow? | Verify redirect URLs for BOTH local and production. Check cookie domain. |
| Task involves image/file storage? | Verify upload-storage-retrieval pipeline. Check URL format (public vs private, CDN path). |
| Task generates user-facing copy? | Run AI-slop check (Step 8). |
| Task references external URLs or data? | Verify every URL exists. Never fabricate. Flag for manual verification if unsure. |

### 1C. Cross-Session Safety

| Check | Action if triggered |
|---|---|
| Are there uncommitted changes from another session? | `git stash list` + `git status`. Do NOT overwrite — ask Hannah. |
| Does the task touch files modified in the last 2 hours by a different commit author? | Flag potential conflict. |
| Are any components imported by 3+ files? | Extra caution — deletion cascades. Verify all import sites before removing. |

**Output:** One-line summary of which pre-flight checks fired, or "Pre-flight clean."

---

## Step 2 — Scope the Task

State the task in one line. Identify:
- Files likely to change
- Whether it's greenfield (new) or modification (fix/tweak)
- Design space: multiple valid approaches or one obvious path?
- Integration surface: does this touch external services, APIs, or device-specific behavior?
- Estimated complexity: small (<30 LOC), medium (30-150 LOC), large (>150 LOC)

---

## Step 3 — Judgment Gate

**Three modes.** Default is single pass. Escalate based on signals.

### Parallel threshold

Escalate when >=2 soft signals fire OR any hard signal fires:

**Soft signals:**
- >30 LOC changed
- >1 file touched OR new file created
- Multiple valid architectures exist
- New pattern to the repo
- Touches critical path (auth, checkout, data layer)
- Feature/refactor/greenfield task type
- Open-ended phrasing ("build X", "make Y better")

**Draft count (token budget awareness):**
- Large complexity (>150 LOC, >3 files): N=5
- Medium complexity (30-150 LOC, 2-3 files): N=3
- If rate limits are close or session is long: N=3 regardless

### Debug loop threshold

Escalate when ANY of these fire:
- This is attempt >=2 at the same task (prior attempt failed or was reverted)
- Error involves an external integration (API, third-party service, device-specific, OAuth, CDN)
- Error reproduces in production but not locally (or vice versa)
- Hannah says "this keeps breaking" or "I've tried X already"
- 3+ consecutive fix commits in the same area visible in recent git log

### Single pass (default)

Use when none of the above escalation signals fire:
- <30 LOC changed
- Exactly 1 existing file
- One obviously correct path
- Variation of existing pattern
- Contained to leaf component
- Targeted bug fix with known root cause
- Specific phrasing ("change line 42 to...")

### Hard overrides (any one decides immediately)

- Hannah explicit override: obey
- Not a git repo: offer `git init`; if declined, force single
- Live debugging with rapid iteration: force single (parallel too slow)
- Greenfield prototype from scratch: force parallel
- "This keeps failing" / integration failure: force debug loop

---

## Step 4a — Parallel Path

**Prerequisite:** Claude's working directory must be a git repository. Verify with `git rev-parse --git-dir`. If not in a repo, offer to run `git init`. If declined, downgrade to single pass.

If repo confirmed:

1. Create run log directory: `mkdir -p ~/.claude/skills/code-builder/runs/`

2. Spawn **N `Agent` calls in parallel in a single message**, each with:
   - `isolation: "worktree"`
   - `run_in_background: true`
   - `subagent_type: "general-purpose"`
   - Task prompt includes: the full task description, pre-flight check results, and differentiation bias:
     - Draft 1: simplest possible — fewest lines, no abstractions
     - Draft 2: most idiomatic to this repo — match existing patterns exactly
     - Draft 3: optimize for readability — clearest naming, smallest functions
     - (If N=5) Draft 4: optimize for performance/correctness on edge cases
     - (If N=5) Draft 5: best instinct — your choice

   **Adaptive bias:** If win-rate history exists in run logs, weight the draft order toward historically winning biases for this task type. E.g., if "simplest" wins 70% of bug fixes, assign 2 drafts to simplest variants.

3. Each draft agent prompt must include: "Before coding, check for existing utilities with `grep -r`. After coding, run the project's test command, `tsc --noEmit`, and lint."

4. Each draft should: commit work on its worktree branch, report approach (2 lines), files touched, LOC added/removed, commit SHA, edge cases.

5. Wait for all N to complete. If any fail/timeout, continue with survivors.

---

## Step 4b — Single Path

Execute the task normally. Skip to Step 7.

---

## Step 4c — Debug Loop

For integration failures and iterative debugging. The goal is to prevent spirals.

### Debug Loop Protocol

1. **State the current failure precisely:**
   > What happens: [exact error/behavior]
   > What should happen: [expected behavior]
   > Environment: [local/Vercel/GHA/device]

2. **List what's already been tried** (from git log, conversation, or Hannah's description). Do not repeat failed approaches.

3. **Form exactly one hypothesis.** Write it as a falsifiable statement:
   > Hypothesis: The API returns 403 because the auth header isn't forwarded through the Vercel serverless proxy.

4. **Design the minimal test** to confirm or reject. Prefer:
   - Adding a single `console.log` / debug endpoint over changing production code
   - `curl` to isolate network from application logic
   - Reading source/docs of the external dependency before guessing

5. **Execute the test. Record the result.**
   > Result: CONFIRMED / REJECTED / INCONCLUSIVE
   > Evidence: [what you observed]

6. **If CONFIRMED:** Write the fix. Proceed to Step 7.
   **If REJECTED:** Return to step 3 with a new hypothesis. After 3 rejected hypotheses, stop and ask Hannah.
   **If INCONCLUSIVE:** Refine the test. Do not change multiple things at once.

7. **After fix:** Verify in the same environment where the failure occurred, not just locally.

### Debug Loop Guardrails

- **Max 5 hypothesis cycles** before escalating to Hannah.
- **Never create a new version/iteration** (v3, v4, v5...) without documenting why the previous one failed.
- **Commit debug artifacts** (test endpoints, logging) on a debug branch, not main. Clean up after resolution.

---

## Step 5 — Self-Evaluate and Pick Winner (Parallel Only)

Score each draft out of 100 points:

| Criterion | Weight | Measurement |
|---|---|---|
| Correctness | 25 | Walk each requirement; deduct for misses. |
| Tests pass | 15 | Run project test command. Pass=15, any fail=0. No tests: redistribute to Correctness (40 total). |
| Typecheck clean | 10 | `tsc --noEmit` or equivalent. 0 errors=10. |
| Lint clean | 5 | Project lint command. 0 warnings=5. |
| Minimal diff | 10 | `10 * (min_LOC / this_LOC)` |
| No unnecessary deps | 10 | 0 new=10; each new=-3 unless required. |
| Reuses existing utilities | 10 | Grep evidence; did it avoid duplication? |
| Follows repo conventions | 10 | Naming, file structure, import style. |
| Scope containment | 5 | Deduct if unrelated files touched. |

**Bonus points (tiebreak only):**
- Integration safety: +5 (handles deployment concerns)
- Pre-flight compliance: +5 (all applicable checks addressed)
- Security: +5 (no secret exposure, no injection vectors, input validation)

**Tiebreakers:** (1) smallest diff, (2) draft 2 (most idiomatic).

Record full score breakdown for all drafts in the run log.

---

## Step 6 — Merge Validation

Before declaring done:

1. **Gap check:** Re-read the original task. Does the winner's diff cover all requirements? If a gap exists, check rejected drafts for that piece. Cherry-pick if found; else write fresh.

2. **Redundancy check:** Scan for unused imports, dead code, commented blocks, debug logs, duplicated helpers shadowing existing utilities. Strip them.

3. **Rerun validation:** Tests + typecheck + lint one final time on the merged diff.

4. **Deployment check:** If the task touches Vercel/Render/cloud-deployed code, verify:
   - No `fs` module usage in serverless functions
   - Environment variables are trimmed at read-site
   - Auth redirects use the correct production domain
   - Image/asset URLs use the correct CDN path format

5. **Content check:** If the diff includes user-facing text, scan for AI-slop patterns (see Step 8).

6. **Data verification:** If the diff references external URLs, API endpoints, or third-party identifiers, verify each one exists. Never commit a fabricated URL.

7. **Merge:** Merge winner's branch into the working branch.

8. **Clean up:** Verify cleanup with `git worktree list` — no orphaned worktrees should remain. Delete losing branches. Keep the winner's branch for post-merge-diff mining.

9. **Report in one line:**
   > Merged draft {N}/{total} (score {X}/100). {reason.} Tests / Types / Lint. Pre-flight: {N} checks applied.

---

## Step 7 — Log the Run (Required, Every Time)

```bash
mkdir -p ~/.claude/skills/code-builder/runs/
```

Write to `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`:

```md
---
date: YYYY-MM-DD
task_slug: dark-mode-journal-editor
repo: interior-designer-portfolio
mode: parallel  # or "single" or "debug-loop"
mode_override: null  # or "single -> parallel" if Hannah flipped
draft_count: 5
winner_draft: 3
winner_sha: abc1234
winner_score: 82
winner_bias: readability
cherry_picks_from: [1]
preflight_checks_fired: [env-var-trim, useEffect-cleanup]
debug_hypotheses: null  # or list (debug-loop mode)
domain_tags: [frontend, deployment]
security_checked: true
---

## Task (verbatim)
> add a dark mode toggle to the journal editor

## Pre-flight
- checked: env-var-trim, useEffect-cleanup
- clean: no external URLs, no cross-session conflicts

## Mode Decision
Parallel (N=5) — new feature, multi-file, multiple design choices.

## Drafts
### Draft 1 — simplest possible
- Approach: CSS variable swap via classList
- Files: app/layout.tsx, app/globals.css (34 LOC)
- Score: 78/100
- SHA: abc1111

### Draft 3 — readability (WINNER)
- Score: 82/100
- Why: matched existing ThemeProvider; no new deps; all tests passed.

## Cherry-picks
- From Draft 1: added prefers-color-scheme media query fallback.

## In-session feedback from Hannah (verbatim)
- "make sure it doesn't flash on first load"
```

### Debug Loop Log Format

For debug-loop runs, replace the Drafts section:

```md
## Debug Loop

### Hypothesis 1
> The shortcut sends an empty body because WFJSONValues isn't inlined.
- Test: Added /api/debug-shortcut endpoint logging raw request body
- Result: CONFIRMED — body was {}
- Evidence: Server log showed Content-Length: 2

## Fix Applied
- Inlined WFJSONValues directly in shortcut plist (line 42-58)
- Verified: shortcut now sends correct JSON body
- Cleaned up: removed debug endpoint

## What Caused the Spiral (retrospective)
Previous iterations each changed multiple variables simultaneously.
Root cause was isolated to plist structure, not URL encoding or auth headers.
```

---

## Step 8 — AI-Slop Check (When Applicable)

Triggers when the diff contains user-facing text in code files.

| Pattern | Replace with |
|---|---|
| "I'd be happy to..." / "Let me help you..." | Direct action or remove |
| "Streamline" / "leverage" / "utilize" | "Simplify" / "use" / "use" |
| "Cutting-edge" / "state-of-the-art" / "robust" | Remove or use specific descriptor |
| "Seamless" / "elevate" / "empower" | Remove or use plain language |
| Unnecessarily long descriptions | Shorter, direct version |

**Hannah's voice:** Direct, slightly informal, no corporate buzzwords. If it sounds like a press release, rewrite it.

---

## Learning Sync (Sunday 6pm + On-Demand)

Triggered automatically on Sunday 6pm or on-demand via "code-builder sync" or `/code-builder sync`.

### Staleness Detection

If `Last synced:` date is >14 days old, print on every activation:
> code-builder: learnings are {N} days stale. Run `code-builder sync` or wait for Sunday.

### Sync Workflow

1. **Determine window:** Read `Last synced:` date. Read only runs with date > last sync.

2. **Collect data from 6 sources:**
   - Run logs (`runs/*.md`)
   - Post-merge git diffs — for each run's `winner_sha`:
     ```
     git log {winner_sha}..HEAD --oneline -- <winner's files>
     git diff {winner_sha}..HEAD -- <winner's files>
     ```
     These diffs are the highest-value learning signal: they show what Hannah silently corrected after the skill's output.
   - In-session feedback (in run logs)
   - Judgment/mode overrides (`mode_override` field)
   - Pre-flight check frequency (`preflight_checks_fired`)
   - Cross-repo mining (auto-discovered from `~/.claude/projects/`, not hardcoded):
     ```
     git log --since="<last-sync-date>" --max-count=50 \
       --grep="fix\|revert\|oops\|simplify\|cleanup\|restore\|debug"
     ```

3. **Pass 1 — Count patterns:** Signal repeated >=2 times becomes candidate.

4. **Pass 2 — Refine, don't append blindly:** Update existing learnings; note reversals; add only genuinely new patterns.

5. **Pass 3 — Promote pre-flight checks:** If a learning fires >=3 times across different repos, promote to Step 1 checklist.

6. **Pass 4 — Debug loop retrospective:** Extract what caused spirals and what the first hypothesis should have been.

7. **Pass 5 — Bias win-rate update:** Tabulate which draft biases won per task type (bug fix, feature, refactor). Store in frontmatter for adaptive bias hints.

8. **Pass 6 — Prune:** Hard cap 30 bullets. Remove oldest, least-cited, or superseded entries.

9. **Write:** Update `## Current learnings` section. Update `Last synced:`.

10. **Announce:** `code-builder sync complete — added {N}, refined {M}, pruned {P}, promoted {Q} to pre-flight. Total: {X}/30.`

---

## Current Learnings

**Last synced:** 2026-04-13 (initial backfill — 4 repos + 13 session summaries)

*If a repo's `CLAUDE.md` contradicts a rule below, the repo rule wins.*

### A. Claude Process Failures

- **Never call `Skill()` from inside a scheduled-task body.** Circular dispatch re-triggers on each tick, burning rate limit. Does not apply to on-demand skills from a user turn.

- **No hardcoded tokens or secrets in client JS.** Anything imported into `"use client"` modules or prefixed `NEXT_PUBLIC_` ships to the browser. Cost: credential rotation + disclosure.

- **"Done" requires green tests + typecheck, not "looks right."** Compile-pass alone forces rework 2-3 messages later.

- **Resolve merge conflicts by re-running tests, not eyeballing.** Code was silently lost 3x. Data loss is the hardest class of bug to trace.

- **Guard nullable KV/API responses before destructuring.** Render `<EmptyState />` or early-return when upstream can return `null`/`undefined`. Cross-repo x3. **[PRE-FLIGHT]**

- **Grep for existing helpers before writing new ones.** Duplicated utilities drift and maintenance compounds. **[PRE-FLIGHT]**

### B. Concrete Code-Level Patterns

- **Validate + trim `process.env.X` at the read-site.** Whitespace/quoting variance across Vercel/Render/local causes silent misconfig. Cross-repo x4. **[PRE-FLIGHT]**

- **Floating UI inside scroll/overflow parent needs `position: fixed` + portal.** Absolute clips inside gallery tiles, mobile sheets, modals. Cross-repo x2. **[PRE-FLIGHT]**

- **Rules of Hooks, full form:** no conditional calls, no hooks inside callbacks/effects, no `return` before hook list completes. **[PRE-FLIGHT]**

- **`useEffect` with subscribe/timer/setState must return cleanup.** Missing cleanup is #1 correction category. Does not apply to pure derived-state effects. **[PRE-FLIGHT]**

- **Unscale `getBoundingClientRect()` values when ancestor has CSS transform.** Measurements return in transformed frame; crop overlays compute wrong origin.

- **Save editor selection before opening DOM-mutating modal; restore on close.** Re-opening toolbar action after modal jumps to wrong line.

### C. Deployment & Platform Patterns

- **Vercel serverless functions cannot use Node `fs` module.** Use API routes with fetch, KV, or external storage.

- **Set `trust proxy` when running Express behind Vercel/Render proxy.** Without it, `req.ip` and secure cookie flags break.

- **Auth redirect URLs must match the deployed domain, not localhost.** Check both `NEXTAUTH_URL` and provider console settings.

- **Image/asset URLs have different formats per storage provider.** Migration between providers requires URL rewriting in the database.

- **GitHub Actions secrets have a 48KB limit.** Use gzip+base64 for large auth state files.

- **Playwright timeouts on cold GHA runners need 3-4min, not 30s.**

### D. Debug Loop Patterns

- **Never change multiple variables simultaneously when debugging.** The iOS Shortcut spiral (v3-v13) happened because each version changed auth headers AND body format AND URL encoding at once.

- **When debugging file upload/storage, verify the pipeline end-to-end in ONE test:** upload, store, read back, verify content matches.

- **When external integration fails, read the dependency's source/docs BEFORE guessing.** iOS Shortcut plist format, Vercel serverless constraints, and R2 URL patterns all have documented specs.

- **If you've made 3+ attempts at the same integration, STOP and write down what you've ruled out.**

---

## Marathon Session Detection

If >=8 runs in a single day, or >=3 consecutive debug-loop runs on the same task:

> code-builder: marathon detected. {N} runs today on `{task}`. Consider: (1) reading docs/source for the integration, (2) asking in a forum, (3) taking a break.

Advisory, not blocking. Build log shows marathon days correlate with spirals, not productive shipping.

---

## Changelog

- **2026-05-13 — v3: consolidated from 5 audit sessions**
  - Token budget awareness: N=3 for medium tasks, N=5 for large only
  - mkdir -p for run log directory (prevents first-run failure)
  - Worktree cleanup verification via `git worktree list`
  - Stale learning detection: warns after 14 days without sync
  - Adaptive bias hints based on win-rate history per task type
  - Cross-skill conflict declaration (defers to mcp-contributor when active)
  - Suppressible single-pass activation banner (3rd+ consecutive suppressed)
  - git init offer when not in a repo (instead of silent downgrade)
  - Post-merge diff mining promoted from deferred to active in sync
  - Auto-discovery of repos from ~/.claude/projects/ (no hardcoded names)
  - Security bonus (+5) in scoring rubric
  - Domain tags and security fields in run log frontmatter
  - Bias win-rate tracking in sync Pass 5

- **2026-05-09 — v2: debug loop + pre-flight + deployment validation**
  - Added Mode 3: Debug Loop with hypothesis-test-learn cycle
  - Added Step 1: Pre-flight Check (process, deployment, cross-session)
  - Added deployment/debug learnings (sections C, D)
  - Added Step 8: AI-Slop Check
  - Added marathon session detection
  - Total learnings: 18/30

- **2026-04-13 — v1: initial backfill**
  - 12 bullets from 4 repos + 13 session summaries
