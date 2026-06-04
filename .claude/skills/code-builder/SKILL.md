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

2. **Is there an established library or pattern?** Search npm/PyPI/crates.io for existing solutions. If a maintained library exists, use it instead of hand-rolling.

3. **Has this been attempted before in this repo?** Check git log for prior attempts:
   ```bash
   git log --all --oneline --grep="fix\|revert" -- {files}
   ```
   If 3+ prior attempts found: **stop.** Print the failure history. Suggest either a fundamentally different approach, an external library, or scoping down the feature. Do not iterate on the same strategy.

---

## Step 1 — Pre-flight Checks

Runs in ALL modes before writing code.

### 1A. Git Repo Gate (BLOCKING)

```bash
git rev-parse --git-dir 2>/dev/null
```

If not a git repo: offer `git init`. If declined, force single-pass mode — parallel requires git worktrees. Do NOT proceed with parallel mode in a non-git directory.

### 1B. Language & Framework Detection

Detect the project's stack before assuming commands. Check in order:

| Indicator | Stack | Test cmd | Lint cmd | Type cmd |
|---|---|---|---|---|
| `package.json` + `next.config.*` | Next.js | from scripts | from scripts | `tsc --noEmit` |
| `package.json` + `vite.config.*` | Vite | from scripts | from scripts | `tsc --noEmit` |
| `package.json` (other) | Node.js | from scripts | from scripts | `tsc --noEmit` if tsconfig |
| `Cargo.toml` | Rust | `cargo test` | `cargo clippy` | `cargo check` |
| `go.mod` | Go | `go test ./...` | `go vet ./...` | — |
| `pyproject.toml` / `requirements.txt` | Python | `pytest` | `ruff check .` or `flake8` | `mypy .` if configured |
| `Gemfile` | Ruby | `bundle exec rspec` | `rubocop` | — |
| `pom.xml` / `build.gradle` | Java/Kotlin | `mvn test` / `gradle test` | — | — |

Read from `package.json` scripts when available — don't assume `npm test` exists.

### 1C. Claude Process Failures

| Check | Action |
|---|---|
| Task touches `process.env.*`? | Validate + trim at read-site. Check `NEXT_PUBLIC_` exposure — ships to browser. |
| Task adds a `useEffect`? | Must return cleanup if it subscribes, starts timer, or sets state. |
| Task uses floating UI (tooltip, dropdown, popover)? | Use `position: fixed` + portal, not `absolute` inside scroll parents. |
| Task destructures API/KV response? | Guard nullable response before destructuring. Render `<EmptyState />` or early-return. |
| Task could duplicate existing utility? | `grep -r` for similar helpers before writing new ones. |
| Task adds conditional logic around a hook? | No conditional calls, no hooks in callbacks/effects. |
| Task adds user-facing text? | Run content-quality checks. |

### 1D. Deployment & Integration

| Check | Action |
|---|---|
| Deploying to Vercel? | No `fs` in serverless. `trust proxy` if behind proxy. Invoke vercel-ship if available. |
| Custom server + Vercel? | **Diff dev entry (e.g. `server.ts`) against serverless entry (e.g. `api/index.ts`).** Middleware order, error handler placement, and body parser config must match. Silent 500s come from divergence between these two files. |
| Task changes auth/OAuth? | Verify redirect URLs for local AND production. Check cookie domain. |
| Task involves file storage? | Verify upload-store-retrieve end-to-end. Check URL format. |
| Task references external URLs? | Verify every URL exists. Never fabricate. Use `[TODO: add URL]` if unverified. |
| Monorepo or multi-directory? | Install deps in ALL entry points, not just root. |

### 1E. Cross-Session Safety

| Check | Action |
|---|---|
| Uncommitted changes? | `git stash list` + `git status`. Do NOT overwrite — ask first. |
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

## Step 3 — Judgment Gate (with task-size adaptation)

Four modes. Default is single pass.

### Quick-fix bypass

