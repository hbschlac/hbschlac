# code-builder

## Overview

**code-builder** is a Claude agent skill that improves code quality through three execution modes:

1. **Single pass** — one implementation, fast, for obvious fixes
2. **Parallel (N=5)** — five isolated drafts scored against a 100-point rubric, winner merged
3. **Debug loop** — systematic hypothesis-test-learn cycle for integration failures and iterative fixes

The core hypothesis: single-pass output leaves performance on the table. Parallel attempts with objective evaluation raise the floor. And when the problem is iterative debugging — not first-pass generation — a structured debug loop prevents spirals.

---

## Activation

**Auto-triggers whenever Hannah is writing, changing, or fixing code.** Explicit signals: `/code-builder`, "build this," "fix this bug," "add a feature." Implicit: working in a git repo while describing a coding task, sharing error messages or stack traces, working in known project repositories.

**Do NOT activate for:** pure code reading, research, writing prose (unless editing user-facing copy in code files), design, planning, or meta-tasks like "what are my TODOs?"

**Default rule:** when uncertain, activate. A single-pass run costs negligible resources; missing an actual dev task is worse.

---

## Required Announcement

Before any work begins, print this one-line banner:

> 🔧 **code-builder activated** — [parallel, 5 drafts | single pass | debug loop]. [≤15-word reason.]

Example: `🔧 code-builder activated — parallel, 5 drafts. New feature; multiple architectures viable.`
Example: `🔧 code-builder activated — debug loop. iOS shortcut failing against API; need systematic isolation.`

Hannah can override with "actually, 5x this" or "actually, just fix it" or "actually, debug this" to flip modes.

---

## Step 1 — Pre-flight Check

**Before writing any code**, scan the task against known failure patterns. This runs in ALL modes.

### §A Checks (Claude Process Failures)

| Check | Action if triggered |
|---|---|
| Task touches `process.env.*` or env vars? | Validate + trim at read-site. Check for `NEXT_PUBLIC_` exposure. |
| Task adds a `useEffect`? | Must return cleanup function if it subscribes, starts timer, or sets state. |
| Task uses floating UI (tooltip, dropdown, popover)? | Check for scroll/overflow parent — use `position: fixed` + portal, not `absolute`. |
| Task destructures API/KV response? | Guard nullable response before destructuring. Render `<EmptyState />` or early-return. |
| Task could duplicate an existing utility? | `grep -r` for similar helpers before writing new ones. |
| Task adds conditional logic around a hook? | Verify Rules of Hooks: no conditional calls, no hooks in callbacks/effects. |

### §B Checks (Deployment & Integration)

| Check | Action if triggered |
|---|---|
| Deploying to Vercel? | Verify: no `fs` access in serverless, correct entry point, `trust proxy` if behind proxy. |
| Task changes auth/OAuth flow? | Verify redirect URLs for BOTH local and production. Check cookie domain. |
| Task involves image/file storage? | Verify upload→storage→retrieval pipeline. Check URL format (public vs private, CDN path). |
| Task generates user-facing copy? | Run AI-slop check (Step 8). |
| Task references external URLs or data? | Verify every URL exists. Never fabricate. Flag for manual verification if unsure. |

### §C Checks (Cross-Session Safety)

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

---

## Step 3 — Judgment Gate

**Three modes.** Default is single pass. Escalate based on signals.

### → Parallel (N=5) threshold

Escalate when ≥2 soft signals fire OR any hard signal fires:

**Soft signals:**
- \>30 LOC changed
- \>1 file touched OR new file created
- Multiple valid architectures exist
- New pattern to the repo
- Touches critical path (auth, checkout, data layer)
- Feature/refactor/greenfield task type
- Open-ended phrasing ("build X", "make Y better")

### → Debug loop threshold

Escalate when ANY of these fire:

