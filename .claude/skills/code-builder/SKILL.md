---
name: code-builder
description: >
  Raises the floor of code quality by generating parallel implementations
  of the same dev task, self-scoring them against a project-adaptive rubric,
  and merging the winner. Auto-activates on dev work. Includes session safety,
  debug escalation for fix-churn, and deployment verification. Claude exercises
  judgment to decide parallel-3, parallel-5, single-pass, or debug-escalation;
  not every task warrants parallel drafts.
---

# code-builder

Raises the floor of Claude's dev output by running **parallel implementations**, **self-scoring them against a measurable rubric**, and merging the winner. Five parallel drafts + objective scoring pushes the floor much higher.

**Claude picks the winner, not the user.** The whole point is to save review of N diffs.

---

## When this skill activates

**Any time code is being written, changed, or fixed, activate.** The lists below are *examples*, not exhaustive — use judgment.

**Explicit triggers (examples):**
- `/code-builder` slash command
- "build this / code this / implement X / create a [component|feature|page]"
- "fix this bug / debug / something broke / this isn't working"
- "add a feature to... / change how X works / refactor X"
- "5x this" / "parallel this" — force parallel
- "just fix it" / "quick fix" — force single

**Implicit triggers (examples):**
- Working dir is a git repo AND a coding task is described
- An error, stack trace, or failing log is shared
- Code is pasted with a request for changes
- In a known project repo and a change is requested

**Do NOT activate:**
- Pure research or code reading ("how does X work?", "walk me through this")
- Writing, design, planning, brainstorming, outreach
- Meta tasks ("what are my TODOs?", "summarize this session")

**When uncertain, default to activating.** A single-pass run costs almost nothing; mis-skipping a real dev task is worse.

---

## Announcement (required, every activation)

Before doing anything else, print exactly this one-line banner:

> code-builder activated — [parallel-3 | parallel-5 | single pass | debug-escalation]. [≤15-word reason.]

User can override with "actually, 5x this" or "actually, just fix it" → flip and re-announce.

---

## Workflow

### Step 0 — Session Safety (always runs first)

Before writing any code:

1. Run `git status` — if there are uncommitted changes, **stop and warn the user**. Never silently overwrite or delete uncommitted work. Ask: "These may be from another session. Stash, commit, or work around them?"
2. Run `git stash list` — report any stashes that might contain work from other sessions.
3. If the task touches files modified in the last commit by a different author/session, flag the overlap before proceeding.
4. **Never delete a file or component** that was added in a recent commit unless the current task explicitly requires it. "Cleaning up unused code" is not a valid reason to remove something another session added.

This prevents the "deleted by other session" problem. When in doubt, stash existing work before starting.

### Step 1 — Scope the task

State the task in one line. Identify:
- Files likely to change
- Greenfield (new feature/prototype) vs. modification (bug fix, tweak)
- Design space — multiple valid approaches, or basically fixed?

### Step 2 — Judgment gate

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
- User explicit override → obey
- Not a git repo → force **single** (worktrees require git)
- Live debugging with rapid iteration needed → force **single** (parallel too slow)
- Greenfield prototype from scratch → force **parallel-5**
- Same file/area fixed 3+ times in recent git log → force **debug-escalation** (Step 4c)
- User says "this still doesn't work" / "tried that already" / "same error" → force **debug-escalation**

**Default parallel count is 3.** Escalate to 5 only when the design space is genuinely ambiguous (multiple valid architectures, greenfield). Most real-world tasks need at most 3 perspectives.

**Worked examples:**
- "Add dark mode to the journal editor" → **parallel-3** (new feature, multi-file, but design is constrained)
- "Fix typo in the header" → **single** (1 LOC, 1 file)
- "Refactor share dropdown for per-person edit access" → **parallel-5** (>30 LOC, multiple valid designs)
- "The cron is firing twice — why?" → **single** (debugging)
- "Start a new Next.js prototype" → **parallel-5** (greenfield hard signal)
- "Rename `foo` to `bar` across repo" → **single** (mechanical)
- "This is the 4th time we've fixed the popup close" → **debug-escalation** (fix churn)

### Step 3a — Parallel path

**Prerequisite:** working directory must be a git repo. Run `git rev-parse --git-dir`. If it fails, downgrade to single and re-announce.

1. Spawn **N `Agent` calls in parallel in a single message**, each with:
   - `isolation: "worktree"` (each draft gets its own worktree + branch)
   - `run_in_background: true`
   - `subagent_type: "general-purpose"`
   - The task prompt + a bias hint:

   | Draft | Bias |
   |-------|------|
   | 1 | Simplest possible — fewest lines, no abstractions |
   | 2 | Most idiomatic — match existing repo patterns exactly |
   | 3 | Optimize for readability — clearest naming, smallest functions |
   | 4 | (parallel-5 only) Optimize for correctness / edge cases |
   | 5 | (parallel-5 only) Free choice — go with best instinct |

   - Instruction: "You are one of N parallel drafts. Commit your work on the worktree branch. Report: approach summary (2 lines), files touched, LOC added/removed, commit SHA, edge cases handled."
