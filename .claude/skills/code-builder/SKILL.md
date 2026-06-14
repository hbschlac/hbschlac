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

### Skill precedence (when multiple skills trigger)

code-builder is the execution engine. Domain skills provide context. They co-activate, not compete:

| Task type | Active skills | Who does what |
|---|---|---|
| Portfolio feature | code-builder + portfolio-dev | portfolio-dev: conventions, data model. code-builder: mode selection, execution. |
| Deploy failure | vercel-ship (primary) | vercel-ship owns debugging. code-builder activates only if the fix requires code changes. |
| CSS/styling | code-builder (visual mode) + portfolio-dev | code-builder runs 3 visual drafts. portfolio-dev constrains the design system. |
| User-facing text in code | code-builder + content-quality | code-builder runs Step 6 content check. content-quality validates the text. |
| Production incident | debug-escalation (primary) | debug-escalation owns triage. code-builder's debug loop activates only for the fix itself. |
| Cross-repo coordination | session-safety (primary) | session-safety owns the workflow. code-builder handles per-repo code changes. |

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
| `.github/workflows/*.yml` | GH Actions | per workflow | per workflow | — |
| `supabase/` dir + `package.json` | Next.js + Supabase | from scripts | from scripts | `tsc --noEmit` |

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
| Task outputs files for external systems? | Validate format compliance before the point of no return. Check: file structure, required metadata, size plausibility. See LEARNINGS.md "File Format Compliance." |
| Task builds a multi-step pipeline? | Map all steps, add validation between them. See LEARNINGS.md "Pipeline Hardening." |

### 1C-2. Claude Code Environment (web sessions)

| Check | Action |
|---|---|
| Running in ephemeral container? | No persistent filesystem between sessions. Anything worth keeping must be committed and pushed. |
| Need to search/fetch external info? | Use subagents (`Agent` tool with `subagent_type: "Explore"`) for broad searches. Use `WebFetch`/`WebSearch` for specific URLs. Don't shell out to `curl` for APIs when MCP tools exist. |
| Using MCP tools (GitHub, Vercel, etc.)? | MCP tools can timeout or fail silently. Always verify the result — don't assume success. If a tool returns an error, retry once, then fall back to an alternative approach or flag the user. |
| Need to work across repos? | Check `mcp__claude-code-remote__list_repos` first. If the repo is available, use `add_repo`. If not, write laptop instructions in CLAUDE.md. Don't silently skip cross-repo work. |
| Spawning subagents for parallel work? | Use `Agent` tool with `run_in_background: true` for independent tasks. For research: specify "report in under 200 words" to keep context lean. For code changes: use `isolation: "worktree"`. Never spawn more than 3 subagents for one task. |
| Session nearing context limits? | Conversation gets auto-compressed. Keep skill activations minimal after the first 3 — suppress announcements. Prefer direct tool calls over subagent delegation for simple tasks. |

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

**Status: UNTESTED in production.** As of 2026-06-11, no run log exists for parallel mode. The first real parallel run should: (1) use N=3 (not N=5), (2) log the full score breakdown, (3) commit the run log, (4) note whether worktrees worked in the environment (web session vs. laptop). If worktrees fail in a web session sandbox, fall back to single-pass — don't debug the environment.

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

## Rapid Shipping Mode

When building 5+ features in a single session (e.g., kindle-schlacter-me shipped 20 PRs in 2 sessions), normal single-pass mode is correct but needs scoping discipline.

### Activation

- User provides a feature list, PRD, or backlog with 5+ items
- Multiple related features share a codebase and deploy target
- Features can be shipped incrementally (each PR is independently deployable)

### Sequencing rules

