---
name: code-builder
description: >
  Improves code quality through three execution modes: single pass (fast, obvious),
  parallel (N isolated drafts scored on rubric, winner merged), and debug loop
  (hypothesis-test-learn for integration failures). Self-improving via learning sync.
---

# code-builder

## Activation

Auto-triggers on coding tasks. Explicit: `/code-builder`, "build this," "fix this bug."
Implicit: working in a git repo while describing a coding task, sharing error messages.

Do NOT activate for: pure code reading, research, writing prose, design, planning, meta-tasks.

Default: when uncertain, activate. Single-pass costs nothing; missing a dev task is worse.

**Conflict:** If `mcp-contributor` is active (guiding a PR to the MCP org), code-builder defers to its workflow. code-builder handles only code tasks mcp-contributor doesn't claim.

## Announcement

> **code-builder activated** — [parallel, N drafts | single pass | debug loop]. [reason.]

Suppress after 3rd consecutive single-pass in the same session.

---

## Step 1 — Pre-flight Check

Runs in ALL modes before writing code.

### 1A. Claude Process Failures

| Check | Action |
|---|---|
| Task touches `process.env.*`? | Validate + trim at read-site. Check for `NEXT_PUBLIC_` exposure — anything with that prefix ships to browser. |
| Task adds a `useEffect`? | Must return cleanup if it subscribes, starts timer, or sets state. |
| Task uses floating UI (tooltip, dropdown, popover)? | Use `position: fixed` + portal, not `absolute` inside scroll parents. |
| Task destructures API/KV response? | Guard nullable response before destructuring. Render `<EmptyState />` or early-return. |
| Task could duplicate existing utility? | `grep -r` for similar helpers before writing new ones. |
| Task adds conditional logic around a hook? | No conditional calls, no hooks in callbacks/effects. |
| Task adds user-facing text? | Run content-quality checks (see content-quality skill). |

### 1B. Deployment & Integration

| Check | Action |
|---|---|
| Deploying to Vercel? | No `fs` in serverless. Correct entry point. `trust proxy` if behind proxy. Check both dev server entry (`src/app.js`) AND serverless entry (`api/index.js`) — middleware registered in one may be missing from the other. |
| Task changes auth/OAuth flow? | Verify redirect URLs for local AND production. Check cookie domain. |
| Task involves image/file storage? | Verify upload-store-retrieve pipeline end-to-end. Check URL format. |
| Task references external URLs? | Verify every URL exists. Never fabricate. Use `[TODO: add URL]` if unverified. |
| Monorepo or multi-directory? | Install dependencies in ALL entry points, not just root. Check for workspace configs. |

### 1C. Cross-Session Safety

| Check | Action |
|---|---|
| Uncommitted changes from another session? | `git stash list` + `git status`. Do NOT overwrite — ask Hannah. |
| Files modified in last 2 hours by different commit? | Flag potential conflict. |
| Components imported by 3+ files? | Extra caution on deletion — verify all import sites. |
| Similar work exists on other branches? | `git branch -a \| head -30`. If overlap found, build on existing work. |

Output: one-line summary of which checks fired, or "Pre-flight clean."

---

## Step 2 — Scope the Task

State the task in one line. Identify:
- Files likely to change
- Greenfield (new) or modification (fix/tweak)
- Design space: multiple valid approaches or one obvious path?
- Integration surface: external services, APIs, device-specific behavior?
- Estimated complexity: small (<30 LOC), medium (30-150 LOC), large (>150 LOC)

---

## Step 3 — Judgment Gate

Three modes. Default is single pass. Escalate based on signals.

### Parallel threshold

Escalate when >=2 soft signals fire OR any hard signal fires:

Soft signals: >30 LOC, >1 file touched, multiple valid architectures, new pattern to the repo, touches critical path, feature/refactor/greenfield, open-ended phrasing.

**Draft count (token-budget aware):**
- Large (>150 LOC, >3 files) → N=5
- Medium (30-150 LOC) → N=3
- Near rate limits or >2 parallel runs this session → N=3 regardless

### Debug loop threshold

Escalate when ANY fire:
- Attempt >=2 at the same task (prior failed/reverted)
- Error involves external integration (API, OAuth, device-specific)
- Reproduces in production but not locally (or vice versa)
- Hannah says "this keeps breaking" or "I've tried X already"
- 3+ consecutive fix commits in the same area in recent git log
- Same file/function fixed 3+ times in recent `git log`
- Current error matches a recently committed fix (regression)

