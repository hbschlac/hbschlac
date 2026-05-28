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

> **code-builder activated** — [parallel, 5 drafts | single pass]. [15-word reason.]

Examples:
- `code-builder activated — parallel, 5 drafts. New feature; multiple architectures viable.`
- `code-builder activated — single pass. One-line fix; parallel would be noise.`
- `code-builder activated — single pass. Not a git repo; worktree isolation unavailable.`

Hannah can override with "actually, 5x this" or "actually, just fix it" — flip and re-announce.

---

## Workflow

### Step 1 — Detect project type

Before scoping the task, detect the project's language and toolchain. This determines test/lint/typecheck commands used in scoring.

```bash
# Run these checks (stop at first match)
if [ -f "package.json" ]; then
  # Node.js / TypeScript project
  TEST_CMD=$(node -e "try{console.log(JSON.parse(require('fs').readFileSync('package.json')).scripts.test||'')}catch(e){}" 2>/dev/null)
  LINT_CMD=$(node -e "try{const s=JSON.parse(require('fs').readFileSync('package.json')).scripts;console.log(s.lint||s['lint:fix']||'')}catch(e){}" 2>/dev/null)
  TYPECHECK_CMD="npx tsc --noEmit 2>/dev/null"
  [ -f "tsconfig.json" ] && LANG="TypeScript" || LANG="JavaScript"
elif [ -f "Cargo.toml" ]; then
  TEST_CMD="cargo test" && LINT_CMD="cargo clippy" && TYPECHECK_CMD="cargo check" && LANG="Rust"
elif [ -f "go.mod" ]; then
  TEST_CMD="go test ./..." && LINT_CMD="golangci-lint run 2>/dev/null" && TYPECHECK_CMD="go vet ./..." && LANG="Go"
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
  TEST_CMD="pytest 2>/dev/null || python -m unittest discover 2>/dev/null"
  LINT_CMD="ruff check . 2>/dev/null || flake8 . 2>/dev/null"
  TYPECHECK_CMD="mypy . 2>/dev/null || pyright 2>/dev/null"
  LANG="Python"
elif [ -f "Gemfile" ]; then
  TEST_CMD="bundle exec rspec 2>/dev/null || bundle exec rake test 2>/dev/null" && LANG="Ruby"
elif [ -f "pom.xml" ] || [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
  TEST_CMD="./gradlew test 2>/dev/null || mvn test 2>/dev/null" && LANG="Java/Kotlin"
fi
```

Store these for Step 5. If no toolchain detected, set `LANG="unknown"` and redistribute test/typecheck/lint points to Correctness in the rubric.

Also check for repo-level config:
```bash
[ -f ".claude/code-builder.json" ] && cat .claude/code-builder.json
```

If present, override defaults (see §Repo-level config below).

### Step 2 — Scope the task

State the task in one line. Identify:
- Files likely to change
- Greenfield (new feature/prototype) vs. modification (bug fix, tweak)
- Estimated LOC
- Design space — multiple valid approaches, or basically fixed?

### Step 3 — Judgment gate

**Default is single.** Escalate to parallel only when **>=2 parallel signals fire** OR **any hard signal fires.**

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
- Hannah explicit override — obey
- Not a git repo — force **single** (worktrees require git)
- Live debugging with rapid iteration needed — force **single** (parallel too slow)
- Greenfield prototype from scratch — force **parallel**

**Task-size guard rails:**
- Estimated <5 LOC — force **single**, skip scoring in Step 5, go straight to Step 7 (fast path)
- Estimated >300 LOC — warn Hannah: "Large task (~{N} LOC). Parallel drafts may diverge significantly. Recommend splitting into smaller chunks, or proceed with parallel? Default: parallel."

**Worked examples:**
- "Add dark mode to the journal editor" — **parallel** (new feature, multi-file, multiple design choices)
- "Fix typo in the header" — **single** (1 LOC, 1 file)
- "Refactor share dropdown for per-person edit access" — **parallel** (>30 LOC, design space)
- "The cron is firing twice — why?" — **single** (debugging)
- "Start a new Next.js prototype" — **parallel** (greenfield hard signal)
- "Rename `foo` to `bar` across repo" — **single** (mechanical)
- "Build a recommendation engine for related posts" — **parallel** (design space)

### Step 4a — Parallel path (N=5)

**MANDATORY prerequisite — enforce before ANY agent spawn:**

```bash
git rev-parse --git-dir 2>/dev/null
```

If this fails: **stop immediately**. Downgrade to single pass. Re-announce:
> **code-builder** — downgraded to single pass. Worktree isolation requires a git repo; currently at `{cwd}`. Restart from the project directory to enable parallel drafts.

