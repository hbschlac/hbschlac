---

name: code-builder
description: >
  Raises the floor of code quality by generating parallel implementations
  of the same dev task, self-scoring them against a measurable rubric, and
  merging the winner. Auto-activates whenever Hannah is writing, changing,
  or fixing code — OR iterating on content/copy within a code project.
  Claude exercises judgment to decide parallel vs single vs content vs
  rapid-iteration mode; not every task warrants full parallel. Announces
  activation on every run so Hannah knows the skill is active. Works in
  local terminals AND Claude Code web sessions (worktree isolation when
  available, sequential drafts as fallback). The trigger lists below are
  illustrative, not exhaustive — use judgment to recognize work from context.

---

# code-builder

Raises the floor of Claude's dev output by running **parallel implementations**, **self-scoring them against a measurable rubric**, and merging the winner. The bet: if Claude lands good code ~80% of the time, single-pass output is suboptimal 1-in-5 tasks. Multiple drafts + objective scoring pushes the floor much higher.

**Claude picks the winner, not Hannah.** The whole point is to save Hannah from reviewing diffs.

---

## When this skill activates

**Any time Hannah is writing, changing, or fixing code OR iterating on content/copy within a code project, activate.** The lists below are *examples*, not a complete enumeration — use judgment.

**Explicit triggers (examples):**
- `/code-builder` slash command
- "build this / code this / implement X / create a [component|feature|page]"
- "fix this bug / debug / something broke / this isn't working / X just crashed"
- "add a feature to... / change how X works / refactor X"
- "write me a [function|class|module]"
- "make a prototype for X"
- "5x this" / "parallel this" — force parallel
- "just fix it" / "quick fix" — force single
- "change the copy to..." / "update the text..." / "swap the photo..."

**Implicit triggers (examples):**
- Working dir is a git repo AND Hannah describes a coding task
- Hannah shares an error, stack trace, or failing log
- Hannah pastes code and asks about/for a change
- Hannah is in a known project repo and asks for a change
- Hannah says "something broke" / "this page is broken" / "the test is failing"
- Hannah says "I'm starting a new [prototype|app|project]"
- Hannah is editing JSX/HTML content strings, copy, or static data within code files

**Do NOT activate:**
- Pure research or code reading ("how does X work?", "walk me through this")
- Planning or brainstorming not tied to a specific code change
- Meta tasks ("what are my TODOs?", "summarize this session")
- Writing prose outside of code files (emails, docs, messages)

**When uncertain, default to activating.** A single-pass run costs almost nothing; mis-skipping a real task is worse.

---

## Announcement (required, every activation)

Before doing anything else, print exactly this one-line banner:

> 🔧 **code-builder activated** — [mode]. [≤15-word reason.]

Modes: `parallel, 5 drafts` | `parallel, 3 sequential drafts` | `single pass` | `content, 2 variants` | `rapid iteration`

Examples:
- `🔧 code-builder activated — parallel, 5 drafts. New feature; multiple architectures viable.`
- `🔧 code-builder activated — parallel, 3 sequential drafts. Web session; worktrees unavailable.`
- `🔧 code-builder activated — single pass. One-line fix; parallel would be noise.`
- `🔧 code-builder activated — content, 2 variants. Copy change in JSX; tone matters.`
- `🔧 code-builder activated — rapid iteration. 4th consecutive edit to same component this session.`

Hannah can override with "actually, 5x this" or "actually, just fix it" → flip and re-announce.

---

## Staleness check (before every activation)

Read the `Last synced:` date in `## Current learnings` below. If it is **>14 days ago**, print after the banner:

> ⚠️ Learnings last synced {N} days ago. Say "code-builder sync" to refresh.

---

## Workflow

### Step 1 — (No read step)

Learnings are embedded in the `## Current learnings` section at the bottom of this file and already loaded with the skill description. Proceed straight to Step 2.

### Step 2 — Scope the task