### Single pass (default)

<30 LOC, 1 file, one obvious path, existing pattern, leaf component, known root cause.

### Hard overrides

- Hannah explicit override: obey
- Not a git repo: offer `git init`; if declined, force single
- Live debugging with rapid iteration: force single
- Greenfield prototype from scratch: force parallel
- "This keeps failing" / integration failure: force debug loop

---

## Step 4a — Parallel Path

1. Verify git repo: `git rev-parse --git-dir`. If not, offer `git init`.

2. Create run log dir: `mkdir -p ~/.claude/skills/code-builder/runs/`

3. Spawn **N `Agent` calls in parallel** (single message), each with:
   - `isolation: "worktree"`, `run_in_background: true`, `subagent_type: "general-purpose"`
   - Differentiation bias:
     - Draft 1: simplest possible — fewest lines, no abstractions
     - Draft 2: most idiomatic to this repo — match existing patterns exactly
     - Draft 3: optimize for readability — clearest naming, smallest functions
     - (N=5) Draft 4: optimize for performance/correctness on edge cases
     - (N=5) Draft 5: best instinct — free choice
   - Adaptive bias: if win-rate history exists in run logs, weight toward historically winning biases.
   - Each prompt includes: "Before coding, `grep -r` for existing utilities. After coding, run tests, `tsc --noEmit`, and lint."

4. Each draft: commit on worktree branch, report approach (2 lines), files touched, LOC, SHA, edge cases.

5. Wait for all N. Continue with survivors if any fail/timeout.

## Step 4b — Single Path

Execute normally. Skip to Step 7.

## Step 4c — Debug Loop

### Pre-Step 0: Failed Approach Check (mandatory)

Before forming ANY hypothesis:

```bash
git log --all --oneline -20 -- {file}
git log --all --oneline --grep="fix" -- {file}
```

Scan for prior fix attempts across ALL branches. List them:

```
Prior attempts found:
- {sha} {date}: {what was tried}
These approaches are OFF LIMITS.
```

### Step 1: State the failure precisely

> What happens: [exact error/behavior]
> What should happen: [expected behavior]
> Environment: [local/Vercel/GHA/device]

### Step 2: Read before writing

Do NOT write any code. Instead:
1. Read the full function, its callers, and dependencies — not just the error line.
2. Read the last 3-5 diffs touching this area: `git log -p -5 -- {file}`
3. Read error messages, stack traces, browser console output.
4. Check if the bug is environment-specific (Vercel serverless vs local, case-sensitive imports, missing env vars).

### Step 3: Hypothesize

Form a single-sentence hypothesis about the ROOT CAUSE (not the symptom):

```
debug-loop: hypothesis — {one sentence}
```

Root cause vs symptom examples:
- Symptom: "popup doesn't close" / Root: "window.close() blocked because reload() cleared opener reference"
- Symptom: "API returns 500" / Root: "trust proxy not set in Vercel serverless, rate limiter reads 127.0.0.1"

### Step 4: Prove it

Write a minimal diagnostic (NOT the fix):
- Single console.log at suspected root cause
- Failing test that reproduces the bug
- curl command demonstrating API behavior

### Step 5: Fix (only after proof)

Target the proven root cause. The fix must:
- Address root cause, not paper over symptom
- Not revert to an approach that already failed (checked in Pre-Step 0)
- Include a guard or test preventing regression

### Step 6: Verify

Run the same diagnostic from Step 4. Check for side effects. Run tests.

### Debug Loop Limits

- **5 hypothesis cycles max.** After 5:
  ```
  debug-loop: exhausted after 5 cycles.
  Ruled out: [list with evidence]
  Remaining unknowns: [what would narrow it down]
  Suggested next steps: [specific questions or data Hannah could provide]
  ```
- **Never change multiple variables simultaneously.** One hypothesis, one change, one test.
- **Never repeat a failed approach.** If a similar fix was already tried and committed, it didn't work.
- **After 3+ attempts at the same integration, STOP and write what you've ruled out.**

---

## Step 5 — Self-Evaluate and Pick Winner (Parallel Only)

Score each draft out of 100:

| Criterion | Weight |
|---|---|
| Correctness (walk each requirement) | 25 |
| Tests pass | 15 (0 if any fail; redistribute to Correctness if no tests) |
| Typecheck clean | 10 |
| Lint clean | 5 |
| Minimal diff (`10 * min_LOC / this_LOC`) | 10 |
| No unnecessary deps (0 new=10; each new=-3) | 10 |
| Reuses existing utilities | 10 |
| Follows repo conventions | 10 |
| Scope containment | 5 |

