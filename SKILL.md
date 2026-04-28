# code-builder

> Raises the floor of code quality by generating **5 parallel implementations** of the same dev task, self-scoring them against a measurable rubric, and merging the winner. Claude picks the winner so the user doesn't review five diffs.

---

## 1 — Triggers

### Activate on

- Slash: `/code-builder`
- Phrases: "build this," "fix this bug," "add a feature," "write me a function," "make a prototype," "refactor this"
- Force directives: "force-parallel," "force-single"
- Implicit: working in a git repo while describing a coding task, sharing error logs, pasting code for modification, working in known repos, detecting broken features

### Do NOT activate on

- Pure research / reading code
- Writing, design, planning, or strategy docs
- Meta-tasks (config, env, settings)
- **Content-only tasks** — populating screenshots, writing copy, updating text on a page, swapping images. These are single-pass by definition (no design-space breadth). Announce: `📝 content task — single pass, code-builder scoring skipped.`

### Default

Activate when uncertain; false positives are low-cost.

---

## 2 — Announce

Before any action, print:

```
🔧 code-builder activated — [parallel, 5 drafts | single pass]. [≤15-word reason.]
```

---

## 3 — Scope

State the task in one line. Then:

- Files likely to change
- Greenfield vs. modification
- Design-space breadth (narrow fix → single; open design → parallel)

---

## 4 — Judgment Gate

Default to **single**; escalate to **parallel** when **≥2 signals fire** or **any hard signal fires**.

| Signal | → Parallel | → Single |
|--------|-----------|----------|
| LOC estimate | >30 | <10 |
| File count | >1 file OR new file | exactly 1 existing |
| Architecture options | multiple valid approaches | obvious path |
| Pattern novelty | new pattern for this repo | existing variation |
| Risk | critical-path / user-facing | contained / internal |
| Task type | feature / refactor / greenfield | targeted fix / content |
| Phrasing | open-ended | specific |

**Hard overrides:**

| Condition | Action |
|-----------|--------|
| User explicit override | obey |
| Not a git repo | force single |
| Live debugging | force single |
| Greenfield prototype | force parallel |
| Content-only task | force single |

---

## 5a — Parallel Path (N=5)

### Prerequisite

Must be in a git repo: `git rev-parse --git-dir`. If not, downgrade to single and re-announce.

### Spawn

5 Agent calls in parallel:
- `isolation: "worktree"`
- `run_in_background: true`
- `subagent_type: "general-purpose"`

### Differentiation hints

| Draft | Bias |
|-------|------|
| 1 | **Simplest** — fewest lines, no abstractions |
| 2 | **Most idiomatic** — match repo patterns exactly |
| 3 | **Readability** — clearest naming, smallest functions |
| 4 | **Correctness** — edge cases, null safety, mobile viewports |
| 5 | **Free choice** — best instinct |

### Each draft reports

- 2-line approach summary
- Files touched (created, modified, deleted)
- LOC delta
- Commit SHA
- Edge cases handled
- **New files created** (explicit list — critical for staging verification)

---

## 5b — Single Path

Execute normally; skip to Step 8 (logging).

---

## 6 — Self-Evaluate (Parallel Only)

Score each draft out of 100:

| Criterion | Weight | How to score |
|-----------|--------|-------------|
| Correctness | 25 | Walk every requirement; −5 per miss |
| Tests pass | 15 | Run project test suite. 15 = pass, 0 = fail |
| Typecheck | 10 | `tsc --noEmit` or equivalent. 0 errors = 10 |
| Lint | 5 | Project lint command. 0 warnings = 5 |
| Minimal diff | 10 | `10 × (min_LOC / this_LOC)` |
| No new deps | 10 | 0 new = 10; −3 per new (unless justified) |
| Reuses utilities | 10 | Grep for + reuse existing helpers |
| Repo conventions | 10 | Naming, structure, import style alignment |
| Scope containment | 5 | Deduct for unrelated file touches |

**Bonus modifiers (±5 each, can exceed 100):**

| Modifier | Condition |
|----------|-----------|
| +5 Mobile-safe | Verified no position:absolute in scroll/overflow, no un-unscaled getBoundingClientRect, touch targets ≥44px |
| +5 Null-safe | All KV/API/DB reads guarded with optional chaining + empty-state fallback |
| −5 Mega-commit | Touches >3 unrelated bug fixes in one commit |
| −5 Phantom files | Creates files not listed in draft report or not git-staged |