State the task in one line. Identify:
- Files likely to change
- Greenfield (new feature/prototype) vs. modification (bug fix, tweak)
- Design space — multiple valid approaches, or basically fixed?
- **Task type**: code (logic, structure, behavior) vs. content (copy, data, assets within code files) vs. mixed

### Step 3 — Judgment gate

Determine the mode: **parallel** | **single** | **content** | **rapid-iteration**

#### 3a. Rapid-iteration check (first)

If **all** of these are true, enter rapid-iteration mode:
- ≥3 changes to the same file or component in this session
- Each change is ≤10 LOC
- Changes are content/copy/styling, not structural logic

Rapid-iteration mode: apply changes immediately, skip scoring. Accumulate changes. Run a single quality check when Hannah says "done" or switches to a different file/task. Log one aggregate entry.

#### 3b. Content check (second)

If the task is primarily content — copy changes, static data updates, photo/asset swaps, layout tweaks within existing code structure — enter content mode.

Content mode: generate **2 variants** (concise vs. descriptive, or option A vs. option B). Score on content rubric (see Step 5b). Pick the winner. One commit.

#### 3c. Code judgment (parallel vs. single)

**Default is single.** Escalate to parallel only when **≥2 parallel signals fire** OR **any hard signal fires.**

| Gate | Parallel threshold | Single threshold |
|---|---|---|
| **LOC estimate** | >30 lines changed | <10 lines |
| **Files touched** | ≥2 files (including new files) | Exactly 1 existing file |
| **Design space** | Multiple valid architectures | One obviously correct path |
| **Novelty** | New pattern in this repo | Variation of existing pattern |
| **Risk** | Touches critical path (auth, checkout, data layer) | Contained to a leaf component |
| **Task type** | Feature / refactor / greenfield | Targeted bug fix with known root cause |
| **Phrasing** | Open-ended ("build X", "make Y better") | Specific ("change line 42 to...") |
| **Mixed code+content** | Changes both logic and content | Content-only or logic-only |

**Hard signals (any one decides):**
- Hannah explicit override → obey
- Not a git repo → force **single** (worktrees require git)
- Live debugging with rapid iteration needed → force **single** (parallel too slow)
- Greenfield prototype from scratch → force **parallel**
- External platform integration with undocumented behavior (iOS Shortcuts, OAuth, PWA) → force **parallel**
- Data migration or storage layer change → force **parallel**

### Step 4a — Parallel path: worktree mode (N=5)

**Prerequisite: local git repo with worktree support.**

1. Confirm working dir is a git repo: `git rev-parse --git-dir`. If it fails, fall through to Step 4b.
2. Test worktree support: `git worktree list`. If it fails or the environment doesn't support Agent `isolation: "worktree"`, fall through to Step 4b.
3. Spawn **5 `Agent` calls in parallel in a single message**, each with:
   - `isolation: "worktree"`
   - `run_in_background: true`
   - `subagent_type: "general-purpose"`
   - The task prompt + a bias hint for differentiation:
     - Draft 1: *simplest possible — fewest lines, no abstractions*
     - Draft 2: *most idiomatic to this repo — match existing patterns exactly*
     - Draft 3: *optimize for readability — clearest naming, smallest functions*
     - Draft 4: *optimize for performance / correctness on edge cases*
     - Draft 5: *your choice — go with your best instinct*
   - Instruction: "You are one of 5 parallel drafts. Commit your work on the worktree branch. Report: approach summary (2 lines), files touched, LOC added/removed, commit SHA, any edge cases you handled."
4. Wait for all 5 to complete. If any fail/timeout, score the survivors.
5. Proceed to Step 5a.

### Step 4b — Parallel path: sequential-draft mode (N=3)

**Fallback for web sessions, non-git environments, or when worktrees aren't available.**