- **This is attempt ≥2** at the same task (prior attempt failed or was reverted)
- Error involves an **external integration** (API endpoint, third-party service, device-specific behavior, OAuth provider, CDN/storage)
- Error **reproduces in production but not locally** (or vice versa)
- Hannah says "this keeps breaking" or "I've tried X already"
- **3+ consecutive fix commits** in the same area visible in recent git log

### → Single pass (default)

Use when none of the above escalation signals fire:
- <10 lines changed
- Exactly 1 existing file
- One obviously correct path
- Variation of existing pattern
- Contained to leaf component
- Targeted bug fix with known root cause
- Specific phrasing ("change line 42 to...")

### Hard overrides (any one decides immediately)

- Hannah explicit override → obey
- Not a git repo → force **single** (worktrees require git)
- Live debugging with rapid iteration → force **single** (parallel too slow)
- Greenfield prototype from scratch → force **parallel**
- "This keeps failing" / integration failure → force **debug loop**

---

## Step 4a — Parallel Path (N=5)

**Prerequisite:** Claude's working directory must be a git repository. Verify with `git rev-parse --git-dir`. If not in a repo, downgrade to single pass.

If repo confirmed:

1. Spawn **5 `Agent` calls in parallel in a single message**, each with:
   - `isolation: "worktree"` (isolated branch per draft)
   - `run_in_background: true`
   - `subagent_type: "general-purpose"`
   - Task prompt includes: the full task description, pre-flight check results, and differentiation bias:
     - Draft 1: simplest possible — fewest lines, no abstractions
     - Draft 2: most idiomatic to this repo — match existing patterns exactly
     - Draft 3: optimize for readability — clearest naming, smallest functions
     - Draft 4: optimize for performance/correctness on edge cases
     - Draft 5: best instinct — your choice

2. Each draft agent prompt must include: "Before coding, check for existing utilities with `grep -r`. After coding, run the project's test command, `tsc --noEmit`, and lint."

3. Each draft should: commit work on its worktree branch, report approach (2 lines), files touched, LOC added/removed, commit SHA, edge cases.

4. Wait for all 5 to complete. If any fail/timeout, continue with survivors.

---

## Step 4b — Single Path

Execute the task normally. Skip to Step 7.

---

## Step 4c — Debug Loop

For integration failures and iterative debugging. The goal is to **prevent spirals** by forcing structured hypothesis testing.

### Debug Loop Protocol

1. **State the current failure precisely:**
   > What happens: [exact error/behavior]
   > What should happen: [expected behavior]
   > Environment: [local/Vercel/GHA/device]

2. **List what's already been tried** (from git log, conversation, or Hannah's description). Do not repeat failed approaches.

3. **Form exactly one hypothesis.** Write it as a falsifiable statement:
   > Hypothesis: The API returns 403 because the auth header isn't forwarded through the Vercel serverless proxy.

4. **Design the minimal test** to confirm or reject the hypothesis. Prefer:
   - Adding a single `console.log` / debug endpoint over changing production code
   - `curl` to isolate network from application logic
   - Reading source/docs of the external dependency before guessing

5. **Execute the test. Record the result.**
   > Result: CONFIRMED / REJECTED / INCONCLUSIVE
   > Evidence: [what you observed]

6. **If CONFIRMED:** Write the fix. Proceed to Step 7.
   **If REJECTED:** Return to step 3 with a new hypothesis. After 3 rejected hypotheses, **stop and ask Hannah** — you may be missing context.
   **If INCONCLUSIVE:** Refine the test. Do not change multiple things at once.

7. **After fix:** Verify in the same environment where the failure occurred, not just locally.

### Debug Loop Guardrails

- **Max 5 hypothesis cycles** before escalating to Hannah. Print: "🔧 debug loop: 5 hypotheses tested, none confirmed. Here's what I've ruled out: [list]. What am I missing?"
- **Never create a new version/iteration** (v3, v4, v5...) without documenting why the previous one failed. The iOS Shortcut spiral (v3→v13) happened because failures weren't recorded.
- **Commit debug artifacts** (test endpoints, logging) on a debug branch, not main. Clean up after resolution.

