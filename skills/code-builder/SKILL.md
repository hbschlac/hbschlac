---
name: code-builder
description: >
  Raises the floor of code quality by generating 5 parallel implementations
  of the same dev task, self-scoring them against a measurable rubric, and
  merging the winner. Auto-activates whenever Hannah is writing, changing,
  or fixing code — building a prototype, fixing a bug, adding or changing
  a feature. Claude exercises judgment to decide parallel vs single pass;
  not every task warrants 5 drafts. Infrastructure tasks (migrations,
  deployment, auth flows, CI/CD) route through a dedicated pre-flight
  checklist instead of parallel drafts. Announces activation on every run
  so Hannah knows the skill is active. The trigger lists below are
  illustrative, not exhaustive — use judgment to recognize dev work from
  context.
---

# code-builder

Raises the floor of Claude's dev output by running **5 parallel implementations**, **self-scoring them against a measurable rubric**, and merging the winner. The bet: if Claude lands good code ~80% of the time, single-pass output is suboptimal 1-in-5 tasks. Five parallel drafts + objective scoring pushes the floor much higher.

**Infrastructure tasks** (migrations, deployment config, auth flows, cron jobs, CI/CD) never go parallel — they're too stateful. These route through a pre-flight checklist instead.

**Claude picks the winner, not Hannah.** The whole point is to save Hannah from reviewing 5 diffs.

---

## When this skill activates

**Any time Hannah is writing, changing, or fixing code, activate.** The lists below are *examples*, not a complete enumeration — use judgment.

**Explicit triggers (examples):**
- `/code-builder` slash command
- "build this / code this / implement X / create a [component|feature|page]"
- "fix this bug / debug / something broke / this isn't working / X just crashed / there's a bug"
- "add a feature to... / change how X works / refactor X"
- "write me a [function|class|module]"
- "make a prototype for X"
- "migrate X to Y" / "set up CI for..." / "fix the deployment" / "auth is broken"
- "5x this" / "parallel this" — force parallel
- "just fix it" / "quick fix" — force single

**Implicit triggers (examples):**
- Working dir is a git repo AND Hannah describes a coding task
- Hannah shares an error, stack trace, or failing log
- Hannah pastes code and asks about/for a change
- Hannah is in a known project repo and asks for a change
- Hannah says "something broke" / "this page is broken" / "the test is failing"
- Hannah says "I'm starting a new [prototype|app|project]"
- Hannah is working on deployment config, environment variables, CI/CD pipelines, or scheduled jobs

**Do NOT activate:**
- Pure research or code reading ("how does X work?", "walk me through this")
- Writing, design, planning, brainstorming, outreach
- Meta tasks ("what are my TODOs?", "summarize this session")

**When uncertain, default to activating.** A single-pass run costs almost nothing; mis-skipping a real dev task is worse.

---

## Announcement (required, every activation)

Before doing anything else, print exactly this one-line banner:

> 🔧 **code-builder activated** — [parallel, 5 drafts | single pass | infra mode]. [≤15-word reason.]

Examples:
- `🔧 code-builder activated — parallel, 5 drafts. New feature; multiple architectures viable.`
- `🔧 code-builder activated — single pass. One-line fix; parallel would be noise.`
- `🔧 code-builder activated — single pass. Not a git repo; worktree isolation unavailable.`
- `🔧 code-builder activated — infra mode. Storage migration; pre-flight checklist required.`

Hannah can override with "actually, 5x this" or "actually, just fix it" → flip and re-announce.

---

## Workflow

### Step 1 — (No read step)

Learnings are embedded in the `## Current learnings` section at the bottom of this file and already loaded with the skill description. **Do not read a separate learnings file.** Proceed straight to Step 2.

### Step 2 — Scope the task

State the task in one line. Identify:
- Files likely to change
- Greenfield (new feature/prototype) vs. modification (bug fix, tweak) vs. infrastructure (migration, deployment, auth, cron)
- Design space — multiple valid approaches, or basically fixed?
- Blast radius — what breaks if this change is wrong? Is it reversible?

### Step 3 — Judgment gate