1. Read the current state of all files that will change.
2. Generate **Draft 1** (simplest approach). Record the full diff mentally. Do NOT apply yet.
3. Generate **Draft 2** (most idiomatic to repo). Record the full diff. Do NOT apply.
4. Generate **Draft 3** (best instinct). Record the full diff. Do NOT apply.
5. Score all 3 using the rubric in Step 5a (adapted: skip test/typecheck/lint execution since we can't run them in parallel; score based on static analysis).
6. Apply ONLY the winning draft.
7. Proceed to Step 6 (build gate).

### Step 4c — Single path

Just do the task normally. Proceed to Step 6 (build gate).

### Step 4d — Content path (2 variants)

1. Identify the content being changed (copy text, data values, asset references).
2. Generate **Variant A** — concise, direct, minimal words.
3. Generate **Variant B** — descriptive, with more context/detail.
4. Score both using the content rubric in Step 5b.
5. Apply the winner. If the scores are within 5 points, apply whichever is shorter.
6. Proceed to Step 6 (build gate).

### Step 4e — Rapid-iteration path

1. Apply the change immediately.
2. Track: file changed, what changed, change number in this session.
3. When the user switches files, says "done," or reaches change #10: run a quality check on all accumulated changes (scan for typos, broken links/references, consistency with surrounding content, stale data). Report any issues found.
4. Log one aggregate entry (Step 7).

---

## Step 5a — Self-evaluate: code rubric (parallel only)

**Claude picks. Do NOT ask Hannah to review diffs.**

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

Record the full score breakdown for all drafts in the run log.

## Step 5b — Self-evaluate: content rubric (content mode only)

Score each variant out of **100 points**:

| Criterion | Weight | Measurement |
|---|---|---|
| Accuracy | 25 | All facts, names, dates, prices are correct. |
| Tone consistency | 20 | Matches the voice/style of surrounding content on the same page. |
| Completeness | 20 | All information the user requested is present. |
| Conciseness | 15 | No filler words, no redundancy, respects mobile screen space. |
| Mobile readability | 10 | Lines aren't too long; no elements that will wrap awkwardly on small screens. |
| Link/reference correctness | 10 | All URLs, image paths, cross-references resolve. |

---

## Step 6 — Pre-commit build gate (ALL paths)

Before committing, run the project's build/validation command:

1. **Detect build command** (in priority order):
   - `package.json` → `npm run build` or `next build`
   - `pyproject.toml` / `setup.py` → project's test/build cmd
   - `Makefile` → `make build` or `make check`
   - No build system → skip this step

2. **Run it.** If it fails:
   - Read the error. Fix the issue. Re-run.
   - If the fix is non-trivial (>5 LOC), re-score the draft that was selected.
   - If the fix requires reverting to a different draft, do so.
   - Log the build failure in the run file.

3. **Also run** (if available): typecheck (`tsc --noEmit`), lint (project's lint cmd).

Only proceed to commit after build + typecheck + lint all pass.

---

## Step 6b — Merge validation (parallel path only — prevent loss + redundancy)

Before declaring done:

1. **Gap check.** Re-read the original task. Walk each requirement; confirm the winner's diff covers it. For any gap, check rejected drafts — if any solved the gap, cherry-pick just that change. If none did, write it fresh.
2. **Redundancy check.** Scan the winner's diff for: unused imports, dead code, commented-out blocks, debug logs, duplicate helpers shadowing existing utilities. Strip any found.
3. **Rerun validation.** Tests + typecheck + lint one more time on the final diff.
4. **Merge.** Merge the winner's branch into the working branch (fast-forward if possible; else `git merge --no-ff`).
5. **Clean up worktrees.** `git worktree remove` all. Delete losing branches. **Keep the winner's branch.**
6. **Report in one line:**
   > ✓ Merged draft {N}/{total} (score {X}/100). {≤15-word reason.} {Cherry-picked {Y} from draft M | No gaps.} Tests ✓ Types ✓ Lint ✓.

---

## Step 6c — Visual verification (UI-facing changes only)

If the change affects anything the user will see (components, pages, styles, content):

1. **If `/run` or `/verify` skills are available:** Use them to render the page and confirm the change looks correct.
2. **If a dev server is running:** Check the page in a browser.
3. **If neither is available:** Explicitly state: "Visual verification not possible in this environment — recommend checking [page/component] in browser."

Do NOT silently skip this. Either verify or flag that you couldn't.

---

## Step 7 — Log the run (required, always)

Write `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`:

```md
---
date: 2026-05-31
task_slug: dark-mode-journal-editor
repo: hannah-portfolio
mode: parallel-worktree  # or "parallel-sequential" | "single" | "content" | "rapid-iteration"
environment: web  # or "local"
judgment_override: null  # or "single → parallel" if Hannah flipped it
winner_draft: 3
winner_sha: abc1234
winner_score: 82
cherry_picks_from: [1]
build_gate_passed: true  # false if build failed before fix
---

## Task (verbatim)
> add a dark mode toggle to the journal editor

## Judgment
Parallel — new feature, multi-file, multiple design choices.
Environment: web session (sequential-draft fallback).

## Drafts
...

## Build gate
✓ `next build` passed on first attempt.

## Visual verification
✓ Checked via dev server — toggle works, no flash on load.
# or: ⚠️ Not verified — no browser access in this environment.

## In-session feedback from Hannah (verbatim)
...
```

**For rapid-iteration mode**, log one aggregate entry:
```md
---
date: 2026-05-26
task_slug: jamie-bach-copy-iterations
repo: hannah-portfolio
mode: rapid-iteration
environment: web
changes_count: 12
files_touched: [app/jamie-bach-2026/page.tsx, app/jamie-bach-2026/data.ts]
end_of-session_check: passed  # or "found 2 issues: ..."
---

## Changes (summary)
12 copy/layout changes to Jamie's bach page over 45 minutes.
Key changes: updated venue photos, cost math corrections, itinerary copy tweaks.

## End-of-session quality check
- ✓ No broken image references
- ✓ All prices sum correctly
- ✓ No TypeScript errors
- ⚠️ Found: "pastries" still referenced in one tooltip (fixed)
```

Log **all fields every run** — the sync depends on them being structured.

---

## Syncing learnings (Sunday 6pm + on-demand)

Scheduled cron: `0 18 * * 0`. Also trigger on-demand: Hannah says anything containing "sync" + "code-builder" or "learnings" or "update learnings" or runs `/code-builder sync`.

### Sync workflow

1. **Determine window.** Read the `Last synced:` date below. If "never", read all `runs/*.md`. Otherwise read only runs with date > last sync.

2. **Collect data from 5 sources:**
   - **a. Run logs.** Read every new `runs/*.md`.
   - **b. Post-merge git diffs** — for each run's `winner_sha`, in that repo:
     ```
     git log {winner_sha}..HEAD --oneline -- <winner's files>
     git diff {winner_sha}..HEAD -- <winner's files>
     ```
     Reveals what Hannah silently edited after merge.
   - **c. In-session feedback** — already captured in run logs.
   - **d. Judgment overrides** — `judgment_override` field in run frontmatter.
   - **e. Cross-repo mining (bounded).** For each active personal repo:
     ```
     cd <repo> && git fetch --all && \
     git log --since="<last-sync-date>" --max-count=50 \
       --author="Hannah Schlacter" \
       --grep="fix\|revert\|oops\|simplify\|cleanup"
     ```
     Hard bounds: `--max-count=50`, author filter, `--since` window.

3. **Pass 1 — Count patterns.** Any signal repeated ≥2 times across runs becomes a candidate learning.

4. **Pass 2 — Refine the existing learnings, don't blindly append:**
   - Duplicate of existing → increment citation count only
   - Contradicts existing → supersede; note reversal with date
   - Strengthens existing → update citation count + date
   - New → add

5. **Pass 3 — Prune.** Enforce **hard cap of 30 bullets** in `## Current learnings`. If over: remove by priority (oldest, fewest citations, superseded).

6. **Write.** Use `Edit` to update the `## Current learnings` section below. Update `Last synced:` to today.

7. **Announce:** `🔧 code-builder sync complete — added {N}, refined {M}, pruned {P}. Total learnings: {X}/30.`

---

## Current learnings

Last synced: 2026-05-31 (v2 audit backfill — prior 12 rules carried forward + 12 new from Mar-May sessions)

*If a repo's `CLAUDE.md` contradicts a rule below, the repo rule wins.*

### §A. Claude process failures

1. **Never call `Skill()` from inside a scheduled-task body.** Circular dispatch re-triggers on each tick. *Does not apply to* on-demand skills invoked from a user turn. (1 citation)
2. **No hardcoded tokens or secrets in client JS — even for internal tools.** Anything in a `"use client"` module or prefixed `NEXT_PUBLIC_` ships to the browser. (1 citation)
3. **"Done" requires green build + typecheck, not "looks right."** Declaring completion off a compile-pass alone forces a rework loop. (3 citations: calmar, ramp, lodging-TS-build 2026-05-26)
4. **Resolve merge conflicts by re-running tests, not by eyeballing.** Code was silently lost 3× in calmar. (1 citation)
5. **Guard nullable KV/API responses before destructuring.** Render `<EmptyState />` or early-return when upstream can return `null`/`undefined`. Cross-repo ×3. (3 citations)
6. **Grep for existing helpers before writing a new one.** Calmar accumulated 3× duplicated date-formatting utilities. (1 citation)
7. **Run the project's build command before pushing — not just typecheck.** `next build` catches SSR-only errors, missing env vars, and import-time failures that `tsc` misses. (1 citation: lodging-TS-build 2026-05-26)
8. **In web sessions, test worktree support before spawning 5 agents.** Fail fast and fall back to sequential drafts rather than wasting 5 agent spawns that all fail. (1 citation: v2 audit)

### §B. Concrete code-level patterns

9. **Validate + trim `process.env.X` at the read-site.** Whitespace, quoting, and trailing-newline variance across Vercel/Render/local cause silent misconfig. Cross-repo ×2. (4 citations)
10. **Floating UI inside a scroll/overflow parent needs `position: fixed` + a portal — not `position: absolute`.** Clips inside gallery tiles, mobile bottom sheets, and modal bodies. Cross-repo ×2. (1 citation)
11. **Rules of Hooks, full form: no conditional hook calls, no hooks inside callbacks/effects, no `return` before the hooks list is complete.** Cross-repo ×2. (1 citation)
12. **`useEffect` that subscribes, starts a timer, or sets state must return a cleanup function.** Missing cleanup is the #1 correction category in calmar. ×4. (1 citation)
13. **Unscale `getBoundingClientRect()` values when an ancestor has a CSS transform.** Measurements return in the transformed frame. (2 citations)
14. **Save editor selection before opening any DOM-mutating modal; restore on close.** (2 citations)

### §C. Content & deployment patterns (new in v2)

15. **Check image/asset paths exist before committing.** Photo swaps in content-heavy pages (jamie-bach, interior-designer) frequently reference images that haven't been uploaded yet. (1 citation: v2 audit — inferred from rapid photo-swap commits)
16. **Cost/price math in static data: verify sums match displayed totals.** The Jamie's bach cost page had division corrections (Hotel /9, Cruise /8, Pilates /8) suggesting math wasn't verified on first pass. (1 citation: commit "cost page math" 2026-05-26)
17. **Subdomain routing changes need both middleware AND DNS/Vercel domain config.** Middleware rewrites alone don't work without the domain being configured in Vercel. (1 citation: jamie-bach subdomain setup 2026-05-26)
18. **OG/meta tags: test with actual sharing, not just HTML inspection.** iMessage/Slack/Twitter each cache and render OG differently. The "custom OG card" commit suggests the first version didn't render correctly in all targets. (1 citation: commit "custom OG card for iMessage/Slack/Twitter previews" 2026-05-26)
19. **Never generate URLs from memory — verify every link before committing.** Fabricated Reddit URLs shipped to production and had to be manually replaced. (1 citation: "Replace fabricated curated URLs with verified Reddit posts" 2026-04-12)
20. **When concurrent Claude Code sessions are active, grep for recent commits before making structural changes.** One session deleted BugReportButton that another session had just added; required manual restore. (2 citations: "restore: re-add BugReportButton" + "restore: re-apply bug-fixer types" 2026-04-05)
21. **Data migrations are high-risk — always dry-run first and keep a rollback path.** Vercel Blob → R2 migration produced 1×1 placeholder images, required 5 repair/remigrate rounds over 2 days. (5 citations: restore-and-remigrate, purge-broken-r2, repair-from-source, debug-urls, migrate-blob-to-r2 fixes, Apr 1-2)
22. **Match the user's voice, not Claude's default tone.** Content that sounds like generic AI prose ("AI slop") requires a full rewrite. When writing copy, read 2-3 existing paragraphs on the same page and mirror that register. (1 citation: "rewrite memo copy to kill AI slop" 2026-04-13)
23. **External platform integrations (iOS Shortcuts, PWA, OAuth) have undocumented behaviors — always parallel.** The iOS Shortcuts photo upload took 10+ serial iterations (v3→v13) over 3 days. Parallel drafts testing different approaches simultaneously would have compressed this. (10 citations: shortcut versions v3-v13, Apr 1-3)
24. **Race conditions in sequential API calls: default to sequential writes, parallel reads.** Two separate bugs from parallel writes: GitHub SHA race condition, Reddit PUT ordering. (2 citations: "Fix GitHub SHA race condition" + "actually make GitHub PUTs sequential" 2026-04-13-14)

## Meta notes

- The `isolation: "worktree"` Agent parameter fails when Claude's cwd is not a git repo or in web sessions. v2 adds sequential-draft fallback (Step 4b) so parallel quality improvement is available everywhere.
- **Content mode** (Step 4d) is new in v2. The original skill excluded all non-code work, but content iteration in code files is the #1 use case by commit volume.
- **Rapid-iteration mode** (Step 4e) is new in v2. Designed for the pattern seen in Jamie's bach: 15+ small changes in one session.
- **Pre-commit build gate** (Step 6) is new in v2. Now mandatory for ALL paths, not just parallel drafts.
- **Deferred to later syncs:** holdout-commit eval, N=5 live-task precision/recall eval, citation-validity pre-commit lint, token-budget hard cap enforcement, stale-rule quarterly audit, cross-skill conflict scan.
- **Source pinning:** initial backfill drew from session summaries (backfill-only source, not recurring). Weekly sync pulls from run logs + post-merge diffs + cross-repo git mining.

## Changelog

- **2026-05-31 v2 audit** — 14 findings across code-builder, mcp-contributor, build-log (200+ entries), and 50+ Vercel deployments. Implemented: sequential-draft fallback for web sessions (Step 4b), content mode for copy/design iteration (Step 4d), rapid-iteration mode for high-frequency small changes (Step 4e), mandatory pre-commit build gate for all paths (Step 6), visual verification step (Step 6c), staleness warning, environment tracking in run logs, 2 new hard parallel signals (external integrations, data migrations). Added 12 new learnings (§A7-8, §C15-24) from Mar-May 2026 sessions. Lowered file-count parallel threshold. Broadened activation triggers to include content-in-code tasks. Total learnings: 24/30.
- **2026-04-13 backfill sanity test** — initial learnings populated from 4 repos + 13 session summaries.
