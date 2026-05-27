---
name: code-builder
description: >
  Improves code quality through four execution modes: single pass (fast, obvious),
  parallel (N isolated drafts scored on rubric, winner merged), debug loop
  (hypothesis-test-learn for integration failures), and visual (3 drafts for
  CSS/styling). Self-improving via learning sync.
---

# code-builder

## Activation

Auto-triggers on coding tasks. Explicit: `/code-builder`, "build this," "fix this bug."
Implicit: working in a git repo while describing a coding task, sharing error messages.

Do NOT activate for: pure code reading, research, writing prose, design, planning, meta-tasks.

Default: when uncertain, activate. Single-pass costs nothing; missing a dev task is worse.

**Conflict:** If `mcp-contributor` is active (guiding a PR to the MCP org), code-builder defers. code-builder handles only code tasks mcp-contributor doesn't claim.

## Announcement

> **code-builder activated** — [parallel, N drafts | single pass | debug loop | visual, 3 drafts]. [reason.]

Suppress after 3rd consecutive single-pass in the same session.

---

## Step 0 — Pre-flight Research Gate

Before writing any code, answer three questions silently:

1. **Is the domain well-understood?** Standard web dev, API integration, DB queries → yes. Binary formats (plists, Shortcuts, protocol buffers), undocumented vendor APIs, hardware protocols → no. If no: tell the user before coding. Propose a spike: a throwaway prototype that validates the approach in <30 minutes. Don't commit spike output.

2. **Is there an established library or pattern?** Search npm/PyPI for existing solutions. If a maintained library exists, use it instead of hand-rolling.

3. **Has this been attempted before in this repo?** Check git log for prior attempts:
   ```bash
   git log --all --oneline --grep="fix\|revert" -- {files}
   ```
   If 3+ prior attempts found: **stop.** Print the failure history. Suggest either a fundamentally different approach, an external library, or scoping down the feature. Do not iterate on the same strategy.

---

## Step 1 — Pre-flight Checks

Runs in ALL modes before writing code.

### 1A. Claude Process Failures

| Check | Action |
|---|---|
| Task touches `process.env.*`? | Validate + trim at read-site. Check `NEXT_PUBLIC_` exposure — ships to browser. |
| Task adds a `useEffect`? | Must return cleanup if it subscribes, starts timer, or sets state. |
| Task uses floating UI (tooltip, dropdown, popover)? | Use `position: fixed` + portal, not `absolute` inside scroll parents. |
| Task destructures API/KV response? | Guard nullable response before destructuring. Render `<EmptyState />` or early-return. |
| Task could duplicate existing utility? | `grep -r` for similar helpers before writing new ones. |
| Task adds conditional logic around a hook? | No conditional calls, no hooks in callbacks/effects. |
| Task adds user-facing text? | Run content-quality checks. |

### 1B. Deployment & Integration

| Check | Action |
|---|---|
| Deploying to Vercel? | No `fs` in serverless. `trust proxy` if behind proxy. Verify BOTH dev entry (`src/app.js`) AND serverless entry (`api/index.js`). |
| Task changes auth/OAuth? | Verify redirect URLs for local AND production. Check cookie domain. |
| Task involves file storage? | Verify upload-store-retrieve end-to-end. Check URL format. |
| Task references external URLs? | Verify every URL exists. Never fabricate. Use `[TODO: add URL]` if unverified. |
| Monorepo or multi-directory? | Install deps in ALL entry points, not just root. |

### 1C. Cross-Session Safety

| Check | Action |
|---|---|
| Uncommitted changes? | `git stash list` + `git status`. Do NOT overwrite — ask Hannah. |
| Files modified in last 2 hours by different commit? | Flag potential conflict. |
| Components imported by 3+ files? | Extra caution on deletion — verify all import sites. |
| Similar work on other branches? | `git branch -a --sort=-committerdate | head -20`. Build on existing work. |

Output: one-line summary of checks that fired, or "Pre-flight clean."

---

## Step 2 — Scope the Task