If ALL of these are true, skip directly to single-pass (Step 4b):
- <10 LOC change
- Single file
- Obvious fix (typo, missing import, off-by-one, rename)
- No design decisions

Skip the full rubric scoring for these. Just fix it.

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
- User says "this keeps breaking" or "I've tried X already"
- 3+ consecutive fix commits in same area in recent git log
- Current error matches a recently committed fix (regression)

### Single pass (default)

<30 LOC, 1 file, one obvious path, existing pattern, leaf component, known root cause.

### Hard overrides

- User explicit override → obey
- Not a git repo → force single (after offering `git init`)
- Live debugging with rapid iteration → force single
- Greenfield prototype from scratch → force parallel
- "This keeps failing" / integration failure → force debug loop

---

## Step 4a — Parallel Path

1. **Git repo gate (BLOCKING):** `git rev-parse --git-dir` must succeed. If not, abort parallel — do NOT silently fall back to single.

2. `mkdir -p ~/.claude/skills/code-builder/runs/`

3. Spawn **N `Agent` calls in parallel** (single message), each with:
   - `isolation: "worktree"`, `run_in_background: true`, `subagent_type: "general-purpose"`
   - Differentiation bias:
     - Draft 1: simplest possible — fewest lines, no abstractions
     - Draft 2: most idiomatic to this repo — match existing patterns exactly
     - Draft 3: optimize for readability — clearest naming, smallest functions
     - (N=5) Draft 4: optimize for edge cases and defensive correctness
     - (N=5) Draft 5: best instinct — free choice
   - Each prompt includes: the detected test/lint/typecheck commands from Step 1B (not hardcoded npm/pytest). "Before coding, `grep -r` for existing utilities. After coding, run [detected test cmd], [detected typecheck cmd], and [detected lint cmd]."

4. Each draft: commit on worktree branch, report approach (2 lines), files touched, LOC, SHA, edge cases.

5. **Quorum and failure handling:**
   - Wait for all N. Timeout: 5 minutes per draft.
   - If 1-2 drafts fail/timeout: continue with survivors. Score normally.
   - If 3+ drafts fail (N=5) or 2+ fail (N=3): **abort parallel.** Report which failed and why. Fall back to single-pass with the best surviving draft as starting point, or debug-loop if failures suggest an integration issue.
   - If ALL fail: do NOT retry parallel. Switch to debug-loop mode. The task likely has an environmental or integration issue that parallel drafts won't solve.

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

Run the same diagnostic from Step 4. Check for side effects. Run detected test commands.

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
| Tests pass (using detected test cmd) | 15 (0 if any fail; redistribute to Correctness if no tests) |
| Typecheck clean (using detected type cmd) | 10 |
| Lint clean (using detected lint cmd) | 5 |
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
2. **Cherry-pick rollback:** If cherry-pick conflicts or breaks tests, abort the cherry-pick (`git cherry-pick --abort`) and note what couldn't be recovered. Do not force.
3. **Redundancy check:** Strip unused imports, dead code, debug logs, duplicated helpers.
4. **Rerun validation:** Detected test + typecheck + lint on merged diff.
5. **Deployment check:** No `fs` in serverless, env vars trimmed, auth redirects use production domain. If Vercel multi-builder, verify BOTH entry points.
6. **Content check:** If diff includes user-facing text, invoke content-quality skill.
7. **Data check:** Verify all external URLs/endpoints exist.
8. **Merge** winner's branch. Clean up: `git worktree list` then `git worktree remove`.
9. **Report:** `Merged draft {N}/{total} (score {X}/100). {reason.} Tests / Types / Lint.`

---

## Step 7 — Log the Run

Determine log location based on environment:
- **Laptop/persistent:** `~/.claude/skills/code-builder/runs/`
- **Web session (ephemeral container):** `.claude/runs/` in the current repo (survives via git push)

```bash
if [ -d "$HOME/.claude/skills/code-builder" ]; then
  LOG_DIR="$HOME/.claude/skills/code-builder/runs"
else
  LOG_DIR=".claude/runs"
fi
mkdir -p "$LOG_DIR"
```

