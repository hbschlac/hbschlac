---
name: code-builder
description: >
  Raises the floor of code quality by generating 5 parallel implementations
  of the same dev task, self-scoring them against a measurable rubric, and
  merging the winner. Auto-activates whenever Hannah is writing, changing,
  or fixing code — building a prototype, fixing a bug, adding or changing
  a feature. Claude exercises judgment to decide parallel vs single pass;
  not every task warrants 5 drafts. Announces activation on every run so
  Hannah knows the skill is active. The trigger lists below are
  illustrative, not exhaustive — use judgment to recognize dev work from
  context.
---

# code-builder

Raises the floor of Claude's dev output by running **5 parallel implementations**, **self-scoring them against a measurable rubric**, and merging the winner. The bet: if Claude lands good code ~80% of the time, single-pass output is suboptimal 1-in-5 tasks. Five parallel drafts + objective scoring pushes the floor much higher.

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
- "5x this" / "parallel this" — force parallel
- "just fix it" / "quick fix" — force single

**Implicit triggers (examples):**
- Working dir is a git repo AND Hannah describes a coding task
- Hannah shares an error, stack trace, or failing log
- Hannah pastes code and asks about/for a change
- Hannah is in a known project repo (hannah-portfolio, interior-designer-portfolio, muse-shopping, libby-hold-monitor, etc.) and asks for a change
- Hannah says "something broke" / "this page is broken" / "the test is failing"
- Hannah says "I'm starting a new [prototype|app|project]"

**Do NOT activate:**
- Pure research or code reading ("how does X work?", "walk me through this")
- Writing, design, planning, brainstorming, outreach
- Meta tasks ("what are my TODOs?", "summarize this session")

**When uncertain, default to activating.** A single-pass run costs almost nothing; mis-skipping a real dev task is worse.

---

## Announcement (required, every activation)

Before doing anything else, print exactly this one-line banner:

> 🔧 **code-builder activated** — [parallel, 5 drafts | single pass]. [≤15-word reason.]

Examples:
- `🔧 code-builder activated — parallel, 5 drafts. New feature; multiple architectures viable.`
- `🔧 code-builder activated — single pass. One-line fix; parallel would be noise.`
- `🔧 code-builder activated — single pass. Not a git repo; worktree isolation unavailable.`

Hannah can override with "actually, 5x this" or "actually, just fix it" → flip and re-announce.

---

## Workflow

### Step 1 — Check known patterns before writing code

Before writing anything, scan the `## Current learnings` section at the bottom of this file. If the task matches a known pattern (e.g., env var handling, floating UI, modal state), apply the pattern directly. This prevents the multi-commit fix chains that learnings were captured to avoid.

**Anti-pattern check:** if the task involves any of these, pause and consult learnings:
- Environment variables or secrets
- Popups, modals, or overlays inside scrollable containers
- React hooks (especially useEffect with subscriptions/timers)
- Auth/OAuth flows
- CSS transforms + getBoundingClientRect
- Editor selection / caret management
- KV/API responses that could be null

### Step 2 — Scope the task

State the task in one line. Identify:
- Files likely to change
- Greenfield (new feature/prototype) vs. modification (bug fix, tweak)
- Design space — multiple valid approaches, or basically fixed?

### Step 3 — Judgment gate

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
| **Iteration history** | Task is a re-attempt of something that failed before | First attempt |

