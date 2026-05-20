---
name: code-builder
description: >
  Raises the floor of code quality by generating parallel implementations,
  self-scoring against a measurable rubric, and merging the winner.
  Auto-activates on dev work. Adapts to environment — full parallel mode
  in local git repos, quality-gated single pass elsewhere.
---

# code-builder

Five parallel drafts + objective scoring pushes the quality floor higher than single-pass output. Claude picks the winner, not Hannah.

---

## Step 0 — Environment check (runs before anything else)

Before activating, silently determine the execution environment:

```
ENV_TYPE = "unknown"
1. git rev-parse --git-dir → if fails → ENV_TYPE = "no-git"
2. Check if ~/.claude/skills/code-builder/runs/ is writable → if fails → ENV_TYPE = "ephemeral"
3. If both pass → ENV_TYPE = "full"
```

| ENV_TYPE | Parallel? | Logging | Learning sync |
|----------|-----------|---------|---------------|
| full | Yes (5 worktree drafts) | Local runs/ dir | Full weekly sync |
| ephemeral | No (single pass only) | Commit-message metadata | Skip (no persistent state) |
| no-git | No (single pass only) | None | Skip |

Do NOT attempt to spawn worktree agents in `ephemeral` or `no-git` mode. This avoids wasting tokens on 5 guaranteed failures.

---

## When this skill activates

**Any time Hannah is writing, changing, or fixing code, activate.** The lists below are examples, not exhaustive — use judgment.

**Explicit triggers:**
- `/code-builder`, "build/code/implement/create X", "fix/debug/something broke"
- "add a feature", "refactor X", "write me a function/class/module"
- "5x this" / "parallel this" → force parallel
- "just fix it" / "quick fix" → force single

**Implicit triggers:**
- Working dir is a git repo AND Hannah describes a coding task
- Hannah shares an error, stack trace, or failing log
- Hannah pastes code and asks for a change
- Hannah says "start a new prototype/app/project"

**Do NOT activate:**
- Pure research, code reading, writing, design, planning, brainstorming
- Meta tasks ("what are my TODOs?", "summarize this session")

**When uncertain, default to activating.** Single-pass costs almost nothing; skipping real dev work is worse.

---

## Announcement (required, every activation)

> **code-builder activated** — [parallel, 5 drafts | single pass]. [15-word reason.] [ENV: full|ephemeral|no-git]

Hannah can override: "actually, 5x this" or "actually, just fix it" → flip and re-announce.

---

## Step 1 — Scope the task

State the task in one line. Identify:
- Files likely to change
- Greenfield vs. modification
- Design space — multiple valid approaches, or fixed?

---

## Step 2 — Judgment gate

**Default is single.** Escalate to parallel only when **>=2 parallel signals** OR **any hard signal** fires.

| Gate | Parallel | Single |
|------|----------|--------|
| LOC estimate | >30 lines | <10 lines |
| Files touched | >1 file or new file | 1 existing file |
| Design space | Multiple valid architectures | One obvious path |
| Novelty | New pattern in this repo | Existing pattern variation |
| Risk | Critical path (auth, checkout, data) | Leaf component |
| Task type | Feature / refactor / greenfield | Targeted bug fix |
| Phrasing | Open-ended ("build X") | Specific ("change line 42") |

**Hard signals (any one decides):**
- Hannah explicit override → obey
- ENV_TYPE != "full" → force **single**
- Live debugging with rapid iteration → force **single**
- Greenfield prototype from scratch → force **parallel** (if ENV_TYPE = "full")

---

## Step 3a — Parallel path (N=5, only when ENV_TYPE = "full")

1. Spawn **5 Agent calls in parallel in a single message**, each with:
   - `isolation: "worktree"`, `run_in_background: true`, `subagent_type: "general-purpose"`
   - Differentiation bias:
     - Draft 1: simplest possible — fewest lines, no abstractions
     - Draft 2: most idiomatic to this repo — match existing patterns exactly
     - Draft 3: optimize for readability — clearest naming, smallest functions
     - Draft 4: optimize for performance / correctness on edge cases
     - Draft 5: best instinct — free choice
   - Instruction: "You are one of 5 parallel drafts. Commit on the worktree branch. Report: approach (2 lines), files touched, LOC delta, commit SHA, edge cases handled."
2. Wait for all 5. Score survivors if any fail/timeout.

## Step 3b — Single path (all environments)

Do the task. Then proceed to **Step 5 — Single-pass quality gate** before declaring done.

---

## Step 4 — Score and pick winner (parallel only)

Claude picks. Do NOT ask Hannah to review 5 diffs.

Score each draft out of **100 points**:

| Criterion | Weight | Measurement |
|-----------|--------|-------------|
| Correctness | 25 | Walk each requirement; deduct for misses |
| Tests pass | 15 | Run project test command. Pass=15, fail=0. No tests → redistribute to Correctness (40 total) |
| Typecheck clean | 10 | `tsc --noEmit` or equiv. 0 errors=10 |
| Lint clean | 5 | Project lint command. 0 warnings=5 |
| Minimal diff | 10 | `10 * (min_LOC / this_LOC)` |
| No unnecessary deps | 10 | 0 new=10; each new=-3 unless required |
| Reuses existing utils | 10 | Grepped for and reused existing helpers? |
| Follows repo conventions | 10 | Naming, structure, imports vs. neighbors |
| Scope containment | 5 | Deduct if unrelated files touched |

**Tiebreakers:** (1) smallest diff, (2) draft 2 (most idiomatic).