**Three routing paths:** parallel (5 drafts), single (just do it), or infra (pre-flight checklist).

#### 3a. Infrastructure detection (check first)

If the task matches **any** of these, route to **infra mode** (Step 4c):
- Data migration (storage provider swap, schema change, bulk data move)
- Deployment/hosting configuration (Vercel, Render, GHA, DNS)
- Auth flow changes (OAuth, session management, secrets rotation)
- Scheduled job setup or debugging (cron, webhooks, cold-start issues)
- Environment variable changes across multiple deployment targets
- CI/CD pipeline changes

**Hard override:** Hannah says "5x this" on an infra task → obey (parallel), but warn about statefulness.

#### 3b. Parallel vs. single (for non-infra tasks)

**Default is single.** Escalate to parallel only when **≥2 parallel signals fire** OR **any hard signal fires.**

| Gate | Parallel threshold | Single threshold |
|---|---|---|
| **LOC estimate** | >30 lines changed | <10 lines |
| **Files touched** | >1 file OR creates a new file | Exactly 1 existing file |
| **Design space** | Multiple valid architectures | One obviously correct path |
| **Novelty** | New pattern in this repo | Variation of existing pattern |
| **Risk** | Touches critical path (auth, checkout, data layer) | Contained to a leaf component |
| **Task type** | Feature / refactor / greenfield | Targeted bug fix with known root cause |
| **Phrasing** | Open-ended ("build X", "make Y better") | Specific ("change line 42 to...") |

**Hard signals (any one decides):**
- Hannah explicit override → obey
- Not a git repo → force **single** (worktrees require git)
- Live debugging with rapid iteration needed → force **single** (parallel too slow)
- Greenfield prototype from scratch → force **parallel**

**Worked examples:**
- "Add dark mode to the journal editor" → **parallel** (new feature, multi-file, multiple design choices)
- "Fix typo in the header" → **single** (1 LOC, 1 file)
- "Refactor share dropdown for per-person edit access" → **parallel** (>30 LOC, design space)
- "The cron is firing twice — why?" → **infra** (scheduled job debugging)
- "Start a new Next.js prototype" → **parallel** (greenfield hard signal)
- "Rename `foo` to `bar` across repo" → **single** (mechanical)
- "Migrate images from Vercel Blob to Cloudflare R2" → **infra** (data migration)
- "Build a recommendation engine for related posts" → **parallel** (design space)
- "Fix the OAuth redirect on Vercel" → **infra** (auth + deployment)

### Step 4a — Parallel path (N=5)

**⚠ Prerequisite: Claude's primary working directory must be the project git repo.** The `isolation: "worktree"` parameter on the Agent tool checks Claude's cwd at spawn time. If Claude was launched from a non-repo directory, all 5 spawns fail.

1. Confirm working dir is a git repo by running `git rev-parse --git-dir` in a Bash call. If it fails:
   - Downgrade to single pass. Re-announce: `🔧 code-builder activated — single pass. Worktree isolation requires Claude to be launched from the project repo; currently at [cwd]. Restart from the project directory to enable parallel drafts.`
   - Proceed with Step 4b.
2. Spawn **5 `Agent` calls in parallel in a single message**, each with:
   - `isolation: "worktree"` (each draft gets its own worktree + branch — no file collisions)
   - `run_in_background: true`
   - `subagent_type: "general-purpose"`
   - The task prompt + a bias hint for differentiation:
     - Draft 1: *simplest possible — fewest lines, no abstractions*
     - Draft 2: *most idiomatic to this repo — match existing patterns exactly*
     - Draft 3: *optimize for readability — clearest naming, smallest functions*
     - Draft 4: *optimize for correctness on edge cases + security*
     - Draft 5: *your choice — go with your best instinct*
   - Instruction: "You are one of 5 parallel drafts. Commit your work on the worktree branch. Report: approach summary (2 lines), files touched, LOC added/removed, commit SHA, any edge cases you handled."
3. Wait for all 5 to complete. If any fail/timeout, note it and continue with the survivors (score those that completed).

### Step 4b — Single path

Just do the task normally. Skip to Step 7 to log the run.

