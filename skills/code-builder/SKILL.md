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
- Hannah is in a known project repo and asks for a change
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

### Step 1 — (No read step)

Learnings are embedded in the `## Current learnings` section at the bottom of this file and already loaded with the skill description. **Do not read a separate learnings file.** Proceed straight to Step 2.

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

**Hard signals (any one decides):**
- Hannah explicit override → obey
- Not a git repo → force **single** (worktrees require git)
- Live debugging with rapid iteration needed → force **single** (parallel too slow)
- Greenfield prototype from scratch → force **parallel**

**Bias-hint adaptation (NEW):** Before spawning drafts, check `## Bias win-rate` below. If a bias has <15% win rate across 10+ runs for this task type (feature/bugfix/refactor), demote it from a full draft to a "scout" — still spawned but with a smaller scope budget (max 50 LOC). This frees cognitive budget for the biases that historically win.

**Worked examples:**
- "Add dark mode to the journal editor" → **parallel** (new feature, multi-file, multiple design choices)
- "Fix typo in the header" → **single** (1 LOC, 1 file)
- "Refactor share dropdown for per-person edit access" → **parallel** (>30 LOC, design space)
- "The cron is firing twice — why?" → **single** (debugging)
- "Start a new Next.js prototype" → **parallel** (greenfield hard signal)
- "Rename `foo` to `bar` across repo" → **single** (mechanical)
- "Build a recommendation engine for related posts" → **parallel** (design space)

### Step 4a — Parallel path (N=5)

**⚠ Prerequisite: Claude's primary working directory must be the project git repo.** The `isolation: "worktree"` parameter on the Agent tool checks Claude's cwd at spawn time. If Claude was launched from a non-repo directory, all 5 spawns fail.

1. Confirm working dir is a git repo by running `git rev-parse --git-dir` in a Bash call. If it fails:
   - Downgrade to single pass. Re-announce: `🔧 code-builder activated — single pass. Not in a git repo — worktree isolation unavailable. Run from the project directory to enable parallel drafts.`
   - Proceed with Step 4b.

2. **Token budget check (NEW).** Estimate total tokens for 5 parallel agents based on the task scope:
   - Small task (<50 LOC estimate): proceed normally
   - Medium task (50-200 LOC): proceed normally
   - Large task (>200 LOC): warn Hannah before spawning: `⚠ Large task — 5 parallel drafts may use significant tokens. Proceed? (or "3x this" for 3 drafts, "just do it" for single pass)`
   - If Hannah says nothing after 10s, proceed with 5 drafts.

3. Spawn **5 `Agent` calls in parallel in a single message**, each with:
   - `isolation: "worktree"` (each draft gets its own worktree + branch — no file collisions)
   - `run_in_background: true`
   - `subagent_type: "general-purpose"`
   - The task prompt + a bias hint for differentiation:
     - Draft 1: *simplest possible — fewest lines, no abstractions*
     - Draft 2: *most idiomatic to this repo — match existing patterns exactly*
     - Draft 3: *optimize for readability — clearest naming, smallest functions*
     - Draft 4: *optimize for performance / correctness on edge cases*
     - Draft 5: *your choice — go with your best instinct*
   - Instruction: "You are one of 5 parallel drafts. Commit your work on the worktree branch. Report: approach summary (2 lines), files touched, LOC added/removed, commit SHA, any edge cases you handled."
4. Wait for all 5 to complete. If any fail/timeout, note it and continue with the survivors (score those that completed).

### Step 4b — Single path

Just do the task normally. Skip to Step 7 to log the run.

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
| No unnecessary new deps | 10 | 0 new = 10; each new = −3 unless genuinely required. |
| Reuses existing utilities | 10 | Did the draft grep for and reuse existing helpers? |
| Follows repo conventions | 10 | Naming, file structure, import style vs. neighboring files. |
| Scope containment | 5 | Deduct if unrelated files were touched. |

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

### Step 7 — Log the run (required, always)

Write `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`:

```md
---
date: 2026-04-13
task_slug: dark-mode-journal-editor
repo: 662-calmar-portfolio
judgment: parallel  # or "single"
judgment_override: null  # or "single → parallel" if Hannah flipped it
winner_draft: 3
winner_bias: readability  # NEW: track which bias won
winner_sha: abc1234
winner_score: 82
task_type: feature  # NEW: feature | bugfix | refactor | greenfield | mechanical
cherry_picks_from: [1]  # draft indices cherry-picked from
all_scores: [78, 75, 82, 71, 68]  # NEW: ordered scores for bias tracking
---

## Task (verbatim)
> add a dark mode toggle to the journal editor

## Judgment
Parallel — new feature, multi-file (context + CSS + storage), multiple design choices.

## Drafts

### Draft 1 — simplest possible
- Approach: CSS variable swap via `document.documentElement.classList`
- Files: `app/layout.tsx`, `app/globals.css` (34 LOC)
- Score: 78/100 (correctness 22, tests 15, typecheck 10, lint 5, diff 10, deps 10, reuse 6, conv 0, scope 0)
- SHA: `abc1111`

### Draft 2 — most idiomatic
...

### Draft 3 — readability ⭐ WINNER
- Score: 82/100
- Why it won: Matched existing ThemeProvider pattern; no new deps; passed all tests.

### Draft 4 — performance
...

### Draft 5 — free choice
...

## Cherry-picks
- From Draft 1: added `prefers-color-scheme` media query fallback (winner missed this).

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
   - **b. Post-merge git diffs.** For each run's `winner_sha`, in that repo:
     ```bash
     git log {winner_sha}..HEAD --oneline -- <winner's files>
     git diff {winner_sha}..HEAD -- <winner's files>
     ```
     Reveals what Hannah silently edited after merge — the skill's highest-value learning signal. **Classify each post-merge edit:**
     - *Style fix* (rename, reformat, comment) → weak signal, increment count only
     - *Logic change* (different approach, added guard, changed flow) → strong signal, create candidate learning
     - *Revert/replace* (Hannah threw out the approach) → very strong signal, flag for rubric weight adjustment
   - **c. In-session feedback** — already captured in run logs.
   - **d. Judgment overrides** — `judgment_override` field in run frontmatter.
   - **e. Cross-repo mining (auto-discovered).** Scan `~/.claude/projects/` for directories containing `.git`:
     ```bash
     find ~/.claude/projects/ -maxdepth 3 -name ".git" -type d | \
       while read gitdir; do
         repo=$(dirname "$gitdir")
         cd "$repo" && git fetch --all 2>/dev/null && \
         git log --since="<last-sync-date>" --max-count=50 \
           --author="Hannah" \
           --grep="fix\|revert\|oops\|simplify\|cleanup" \
           --oneline
       done
     ```
     Auto-discovers repos instead of hardcoding names. Hard bounds (`--max-count=50`, author filter, `--since` window) prevent a noisy repo from dominating.

3. **Pass 1 — Count patterns.** Any signal repeated ≥2 times across runs becomes a candidate learning:
   - "3 runs: Hannah overrode single → parallel when task touched ≥2 files → lower the file-count threshold"
   - "4 runs: post-merge diffs removed `try/catch` around internal calls → anti-pattern"
   - "2 runs: winner scored lowest on 'reuses existing utilities' but Hannah kept it → reduce that weight"

4. **Pass 2 — Refine the existing learnings, don't blindly append:**
   - Duplicate of existing → increment citation count only
   - Contradicts existing → supersede; note reversal with date
   - Strengthens existing → update citation count + date
   - New → add

5. **Pass 3 — Prune.** Enforce **hard cap of 30 bullets** in `## Current learnings`. If over: remove by priority (oldest, fewest citations, superseded).

6. **Pass 4 — Update bias win-rate (NEW).** Read `winner_bias` and `task_type` from all run logs. Compute win rate per bias per task type. Update the `## Bias win-rate` section below. If any bias has <15% win rate across 10+ runs for a task type, note it for demotion in Step 3.

7. **Write.** Use `Edit` to update the `## Current learnings` and `## Bias win-rate` sections below. Update `Last synced:` to today. Commit nothing — this file lives in `~/.claude/skills/`, not in a repo.

8. **Announce:** `🔧 code-builder sync complete — added {N}, refined {M}, pruned {P}. Total learnings: {X}/30. Bias win-rates updated.`

---

## Cross-skill integration (NEW)