**Tiebreakers:** (1) smallest diff, (2) draft 2 (most idiomatic).

Record full score breakdowns for all 5 drafts in the run log.

---

## 7 — Merge Validation

### 7a. Gap check
Walk original requirements against winner's diff. Cherry-pick missing solutions from other drafts if needed.

### 7b. Redundancy check
Strip unused imports, dead code, comments, debug logs, duplicate helpers.

### 7c. Git staging verification ← NEW
```bash
# List all files that exist on disk but aren't tracked
git status --porcelain | grep '^\?\?'
# If any new files match what this task created, stage them
# NEVER push with untracked files that the task created
```
Fail the merge if any task-created files are unstaged. This prevents the "created locally but never committed" class of bugs (e.g., ShareDropdown.tsx incident).

### 7d. Revalidate
Run the full chain: **tests → typecheck → lint** on the final diff. All three must pass.

### 7e. Atomic commits ← NEW
If the task fixes multiple independent bugs, split into **one commit per bug**. Each commit must independently pass typecheck. Rationale: mega-commits prevent clean reverts and obscure bisection.

### 7f. Merge
Fast-forward or `git merge --no-ff`; clean up worktrees; keep winner's branch.

### 7g. Post-push deployment check ← NEW
After `git push`, if the project deploys to Vercel:
1. Wait 60 seconds
2. Check the deployment URL or Vercel dashboard
3. If deployment state = ERROR, investigate build logs immediately — do NOT leave a broken production deploy
4. Report deployment status in the final message

### 7h. Report
```
✓ Merged draft {N}/5 (score {X}/100). {reason}. {cherry-pick status}.
  Tests ✓  Types ✓  Lint ✓  Deploy: {✓ | ⚠ checking | ✗ error — investigating}
  Files: {count} modified, {count} created, {count} deleted
```

---

## 8 — Log the Run

Write `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`:

```yaml
---
date: YYYY-MM-DD
task_slug: kebab-case-name
repo: owner/repo
judgment: parallel | single
override: none | user-forced-X
winner: N
sha: abc123
score: NN
cherry_picks: [list or none]
deploy_status: success | error | not-applicable
mobile_tested: true | false
files_created: [list]
---
```

Body sections:
- Task (verbatim user request)
- Judgment explanation
- All 5 drafts: approach, files, LOC, score, SHA
- Cherry-picks (if any)
- In-session user feedback
- Deployment outcome
- Notes (timeouts, failures, workarounds)

---

## 9 — Sync Workflow

**Schedule:** Sunday 6 PM or `code-builder sync`. If >10 days since last sync, print a reminder at session start.

### Data sources
1. New run logs since last sync
2. Post-merge git diffs on winner branches
3. In-session feedback in run logs
4. Judgment overrides (run frontmatter)
5. Cross-repo git mining (bounded: `--max-count=50`, author filter, `--since` window)
6. **Vercel deployment logs** — ERROR deploys since last sync ← NEW