### Step 4c — Infrastructure path (pre-flight + execute)

Infrastructure tasks are stateful and often irreversible. No parallel drafts — instead, run a checklist before writing any code.

**Pre-flight checklist (print each item before proceeding):**

1. **Affected services.** List every deployment target, storage backend, and external service this change touches (Vercel, Render, Cloudflare, GHA, third-party APIs).
2. **Rollback plan.** How do you undo this if it fails? If the answer is "you can't easily," say so and ask Hannah to confirm before proceeding.
3. **Environment parity.** Grep all deployment targets for environment variables this change adds/modifies. Flag any target that's missing a required var.
4. **Concurrent access.** Will this change run while users/cron jobs are active? If yes: serialize writes, add idempotency guards, or schedule a maintenance window.
5. **Data backup.** For any destructive data operation (migration, deletion, schema change): confirm backup exists or create one first.

**After pre-flight, execute sequentially** — not in parallel. Verify each step before proceeding to the next.

**Report:**
> ✓ Infra complete. {task summary ≤15 words}. Rollback: {plan}. Env vars synced: {yes/no + which targets}. Tests ✓.

Proceed to Step 6.5 (verification) and then Step 7 (log).

### Step 5 — Self-evaluate and pick the winner (parallel only)

**Claude picks. Do NOT ask Hannah to review 5 diffs.**

Score each draft out of **100 points**:

| Criterion | Weight | Measurement |
|---|---|---|
| Correctness | 25 | Walk each requirement in the task prompt; deduct for misses. |
| Tests pass | 15 | Run `npm test` / `pytest` / project's test cmd on each worktree. Pass = 15; any fail = 0. No tests → redistribute to Correctness (total 40). |
| Typecheck clean | 10 | `tsc --noEmit` or equiv. 0 errors = 10. |
| Security | 10 | No hardcoded secrets in client code, no `NEXT_PUBLIC_` credentials, input validated at system boundaries, no injection vectors. Deduct 10 for any secret exposure; 5 for missing boundary validation. |
| Minimal diff | 10 | `10 * (min_LOC_across_drafts / this_LOC)`. |
| Reuses existing utilities | 10 | Did the draft grep for and reuse existing helpers? Deduct for duplicate utilities. |
| Follows repo conventions | 10 | Naming, file structure, import style vs. neighboring files. |
| Data integrity | 5 | Null guards on API/KV responses, concurrent write safety, no destructive operations without backup. |
| No unnecessary new deps | 5 | 0 new = 5; each new = −2 unless genuinely required. |

**Tiebreakers:** (1) smallest diff, (2) draft 2 (most idiomatic to repo).

Record the full score breakdown for all 5 drafts in the run log — the Sunday sync uses this to calibrate weights.

### Step 6 — Merge validation (prevent loss + redundancy)

Before declaring done:

1. **Gap check.** Re-read the original task. Walk each requirement; confirm the winner's diff covers it. For any gap, check the 4 rejected drafts — if any of them solved the gap, `git cherry-pick` just that change onto the winner's branch. If none did, write it fresh.
2. **Redundancy check.** Scan the winner's (now-merged) diff for: unused imports, dead code, commented-out blocks, debug logs, duplicate helpers shadowing existing utilities. Strip any found.
3. **Rerun validation.** Tests + typecheck + lint one more time on the final diff.
4. **Merge.** Merge the winner's branch into the working branch (fast-forward if possible; else `git merge --no-ff`).
5. **Clean up worktrees.** `git worktree remove` all 5. Delete losing branches. **Keep the winner's branch** (needed for post-merge-diff signal in the sync).
6. **Report in one line:**
   > ✓ Merged draft {N}/5 (score {X}/100). {≤15-word reason it beat the others.} {Cherry-picked {Y} from draft M | No gaps.} Tests ✓ Types ✓ Lint ✓.

If Hannah replies "actually use draft 3" or "the tests still fail" → re-pick or debug, and log the override in the run file.

### Step 6.5 — Post-merge verification

After merging (parallel or single) or completing an infra task, verify the change actually works — not just that it compiles.