- **mcp-contributor:** When Hannah is contributing to MCP repos (github.com/modelcontextprotocol/*), code-builder should auto-activate for the PR code. The mcp-contributor skill handles governance/process; code-builder handles the implementation quality.
- **insights-dashboard:** The aggregator's hours-per-project data can inform learning priority — projects where Hannah spends more hours likely have more post-merge edits and richer learning signal. During sync, check if `claude-code-stats.json` exists and weight cross-repo mining toward top-hours projects.

---

## Current learnings

Last synced: 2026-04-13 (initial backfill — 4 repos + 13 session summaries; 12 bullets)

*If a repo's `CLAUDE.md` contradicts a rule below, the repo rule wins.* This section captures cross-repo patterns; per-repo rules override.

### §A. Claude process failures

- **Never call `Skill()` from inside a scheduled-task body.** Circular dispatch re-triggers on each tick, burning rate limit until the task is killed. *Does not apply to* on-demand skills invoked from a user turn. (1 citation: `summary:scheduled-tasks-bug-fixer-fix.md`)
- **No hardcoded tokens or secrets in client JS — even for internal tools.** Anything imported into a `"use client"` module or prefixed `NEXT_PUBLIC_` ships to the browser; credential rotation + disclosure is the cost. (1 citation: `summary:calmar-upload-security.md`)
- **"Done" requires green tests + typecheck, not "looks right."** Declaring completion off a compile-pass alone forces a rework loop when the real failure surfaces 2–3 messages later. (2 citations: `summary:calmar-jose-notes-recovery.md`, `summary:ramp-resume.md`)
- **Resolve merge conflicts by re-running tests, not by eyeballing which side to keep.** Code was silently lost 3x in calmar — data loss is the hardest class of bug to trace. (1 citation: calmar `ff5ac3a "Resolve merge conflict, keep upstream DesignerBriefClient"`)
- **Guard nullable KV/API responses before destructuring.** Render `<EmptyState />` or early-return when the upstream can return `null`/`undefined`; `const { foo } = res` at the top of a component crashes the page instead of showing empty state. *Does not apply to* responses already narrowed by a guard upstream. Cross-repo x3. (3 citations: calmar `cae05a6`, schlacter.me `26e3345`, muse `f0eeb07`)
- **Grep for existing helpers before writing a new one.** Calmar accumulated 3x duplicated date-formatting utilities this way; copies drift and maintenance compounds. (1 citation: calmar pattern [Agent A mining, 2026-04-13])

### §B. Concrete code-level patterns

- **Validate + trim `process.env.X` at the read-site.** Whitespace, quoting, and trailing-newline variance across Vercel/Render/local cause silent misconfig — four separate schlacter.me fixes alone. *Does not apply to* booleans already normalized upstream. Cross-repo x2 [schlacter.me], [calmar]. (4 citations: `30b8853`, `ac6df91`, `3cb8289`, `818d178`)
- **Floating UI inside a scroll/overflow parent needs `position: fixed` + a portal — not `position: absolute`.** Absolute positioning clips inside gallery tiles, mobile bottom sheets, and modal bodies. Cross-repo x2 [calmar], [muse]. (1 citation: `summary:calmar-notification-share-redesign.md`)
- **Rules of Hooks, full form: no conditional hook calls, no hooks inside callbacks/effects, no `return` before the hooks list is complete.** React's error surfaces one render later, making attribution hard. Cross-repo x2 [calmar], [muse]. (Agent A/B pattern mining, 2026-04-13)
- **`useEffect` that subscribes, starts a timer, or sets state must return a cleanup function.** Missing cleanup is the #1 correction category in calmar. *Does not apply to* pure derived-state effects (no subscription, no timer, no set). x4 [calmar]. (Agent A pattern mining, 2026-04-13)
- **Unscale `getBoundingClientRect()` values when an ancestor has a CSS transform.** Measurements return in the transformed frame, not the source frame; crop overlays compute the wrong origin and zoom jumps. [calmar]. (2 citations: calmar `1e1f242`, `summary:calmar-bug-crop-zoom-and-numbered-list.md`)
- **Save editor selection before opening any DOM-mutating modal; restore on close.** Re-opening a toolbar action after a modal jumps to the wrong line or loses the caret. [calmar]. (2 citations: calmar `21b2d7e`, `summary:calmar-jose-notes-recovery.md`)

---

## Bias win-rate (NEW)

Last synced: never (will populate after first sync with new run log format)

Track which draft bias wins per task type. Used by Step 3 to demote consistently losing biases.

| Bias | Feature wins | Bugfix wins | Refactor wins | Total wins | Total runs | Win % |
|------|-------------|-------------|---------------|------------|------------|-------|
| simplest | — | — | — | — | — | — |
| idiomatic | — | — | — | — | — | — |
| readability | — | — | — | — | — | — |
| performance | — | — | — | — | — | — |
| free choice | — | — | — | — | — | — |

---

## Meta notes

- The `isolation: "worktree"` Agent parameter fails when Claude's cwd is not a git repo. Documented as a prerequisite in Step 4a. If it fails again in future runs, auto-downgrade to single pass and tell Hannah to restart from the project repo.
- **Deferred to later syncs (requires data accumulation):** holdout-commit eval (§12a, needs 20+ parallel runs), N=5 live-task precision/recall eval (§12b, needs 20+ runs), citation-validity pre-commit lint (§12d), stale-rule quarterly audit (§12e), cross-skill conflict scan (§12f).
- **Source pinning:** initial backfill drew from session summaries (backfill-only source, not recurring). Weekly sync pulls from run logs + post-merge diffs + cross-repo git mining (see sync Step 2).

## Changelog

- **2026-05-05 audit improvements** — Added: bias win-rate tracking (Step 3, Step 7 frontmatter, sync Pass 4, new section), auto-discovery for cross-repo mining (replaced hardcoded repo names in sync Step 2e), token budget check (Step 4a.2), post-merge diff classification (sync Step 2b), cross-skill integration section, task_type field to run log format.
- **2026-04-13 backfill sanity test** — task: populate §A + §B + add Source e to sync + `~/.claude/` versioning. Rules that fired: §A3 "done requires green tests + typecheck" (ran structural verification before declaring Phase 1 complete — bullet count, section headers, meta-note preservation), §A6 "grep for existing helpers" (checked for pre-existing `~/.claude/.git`, existing CLAUDE.md in each target repo, existing dotfile structure before drafting new `.gitignore`). Rules not triggered: §A1/§A2/§A4/§A5 and all §B — out of scope for this session's work. Structural loads: SKILL.md 306 lines, §A=6 bullets, §B=6 bullets, Meta notes preserved, sync lists 5 sources. Live-task eval (§12b) deferred to next natural code-builder invocation on a real repo.