---

## Step 5 — Self-Evaluate and Pick Winner (Parallel Only)

**Claude picks.** Do not ask Hannah to review 5 diffs.

Score each draft out of 100 points:

| Criterion | Weight | Measurement |
|---|---|---|
| Correctness | 25 | Walk each requirement; deduct for misses. |
| Tests pass | 15 | Run project test command. Pass=15, any fail=0. No tests → redistribute to Correctness (40 total). |
| Typecheck clean | 10 | `tsc --noEmit` or equivalent. 0 errors=10. |
| Lint clean | 5 | Project lint command. 0 warnings=5. |
| Minimal diff | 10 | `10 × (min_LOC / this_LOC)` |
| No unnecessary deps | 10 | 0 new=10; each new=−3 unless required. |
| Reuses existing utilities | 10 | Grep evidence; did it avoid duplication? |
| Follows repo conventions | 10 | Naming, file structure, import style. |
| Scope containment | 5 | Deduct if unrelated files touched. |

**Bonus points (can exceed 100, used only for tiebreak):**

| Criterion | Bonus | Measurement |
|---|---|---|
| Integration safety | +5 | Handles deployment-specific concerns (env var trimming, proxy headers, CDN URLs). |
| Pre-flight compliance | +5 | All applicable pre-flight checks addressed in the implementation. |

**Tiebreakers:** (1) smallest diff, (2) draft 2 (most idiomatic).

Record full score breakdown for all 5 drafts in the run log.

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

5. **Content check:** If the diff includes user-facing text (button labels, headings, descriptions, error messages), scan for AI-slop patterns: "I'd be happy to", "streamline", "leverage", "utilize", "cutting-edge", "robust", unnecessarily formal language, or marketing-speak that doesn't match Hannah's voice. Rewrite to plain, direct language.

6. **Data verification:** If the diff references external URLs, API endpoints, or third-party identifiers, verify each one exists. Never commit a fabricated URL.

7. **Merge:** Merge winner's branch into the working branch (fast-forward if possible, else `--no-ff`).

8. **Clean up:** `git worktree remove` all 5. Delete losing branches. **Keep the winner's branch** (for post-merge-diff signals in Sunday sync).

9. **Report in one line:**
   > ✓ Merged draft {N}/5 (score {X}/100). {≤15-word reason.} {Cherry-picked {Y} from draft M | No gaps.} Tests ✓ Types ✓ Lint ✓. {Pre-flight: N checks applied.}

If Hannah says "actually use draft 3" or "tests still fail," re-pick or debug and log the override in the run file.

---

## Step 7 — Log the Run (Required, Every Time)

Write to `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`:

```md
---
date: 2026-04-13
task_slug: dark-mode-journal-editor
repo: interior-designer-portfolio
mode: parallel  # or "single" or "debug-loop"
mode_override: null  # or "single → parallel" if Hannah flipped it
winner_draft: 3
winner_sha: abc1234
winner_score: 82
cherry_picks_from: [1]
preflight_checks_fired: [env-var-trim, useEffect-cleanup]
debug_hypotheses: null  # or list of hypotheses tested (debug-loop mode)
---

## Task (verbatim)
> add a dark mode toggle to the journal editor

## Pre-flight
- ✓ env-var-trim: checked NEXT_PUBLIC_THEME_KEY
- ✓ useEffect-cleanup: added cleanup for theme listener
- ○ no external URLs referenced
- ○ no cross-session conflicts detected

## Mode Decision
Parallel — new feature, multi-file (context + CSS + storage), multiple design choices.

## Drafts

### Draft 1 — simplest possible
- Approach: CSS variable swap via `document.documentElement.classList`
- Files: `app/layout.tsx`, `app/globals.css` (34 LOC)
- Score: 78/100
- SHA: `abc1111`

### Draft 2 — most idiomatic
[details...]

### Draft 3 — readability ⭐ WINNER
- Score: 82/100
- Why it won: Matched existing ThemeProvider; no new deps; passed all tests.

### Draft 4 — performance
[details...]

### Draft 5 — free choice
[details...]

## Cherry-picks
- From Draft 1: added `prefers-color-scheme` media query fallback.

## In-session feedback from Hannah (verbatim)
- "make sure it doesn't flash on first load"

## Notes
Draft 5 timed out at 3min. Scored based on partial diff.
```