1. **Build the core path first.** The feature that everything else depends on ships first. Don't build the error UI before the happy path works.
2. **Validation before polish.** PR order: core feature → input validation → error handling → edge cases → UX polish → escape hatches. kindle-schlacter-me: send (PR#1) → EPUB validation (PR#7) → failure visibility (PR#13) → fake detection (PR#17) → stuck status fix (PR#18).
3. **Group by pipeline stage, not by feature type.** Don't do "all search features, then all send features." Do "search happy path + send happy path, then search edge cases + send edge cases."
4. **Ship after each PR, not after the batch.** Each PR should be deployed and smoke-tested before starting the next. This surfaces real-world failures that inform the next PR.

### Scope management (when to stop iterating)

Rapid iteration on a pipeline (search → download → validate → send) generates a growing backlog of discovered issues. Without boundaries, this becomes unbounded:

| Signal | Action |
|---|---|
| New issue is in the same pipeline step you just fixed | You're churning. Escalate to debug-escalation. |
| New issue is a different failure mode you haven't seen | Healthy iteration. Keep going. |
| You've shipped 10+ PRs and the core path works reliably | Declare the pipeline "hardened." Remaining issues go to a backlog, not the current session. |
| Edge case affects <5% of users | Add it to the backlog. Don't optimize for rare cases during initial shipping. |
| You're adding UX polish to a feature that has unhandled errors | Stop polishing. Fix the errors first. |

### Anti-pattern: the 15-PR pipeline

kindle-schlacter-me PRs #6-20 hardened the download→validate→send pipeline over 15 iterations. A pipeline audit (see debug-escalation's pipeline hardening) at PR #6 would have identified format compliance (#7), content integrity (#17), delivery confirmation (#18), and fallback sources (#11) in 3-4 comprehensive PRs instead of 15 reactive ones.

**Rule:** After 5 PRs targeting the same pipeline, STOP. Run debug-escalation's pipeline hardening audit (map all steps, audit each for failure modes, prioritize by blast radius). Then batch the remaining fixes into 2-3 comprehensive PRs.

---

## Learnings Reference

Patterns from real projects are in `LEARNINGS.md` (same directory). Read it when you need reference patterns for a specific domain (Supabase, API resilience, testing, CI, performance, etc.).

Last synced: 2026-06-13. GH Action deployed at `.github/workflows/code-builder-sync.yml`.

---

## Changelog

- **2026-06-14 — v8.4: Rapid shipping mode, scope management**
  - ADDED: Rapid shipping mode — sequencing rules for 5+ feature batches (core path first, validation before polish, group by pipeline stage, ship after each PR)
  - ADDED: Scope management table — when to keep iterating vs. stop and backlog remaining issues
  - ADDED: Anti-pattern "the 15-PR pipeline" — after 5 PRs targeting the same pipeline, stop and audit
  - Evidence: kindle-schlacter-me shipped 20 PRs in 2 sessions. PRs #6-20 all targeted the same download→validate→send pipeline. A pipeline audit at PR #6 would have compressed 15 reactive PRs into 3-4 comprehensive ones.
- **2026-06-13 — v8.3: Pipeline hardening, format compliance, mobile/PWA pre-flight checks**
  - ADDED: Pre-flight checks for file format compliance (validate before point of no return) and multi-step pipeline hardening
  - ADDED: 6 new LEARNINGS.md sections — PWA/mobile web (iOS Safari, safe-area, lost responses), search engineering (query parsing, multi-source ranking), file format compliance (EPUB validation, stub detection), client-server state sync (polling, durable status, reconciliation), feature gating (gate risky features OFF), pipeline hardening (audit-all-steps pattern)
  - Evidence: kindle-schlacter-me PRs #4-20 — 15 PRs hardening the download→validate→send pipeline; iOS Safari UX issues; "Sending" stuck state; search recall failures. These patterns were completely uncovered.
- **2026-06-12 — v8.2: Claude Code web session patterns**
  - ADDED: Pre-flight check 1C-2 — Claude Code environment (ephemeral containers, MCP tool failures, subagent patterns, cross-repo access, context limits)
  - ADDED: Test framework setup section in LEARNINGS.md (Jest, Vitest, pytest initial config)
  - Evidence: every web session faces these constraints but no skill addressed them; projects starting tests from zero had no setup guidance
- **2026-06-11 — v8.1: Skill precedence table, parallel mode untested flag**
  - ADDED: Skill precedence table — defines which skill leads when multiple trigger simultaneously
  - ADDED: Parallel mode untested warning with first-run guidance (N=3, log everything, test worktrees)
  - Evidence: 4+ skills can trigger on a single task (portfolio + vercel + visual + content-quality) with no routing; parallel mode has zero production run logs after 7 versions
- **2026-06-10 — v8: Extract learnings, deploy GH Action, add large-codebase patterns**
  - MOVED: 15 learnings subsections (~280 lines) to `LEARNINGS.md` — keeps workflow crisp, reference accessible
  - ADDED: "Working on Large Existing Codebases" section in LEARNINGS.md (read-before-change, smallest fix, incremental CI, tech debt triage)
  - DEPLOYED: `.github/workflows/code-builder-sync.yml` — resolves known issue #1 (learning sync never ran, 65+ days)
  - FIXED: Sync staleness warning replaced with pointer to LEARNINGS.md + deployed GH Action
  - Skill file reduced from 581 → ~380 lines. No workflow steps changed.
- **2026-06-09 — v7.5: Performance optimization, async workflows, feature batching, stacked PR unblocking**
  - ADDED: Performance optimization learnings (profile before parallelize, per-source timeout budgets, benchmark before/after, sequential→parallel)
  - ADDED: Async multi-step workflow learnings (explicit state machines, event-time ordering, idempotent handlers, separate trigger from work)
  - ADDED: Feature batching learnings (deployable rounds, preview-first, list features in PR body)
  - ADDED: Stacked PR unblocking guidance (merge #1 immediately, retarget, don't let stacks rot)
  - Evidence: kindle-connector PR#1 (30s→3s parallel fan-out), kindle-schlacter-me PR#1 (R0-R10 feature rounds, send stage state machine, Resend webhooks), recs.community PRs #1-7 (stacked but unmerged for 13+ days)
- **2026-06-08 — v7.4: Testing strategy, CI/GH Actions, PRD-to-code learnings**
  - ADDED: Testing strategy section (what to test, test-with-bugfix, no-test-for-glue, gradual CI adoption)
  - ADDED: CI / GitHub Actions section (PR gate template, separate CI from features)
  - ADDED: PRD-to-code section (stacked PRs from PRD, vertical slicing, schema-first, out-of-scope lists)
  - Evidence: kindle-schlacter-me 71 tests + resilientDownload.test.ts, muse-shopping PR#1 CI gate, recs.community 7 PRs from PRD
  - Resolves CLAUDE.md known issues #4 (PM/PRD workflow) and #8 (testing strategy)
- **2026-06-06 — v7.3: Supabase, API resilience, KV/caching, multi-developer learnings**
  - ADDED: Supabase to framework detection table
  - ADDED: Supabase learnings section (RLS, migrations, security-definer, auth middleware, triggers)
  - ADDED: API resilience learnings (cross-source fallback, dead-resource fast-fail, parallel fan-out, quota-after-success)
  - ADDED: KV/caching learnings (key design, event-time monotonic guards, shared cache)
  - ADDED: Multi-developer learnings (PR stacking, COORDINATION.md, review checklists, self-onboarding)
  - Evidence: 14 PRs across kindle-schlacter-me, kindle-connector, recs.community, muse-shopping (May-Jun 2026)
- **2026-06-05 — v7.2: Python patterns, automation/scheduling learnings, GH Action template for sync**
  - ADDED: Python-specific learnings section (venv, pathlib, entry points, dep pinning)
  - ADDED: Automation/scheduling learnings (cron UTC, workflow_dispatch, timeouts)
  - ADDED: Concrete GH Action YAML template to unblock the learning sync (known issue #1)
  - ADDED: GH Actions to language/framework detection table
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