---

## Step 5 — Single-pass quality gate (single path only)

Before declaring done on single-pass work, self-review against a subset of the rubric:

| Check | Action if fails |
|-------|----------------|
| Walk each requirement in the task — any missed? | Fix before reporting |
| Run tests if they exist | Fix failures |
| Run typecheck/lint if configured | Fix errors |
| Any files touched that aren't needed? | Revert |
| New dependency added — is it necessary? | Remove if not |
| Grep for existing helper before writing a new one | Reuse if found |

Report: `code-builder single-pass complete. [Tests/Types/Lint status]. [1-line summary.]`

This gate ensures single-pass output gets the same correctness standard, just without the multi-draft comparison.

---

## Step 6 — Merge validation (parallel only)

1. **Gap check.** Re-read original task. Walk each requirement against winner's diff. For any gap, cherry-pick from rejected drafts or write fresh.
2. **Redundancy check.** Strip unused imports, dead code, debug logs, duplicate helpers.
3. **Rerun validation.** Tests + typecheck + lint on final diff.
4. **Merge.** Fast-forward if possible; else `git merge --no-ff`.
5. **Clean up worktrees.** Remove all 5. Delete losing branches. Keep winner's branch.
6. **Report:**
   > Merged draft {N}/5 (score {X}/100). {reason it won.} {Cherry-picked from draft M | No gaps.} Tests/Types/Lint status.

---

## Step 7 — Log the run

**If ENV_TYPE = "full":** Write `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md` with structured frontmatter (date, task_slug, repo, judgment, winner_draft, winner_sha, winner_score, cherry_picks_from) and per-draft score breakdowns.

**If ENV_TYPE = "ephemeral":** Append a one-line summary to the commit message:
```
[code-builder: single-pass | correctness OK | tests pass | lint clean]
```
This preserves a minimal signal in git history even when local state is lost.

**If ENV_TYPE = "no-git":** Log nothing. Announce to Hannah that no record was kept.

---

## Learning sync (weekly + on-demand)

Trigger: Sunday 6pm cron OR "code-builder sync" OR `/code-builder sync`.

**Only runs when ENV_TYPE = "full".** In ephemeral environments, announce: "Sync requires persistent local state. Run from a local Claude Code session."

### Sync workflow

1. Read `Last synced:` date from Current learnings below. Read new `runs/*.md` since that date.
2. Collect from 5 sources:
   - a. Run logs
   - b. Post-merge git diffs (what Hannah edited after merge)
   - c. In-session feedback from run logs
   - d. Judgment overrides from run frontmatter
   - e. Cross-repo mining (bounded): discover repos dynamically:
     ```
     find ~/code ~/projects ~/repos -maxdepth 2 -name ".git" -type d 2>/dev/null | head -10
     ```
     For each, check `git log --since="<last-sync>" --max-count=50 --author="Hannah" --grep="fix\|revert\|oops\|simplify\|cleanup"`.
3. Count patterns (>=2 repetitions = candidate learning).
4. Refine existing learnings: dedupe, supersede contradictions, update citations.
5. Prune to **hard cap of 30 bullets**.
6. Update Current learnings section below. Update `Last synced:` date.
7. Announce: `code-builder sync complete — added {N}, refined {M}, pruned {P}. Total: {X}/30.`

---

## Self-test (`/code-builder test`)

Run a quick health check and report:

| Check | How |
|-------|-----|
| ENV_TYPE detection | Run Step 0, report result |
| Skill file loaded | Confirm this file was read |
| Runs directory | Check if `~/.claude/skills/code-builder/runs/` exists and is writable |
| Git worktree support | `git worktree list` succeeds |
| Learning state | Report Last synced date and bullet count |
| Known conflicts | Check if mcp-contributor is also active (warn if both triggered) |

Report: `code-builder health: [ENV_TYPE]. [N] learnings, last synced [date]. [issues found or "all clear"]`

---

## Current learnings

Last synced: 2026-04-13 (initial backfill)

*If a repo's CLAUDE.md contradicts a rule below, the repo rule wins.*

### Process failures
- **Never call `Skill()` from inside a scheduled-task body.** Circular dispatch burns rate limit. (1 citation)
- **No hardcoded tokens/secrets in client JS.** Anything in `"use client"` or `NEXT_PUBLIC_` ships to browser. (1 citation)
- **"Done" requires green tests + typecheck, not "looks right."** (2 citations)
- **Resolve merge conflicts by re-running tests, not eyeballing.** Code was silently lost 3x. (1 citation)
- **Guard nullable KV/API responses before destructuring.** Render empty state or early-return. Cross-repo x3. (3 citations)
- **Grep for existing helpers before writing a new one.** Duplicated utilities drift. (1 citation)

### Code-level patterns
- **Validate + trim `process.env.X` at the read-site.** Whitespace variance causes silent misconfig. Cross-repo x2. (4 citations)
- **Floating UI inside scroll/overflow parent needs `position: fixed` + portal.** Absolute clips. Cross-repo x2. (1 citation)
- **Rules of Hooks full form: no conditional calls, no hooks in callbacks/effects, no return before hooks list complete.** Cross-repo x2. (1 citation)
- **`useEffect` with subscribe/timer/setState must return cleanup.** #1 correction category. x4. (1 citation)
- **Unscale `getBoundingClientRect()` under CSS transform ancestors.** Measurements in transformed frame. (2 citations)
- **Save editor selection before DOM-mutating modal; restore on close.** (2 citations)