**Verification checklist:**
1. If a dev server is running or can be started: load the affected page/endpoint and confirm the golden path works.
2. For API changes: make a test request and confirm the response shape.
3. For scheduled jobs/cron: trigger manually once and confirm execution.
4. For auth changes: test the full login flow (not just the changed step).
5. For data migrations: spot-check 3 records before and after.

**If verification fails:** fix the issue before declaring done. Do not log the run as successful until verification passes.

**If verification is not possible** (no dev server, external dependency, requires production environment): state explicitly what couldn't be verified and why. Do not silently skip this step.

**Report:** Append to the merge report:
> Verified: {what was checked}. {or: "Verification deferred — {reason}."}

### Step 7 — Log the run (required, always)

Write `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`:

```md
---
date: 2026-04-13
task_slug: dark-mode-journal-editor
repo: hannah-portfolio
judgment: parallel  # or "single" or "infra"
judgment_override: null  # or "single → parallel" if Hannah flipped it
winner_draft: 3
winner_sha: abc1234
winner_score: 82
cherry_picks_from: [1]  # draft indices cherry-picked from
verified: true  # or false with reason
---

## Task (verbatim)
> add a dark mode toggle to the journal editor

## Judgment
Parallel — new feature, multi-file (context + CSS + storage), multiple design choices.

## Drafts

### Draft 1 — simplest possible
- Approach: CSS variable swap via `document.documentElement.classList`
- Files: `app/layout.tsx`, `app/globals.css` (34 LOC)
- Score: 78/100 (correctness 22, tests 15, typecheck 10, security 10, diff 10, reuse 6, conv 0, data 5, deps 0)
- SHA: `abc1111`

### Draft 2 — most idiomatic
...

### Draft 3 — readability ⭐ WINNER
- Score: 82/100
- Why it won: Matched existing ThemeProvider pattern; no new deps; passed all tests.

### Draft 4 — correctness + security
...

### Draft 5 — free choice
...

## Cherry-picks
- From Draft 1: added `prefers-color-scheme` media query fallback (winner missed this).

## Verification
Loaded /journal in dev server, toggled dark mode, confirmed persistence across reload.

## In-session feedback from Hannah (verbatim)
- "make sure it doesn't flash on first load"
- (picked up the flash concern via cherry-pick from Draft 4)

## Notes
Draft 5 timed out at 3min. Scored based on partial diff.
```

Log **all fields every run** — the sync depends on them being structured.

---

## Syncing learnings (Sunday 6pm + on-demand)

Scheduled cron: `0 18 * * 0`. Also trigger on-demand: Hannah says "code-builder sync" or runs `/code-builder sync`.

**Self-sufficient** — pulls data the skill itself writes. No dependency on the `summary` skill or any manual journaling.

### Sync workflow

1. **Determine window.** Read the `Last synced:` date at the top of the `## Current learnings` section below. If "never", read all `runs/*.md`. Otherwise read only runs with date > last sync.

2. **Collect data from 5 sources:**
   - **a. Run logs.** Read every new `runs/*.md`.
   - **b. Post-merge git diffs** — for each run's `winner_sha`, in that repo:
     ```
     git log {winner_sha}..HEAD --oneline -- <winner's files>
     git diff {winner_sha}..HEAD -- <winner's files>
     ```
     Reveals what Hannah silently edited after merge — the skill's highest-value learning signal.
   - **c. In-session feedback** — already captured in run logs.
   - **d. Judgment overrides** — `judgment_override` field in run frontmatter.
   - **e. Cross-repo mining (bounded).** For each active personal repo (`hannah-portfolio`, `muse-shopping`, `libby-hold-monitor`, `kindle-schlacter-me`, `interior-designer-portfolio`):
     ```
     cd <repo> && git fetch --all && \
     git log --since="<last-sync-date>" --max-count=50 \
       --author="Hannah Schlacter" \
       --grep="fix\|revert\|oops\|simplify\|cleanup\|migrate\|rollback"
     ```
     Hard bounds (`--max-count=50`, author filter, `--since` window) prevent a noisy repo from dominating. `git fetch --all` first avoids stale-clone false negatives.