Tiebreak bonus: integration safety +5, pre-flight compliance +5, security +5.
Final tiebreak: (1) smallest diff, (2) draft 2 (most idiomatic).

Record full score breakdown in run log.

---

## Step 6 — Merge Validation

1. **Gap check:** Re-read original task. Does winner cover all requirements? Cherry-pick from rejected drafts if gap found.
2. **Redundancy check:** Strip unused imports, dead code, debug logs, duplicated helpers.
3. **Rerun validation:** Tests + typecheck + lint on merged diff.
4. **Deployment check:** No `fs` in serverless, env vars trimmed, auth redirects use production domain, correct CDN paths. If Vercel multi-builder, verify BOTH entry points.
5. **Content check:** If diff includes user-facing text, invoke content-quality skill checks.
6. **Data check:** Verify all external URLs/endpoints exist. Never commit fabricated URLs.
7. **Merge** winner's branch. Clean up worktrees: `git worktree list` then `git worktree remove`.
8. **Report:** `Merged draft {N}/{total} (score {X}/100). {reason.} Tests / Types / Lint.`

---

## Step 7 — Log the Run

Write to `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`:

```md
---
date: YYYY-MM-DD
task_slug: dark-mode-journal-editor
repo: interior-designer-portfolio
mode: parallel | single | debug-loop
draft_count: 5
winner_draft: 3
winner_sha: abc1234
winner_score: 82
winner_bias: readability
cherry_picks_from: [1]
preflight_checks_fired: [env-var-trim, useEffect-cleanup]
debug_hypotheses: null
domain_tags: [frontend, deployment]
---

## Task (verbatim)
> add a dark mode toggle to the journal editor

## Pre-flight
- checked: env-var-trim, useEffect-cleanup
- clean: no external URLs, no cross-session conflicts

## Mode Decision
Parallel (N=5) — new feature, multi-file, multiple design choices.

## In-session feedback from Hannah (verbatim)
- "make sure it doesn't flash on first load"
```

---

## Step 8 — AI-Slop Check

Triggers when diff contains user-facing text. Defers to content-quality skill
if loaded; otherwise applies these inline:

| Pattern | Replace with |
|---|---|
| "I'd be happy to..." / "Let me help you..." | Direct action or remove |
| "Streamline" / "leverage" / "utilize" | "simplify" / "use" / "use" |
| "Cutting-edge" / "state-of-the-art" / "robust" | Remove or use specific descriptor |
| "Seamless" / "elevate" / "empower" | Remove or use plain language |
| "Comprehensive" / "holistic" / "delve" | Remove or say what actually happens |

Hannah's voice: direct, slightly informal, no corporate buzzwords.

---

## Learning Sync

Triggered Sunday 6pm or on-demand via "code-builder sync."

**Staleness detection:** If `Last synced:` is >14 days old, print on every activation:
> code-builder: learnings are {N} days stale. Run `code-builder sync`.

### Sync workflow

1. Read `Last synced:` date. Read only runs after that date.
2. Collect from: run logs, post-merge git diffs (what Hannah corrected after skill output), in-session feedback, mode overrides, pre-flight check frequency, cross-repo mining (`git log --since --max-count=50 --grep="fix|revert|oops|simplify|restore|debug"`).
3. Signal repeated >=2 times → candidate.
4. Update existing learnings; note reversals; add only genuinely new patterns.
5. Promote pre-flight checks that fire >=3 times across repos.
6. Extract what caused debug spirals and what the first hypothesis should have been.
7. Update bias win-rates per task type.
8. Hard cap 30 bullets. Remove oldest/least-cited.
9. Update `## Current learnings` and `Last synced:`.

### Sync bounds

| Source | Scope | Bound |
|---|---|---|
| Run logs | Since last sync | All |
| Cross-repo git log | Since last sync | `--max-count=50` per repo |
| Session summaries | Backfill only | Not recurring — too expensive for marginal value |

### Author filter

Only mine commits from Hannah, `claude[bot]`, or Claude's local commit identity.
Exclude outside contributor PRs — their patterns aren't Claude's failures.

### Work/personal firewall

No Walmart or internal session content enters learnings. Allowed personal repos:
`hbschlac/hbschlac`, `hannah-portfolio`, `libby-hold-monitor`, `muse-shopping`,
`claude-code-insights-dashboard`, `claude-config`.

---

## Current Learnings