Log entry (append to `{LOG_DIR}/{date}.jsonl`):

```json
{
  "date": "YYYY-MM-DD",
  "mode": "parallel|single|debug|visual",
  "task": "one-line summary",
  "drafts": 5,
  "winner": 2,
  "winner_bias": "idiomatic",
  "scores": [72, 89, 85, 78, 81],
  "cherry_picked": [4],
  "lang": "typescript",
  "framework": "nextjs",
  "repo": "repo-name",
  "loc_changed": 47,
  "files_changed": 3
}
```

---

## Current Learnings

Last synced: 2026-05-29 (manual consolidation from 28 session branches — automated sync has NEVER executed)

**WARNING:** The weekly sync (Sunday 6pm) is this skill's core differentiator but no cron/GH Action has ever been set up. These learnings are static since the initial backfill. Set up the sync runner before trusting these as current.

### Process

- **Trim all `process.env` at the read-site.** 4 separate fixes across schlacter.me; also hit in muse OAuth. Pattern: `process.env.X?.trim()`. (5 citations)
- **Verify BOTH dev server AND serverless entry middleware order.** Silent 500s when error handler is before routes in one but not the other. (1 citation: muse `d01750d`)
- **Set `trust proxy` behind any reverse proxy.** Broke OAuth in muse, session validation in calmar. (2 citations: muse `0c92c13`, `3a83f67`)
- **Don't iterate on the same strategy 3+ times.** If it didn't work twice, the approach is wrong, not the execution. (build-log: 13 iOS Shortcut versions, Playwright timeout escalation)
- **Guard nullable API responses before destructuring.** KV/API calls return null on miss. (2 citations)
- **Check for existing utilities before writing new ones.** Duplicated helpers across 3 repos. (3 citations)

### Integration

- **Offload Playwright/puppeteer to GHA instead of serverless.** Cold starts on Vercel/Render exceed 30s. (1 citation: libby-hold-monitor architecture pivot)
- **Register both www and non-www OAuth redirect URIs.** Google treats them as different. (1 citation: muse `68d29d4`)
- **Handle OAuth-only accounts in password login flow.** `bcrypt.compare(input, null)` crashes. (1 citation: muse `3a83f67`)

### Merge Safety

- **Never force-push without checking other sessions' branches.** 3 incidents of code loss from merge conflicts in calmar. (3 citations)
- **Check `git branch -a --sort=-committerdate` before starting.** Build on existing branch work, don't start over. (28 orphaned branches as evidence)

---

## Changelog

- **2026-06-04 — v7.1: Web-session run logging, sync staleness warning, dual-entry-point check**
  - FIXED: Run log path adapts to web (ephemeral) vs laptop (persistent) environments
  - FIXED: Sync staleness warning now explicitly states the automated sync has never run
  - ADDED: Explicit dual-entry-point diff check for custom server + Vercel deployments
- **2026-05-29 — v7: Critical gap fixes (git gate, quorum, language detection, task-size adaptation)**
  - FIXED: Git repo check is now a BLOCKING gate for parallel mode (was a suggestion)
  - FIXED: Added quorum/failure handling — 3+ draft failures abort parallel, switch to debug-loop
  - FIXED: Language/framework detection replaces hardcoded npm/pytest assumptions
  - FIXED: Quick-fix bypass skips full rubric for <10 LOC obvious fixes
  - FIXED: Cherry-pick has rollback strategy (`git cherry-pick --abort`)
  - FIXED: Parallel draft prompts use detected commands, not assumed ones
  - FIXED: Added timeout (5 min/draft) for parallel mode
  - Consolidated from v6 (YapzR) + audit findings (358hG)
- **2026-05-27 — v6: Four execution modes, visual path, pre-flight research gate**
- **2026-05-24 — v4: Consolidated from 25 session branches**
- **2026-04-14 — v1: Initial version**