3. **Pass 1 — Count patterns.** Any signal repeated ≥2 times across runs becomes a candidate learning:
   - "3 runs: Hannah overrode single → parallel when task touched ≥2 files → lower the file-count threshold"
   - "4 runs: post-merge diffs removed `try/catch` around internal calls → anti-pattern"
   - "2 runs: winner scored lowest on 'reuses existing utilities' but Hannah kept it → reduce that weight"
   - "2 runs: infra tasks took 3× longer without rollback plan → reinforce pre-flight"

4. **Pass 2 — Refine the existing learnings, don't blindly append:**
   - Duplicate of existing → increment citation count only
   - Contradicts existing → supersede; note reversal with date
   - Strengthens existing → update citation count + date
   - New → add

5. **Pass 3 — Prune.** Enforce **hard cap of 30 bullets** in `## Current learnings`. If over: remove by priority (oldest, fewest citations, superseded).

6. **Write.** Use `Edit` to update the `## Current learnings` section below. Update `Last synced:` to today. Commit nothing — this file lives in `~/.claude/skills/`, not in a repo.

7. **Announce:** `🔧 code-builder sync complete — added {N}, refined {M}, pruned {P}. Total learnings: {X}/30.`

---

## Current learnings

Last synced: 2026-05-22 (backfill from build-log 221 entries + 4 repos + portfolio 187 sessions; 24 bullets)

*If a repo's `CLAUDE.md` contradicts a rule below, the repo rule wins.* This section captures cross-repo patterns; per-repo rules override.

### §A. Claude process failures

- **Never call `Skill()` from inside a scheduled-task body.** Circular dispatch re-triggers on each tick, burning rate limit until the task is killed. *Does not apply to* on-demand skills invoked from a user turn. (1 citation: `summary:scheduled-tasks-bug-fixer-fix.md`)
- **No hardcoded tokens or secrets in client JS — even for internal tools.** Anything imported into a `"use client"` module or prefixed `NEXT_PUBLIC_` ships to the browser; credential rotation + disclosure is the cost. (1 citation: `summary:calmar-upload-security.md`)
- **"Done" requires green tests + typecheck + verification, not "looks right."** Declaring completion off a compile-pass alone forces a rework loop when the real failure surfaces 2–3 messages later. Post-merge verification (Step 6.5) exists for this reason. (2 citations: `summary:calmar-jose-notes-recovery.md`, `summary:ramp-resume.md`)
- **Resolve merge conflicts by re-running tests, not by eyeballing which side to keep.** Code was silently lost 3× — data loss is the hardest class of bug to trace. (1 citation: calmar `ff5ac3a`)
- **Guard nullable KV/API responses before destructuring.** Render `<EmptyState />` or early-return when the upstream can return `null`/`undefined`; `const { foo } = res` at the top of a component crashes the page. Cross-repo ×3. (3 citations: calmar `cae05a6`, schlacter.me `26e3345`, muse `f0eeb07`)
- **Grep for existing helpers before writing a new one.** Accumulated 3× duplicated date-formatting utilities; copies drift and maintenance compounds. (1 citation: calmar pattern mining)
- **Serialize writes to the same resource.** Parallel PUTs to the same GitHub file / KV key cause data loss via race condition. Always serialize writes to shared state. (1 citation: build-log GitHub API race condition)
- **Always have a migration/rollback path for cloud storage.** Vercel Blob was suspended without warning requiring emergency R2 migration. Every storage integration needs a documented escape hatch. (1 citation: build-log Vercel Blob suspension + R2 migration)

### §B. Concrete code-level patterns