**Last synced:** 2026-05-24 (consolidated from 25 session branches)

*If a repo's CLAUDE.md contradicts a rule below, the repo rule wins.*

### A. Claude Process Failures

- **Never call `Skill()` from inside a scheduled-task body.** Circular dispatch re-triggers on each tick. Does not apply to on-demand skills from a user turn.
- **No hardcoded tokens or secrets in client JS.** `"use client"` modules or `NEXT_PUBLIC_` prefix ships to browser. Cost: credential rotation.
- **"Done" requires green tests + typecheck, not "looks right."** Declare completion only after running the repo's actual test/lint commands.
- **Resolve merge conflicts by re-running tests, not eyeballing.** Code was silently lost 3x across repos.
- **Guard nullable KV/API responses before destructuring.** Render `<EmptyState />` or early-return. Cross-repo x3. **[PRE-FLIGHT]**
- **Grep for existing helpers before writing new ones.** Duplicated utilities drift. **[PRE-FLIGHT]**
- **Don't create orphaned analysis files (AUDIT.md, REVIEW.md).** Put findings in CLAUDE.md or inline. Orphaned docs die on branches.

### B. Concrete Code-Level Patterns

- **Validate + trim `process.env.X` at the read-site.** Whitespace/quoting variance across Vercel/Render/local. Cross-repo x4. **[PRE-FLIGHT]**
- **Floating UI inside scroll/overflow parent needs `position: fixed` + portal.** Cross-repo x2. **[PRE-FLIGHT]**
- **Rules of Hooks, full form:** no conditional calls, no hooks inside callbacks/effects. **[PRE-FLIGHT]**
- **`useEffect` with subscribe/timer/setState must return cleanup.** #1 correction category. **[PRE-FLIGHT]**
- **Unscale `getBoundingClientRect()` values when ancestor has CSS transform.**
- **Save editor selection before opening DOM-mutating modal; restore on close.**

### C. Deployment & Platform Patterns

- **Vercel serverless cannot use Node `fs`.** Use API routes with fetch, KV, or external storage.
- **Set `trust proxy` behind Vercel/Render proxy.** Without it, `req.ip` and secure cookies break.
- **Auth redirect URLs must match deployed domain, not localhost.**
- **GitHub Actions secrets have 48KB limit.** Use gzip+base64 for large auth state.
- **Playwright on cold GHA runners needs 3-4min timeout, not 30s.**
- **Vercel multi-builder projects: verify serverless entry point imports match dev server.** Middleware registered in `src/app.js` is often missing from `api/index.js`.

### D. Debug Loop Patterns

- **Never change multiple variables simultaneously when debugging.**
- **Verify file upload/storage end-to-end in ONE test:** upload, store, read back, verify content.
- **Read dependency source/docs BEFORE guessing.** iOS Shortcut plist, Vercel serverless, R2 URLs all have specs.
- **After 3+ attempts at the same integration, STOP and write what you've ruled out.**
- **Check for stale caches before complex debugging.** `rm -rf .next && npm run build` catches phantom issues.

---

## Marathon Session Detection

If >=8 runs in a day, or >=3 consecutive debug-loop runs on same task:

> code-builder: marathon detected. {N} runs today on `{task}`. Consider: (1) reading docs/source, (2) asking in a forum, (3) taking a break.

---

## Changelog

- **2026-05-24 — v5: definitive consolidation from 25 session branches**
  - Fixed: token-budget-aware draft count (N=3 for medium tasks, was always N=5)
  - Fixed: `mkdir -p` for run log directory (was missing, first run failed)
  - Fixed: worktree cleanup (`git worktree remove` after merge)
  - Added: Vercel multi-builder entry point validation in pre-flight and merge
  - Added: cross-skill conflict declaration (defers to mcp-contributor)
  - Added: content-quality cross-reference in Step 8
  - Added: branch scan in cross-session safety (prevents Groundhog Day)
  - Added: stale cache check in debug patterns
  - Added: "no orphaned analysis files" learning
  - Added: author filter and work/personal firewall for sync
  - Added: sync bounds table with explicit limits
  - Merged debug-escalation into debug loop (was separate skill, redundant)
  - Suppressible single-pass activation banner
- **2026-05-19 — v4: consolidated from 20 session branches**
- **2026-05-13 — v3: token budget, adaptive bias, cross-skill conflict**
- **2026-05-09 — v2: debug loop, pre-flight, deployment validation**
- **2026-04-13 — v1: initial backfill (12 bullets from 4 repos)**
