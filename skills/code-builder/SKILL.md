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

Raises the floor of Claude's dev output by running 5 parallel
implementations, self-scoring them against a measurable rubric, and merging
the winner.

The bet: if Claude lands good code ~80 % of the time, single-pass output is
suboptimal 1-in-5 tasks. Five parallel drafts + objective scoring pushes the
floor much higher. Claude picks the winner, not Hannah.

---

## When this skill activates

**Explicit triggers** (always activate):
`/code-builder`, "build this", "fix this bug", "add a feature",
"refactor X", "write a test for Y", "implement Z", or any phrasing that
clearly requests code creation or modification.

**Implicit triggers** (activate when context confirms a coding task):
- cwd is a git repo AND the conversation is about changing code
- Hannah shares an error, stack trace, or broken behavior
- The conversation references a known project repo (hannah-portfolio,
  kindle-connector, muse-shopping, libby-hold-monitor, recs.community, etc.)

**Exclusions** (never activate):
- Pure research, architecture discussion, or planning (no code yet)
- Writing prose, docs, or non-code content
- Meta-tasks about skills themselves (editing SKILL.md, CLAUDE.md, etc.)
- Skill/config file edits — use single-pass only, never parallel

**Default when uncertain:** activate in single-pass mode.

---

## Announcement (required, every activation)

Print exactly one line before any other output:

```
🔧 code-builder activated — [parallel, 5 drafts | single pass]. [reason.]
```

Hannah can override the mode at any time ("just do it" → single,
"try a few approaches" → parallel).

---

## Workflow

### Step 1 — Gather project context

Before writing any code, spend 30 seconds understanding the project:

1. Read `CLAUDE.md` and `AGENTS.md` if they exist in the repo root.
2. Scan the last 10 git log messages to understand recent work and patterns.
3. Check if there is a `.claude/skills/` directory with project-specific skills.
4. Note the stack: language, framework, deployment target (Vercel, GitHub Actions, etc.).

This context feeds into both the implementation and the scoring rubric. Skip
this step only if you already have project context from earlier in the
conversation.

### Step 2 — Scope the task

Write one sentence: what will change, and why.
- List files likely to touch.
- Note if this is greenfield vs modification of existing code.
- Note if this involves data migration, external APIs, or platform-specific behavior.
- Identify the design space: is there meaningfully more than one reasonable approach?

### Step 3 — Judgment gate

**Default: single pass.** Escalate to parallel when the task has enough
complexity that multiple approaches could produce meaningfully different
quality outcomes.

#### Signal table

| Signal | Weight | Fires when… |
|--------|--------|-------------|
| LOC estimate | +1 | > 60 lines changed |
| Files touched | +1 | >= 3 files |
| Design space | +1 | > 1 reasonable approach visible |
| Novelty | +1 | Pattern not seen in current learnings |
| Risk | +1 | Touches auth, payments, data migration, or user-facing state |
| Task type | +1 | Greenfield feature or architecture change |
| Phrasing | +1 | "explore", "try different approaches", "best way" |
| Multi-file feature | +2 | Feature spans frontend + backend or 4+ files |

**Escalate to parallel when total >= 3** (lowered from previous >= 4
threshold — the fix-commit record shows single-pass misses edge cases
on medium-complexity tasks).

#### Hard signals (parallel regardless of score)

- Hannah explicitly requests it
- Greenfield prototype with > 100 LOC

#### Hard signals (single-pass regardless of score)

- Not a git repo (worktrees require git)
- Live debugging / interactive troubleshooting
- Skill/config file editing
- Task is a one-line fix or config change

#### Worked examples

| Task | Signals | Decision |
|------|---------|----------|
| "fix the TypeScript build error" | LOC ~5, 1 file, no design space | Single |
| "add a read-it-later app with KV backend" | LOC 200+, 5+ files, greenfield, design space | Parallel (hard: greenfield > 100 LOC) |
| "proxy preview images so CDNs load" | LOC ~30, 2 files, 1 approach | Single |
| "implement v1→v2 data migration" | Risk (data migration), 3+ files, design space | Parallel (score = 4) |
| "add subdomain routing via middleware" | 3 files, novelty, risk (routing) | Parallel (score = 3) |

### Step 4a — Parallel path (N = 5)

**Prerequisite:** cwd must be a git repo. If `isolation: "worktree"` fails
(disk space, git state, permissions), fall back to single-pass with a note:
`⚠️ Worktree creation failed — falling back to single pass. [error]`