### Debug Loop Log Format

For debug-loop runs, replace the Drafts section:

```md
## Debug Loop

### Hypothesis 1
> The shortcut sends an empty body because WFJSONValues isn't inlined in the plist.
- Test: Added `/api/debug-shortcut` endpoint logging raw request body
- Result: CONFIRMED — body was `{}`
- Evidence: Server log showed Content-Length: 2

### Hypothesis 2 (if needed)
[...]

## Fix Applied
- Inlined WFJSONValues directly in shortcut plist (line 42-58)
- Verified: shortcut now sends correct JSON body
- Cleaned up: removed `/api/debug-shortcut` endpoint

## What Caused the Spiral (retrospective)
Previous iterations (v3-v8) each changed multiple variables simultaneously.
Root cause was isolated to plist structure, not URL encoding or auth headers.
```

Log all fields every run — the Sunday sync depends on them being structured.

---

## Step 8 — AI-Slop Check (When Applicable)

Triggers when the diff contains user-facing text in code files (JSX, HTML, markdown content in components).

**Scan for these patterns and rewrite:**

| Pattern | Replace with |
|---|---|
| "I'd be happy to..." / "Let me help you..." | Direct action or remove |
| "Streamline" / "leverage" / "utilize" | "Simplify" / "use" / "use" |
| "Cutting-edge" / "state-of-the-art" / "robust" | Remove or use specific descriptor |
| "Seamless" / "elevate" / "empower" | Remove or use plain language |
| Unnecessarily long descriptions | Shorter, direct version |
| Marketing-speak that doesn't match the product | Match the product's actual voice |

**Hannah's voice:** Direct, slightly informal, no corporate buzzwords. If it sounds like a press release, rewrite it.

---

## Sunday Sync (Scheduled, 6pm + On-Demand)

Triggered automatically on Sunday 6pm or on-demand when Hannah says "code-builder sync" or runs `/code-builder sync`.

### Sync Workflow

1. **Determine window:** Read `Last synced:` date at top of `## Current learnings` below. If "never," read all `runs/*.md`. Otherwise, read only runs with date > last sync.

2. **Collect data from 6 sources:**
   - Run logs (`runs/*.md`) — including new debug-loop logs
   - Post-merge git diffs — for each run's `winner_sha`, in that repo:
     ```
     git log {winner_sha}..HEAD --oneline -- <winner's files>
     git diff {winner_sha}..HEAD -- <winner's files>
     ```
   - In-session feedback (already in run logs)
   - Judgment/mode overrides (`mode_override` field in frontmatter)
   - Pre-flight check frequency (`preflight_checks_fired` in frontmatter) — which checks fire most?
   - Cross-repo mining (bounded) — for each active repo, run:
     ```
     git log --since="<last-sync-date>" --max-count=50 \
       --grep="fix\|revert\|oops\|simplify\|cleanup\|restore\|debug"
     ```

3. **Pass 1 — Count patterns:** Any signal repeated ≥2 times becomes a candidate learning.

4. **Pass 2 — Refine, don't append blindly:** Update existing learnings; note reversals; add only genuinely new patterns.

5. **Pass 3 — Promote pre-flight checks:** If a learning fires ≥3 times across different repos, promote it to the pre-flight checklist in Step 1.

6. **Pass 4 — Debug loop retrospective:** For any debug-loop runs this week, extract: (a) what caused the spiral, (b) what the first hypothesis should have been in hindsight. Add to §D learnings.

7. **Pass 5 — Prune:** Enforce hard cap of 30 bullets. Remove oldest, least-cited, or superseded entries if over.