Proceed with Step 4b.

If it succeeds:

1. Spawn **5 `Agent` calls in parallel in a single message**, each with:
   - `isolation: "worktree"` (each draft gets its own worktree + branch — no file collisions)
   - `run_in_background: true`
   - `subagent_type: "general-purpose"`
   - The task prompt + project context (detected language, test command, existing patterns) + a bias hint:
     - Draft 1: *simplest possible — fewest lines, no abstractions*
     - Draft 2: *most idiomatic to this repo — match existing patterns exactly*
     - Draft 3: *optimize for readability — clearest naming, smallest functions*
     - Draft 4: *optimize for performance / correctness on edge cases*
     - Draft 5: *your choice — go with your best instinct*
   - Include detected commands: "Test: `{TEST_CMD}`, Lint: `{LINT_CMD}`, Typecheck: `{TYPECHECK_CMD}`. Run these before reporting."
   - Instruction: "You are one of 5 parallel drafts. Commit your work on the worktree branch with message format: `{task summary} — {approach}`. Report: approach summary (2 lines), files touched, LOC added/removed, commit SHA, edge cases handled, test/typecheck/lint results."

2. Wait for all 5 to complete (timeout: 10 minutes per draft).

3. **Quorum check:**
   - 3+ drafts completed — proceed to Step 5 with survivors
   - 1-2 drafts completed — warn Hannah: "Only {N}/5 drafts completed. Scoring with limited sample. Consider re-running or proceeding with best available."
   - 0 drafts completed — fall back to single pass. Log failure reason. Re-announce: `code-builder — all 5 drafts failed. Falling back to single pass. Reason: {reason}.`

### Step 4b — Single path

Just do the task normally. If the judgment gate fast-pathed (<5 LOC), skip scoring entirely — go straight to Step 7.

### Step 5 — Self-evaluate and pick the winner (parallel only)

**Claude picks. Do NOT ask Hannah to review 5 diffs.**

Score each draft out of **100 points**:

| Criterion | Weight | Measurement |
|---|---|---|
| Correctness | 25 | Walk each requirement in the task prompt; deduct for misses. |
| Tests pass | 15 | Run detected `TEST_CMD` on each worktree. Pass = 15; any fail = 0. No tests detected — redistribute to Correctness (total 40). |
| Typecheck clean | 10 | Run detected `TYPECHECK_CMD`. 0 errors = 10. No typecheck available — redistribute to Correctness. |
| Lint clean | 5 | Run detected `LINT_CMD`. 0 warnings = 5. No lint available — redistribute to Correctness. |
| Minimal diff | 10 | `10 * (min_LOC_across_drafts / this_LOC)`. |
| No unnecessary new deps | 10 | 0 new = 10; each new = -3 unless genuinely required. |
| Reuses existing utilities | 10 | Did the draft grep for and reuse existing helpers? |
| Follows repo conventions | 10 | Naming, file structure, import style vs. neighboring files. |
| Scope containment | 5 | Deduct if unrelated files were touched. |

**Score redistribution for unknown languages:** If `LANG="unknown"`, redistribute Tests (15) + Typecheck (10) + Lint (5) to Correctness (total 55). Mark in run log: `scoring_note: "no toolchain detected; 55pt correctness"`.

**Tiebreakers:** (1) smallest diff, (2) draft 2 (most idiomatic to repo).

**Compute success metric:** Record `winner_score`, `avg_score` (across all completed drafts), `min_score`, `max_score`, and `lift` = `winner_score - avg_score`. This feeds the sync's cost-benefit analysis.

Record the full score breakdown for all drafts in the run log — the sync uses this to calibrate weights.

### Step 6 — Merge validation (prevent loss + redundancy)

Before declaring done:

1. **Gap check.** Re-read the original task. Walk each requirement; confirm the winner's diff covers it. For any gap, check the rejected drafts — if any of them solved the gap:
   - `git cherry-pick --no-commit {SHA}` (stage without committing)
   - Run tests + typecheck immediately
   - If tests fail: `git cherry-pick --abort` and code the gap fresh
   - If tests pass: commit with message `Cherry-pick gap fix from draft {N}: {description}`
   - Log what was cherry-picked and why