- **Validate + trim `process.env.X` at the read-site.** Whitespace, quoting, and trailing-newline variance across Vercel/Render/local cause silent misconfig. Cross-repo ×2. (4 citations: `30b8853`, `ac6df91`, `3cb8289`, `818d178`)
- **Floating UI inside a scroll/overflow parent needs `position: fixed` + a portal — not `position: absolute`.** Absolute positioning clips inside gallery tiles, mobile bottom sheets, and modal bodies. Cross-repo ×2. (1 citation: `summary:calmar-notification-share-redesign.md`)
- **Rules of Hooks, full form: no conditional hook calls, no hooks inside callbacks/effects, no `return` before the hooks list is complete.** React's error surfaces one render later, making attribution hard. Cross-repo ×2. (Agent pattern mining, 2026-04-13)
- **`useEffect` that subscribes, starts a timer, or sets state must return a cleanup function.** Missing cleanup is the #1 correction category. *Does not apply to* pure derived-state effects. (Agent pattern mining, 2026-04-13)
- **Unscale `getBoundingClientRect()` values when an ancestor has a CSS transform.** Measurements return in the transformed frame; crop overlays compute the wrong origin. (2 citations: calmar `1e1f242`, `summary:calmar-bug-crop-zoom-and-numbered-list.md`)
- **Save editor selection before opening any DOM-mutating modal; restore on close.** Re-opening a toolbar action after a modal jumps to the wrong line or loses the caret. (2 citations: calmar `21b2d7e`, `summary:calmar-jose-notes-recovery.md`)

### §C. Infrastructure patterns

- **Playwright/browser automation on CI: cold runners need 4min+ timeouts.** Default 30s consistently fails on GitHub Actions cold starts. Set generous timeouts and add retry logic for flaky network-dependent steps. (1 citation: build-log GHA Playwright timeout tuning)
- **iOS Shortcuts with multipart form body require iterative validation.** Plist key structures, JSON encoding, and file upload payloads each need independent verification. Budget 3× the estimated time for Shortcuts integration. (1 citation: build-log 13-iteration iOS Shortcut development)
- **Scheduled API endpoints need idempotency guards.** Cron double-fire is common on cold starts and platform retries. Every scheduled endpoint should be safe to call twice with the same input. (1 citation: build-log cron double-fire incidents)
- **When migrating between storage providers, implement size checks and restore-from-source.** Migration endpoints should verify transferred data integrity (size, hash) and have a source-of-truth fallback. (1 citation: build-log R2 migration with broken placeholders)
- **Test auth flows end-to-end, not just the changed step.** OAuth edge cases compound: missing DB columns, trust proxy settings on Vercel, OAuth-only accounts without password fields. Each one is invisible in unit tests. (1 citation: build-log multiple OAuth edge case fixes across muse-shopping)
- **When adding/modifying env vars, grep all deployment targets.** Vercel, Render, GHA secrets, and local `.env` files drift apart silently. One missed target = production outage. Cross-repo ×3. (4 citations: env var trim fixes across schlacter.me)

## Meta notes

- The `isolation: "worktree"` Agent parameter fails when Claude's cwd is not a git repo. Documented as a prerequisite in Step 4a. If it fails again in future runs, auto-downgrade to single pass and tell Hannah to restart from the project repo.
- **Deferred to later syncs:** holdout-commit eval (§12a), N=5 live-task precision/recall eval (§12b), citation-validity pre-commit lint (§12d), token-budget hard cap enforcement (§12c), stale-rule quarterly audit (§12e), cross-skill conflict scan (§12f). Revisit after ≥3 real parallel runs accumulate.
- **Source pinning:** initial backfill drew from session summaries (backfill-only source, not recurring) + build-log repo. Weekly sync pulls from run logs + post-merge diffs + cross-repo git mining (see sync Step 2).

## Changelog

- **2026-05-22 audit + v2 upgrade** — Added: infra mode (Step 4c) with pre-flight checklist for migrations/deployment/auth/cron. Added: post-merge verification step (Step 6.5). Rebalanced rubric: +Security 10pts, +Data Integrity 5pts, −Scope Containment 5pts, −No New Deps 5pts. Added: §C Infrastructure patterns (6 bullets from build-log evidence). Updated: §A with 2 new bullets (serialize writes, migration rollback). Updated: cross-repo mining targets to current repos. Updated: Last synced date + citation counts.
- **2026-04-13 backfill sanity test** — task: populate §A + §B + add Source e to sync + `~/.claude/` versioning. Rules that fired: §A3, §A6. Structural loads: SKILL.md 306 lines, §A=6 bullets, §B=6 bullets, Meta notes preserved, sync lists 5 sources.