Spawn 5 Agent calls in a single message, each with `isolation: "worktree"`:

| Draft | Differentiation bias |
|-------|---------------------|
| 1 | Simplest possible — fewest lines, minimal abstraction |
| 2 | Most idiomatic — follow framework conventions exactly |
| 3 | Most defensive — handle every edge case and platform quirk |
| 4 | Best performance — optimize for runtime, minimize re-renders/queries |
| 5 | Free choice — whatever approach Claude judges best for this task |

Each draft prompt must include:
- The full task description from Step 2
- Project context from Step 1 (stack, recent patterns, known gotchas)
- Instruction to commit on its worktree branch
- Instruction to report: approach summary, files touched, LOC, commit SHA,
  edge cases considered, platform-specific behaviors handled

### Step 4b — Single path

Just do the task. Apply project context from Step 1. Skip to Step 7.

### Step 5 — Self-evaluate and pick the winner

Score each draft out of 100:

| Criterion | Points | What it measures |
|-----------|--------|-----------------|
| **Correctness** | 20 | Does it do what was asked? Logic errors? |
| **Edge-case coverage** | 15 | Null/empty/missing states, platform quirks, error paths |
| **Tests pass** | 15 | Existing test suite still green, new tests if appropriate |
| **Typecheck clean** | 5 | `tsc --noEmit` or equivalent passes |
| **Lint clean** | 5 | No new lint violations |
| **Minimal diff** | 10 | Smallest change that solves the problem |
| **No unnecessary new deps** | 5 | Prefer stdlib and existing packages |
| **Reuses existing utilities** | 10 | grep for helpers before writing new ones |
| **Follows repo conventions** | 10 | Naming, file structure, patterns match the codebase |
| **Scope containment** | 5 | Doesn't touch unrelated code |

**Key change from v1:** Edge-case coverage is now a separate 15-point
dimension. This catches the class of bugs where all drafts make the same
correct-looking implementation but miss platform-specific behavior (Vercel KV
empty blobs, CDN hotlink blocking, Next.js route group scoping, etc.).

**Tiebreaker:** smallest diff wins. Then draft 3 (defensive bias).

### Step 6 — Merge and validate

1. **Gap check** — Walk each requirement from Step 2. If the winner missed
   something that a rejected draft handled, cherry-pick that piece. If
   cherry-pick conflicts, re-implement the gap manually instead of forcing it.
2. **Redundancy check** — Remove any dead code or unused imports from the merge.
3. **Validation** — Run the project's test/typecheck/lint commands.
4. **Merge** — Fast-forward preferred. Squash if the worktree branch has
   multiple commits.
5. **Clean up** — Remove worktree branches.
6. **Report** — One-line summary: which draft won, score, what was cherry-picked.

### Step 7 — Log the run

Write to `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`:

```yaml
---
date: YYYY-MM-DD HH:MM
task: one-line description
mode: parallel | single
project: repo-name
winner: draft N (score)
runner_up: draft M (score)
cherry_picked: [list] or none
fix_within_1h: false
---
```

Followed by a brief narrative: what differentiated the winner, what the other
drafts got wrong, any surprises.

**Remote session handling:** If `~/.claude/skills/` doesn't exist (ephemeral
container), log to `.claude/runs/` in the project repo instead. These logs
can be synced later.

---

## Learnings sync

### When to sync

- **Self-trigger:** At activation, check the "Last synced" date below. If
  > 14 days stale, run an inline sync before starting the task. Announce:
  `🔄 code-builder learnings are [N] days stale — running quick sync.`
- **On-demand:** Hannah says "sync learnings" or "/code-builder sync".
- **Post-merge signal:** After merging, scan the last 5 commits for fix
  patterns (commits within 2 hours that touch the same files). If found,
  extract what the fix corrected and add it as a learning candidate.

### Sync process