State the task in one line. Identify:
- Files likely to change
- Greenfield (new) or modification (fix/tweak)
- Design space: multiple valid approaches or one obvious path?
- Integration surface: external services, APIs, device-specific behavior?
- Estimated complexity: small (<30 LOC), medium (30-150 LOC), large (>150 LOC)
- Visual: is this primarily CSS/styling/layout?

---

## Step 3 — Judgment Gate

Four modes. Default is single pass.

### Parallel threshold (N=3 or N=5)

Escalate when >=2 soft signals fire OR any hard signal fires:

Soft signals: >30 LOC, >1 file, multiple valid architectures, new pattern to repo, touches critical path, feature/refactor/greenfield, open-ended phrasing.

**Draft count:**
- Large (>150 LOC, >3 files) → N=5
- Medium (30-150 LOC) → N=3
- Near rate limits or long session → N=3 regardless

### Visual mode threshold (N=3)

Escalate when the task is primarily CSS, styling, or layout:
- Adding/redesigning a visual component (card, hero, navigation, gallery)
- Color scheme, spacing, typography, or animation changes
- Responsive layout or mobile-specific styling
- ">60% of the change is CSS/Tailwind/styled-components"

### Debug loop threshold

Escalate when ANY fire:
- Attempt >=2 at the same task (prior failed/reverted)
- Error involves external integration (API, OAuth, device-specific)
- Reproduces in production but not locally (or vice versa)
- Hannah says "this keeps breaking" or "I've tried X already"
- 3+ consecutive fix commits in same area in recent git log
- Current error matches a recently committed fix (regression)

### Single pass (default)

<30 LOC, 1 file, one obvious path, existing pattern, leaf component, known root cause.

### Hard overrides

- Hannah explicit override → obey
- Not a git repo → offer `git init`; if declined, force single
- Live debugging with rapid iteration → force single
- Greenfield prototype from scratch → force parallel
- "This keeps failing" / integration failure → force debug loop

---

## Step 4a — Parallel Path

1. Verify git repo: `git rev-parse --git-dir`. If not, offer `git init`.

2. `mkdir -p ~/.claude/skills/code-builder/runs/`

3. Spawn **N `Agent` calls in parallel** (single message), each with:
   - `isolation: "worktree"`, `run_in_background: true`, `subagent_type: "general-purpose"`
   - Differentiation bias:
     - Draft 1: simplest possible — fewest lines, no abstractions
     - Draft 2: most idiomatic to this repo — match existing patterns exactly
     - Draft 3: optimize for readability — clearest naming, smallest functions
     - (N=5) Draft 4: optimize for edge cases and defensive correctness
     - (N=5) Draft 5: best instinct — free choice
   - Adaptive bias: if win-rate history exists in run logs, weight toward historically winning biases.
   - Each prompt includes: "Before coding, `grep -r` for existing utilities. After coding, run tests, `tsc --noEmit`, and lint."

4. Each draft: commit on worktree branch, report approach (2 lines), files touched, LOC, SHA, edge cases.

5. Wait for all N. Continue with survivors if any fail/timeout.

## Step 4b — Single Path

Execute normally. Skip to Step 7.

## Step 4c — Debug Loop

### Pre-Step 0: Failed Approach Scan (mandatory)

```bash
git log --all --oneline -20 -- {file}
git log --all --oneline --grep="fix" -- {file}
```

List prior attempts. These approaches are OFF LIMITS.

### Step 1: State the failure

> What happens: [exact error/behavior]
> What should happen: [expected behavior]
> Environment: [local/Vercel/GHA/device]

### Step 2: Read before writing

Do NOT write any code yet. Instead:
1. Read the full function, its callers, and dependencies — not just the error line.
2. Read the last 3-5 diffs touching this area: `git log -p -5 -- {file}`
3. Read error messages, stack traces, browser console output.
4. Check if the bug is environment-specific.

### Step 3: Hypothesize

Single-sentence hypothesis about ROOT CAUSE (not symptom):

```
debug-loop: hypothesis — {one sentence}
```

Root cause vs symptom:
- Symptom: "popup doesn't close" / Root: "window.close() blocked because reload() cleared opener reference"
- Symptom: "API returns 500" / Root: "trust proxy not set, rate limiter reads 127.0.0.1"

### Step 4: Prove it