2. Wait for all to complete. Score survivors if any fail/timeout.

### Step 3b — Single path

Just do the task normally. Skip to Step 6 to log.

### Step 3c — Debug Escalation path

Activates on fix churn. Instead of generating parallel implementations of a misunderstood bug:

1. **Stop and read.** Read the relevant code thoroughly — the full function, its callers, its dependencies. Read the last 3-5 diffs that touched this area (`git log -p -5 -- {file}`). Read error messages, stack traces, console output.

2. **Hypothesize.** Form a single-sentence hypothesis about the ROOT CAUSE (not the symptom):
   ```
   debug-escalation: hypothesis — {one sentence}
   ```
   Print and wait for confirmation. Root cause vs symptom examples:
   - Symptom: "popup doesn't close" / Root cause: "window.close() blocked because opener ref nulled by reload()"
   - Symptom: "API returns 500" / Root cause: "trust proxy not set, Express reads 127.0.0.1, rate limiter blocks"
   - Symptom: "image shows 1x1 pixel" / Root cause: "migration fetched blob URL without auth, got HTML error, saved that as image"

3. **Prove it.** Write a minimal diagnostic (console.log, test case, curl command) that proves/disproves the hypothesis. This is NOT the fix.

4. **Fix (only after proof).** Target the proven root cause. Check git log to never repeat a failed approach.

5. **Verify.** Re-run the diagnostic. Check for side effects.

**3 hypothesis cycles max.** If 3 are wrong: "I've tried 3 root-cause hypotheses and none panned out. Here's what I've ruled out: [list]. I need more context."

### Step 4 — Self-evaluate and pick the winner (parallel only)

**Claude picks. Do NOT ask user to review N diffs.**

Detect project type from package.json, file structure, and CLAUDE.md, then apply the matching rubric column:

| Criterion | Portfolio/UI | API/Backend | Library/SDK | CLI/Tool |
|---|---|---|---|---|
| Correctness | 20 | 25 | 30 | 25 |
| Tests pass | 10 | 20 | 20 | 15 |
| Typecheck clean | 10 | 10 | 15 | 10 |
| Lint clean | 5 | 5 | 5 | 5 |
| Minimal diff | 15 | 10 | 10 | 10 |
| No unnecessary new deps | 5 | 10 | 10 | 10 |
| Reuses existing utilities | 10 | 10 | 5 | 10 |
| Follows repo conventions | 15 | 5 | 5 | 10 |
| Scope containment | 10 | 5 | 0 | 5 |

For Portfolio/UI: visual consistency and convention-following matter more than test coverage.
For libraries: correctness and type safety dominate.

Tests pass: run project's test cmd. Pass = full weight; any fail = 0. No tests → redistribute to Correctness.
Minimal diff: `weight * (min_LOC_across_drafts / this_LOC)`.

**Tiebreakers:** (1) smallest diff, (2) draft 2 (most idiomatic).

Record the full score breakdown for all drafts in the run log — the sync uses this to calibrate.

### Step 5 — Merge validation

Before declaring done:

1. **Gap check.** Re-read the original task. Walk each requirement; confirm the winner covers it. Cherry-pick from rejected drafts for any gaps.
2. **Redundancy check.** Scan for unused imports, dead code, commented-out blocks, debug logs, duplicate helpers.
3. **Language check.** Verify no language confusion — Python idioms in JS, wrong string escaping, wrong iteration patterns. This catches the "Python ate the apostrophe" class of bugs.
4. **Revalidation.** Tests + typecheck + lint one more time on the final diff.
5. **Deployment check.** If the project deploys to Vercel/Netlify/etc., verify the build succeeds locally (`npm run build` or equivalent) before committing.
6. **Merge.** Fast-forward if possible; else `git merge --no-ff`.
7. **Clean up worktrees.** Keep the winner's branch (needed for post-merge-diff signal in the sync).
8. **Report in one line:**
   > Merged draft {N}/{total} (score {X}/100). {≤15-word reason.} {Cherry-picked from draft M | No gaps.} Tests/Types/Lint status.

### Step 6 — Log the run (required, always)

Write `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`:

```md
---
date: {date}
task_slug: {slug}
repo: {repo}
judgment: {single|parallel-3|parallel-5|debug-escalation}
judgment_override: null  # or "single → parallel-3" if user flipped
winner_draft: {N}
winner_sha: {sha}
winner_score: {X}
cherry_picks_from: []
session_safety: {clean|stashed|warned}
debug_cycles: {count, if debug-escalation}
---

## Task (verbatim)
> {original task}

## Judgment
{mode} — {reasoning}.

## Drafts
### Draft 1 — {bias}
- Approach: {2 lines}
- Files: {list} ({LOC})
- Score: {X}/100 (breakdown)
- SHA: {sha}

...

## Cherry-picks
{list or "none"}

## In-session feedback (verbatim)
{any user corrections or overrides}
```

Log **all fields every run** — the sync depends on structured data.

---

## Syncing learnings (weekly + on-demand)