Collect from 5 sources:
1. Run logs in `runs/` (or `.claude/runs/`)
2. Post-merge git diffs (what Hannah changed after the skill's merge)
3. In-session feedback ("that's wrong", "no, do X instead")
4. Judgment overrides (Hannah switched mode or rejected the winner)
5. Fix-commit patterns (same-file commits within 2 hours of a skill merge)

Three-pass process:
1. **Count patterns** — only candidates with >= 2 occurrences become learnings
2. **Refine existing bullets** — update wording, don't blindly append
3. **Prune** — hard cap at 35 bullets (increased from 30 to accommodate
   project-specific patterns)

---

## Current learnings

Last synced: 2026-06-03

### A — Claude process failures

1. Never call `Skill()` inside a scheduled-task body or background agent — it's not available there.
2. Never put secrets or tokens in client-side JavaScript — use server actions or API routes.
3. "Done" means tests pass + typecheck clean + the feature works in the browser. Don't declare done before verifying.
4. When merge conflicts appear, re-run tests after resolution — don't assume the merge preserved correctness.
5. Guard nullable responses (KV, API, localStorage) before destructuring — empty string is not null.
6. `grep` for existing helpers before writing new utility functions.

### B — Concrete code-level patterns

7. Validate and trim `process.env.X` at the read site, not deep in business logic.
8. Floating UI inside a scroll parent needs `position: fixed` + portal mount.
9. Rules of Hooks: no hooks inside conditions, loops, or nested functions — full form, no shortcuts.
10. `useEffect` subscriptions must return a cleanup function.
11. Unscale `getBoundingClientRect()` when an ancestor has a CSS `transform`.
12. Save editor selection/cursor before opening a DOM-mutating modal, restore after close.

### C — Platform-specific patterns (NEW)

13. Vercel KV returns empty string `""` for unset keys, not `null` — always check `!value` not `value === null`.
14. Next.js App Router route groups `(groupName)` do NOT inherit layouts from sibling groups — icons, metadata, and layouts must be placed at or above the route group level.
15. External CDN images (product photos, brand assets) will fail in `next/og` and social previews due to hotlink blocking — proxy through your own API route.
16. Next.js middleware for subdomain routing: match on `request.headers.get('host')`, rewrite to a path-based route, and handle both www and bare domain.
17. `next/og` ImageResponse renders differently across iMessage, Slack, and Twitter — test with each platform's preview debugger, not just the browser.
18. Data migrations between storage backends (localStorage → KV, v1 → v2) must handle: partial migration state, items that exist in both old and new stores, and empty/corrupt old-format data.
19. When deploying to Vercel with `npm run build`, TypeScript strict mode catches errors that dev mode doesn't — always run `tsc --noEmit` before committing.
20. Favicons and apple-touch-icons in Next.js App Router must be in the root `app/` directory or a layout route that covers all paths — NOT inside a route group.

### D — Architecture patterns

21. For multi-subdomain Next.js apps, keep a single repo with middleware routing rather than separate deployments — simpler to maintain and deploy.
22. Read-it-later / bookmarking apps need offline-first architecture: write to localStorage immediately, sync to backend async, reconcile on next load.
23. Cost/budget calculation pages should derive totals from a single data source (array of items) — never hardcode math that duplicates the data.

---

## Composition guard

When another skill is active in the same session (e.g., mcp-contributor,
interior-designer-skill), code-builder defers to the domain skill for
task-specific decisions but still applies its quality process. Exception:
when editing skill files (SKILL.md, CLAUDE.md, settings.json), code-builder
uses single-pass only and does NOT spawn parallel drafts.

---

## Meta notes

- `isolation: "worktree"` requires the cwd to be a git repo.
- If the project has no test suite, "Tests pass" (15 pts) is redistributed:
  +10 to Edge-case coverage, +5 to Correctness.
- Token budget awareness: if the conversation is already long (> 150k tokens
  estimated), use N=3 drafts instead of N=5 to stay within limits.

### Deferred items (prioritized)

1. **Post-merge fix tracking** — implemented in sync process above
2. **Token-budget cap** — implemented as N=3 fallback above
3. **Project-specific learning partitions** — learnings section C above
4. **Holdout-commit eval** — run the rubric on a random past commit to calibrate scoring
5. **Stale-rule audit** — flag learnings that haven't been reinforced in 60 days
6. **Cross-skill conflict scan** — detect when multiple skills give contradictory instructions

## Changelog

- 2026-06-03: Major revision. Lowered parallel threshold (>= 3 signals, was >= 4). Added edge-case coverage as separate scoring dimension (15 pts). Added project context step. Self-triggering sync replaces cron dependency. Post-merge learning signal. Platform-specific learnings from 50+ days of portfolio work. Worktree failure fallback. Remote session awareness. Composition guard.
- 2026-04-13: Initial version with backfill sanity test.