8. **Write:** Use `Edit` to update `## Current learnings` section. Update `Last synced:` to today. Commit nothing — this file lives in `~/.claude/skills/`, not in a repo.

9. **Announce:** `🔧 code-builder sync complete — added {N}, refined {M}, pruned {P}, promoted {Q} to pre-flight. Total learnings: {X}/30.`

---

## Current Learnings

**Last synced:** 2026-04-13 (initial backfill — 4 repos + 13 session summaries; 12 bullets)

*If a repo's `CLAUDE.md` contradicts a rule below, the repo rule wins.*

### §A. Claude Process Failures

- **Never call `Skill()` from inside a scheduled-task body.** Circular dispatch re-triggers on each tick, burning rate limit until killed. Does not apply to on-demand skills invoked from a user turn. (1 citation)

- **No hardcoded tokens or secrets in client JS — even internal tools.** Anything imported into `"use client"` modules or prefixed `NEXT_PUBLIC_` ships to the browser; credential rotation and disclosure is the cost. (1 citation)

- **"Done" requires green tests + typecheck, not "looks right."** Compile-pass alone forces rework loops when real failures surface 2–3 messages later. (2 citations)

- **Resolve merge conflicts by re-running tests, not by eyeballing.** Code was silently lost 3× — data loss is the hardest class of bug to trace. (1 citation)

- **Guard nullable KV/API responses before destructuring.** Render `<EmptyState />` or early-return when upstream can return `null`/`undefined`; `const { foo } = res` crashes instead of showing empty state. Cross-repo ×3. (3 citations)

- **Grep for existing helpers before writing new ones.** Calmar accumulated 3× duplicated date-formatting utilities; copies drift and maintenance compounds. (1 citation)

### §B. Concrete Code-Level Patterns

- **Validate + trim `process.env.X` at the read-site.** Whitespace, quoting, trailing-newline variance across Vercel/Render/local cause silent misconfig. Cross-repo ×4. (4 citations) **[PRE-FLIGHT]**

- **Floating UI inside a scroll/overflow parent needs `position: fixed` + portal, not `position: absolute`.** Absolute clips inside gallery tiles, mobile sheets, modals. Cross-repo ×2. (1 citation) **[PRE-FLIGHT]**

- **Rules of Hooks, full form:** no conditional calls, no hooks inside callbacks/effects, no `return` before hook list completes. React's error surfaces one render later. Cross-repo ×2. (Agent mining, 2026-04-13) **[PRE-FLIGHT]**

- **`useEffect` that subscribes, starts a timer, or sets state must return cleanup function.** Missing cleanup is #1 correction category. Does not apply to pure derived-state effects. ×4. (Agent mining, 2026-04-13) **[PRE-FLIGHT]**

- **Unscale `getBoundingClientRect()` values when ancestor has CSS transform.** Measurements return in transformed frame; crop overlays compute wrong origin and zoom jumps. (2 citations)

- **Save editor selection before opening DOM-mutating modal; restore on close.** Re-opening toolbar action after modal jumps to wrong line or loses caret. (2 citations)

### §C. Deployment & Platform Patterns

- **Vercel serverless functions cannot use Node `fs` module.** Use API routes with fetch, KV, or external storage (R2, Blob). (Build log: interior-designer-portfolio, 3+ citations)

- **Set `trust proxy` when running Express behind Vercel/Render proxy.** Without it, `req.ip` and secure cookie flags break. (Build log: muse-shopping, 2 citations)

- **Auth redirect URLs must match the deployed domain, not localhost.** Google/Apple OAuth will silently fail or redirect to wrong origin. Check both `NEXTAUTH_URL` and provider console settings. (Build log: muse-shopping, 3 citations)

- **Image/asset URLs have different formats per storage provider.** Vercel Blob uses `.public.blob.vercel-storage.com`, R2 uses custom domain or `r2.dev`. Migration between providers requires URL rewriting in the database. (Build log: interior-designer-portfolio, 7+ citations)