Trigger: weekly cron OR user says "code-builder sync".

### Sync workflow

1. **Determine window.** Read `Last synced:` date below. Read only new runs since then.

2. **Collect data from 5 sources:**
   - **a. Run logs.** Every new `runs/*.md`.
   - **b. Post-merge git diffs** — for each run's `winner_sha`:
     ```
     git log {winner_sha}..HEAD --oneline -- <winner's files>
     git diff {winner_sha}..HEAD -- <winner's files>
     ```
     Reveals what was silently edited after merge — highest-value learning signal.
   - **c. In-session feedback** — captured in run logs.
   - **d. Judgment overrides** — `judgment_override` field in run frontmatter.
   - **e. Cross-repo mining (bounded).** For each active repo:
     ```
     git log --since="<last-sync-date>" --max-count=50 \
       --grep="fix\|revert\|oops\|simplify\|cleanup\|restore"
     ```
     Hard bounds prevent noisy repos from dominating.

3. **Pass 1 — Count patterns.** Signals repeated ≥2 times become candidate learnings.

4. **Pass 2 — Refine existing learnings:**
   - Duplicate → increment citation count
   - Contradicts existing → supersede with date
   - Strengthens existing → update citation count
   - New → add

5. **Pass 3 — Prune.** Hard cap of **30 bullets**. Remove by: oldest, fewest citations, superseded.

6. **Write.** Edit the `## Current learnings` section below. Update `Last synced:`. Commit nothing — this file lives in `~/.claude/skills/`.

7. **Announce:** `code-builder sync complete — added {N}, refined {M}, pruned {P}. Total: {X}/30.`

---

## Current learnings

Last synced: 2026-04-13 (initial backfill — 4 repos + 13 session summaries; 12 bullets)

*If a repo's `CLAUDE.md` contradicts a rule below, the repo rule wins.* This section captures cross-repo patterns; per-repo rules override.

### A. Claude process failures

- **Never call `Skill()` from inside a scheduled-task body.** Circular dispatch re-triggers on each tick, burning rate limit until killed. (1 citation)
- **No hardcoded tokens or secrets in client JS — even for internal tools.** Anything in a `"use client"` module or `NEXT_PUBLIC_` ships to browser. (1 citation)
- **"Done" requires green tests + typecheck, not "looks right."** Declaring completion off a compile-pass alone forces rework 2-3 messages later. (2 citations)
- **Resolve merge conflicts by re-running tests, not by eyeballing which side to keep.** Code was silently lost 3x — data loss is the hardest bug class to trace. (1 citation)
- **Guard nullable KV/API responses before destructuring.** `const { foo } = res` crashes the page when upstream returns null. Render `<EmptyState />` or early-return. Cross-repo x3. (3 citations)
- **Grep for existing helpers before writing a new one.** Duplicate utilities drift and maintenance compounds. (1 citation)

### B. Concrete code-level patterns

- **Validate + trim `process.env.X` at the read-site.** Whitespace/quoting/trailing-newline variance across Vercel/Render/local causes silent misconfig. Cross-repo x2. (4 citations)
- **Floating UI inside a scroll/overflow parent needs `position: fixed` + a portal — not `position: absolute`.** Absolute clips inside gallery tiles, mobile sheets, modal bodies. Cross-repo x2. (1 citation)
- **Rules of Hooks, full form: no conditional calls, no hooks inside callbacks/effects, no `return` before hooks list is complete.** React's error surfaces one render later. Cross-repo x2. (pattern mining)
- **`useEffect` that subscribes, starts a timer, or sets state must return a cleanup function.** Missing cleanup is the #1 correction category. x4. (pattern mining)
- **Unscale `getBoundingClientRect()` values when an ancestor has a CSS transform.** Measurements return in transformed frame; crop overlays compute wrong origin. (2 citations)
- **Save editor selection before opening any DOM-mutating modal; restore on close.** Re-opening a toolbar action jumps to wrong line or loses caret. (2 citations)

### C. Session & workflow patterns (new section from build-log analysis)

- **Check for uncommitted changes from other sessions before starting work.** Lost components and restored commits indicate concurrent session conflicts. (2 citations: "restore: re-add BugReportButton", "restore: re-apply bug-fixer types")
- **When the same area has 3+ sequential fix commits, stop guessing and root-cause.** iOS shortcut saga: 10+ versions trying variations without understanding the underlying plist/body format issue. (1 citation: v3→v13 shortcut iterations)
- **Verify URLs before including in content.** Fabricated URLs were committed and had to be replaced. (1 citation: "Replace fabricated curated URLs with verified Reddit posts")
- **After writing content, check claims match shipped features.** Descriptions of planned-but-not-shipped features were committed. (1 citation: "rewrite copy to match what actually shipped")

## Meta notes

- `isolation: "worktree"` fails when cwd is not a git repo. Auto-downgrade to single pass.
- Deferred: holdout-commit eval, N=5 precision/recall eval, citation-validity lint, token-budget cap, stale-rule audit, cross-skill conflict scan.