### Process
- Count patterns ≥2 times across runs → candidate learnings
- Refine existing bullets (don't blindly append); track citation count
- Enforce **30-bullet hard cap**; prune by lowest citations + oldest date
- Update `## Current Learnings` section and `Last synced:` timestamp
- Announce: `🔧 code-builder sync complete — added {N}, refined {M}, pruned {P}. {X}/30 total.`

---

## Current Learnings

**Last synced:** 2026-04-28 (backfill from 4 repos, 20+ sessions, deployment logs)

*Repo-specific `CLAUDE.md` rules override these cross-repo patterns.*

### §A. Process Failures

1. Never call `Skill()` inside scheduled-task bodies — circular dispatch burns rate limits.
2. No hardcoded tokens/secrets in client JS or `NEXT_PUBLIC_`-prefixed modules.
3. "Done" requires green tests + typecheck + successful deploy, not compile-pass alone. *(Refined: added deploy check)*
4. Resolve merge conflicts by re-running tests, not by eyeballing.
5. Guard **every** nullable KV/API/DB response before access — use optional chaining AND render an empty-state fallback. Applies to: gallery images (`.note`), journal entries, admin lists, any data written before a field was required. *(Refined: more specific, added examples)*
6. Grep for existing helpers before writing new ones — avoids utility duplication/drift.
7. **Verify all new files are git-staged before push.** Run `git status --porcelain` and check for `??` entries matching task-created files. The ShareDropdown/PreviewBanner incident: files were created in the working tree but never `git add`-ed, breaking the Vercel build. *(New — from interior-designer-portfolio ERROR deploy)*
8. **One bug per commit.** Multi-bug mega-commits (7+ fixes in one commit) prevent clean revert and bisection. Split independent fixes into atomic commits, each passing typecheck independently. *(New — from interior-designer-portfolio pattern)*
9. **Check deployment status after push.** If Vercel shows ERROR, investigate immediately. Same commit SHA deployed 3-5x suggests push-retry without checking state. *(New — from schlacter-me + interior-designer-portfolio patterns)*

### §B. Code-Level Patterns

1. Validate + trim `process.env.X` at read-site — whitespace/quoting variance causes silent misconfig.
2. Floating UI inside scroll/overflow needs `position: fixed` + portal, not `position: absolute`. **Enforce in scoring: any new tooltip/picker/dropdown in a scrollable container must use fixed positioning.** *(Refined: made scoring-enforceable)*
3. Rules of Hooks (full form): no conditionals, no inside callbacks/effects, hooks list must be complete and stable.
4. `useEffect` subscriptions/timers/state-setters must return cleanup functions. **Includes Next.js client-side navigation** — `beforeunload` does NOT fire on `router.push()`. Use an unmount-cleanup `useEffect` with `fetch(..., {keepalive: true})` for pending saves. *(Refined: added Next.js navigation case from journal save-on-nav-away bug)*
5. Unscale `getBoundingClientRect()` values when ancestor has CSS transform. **Applies to crop handles, image pickers, any drag-and-drop at non-1x zoom.** Use the rendered width directly — do NOT divide by zoomLevel when the browser already reports scaled values. *(Refined: added specific crop-handle context from recurring bug)*
6. Save editor selection before modal open; restore on close — prevents caret/line jump.
7. **When adding a new value to a TypeScript union/enum, grep all consumers** — switch statements, prop type definitions, discriminated unions. The `current-home` NavBar incident: a new page used `activePage="current-home"` but the NavBar prop type didn't include it. *(New — from interior-designer-portfolio TypeScript ERROR deploy)*
8. **Touch targets must be ≥44px on mobile.** Expand arrow buttons, close icons, filter tabs — any interactive element that users report as "not clickable" is likely a tap-target issue. Use `min-height: 44px; min-width: 44px` or equivalent padding. *(New — from bug-report patterns: expand arrow, status filter tabs)*
9. **Numbered/bulleted list auto-format in contentEditable: use Selection API to replace trigger text.** Don't create empty blocks that Chrome merges with the preceding line. *(New — from journal numbered list bug)*
10. **position:fixed elements need scroll-dismiss or reposition logic.** Fixed-position pickers/dropdowns become stale when the user scrolls. Either dismiss on scroll or recompute position in a scroll listener. *(New — from image size picker bug)*

### §C. Content & Deployment Patterns ← NEW SECTION

1. **Content tasks (copy, screenshots, images) are single-pass.** Don't waste 5 parallel drafts on swapping a GIF or rewriting a paragraph. Announce `📝 content task` and execute directly.
2. **Duplicate Vercel deployments from the same SHA are wasted builds.** Before retriggering a deploy, check if the SHA is already deployed and in READY state.
3. **Demo/share links need read-only guardrails.** When creating magic-link or demo access, explicitly hide write operations (add, edit, delete buttons) and show a visible "Demo mode" indicator.

---

## Meta

- `isolation: "worktree"` fails if cwd is not a git repo → auto-downgrade to single pass.
- Sync reminder: if `Last synced` date is >10 days ago, print `⚠ code-builder sync overdue ({N} days). Run 'code-builder sync' to update learnings.`
- Deferred: eval framework benchmarking, stale-rule audit automation, cross-skill conflict detection — wait for ≥5 parallel runs with scoring data.