Write a minimal diagnostic (NOT the fix):
- Single console.log at suspected root cause
- Failing test that reproduces the bug
- curl command demonstrating API behavior

### Step 5: Fix (only after proof)

Target the proven root cause. The fix must:
- Address root cause, not paper over symptom
- Not revert to an approach that already failed
- Include a guard or test preventing regression

### Step 6: Verify

Run the same diagnostic from Step 4. Check for side effects. Run tests.

### Debug Loop Limits

- **5 hypothesis cycles max.** After 5, report what you've ruled out and what data would narrow it down.
- **Never change multiple variables simultaneously.**
- **Never repeat a failed approach.**
- **After 3+ attempts at the same integration, STOP and write what you've ruled out.**

## Step 4d — Visual Path (3 drafts)

For CSS/styling/layout tasks. Uses 3 drafts with visual-specific biases:

1. Spawn **3 `Agent` calls in parallel**, each with `isolation: "worktree"`:
   - Draft 1: minimal CSS — fewest properties, simplest selectors
   - Draft 2: match the repo's existing design language exactly
   - Draft 3: mobile-first, best accessibility

2. Score using the visual rubric variant (Step 5, visual criteria).

---

## Step 5 — Self-Evaluate and Pick Winner (Parallel/Visual Only)

### Standard rubric (100 points)

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

### Visual rubric variant (replaces Tests/Typecheck/Lint with visual criteria)

| Criterion | Weight |
|---|---|
| Correctness (matches design intent) | 20 |
| Mobile responsiveness | 15 |
| Visual consistency with existing design | 15 |
| Accessibility (contrast, focus states, screen reader) | 10 |
| Minimal diff | 10 |
| No unnecessary deps | 10 |
| Follows repo's CSS conventions (Tailwind/modules/styled) | 10 |
| Animation/transition smoothness | 5 |
| Scope containment | 5 |

Record full score breakdown in run log.

---

## Step 6 — Merge Validation

1. **Gap check:** Re-read original task. Cherry-pick from rejected drafts if a gap exists.
2. **Redundancy check:** Strip unused imports, dead code, debug logs, duplicated helpers.
3. **Rerun validation:** Tests + typecheck + lint on merged diff.
4. **Deployment check:** No `fs` in serverless, env vars trimmed, auth redirects use production domain. If Vercel multi-builder, verify BOTH entry points.
5. **Content check:** If diff includes user-facing text, invoke content-quality skill.
6. **Data check:** Verify all external URLs/endpoints exist.
7. **Merge** winner's branch. Clean up: `git worktree list` then `git worktree remove`.
8. **Report:** `Merged draft {N}/{total} (score {X}/100). {reason.} Tests / Types / Lint.`

---

## Step 7 — Log the Run

```bash
mkdir -p ~/.claude/skills/code-builder/runs/
```

Write to `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`:

```md
---
date: YYYY-MM-DD
task_slug: dark-mode-toggle
repo: interior-designer-portfolio
mode: parallel | single | debug-loop | visual
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

Triggers when diff contains user-facing text. Defers to content-quality skill if loaded.

| Pattern | Replace with |
|---|---|
| "I'd be happy to..." | Direct action or remove |
| "Streamline" / "leverage" / "utilize" | "simplify" / "use" / "use" |
| "Cutting-edge" / "robust" / "comprehensive" | Remove or use specific descriptor |
| "Seamless" / "elevate" / "empower" | Remove or use plain language |
| "Delve" / "holistic" / "paradigm shift" | Remove |

Hannah's voice: direct, slightly informal, no corporate buzzwords.

---

## Learning Sync

Triggered Sunday 6pm or on-demand via "code-builder sync."

**Staleness detection:** If `Last synced:` is >14 days old, print on EVERY activation:
> code-builder: learnings are {N} days stale. Run `code-builder sync`.

### Sync workflow

1. Read `Last synced:` date. Process only runs after that date.
2. Collect from: run logs, post-merge git diffs (what Hannah corrected after skill output), in-session feedback, mode overrides, pre-flight check frequency, cross-repo mining (`--max-count=50` per repo, `--grep="fix|revert|oops|simplify|restore|debug"`).
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
| Session summaries | Backfill only | Not recurring |

### Author filter

Only mine commits from Hannah, `claude[bot]`, or Claude's local commit identity.

### Work/personal firewall

No Walmart or internal content enters learnings. Allowed repos:
`hbschlac/hbschlac`, `hannah-portfolio`, `libby-hold-monitor`, `muse-shopping`,
`claude-code-insights-dashboard`, `claude-config`.

---

## Current Learnings

**Last synced:** 2026-05-27 (consolidated from 28 session branches)

*If a repo's CLAUDE.md contradicts a rule below, the repo rule wins.*

### A. Claude Process Failures

- **Never call `Skill()` from inside a scheduled-task body.** Circular dispatch re-triggers on each tick. Does not apply to on-demand skills from a user turn.
- **No hardcoded tokens or secrets in client JS.** `"use client"` modules or `NEXT_PUBLIC_` prefix ships to browser. Cost: credential rotation.
- **"Done" requires green tests + typecheck, not "looks right."** Declare completion only after running the repo's actual test/lint commands.
- **Resolve merge conflicts by re-running tests, not eyeballing.** Code was silently lost 3x across repos.
- **Guard nullable KV/API responses before destructuring.** Render `<EmptyState />` or early-return. Cross-repo x3. **[PRE-FLIGHT]**
- **Grep for existing helpers before writing new ones.** Duplicated utilities drift. **[PRE-FLIGHT]**
- **Don't create orphaned analysis files.** Put findings in CLAUDE.md or skill files. Orphaned docs die on branches.
- **Don't rewrite skills from scratch.** Edit the existing version. 15 independent rewrites of code-builder proved that restarts lose accumulated improvements.

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
- **Vercel multi-builder projects: verify serverless entry point imports match dev server.** Middleware in `src/app.js` is often missing from `api/index.js`.

### D. Debug Loop Patterns

- **Never change multiple variables simultaneously when debugging.**
- **Verify file upload/storage end-to-end in ONE test:** upload, store, read back, verify content.
- **Read dependency source/docs BEFORE guessing.** iOS Shortcut plist, Vercel serverless, R2 URLs all have specs.
- **After 3+ attempts at the same integration, STOP and write what you've ruled out.**
- **Check for stale caches before complex debugging.** `rm -rf .next && npm run build` catches phantom issues.

### E. Visual/CSS Patterns

- **Test responsive layout at 3 breakpoints minimum:** mobile (375px), tablet (768px), desktop (1280px).
- **Use CSS custom properties for colors/spacing referenced in 3+ places.** Avoids drift when the design system changes.
- **Prefer `gap` over margin for component spacing in flex/grid layouts.**
- **Animation: prefer `transform` and `opacity` for GPU-accelerated transitions.** Avoid animating `width`, `height`, `top`, `left`.

---

## Marathon Session Detection

If >=8 runs in a day, or >=3 consecutive debug-loop runs on same task:

> code-builder: marathon detected. {N} runs today on `{task}`. Consider: (1) reading docs/source, (2) asking in a forum, (3) taking a break.

---

## Changelog

- **2026-05-27 — v6: targeted improvements from 28-session retrospective**
  - Added: Step 0 Pre-flight Research Gate (domain familiarity, prior attempt scan, library check) — from TAysv
  - Added: Visual mode (Step 4d) with 3 drafts for CSS/styling tasks + visual rubric variant — from jO2Pd
  - Added: Section E visual/CSS learnings
  - Added: "don't rewrite skills from scratch" learning (from the Groundhog Day retrospective)
  - Added: prior-attempt-scan (`git log --all --grep="fix"`) as mandatory debug loop pre-step
  - Fixed: pre-flight research gate runs BEFORE pre-flight checks (domain understanding first)
  - Kept: all v5 improvements (token budget, worktree cleanup, staleness detection, conflict declaration, etc.)
- **2026-05-24 — v5: consolidated from 25 session branches**
- **2026-05-19 — v4: consolidated from 20 session branches**
- **2026-05-13 — v3: token budget, adaptive bias, cross-skill conflict**
- **2026-05-09 — v2: debug loop, pre-flight, deployment validation**
- **2026-04-13 — v1: initial backfill (12 bullets from 4 repos)**