2. **Redundancy check.** Scan the winner's diff for: unused imports, dead code, commented-out blocks, debug logs, duplicate helpers shadowing existing utilities. Strip any found.
3. **Rerun validation.** Tests + typecheck + lint one more time on the final diff.
4. **Merge.** Merge the winner's branch into the working branch (fast-forward if possible; else `git merge --no-ff`).
5. **Clean up worktrees.** `git worktree remove` all 5. Delete losing branches. **Keep the winner's branch** (needed for post-merge-diff signal in the sync).
6. **Report in one line:**
   > Merged draft {N}/5 (score {X}/100, +{lift} vs avg). {15-word reason it beat the others.} {Cherry-picked {Y} from draft M | No gaps.} Tests: {pass/fail} Types: {pass/fail} Lint: {pass/fail}.

If Hannah replies "actually use draft 3" or "the tests still fail" — re-pick or debug, and log the override in the run file.

### Step 7 — Log the run (required, always)

Write `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`:

```md
---
date: 2026-04-13
task_slug: dark-mode-journal-editor
repo: 662-calmar-portfolio
lang: TypeScript
test_cmd: "npm test"
judgment: parallel  # or "single" or "single-fast" (for <5 LOC)
judgment_override: null  # or "single -> parallel" if Hannah flipped it
winner_draft: 3
winner_sha: abc1234
winner_score: 82
avg_score: 74
min_score: 65
max_score: 82
lift: 8
drafts_completed: 5  # out of 5 attempted
cherry_picks_from: [1]  # draft indices cherry-picked from
scoring_note: null  # e.g. "no toolchain detected; 55pt correctness"
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
- Test/Type/Lint: pass/pass/pass
- SHA: `abc1111`

### Draft 2 — most idiomatic
...

### Draft 3 — readability (WINNER)
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

**Single-pass runs:** Log with `judgment: single` (or `single-fast` for <5 LOC). Record only Draft 1. Set `winner_draft: 1`, `avg_score: null`, `lift: null`. For fast-path runs, set `winner_score: null`.

---

## Repo-level config (optional)

Place `.claude/code-builder.json` in any repo to override defaults:

```json
{
  "min_loc_for_parallel": 50,
  "max_loc_warning": 500,
  "auto_parallel_on_new_files": true,
  "test_cmd": "npm run test:integration",
  "lint_cmd": "npm run lint",
  "typecheck_cmd": "npx tsc --noEmit",
  "skip_scoring_below_loc": 5
}
```

When present, these override the auto-detected values from Step 1 and the default thresholds in Step 3.

---

## Syncing learnings (Sunday 6pm + on-demand)

Scheduled cron: `0 18 * * 0`. Also trigger on-demand: Hannah says "code-builder sync" or runs `/code-builder sync`.

**Self-sufficient** — pulls data the skill itself writes. No dependency on any manual journaling.

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
   - **e. Cross-repo mining (bounded).** For each active personal repo:
     ```
     cd <repo> && git fetch --all && \
     git log --since="<last-sync-date>" --max-count=50 \
       --author="Hannah Schlacter" \
       --grep="fix\|revert\|oops\|simplify\|cleanup"
     ```
   - **f. Success metrics analysis.** Aggregate `lift` values across parallel runs. Report: "Avg lift: {X} points. Parallel was worth it in {Y}/{Z} runs (lift > 5)."

3. **Pass 1 — Count patterns.** Any signal repeated >=2 times across runs becomes a candidate learning.

4. **Pass 2 — Refine the existing learnings, don't blindly append:**
   - Duplicate of existing — increment citation count only
   - Contradicts existing — supersede; note reversal with date
   - Strengthens existing — update citation count + date
   - New — add

5. **Pass 3 — Prune.** Enforce **hard cap of 30 bullets** in `## Current learnings`. If over: remove by priority (oldest, fewest citations, superseded).

6. **Write.** Use `Edit` to update the `## Current learnings` section below. Update `Last synced:` to today. Commit nothing — this file lives in `~/.claude/skills/`, not in a repo.

7. **Announce:** `code-builder sync complete — added {N}, refined {M}, pruned {P}. Total learnings: {X}/30. Avg parallel lift: {Y} points over {Z} runs.`

---

## Current learnings

Last synced: 2026-04-13 (initial backfill — 4 repos + 13 session summaries; 12 bullets)

*If a repo's `CLAUDE.md` contradicts a rule below, the repo rule wins.* This section captures cross-repo patterns; per-repo rules override.

### A. Claude process failures