- **GitHub Actions secrets have a 48KB limit.** Use gzip+base64 encoding for large auth state files. (Build log: libby-hold-monitor, 1 citation)

- **Playwright timeouts on cold GHA runners need 3-4min, not 30s.** Default timeouts cause false failures on first run. (Build log: libby-hold-monitor, 1 citation)

### §D. Debug Loop Patterns

- **Never change multiple variables simultaneously when debugging.** The iOS Shortcut spiral (v3→v13) happened because each version changed auth headers AND body format AND URL encoding at once. Isolate one variable per hypothesis. (Build log: interior-designer-portfolio, 12+ iterations)

- **When debugging file upload/storage, verify the pipeline end-to-end in ONE test:** upload → store → read back → verify content matches. Don't assume intermediate steps work. (Build log: interior-designer-portfolio R2 migration, 7+ citations)

- **When external integration fails, read the external dependency's source/docs BEFORE guessing.** iOS Shortcut plist format, Vercel serverless constraints, and R2 URL patterns all have documented specs that would have prevented trial-and-error. (Retrospective, multiple repos)

- **If you've made 3+ attempts at the same integration, STOP and write down what you've ruled out.** The act of writing forces clarity and prevents re-testing rejected hypotheses. (Meta-pattern from build log analysis)

---

## Marathon Session Detection

If code-builder logs ≥8 runs in a single day, or ≥3 consecutive debug-loop runs on the same task:

> ⚠️ **code-builder: marathon detected.** {N} runs today on `{task}`. Consider: (1) stepping back to read docs/source for the integration, (2) asking in a forum/community, (3) taking a break and returning fresh.

This is advisory, not blocking. But the build log shows that marathon days (Apr 5, Apr 14, Apr 16 with 15-20+ commits each) correlate with debugging spirals, not productive feature shipping.

---

## Meta Notes

- `isolation: "worktree"` Agent parameter fails when Claude's cwd is not a git repo. Documented as prerequisite in Step 4a. If it fails, auto-downgrade to single pass and tell Hannah to restart from the project repo.

- The `insight-detector.py` stub in `claude-code-insights-dashboard` should be implemented to feed friction signals back into this skill's Sunday sync. Deferred until the sync is running reliably.

- Cross-session safety (Step 1, §C checks) is a best-effort heuristic. It catches uncommitted changes and recent conflicting commits but cannot prevent a parallel session from force-pushing. For critical work, use separate branches.

- Deferred to later syncs: holdout-commit eval, N=5 live-task precision/recall, citation-validity lint, token-budget hard cap, stale-rule quarterly audit, cross-skill conflict scan.

---

## Changelog

- **2026-05-09 — v2: debug loop + pre-flight + deployment validation**
  - Added Mode 3: Debug Loop (Step 4c) with hypothesis-test-learn cycle, max 5 hypotheses, structured logging
  - Added Step 1: Pre-flight Check with §A (process), §B (deployment), §C (cross-session) checks
  - Added §C learnings: 6 deployment/platform patterns extracted from build log analysis
  - Added §D learnings: 4 debug loop patterns extracted from iOS Shortcut and R2 migration spirals
  - Added Step 8: AI-Slop Check for user-facing copy in code files
  - Added deployment validation to Step 6 (merge validation)
  - Added data/URL verification to Step 6
  - Added content quality check to Step 6
  - Added marathon session detection
  - Added bonus scoring criteria for integration safety and pre-flight compliance
  - Added debug-loop log format to Step 7
  - Updated Sunday Sync with Pass 3 (promote to pre-flight), Pass 4 (debug retrospective)
  - Marked 4 learnings as **[PRE-FLIGHT]** to indicate proactive checking
  - Total learnings: 18/30 (was 12/30)

- **2026-04-13 backfill sanity test** — task: populate §A + §B. Initial 12 bullets from 4 repos + 13 session summaries.