**Hard signals (any one decides):**
- Hannah explicit override → obey
- Not a git repo → force **single** (worktrees require git)
- Live debugging with rapid iteration needed → force **single** (parallel too slow)
- Greenfield prototype from scratch → force **parallel**
- Task touches auth/OAuth → force **parallel** (historically multi-iteration domain)
- Task is third+ attempt at same fix → force **parallel** (single pass isn't working)

**Worked examples:**
- "Add dark mode to the journal editor" → **parallel** (new feature, multi-file, multiple design choices)
- "Fix typo in the header" → **single** (1 LOC, 1 file)
- "Refactor share dropdown for per-person edit access" → **parallel** (>30 LOC, design space)
- "The cron is firing twice — why?" → **single** (debugging)
- "Start a new Next.js prototype" → **parallel** (greenfield hard signal)
- "Rename `foo` to `bar` across repo" → **single** (mechanical)
- "Build a recommendation engine for related posts" → **parallel** (design space)
- "Hook up Google OAuth" → **parallel** (auth hard signal)
- "This is still broken after two attempts" → **parallel** (retry hard signal)

### Step 4a — Parallel path (N=5)

**⚠ Prerequisite: Claude's primary working directory must be the project git repo.** The `isolation: "worktree"` parameter on the Agent tool checks Claude's cwd at spawn time.

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
     - Draft 4: *optimize for performance / correctness on edge cases*
     - Draft 5: *your choice — go with your best instinct*
   - Include relevant learnings from `## Current learnings` in each draft's prompt. If the task touches a known pattern (env vars, modals, hooks, auth), paste the relevant bullets directly into the prompt so each agent doesn't rediscover the same traps.
   - Instruction: "You are one of 5 parallel drafts. Commit your work on the worktree branch. Report: approach summary (2 lines), files touched, LOC added/removed, commit SHA, any edge cases you handled."
3. Wait for all 5 to complete. If any fail/timeout, note it and continue with the survivors (score those that completed).

### Step 4b — Single path (enhanced)

Do the task, but apply these guardrails that the parallel path gets "for free" from multi-draft competition:

1. **Pre-flight:** before writing code, grep for existing utilities that might already solve part of the problem. Check the repo's lib/, utils/, helpers/ directories.
2. **Write the solution.**
3. **Self-check against rubric criteria** (Step 5's criteria list). Don't score formally, but walk the checklist: correctness, tests, typecheck, lint, minimal diff, no new deps, reuses existing utilities, follows conventions, scope containment.
4. **Run tests + typecheck + lint** before declaring done. "Looks right" is not done.
5. If any check fails, fix before reporting — don't punt to the next conversation turn.

### Step 5 — Self-evaluate and pick the winner (parallel only)

**Claude picks. Do NOT ask Hannah to review 5 diffs.**

Score each draft out of **100 points**:

| Criterion | Weight | Measurement |
|---|---|---|
| Correctness | 25 | Walk each requirement in the task prompt; deduct for misses. |
| Tests pass | 15 | Run `npm test` / `pytest` / project's test cmd on each worktree. Pass = 15; any fail = 0. No tests → redistribute to Correctness (total 40). |
| Typecheck clean | 10 | `tsc --noEmit` or equiv. 0 errors = 10. |
| Lint clean | 5 | Project's lint cmd. 0 warnings = 5. |
| Minimal diff | 10 | `10 * (min_LOC_across_drafts / this_LOC)`. |
| No unnecessary new deps | 5 | 0 new = 5; each new = −2 unless genuinely required. |
| Reuses existing utilities | 10 | Did the draft grep for and reuse existing helpers? |
| Follows repo conventions | 10 | Naming, file structure, import style vs. neighboring files. |
| Scope containment | 5 | Deduct if unrelated files were touched. |
| Known-pattern compliance | 5 | Did the draft follow relevant `## Current learnings` bullets? |

**Tiebreakers:** (1) smallest diff, (2) draft 2 (most idiomatic to repo).

Record the full score breakdown for all 5 drafts in the run log.

### Step 6 — Merge validation (prevent loss + redundancy)

Before declaring done:

1. **Gap check.** Re-read the original task. Walk each requirement; confirm the winner's diff covers it. For any gap, check the 4 rejected drafts — if any of them solved the gap, `git cherry-pick` just that change onto the winner's branch. If none did, write it fresh.
2. **Redundancy check.** Scan the winner's (now-merged) diff for: unused imports, dead code, commented-out blocks, debug logs, duplicate helpers shadowing existing utilities. Strip any found.
3. **Rerun validation.** Tests + typecheck + lint one more time on the final diff.
4. **Merge.** Merge the winner's branch into the working branch (fast-forward if possible; else `git merge --no-ff`).
5. **Clean up worktrees.** `git worktree remove` all 5. Delete losing branches. **Keep the winner's branch** (needed for post-merge-diff signal).
6. **Report in one line:**
   > ✓ Merged draft {N}/5 (score {X}/100). {≤15-word reason it beat the others.} {Cherry-picked {Y} from draft M | No gaps.} Tests ✓ Types ✓ Lint ✓.

If Hannah replies "actually use draft 3" or "the tests still fail" → re-pick or debug.

### Step 7 — Log the run (inline, not to filesystem)

**Important: do NOT depend on ~/.claude/skills/ filesystem persistence.** Sessions may be ephemeral (especially Claude Code web). Instead:

**Option A (git repo available):** Append a structured entry to `.claude/code-builder-runs.md` in the project repo. Create the file if it doesn't exist. Commit with message `code-builder: log run — {task_slug}`.

**Option B (no writable repo):** Print the log entry in the conversation so it's captured in the session transcript. The insights dashboard can mine transcripts for these.

**Log format:**

```md
### {YYYY-MM-DD} — {task_slug}

- **Repo:** {repo name}
- **Judgment:** {parallel|single} {override? "← overridden from X"}
- **Winner:** Draft {N}, score {X}/100 {or "single pass" for single}
- **Cherry-picks:** {from draft M | none}
- **Known-pattern hits:** {which §A/§B bullets were applied}
- **Known-pattern misses:** {patterns that should have applied but didn't}
- **Post-fix needed:** {yes/no — did Hannah have to fix something after?}
```

---

## Syncing learnings (on-demand only)

~~Scheduled cron: `0 18 * * 0`~~ — Cron requires a persistent scheduler that Claude Code sessions don't have. **Sync is on-demand only.**

**Trigger:** Hannah says "code-builder sync" or runs `/code-builder sync`.

**Self-sufficient** — pulls data from in-repo run logs and git history.

### Sync workflow

1. **Determine window.** Read the `Last synced:` date at the top of `## Current learnings`. Read run logs since that date.

2. **Collect data from 3 sources:**
   - **a. Run logs.** Read `.claude/code-builder-runs.md` in the current repo (and any other repos Hannah specifies).
   - **b. Post-merge git diffs** — for each run's winner, check what Hannah changed after merge:
     ```
     git log {winner_sha}..HEAD --oneline -- <winner's files>
     git diff {winner_sha}..HEAD -- <winner's files>
     ```
   - **c. Git history mining.** In the current repo:
     ```
     git log --since="<last-sync-date>" --max-count=50 \
       --author="Hannah" \
       --grep="fix\|revert\|oops\|simplify\|cleanup"
     ```

3. **Pass 1 — Count patterns.** Any signal repeated ≥2 times becomes a candidate learning.

4. **Pass 2 — Refine existing learnings, don't blindly append:**
   - Duplicate of existing → increment citation count only
   - Contradicts existing → supersede; note reversal with date
   - Strengthens existing → update citation count + date
   - New → add

5. **Pass 3 — Prune.** Enforce **hard cap of 30 bullets** in `## Current learnings`. If over: remove by priority (oldest, fewest citations, superseded).

6. **Update.** Edit the `## Current learnings` section. Update `Last synced:` to today.

7. **Announce:** `🔧 code-builder sync complete — added {N}, refined {M}, pruned {P}. Total learnings: {X}/30.`

---

## Current learnings

Last synced: 2026-05-21 (audit sync — 4 repos + build-log + 221 commits analyzed; 22 bullets)

*If a repo's `CLAUDE.md` contradicts a rule below, the repo rule wins.* This section captures cross-repo patterns; per-repo rules override.

### §A. Claude process failures

- **Never call `Skill()` from inside a scheduled-task body.** Circular dispatch re-triggers on each tick, burning rate limit until the task is killed. *Does not apply to* on-demand skills invoked from a user turn. (1 citation: `summary:scheduled-tasks-bug-fixer-fix.md`)
- **No hardcoded tokens or secrets in client JS — even for internal tools.** Anything imported into a `"use client"` module or prefixed `NEXT_PUBLIC_` ships to the browser; credential rotation + disclosure is the cost. (1 citation: `summary:calmar-upload-security.md`)
- **"Done" requires green tests + typecheck, not "looks right."** Declaring completion off a compile-pass alone forces a rework loop when the real failure surfaces 2–3 messages later. (2 citations: `summary:calmar-jose-notes-recovery.md`, `summary:ramp-resume.md`)
- **Resolve merge conflicts by re-running tests, not by eyeballing which side to keep.** Code was silently lost 3× in calmar — data loss is the hardest class of bug to trace. (1 citation: calmar `ff5ac3a`)
- **Guard nullable KV/API responses before destructuring.** Render `<EmptyState />` or early-return when the upstream can return `null`/`undefined`; `const { foo } = res` at the top of a component crashes the page instead of showing empty state. *Does not apply to* responses already narrowed by a guard upstream. Cross-repo ×3. (3 citations: calmar, schlacter.me, muse)
- **Grep for existing helpers before writing a new one.** Calmar accumulated 3× duplicated date-formatting utilities this way; copies drift and maintenance compounds. (1 citation: calmar pattern mining)
- **After fixing a bug class, grep the entire repo (and sister repos) for the same pattern.** Env var trimming was fixed 4× separately in schlacter.me because each instance was found independently. One grep after the first fix would have caught all 4. (4 citations: schlacter.me `30b8853`, `ac6df91`, `3cb8289`, `818d178`)
- **When a fix takes 3+ commits, stop and re-scope.** Multi-commit fix chains (e.g., 13 commits for image storage migration, 6 for OAuth) indicate the approach needs rethinking, not more iterations of the same approach. Step back, identify root cause, then fix once. (build-log pattern: interior-designer-portfolio Apr 1-2, muse-shopping Apr 14-17)

### §B. Concrete code-level patterns

- **Validate + trim `process.env.X` at the read-site.** Whitespace, quoting, and trailing-newline variance across Vercel/Render/local cause silent misconfig. When fixing one env var, grep `process.env` to find all others in the file/repo and fix them all at once. *Does not apply to* booleans already normalized upstream. Cross-repo ×2. (4 citations: schlacter.me env var fixes)
- **Floating UI inside a scroll/overflow parent needs `position: fixed` + a portal — not `position: absolute`.** Absolute positioning clips inside gallery tiles, mobile bottom sheets, and modal bodies. Cross-repo ×2. (1 citation: calmar notification share redesign)
- **Rules of Hooks, full form: no conditional hook calls, no hooks inside callbacks/effects, no `return` before the hooks list is complete.** React's error surfaces one render later, making attribution hard. Cross-repo ×2. (calmar, muse pattern mining)
- **`useEffect` that subscribes, starts a timer, or sets state must return a cleanup function.** Missing cleanup is the #1 correction category in calmar. *Does not apply to* pure derived-state effects (no subscription, no timer, no set). ×4. (calmar pattern mining)
- **Unscale `getBoundingClientRect()` values when an ancestor has a CSS transform.** Measurements return in the transformed frame, not the source frame; crop overlays compute the wrong origin and zoom jumps. (2 citations: calmar crop tool fixes)
- **Save editor selection before opening any DOM-mutating modal; restore on close.** Re-opening a toolbar action after a modal jumps to the wrong line or loses the caret. (2 citations: calmar journal editor fixes)
- **`window.close()` is blocked by browsers unless the window was opened by script.** Don't rely on it for post-auth redirects. Use `window.location.replace()` as fallback, and if that reloads parent state, preserve state before the redirect flow. (build-log: libby-hold-monitor Apr 16-17, multiple attempts)
- **OAuth flows: validate redirect_uri, trust proxy config, and session persistence BEFORE building the happy path.** These three are the source of 80% of auth integration bugs. On Vercel serverless, `app.set('trust proxy', 1)` is required for secure cookies. (build-log: muse-shopping Apr 14-17)
- **iOS Shortcuts: use raw binary POST, not base64-encoded JSON payloads.** Shortcuts' HTTP action silently corrupts large base64 payloads. Send image bytes directly as multipart form data. (build-log: interior-designer-portfolio Apr 1-2, 13 iterations)
- **Vercel KV/Upstash: always set explicit TTLs and handle `null` returns.** KV.get() returns `null` for missing keys (not undefined, not empty string). Destructuring without a null guard crashes at render time. (build-log: calmar, schlacter.me pattern)

### §C. Frontend architecture patterns (from 200+ portfolio commits)

- **Keep all tabs mounted when using tabbed UI with persisted state.** Unmounting a tab on switch loses in-progress edits and triggers unnecessary re-fetches. Use CSS visibility or conditional rendering that preserves the DOM. (hannah-portfolio May 20: "keep all tabs mounted; stop spurious save on task done")
- **Auto-save needs debouncing AND dirty-state tracking.** Don't save on every state change — save on blur/idle with a dirty flag. Saving on task completion events that also mutate state causes recursive save loops. (hannah-portfolio May 20)
- **Drag-and-drop: separate click handlers from drag handlers.** When both are on the same element, clicks trigger incomplete drag gestures. Use a distance threshold (5px) before promoting a mousedown to a drag start. (build-log: interior-designer-portfolio roadmap, 15+ commits)
- **Image crop math: work in the image's natural coordinate space, not the display coordinate space.** Scale factors between natural size and rendered size (especially with CSS transforms) cause off-by-one crop regions. Always: `naturalX = displayX * (naturalWidth / displayWidth)`. (build-log: interior-designer-portfolio crop tool)

## Meta notes

- The `isolation: "worktree"` Agent parameter fails when Claude's cwd is not a git repo. Documented as a prerequisite in Step 4a. If it fails, auto-downgrade to single pass.
- **Filesystem persistence is not guaranteed.** Claude Code web sessions are ephemeral. Run logs are stored in the git repo (`.claude/code-builder-runs.md`), not in `~/.claude/`. This ensures they survive across sessions.
- **Weekly cron sync is retired.** Claude Code sessions don't have persistent schedulers. Sync is on-demand via "code-builder sync".
- **Cross-repo mining requires Hannah to specify target repos.** Don't assume access to repos not in the current session. The old approach of hardcoding repo paths (`~/.claude/projects/`) doesn't work in ephemeral environments.
- **Deferred features:** holdout-commit eval, N=5 live-task precision/recall eval, citation-validity pre-commit lint, token-budget hard cap enforcement, stale-rule quarterly audit, cross-skill conflict scan. Revisit after ≥3 real parallel runs.

## Changelog

- **2026-05-21 audit sync** — Major revision based on comprehensive skill audit. Changes: (1) Added Step 1 known-pattern pre-check to prevent recurrence of fixed bug classes. (2) Enhanced Step 4b single-pass with rubric-inspired guardrails. (3) Added "iteration history" signal to judgment gate — tasks that failed before escalate to parallel. (4) Added auth/OAuth as hard parallel signal based on build-log evidence. (5) Moved run logging from ~/.claude/ filesystem to in-repo `.claude/code-builder-runs.md` for session persistence. (6) Retired cron-based weekly sync; sync is now on-demand only. (7) Reweighted rubric: reduced "no new deps" from 10→5, added "known-pattern compliance" at 5 points. (8) Updated repo references: 662-calmar-portfolio→interior-designer-portfolio, schlacter.me→hannah-portfolio. (9) Added 10 new learnings (§A: 2 new, §B: 4 new, §C: 4 new section) from build-log mining of 221 commits. (10) Added anti-pattern check in Step 1 for known high-recurrence bug classes.
- **2026-04-13 backfill sanity test** — Initial population of §A + §B from 4 repos + 13 session summaries.