- **Never call `Skill()` from inside a scheduled-task body.** Circular dispatch re-triggers on each tick, burning rate limit until the task is killed. *Does not apply to* on-demand skills invoked from a user turn. (1 citation: `summary:scheduled-tasks-bug-fixer-fix.md`)
- **No hardcoded tokens or secrets in client JS — even for internal tools.** Anything imported into a `"use client"` module or prefixed `NEXT_PUBLIC_` ships to the browser; credential rotation + disclosure is the cost. (1 citation: `summary:calmar-upload-security.md`)
- **"Done" requires green tests + typecheck, not "looks right."** Declaring completion off a compile-pass alone forces a rework loop when the real failure surfaces 2-3 messages later. (2 citations: `summary:calmar-jose-notes-recovery.md`, `summary:ramp-resume.md`)
- **Resolve merge conflicts by re-running tests, not by eyeballing which side to keep.** Code was silently lost 3x in calmar — data loss is the hardest class of bug to trace. (1 citation: calmar `ff5ac3a`)
- **Guard nullable KV/API responses before destructuring.** Render `<EmptyState />` or early-return when the upstream can return `null`/`undefined`; `const { foo } = res` crashes the page. Cross-repo x3. (3 citations: calmar `cae05a6`, schlacter.me `26e3345`, muse `f0eeb07`)
- **Grep for existing helpers before writing a new one.** Calmar accumulated 3x duplicated date-formatting utilities. (1 citation: calmar pattern mining)

### B. Concrete code-level patterns

- **Validate + trim `process.env.X` at the read-site.** Whitespace, quoting, and trailing-newline variance across Vercel/Render/local cause silent misconfig. Cross-repo x2. (4 citations: `30b8853`, `ac6df91`, `3cb8289`, `818d178`)
- **Floating UI inside a scroll/overflow parent needs `position: fixed` + a portal — not `position: absolute`.** Cross-repo x2. (1 citation: `summary:calmar-notification-share-redesign.md`)
- **Rules of Hooks, full form: no conditional hook calls, no hooks inside callbacks/effects, no `return` before the hooks list is complete.** Cross-repo x2. (Agent mining)
- **`useEffect` that subscribes, starts a timer, or sets state must return a cleanup function.** Missing cleanup is the #1 correction in calmar. x4. (Agent mining)
- **Unscale `getBoundingClientRect()` values when an ancestor has a CSS transform.** Measurements return in the transformed frame. (2 citations: calmar `1e1f242`, `summary:calmar-bug-crop-zoom-and-numbered-list.md`)
- **Save editor selection before opening any DOM-mutating modal; restore on close.** (2 citations: calmar `21b2d7e`, `summary:calmar-jose-notes-recovery.md`)

### C. Deployment patterns (added 2026-05-28)

- **Set `trust proxy` in Express when behind Vercel/Render/Cloudflare.** `req.ip` and `req.protocol` return wrong values without it; OAuth redirects break. (2 citations: muse `0c92c13`, `3a83f67`)
- **Trim Google OAuth env vars at read-site.** Copy-pasting from GCP console often includes trailing whitespace that silently breaks token exchange. (1 citation: muse `3f11f7e`)
- **Point OAuth redirect URIs at the production domain, not localhost.** Different local vs deployed URIs cause redirect mismatch. Always configure both in the OAuth provider console. (1 citation: muse `68d29d4`)
- **Mount error-handler middleware LAST in Express serverless entries.** Vercel serverless entry points often have different middleware ordering than the dev server. (1 citation: muse `d01750d`)

## Meta notes

- The `isolation: "worktree"` Agent parameter fails when Claude's cwd is not a git repo. Documented and enforced as a mandatory gate in Step 4a.
- **Deferred to later syncs (not in initial backfill):** holdout-commit eval, N=5 live-task precision/recall eval, citation-validity pre-commit lint, token-budget hard cap enforcement, stale-rule quarterly audit, cross-skill conflict scan. Revisit after >=3 real parallel runs accumulate.
- **Source pinning:** initial backfill drew from session summaries (backfill-only source, not recurring). Weekly sync pulls from run logs + post-merge diffs + cross-repo git mining.
- **2026-05-28 audit additions:** Added Section C (Deployment patterns) with 4 learnings from muse-shopping auth debugging sessions. Added language detection (Step 1), task-size guard rails (Step 3), quorum check (Step 4a), score redistribution for unknown languages (Step 5), success metrics (Step 5/7), cherry-pick rollback (Step 6), repo-level config, and clarified single-pass logging format (Step 7).

## Changelog

- **2026-05-28 audit-driven improvements** — Added: Step 1 (project type detection), task-size guard rails in Step 3, mandatory git prerequisite enforcement in Step 4a, quorum/retry strategy in Step 4a, language-aware scoring redistribution in Step 5, success metrics (lift calculation) in Step 5/7, cherry-pick rollback strategy in Step 6, repo-level config (.claude/code-builder.json), Section C learnings (deployment patterns), clarified single-pass logging format.
- **2026-04-13 backfill sanity test** — Populated A + B + sync sources. 12 bullets from 4 repos + 13 session summaries.
