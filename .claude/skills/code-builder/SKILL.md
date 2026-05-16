# code-builder

A Claude Code skill that raises code quality by matching effort to complexity — single-pass for quick fixes, parallel drafts for complex work — with session safety, debug escalation, and project-adaptive scoring.

## Activation

Triggers on any dev task: build, fix, feature, refactor, debug. Does NOT activate for research, reading, writing, design, or meta tasks.

When uncertain, activate — a single-pass run costs nothing extra, while skipping a genuine dev task is worse.

## Banner

Before any work, print exactly one line:

```
code-builder: {mode} · {reason ≤15 words}
```

Modes: `single-pass`, `parallel-3`, `parallel-5`, `debug-escalation`.

## Session Safety (always runs first)

Before writing any code:

1. Run `git status` — if there are uncommitted changes from another session, **stop and warn the user**. Never silently overwrite or delete uncommitted work.
2. Run `git stash list` — report any stashes that might contain work from other sessions.
3. If the task touches files modified in the last commit by a different author/session, flag the overlap before proceeding.

This prevents the "deleted by other session" problem. When in doubt, stash existing work before starting.

## Judgment Gate

Decide the mode using these signals:

| Signal | Single-pass | Parallel |
|--------|-------------|----------|
| Lines of code | <30 | >30 |
| Files touched | 1 | >1 or new file |
| Design ambiguity | One obvious approach | Multiple valid approaches |
| Task type | Bug fix, typo, config | Feature, refactor, greenfield |

**Hard overrides:**
- Greenfield prototype → `parallel-5`
- Live debugging / non-git context → `single-pass`
- Same area fixed 3+ times in recent history → `debug-escalation` (see below)

**Default parallel count is 3, not 5.** Escalate to 5 only when the task is genuinely ambiguous (multiple valid architectures). Most real-world tasks need at most 3 perspectives — the original skill's 5-draft default added overhead without proportional quality gain.

## Debug Escalation Mode

Activates when: the same file/area has been fixed 3+ times in recent git log, OR the user says something like "this still doesn't work" or "tried that already."

Instead of generating parallel implementations of the same approach:

1. **Root-cause first.** Read the relevant code, recent diffs, and error context. Form a hypothesis about WHY previous fixes failed before writing any code.
2. **Print the hypothesis** as a single sentence the user can confirm or redirect.
3. **Write a minimal reproduction** or diagnostic (console.log, test case, curl command) that proves/disproves the hypothesis.
4. **Only then fix.** If the hypothesis was wrong, repeat from step 1 (max 3 cycles before asking the user for more context).

This prevents the "10 sequential commits attacking the same bug" pattern.

## Parallel Execution

Each draft gets a distinct bias:

| Draft | Bias |
|-------|------|
| 1 | Simplest possible — fewest lines, minimal abstraction |
| 2 | Most idiomatic — matches existing repo patterns exactly |
| 3 | Correctness-focused — edge cases, error paths, defensive |
| 4 | (parallel-5 only) Performance-optimized |
| 5 | (parallel-5 only) Free choice — Claude's best instinct |

Each runs in an isolated git worktree with `isolation: "worktree"`.

## Project-Adaptive Scoring

The rubric weights shift based on project type. Detect the project type from package.json, file structure, and CLAUDE.md.

### Base Rubric (100 points)

| Criterion | Portfolio/UI | API/Backend | Library | CLI |
|-----------|-------------|-------------|---------|-----|
| Correctness | 20 | 25 | 30 | 25 |
| Tests passing | 10 | 20 | 20 | 15 |
| Type checking | 10 | 10 | 15 | 10 |
| Lint compliance | 5 | 5 | 5 | 5 |
| Minimal diff | 15 | 10 | 10 | 10 |
| No unnecessary deps | 5 | 10 | 10 | 10 |
| Reuses existing utils | 10 | 10 | 5 | 10 |
| Follows repo conventions | 15 | 5 | 5 | 10 |
| Scope containment | 10 | 5 | 0 | 5 |

For Portfolio/UI projects: visual consistency and convention-following matter more than test coverage. For libraries: correctness and type safety dominate.

**Claude picks the winner.** Tiebreaker: smallest diff, then most idiomatic (Draft 2).

## Merge Validation

1. **Gap check** — verify the winner covers all requirements; cherry-pick from rejected drafts if needed
2. **Redundancy check** — remove unused imports, dead code, duplicate helpers
3. **Language check** — verify no language confusion (e.g., Python idioms in JS, wrong string escaping). This catches the "Python ate the apostrophe" class of bugs.
4. **Revalidation** — run tests, typecheck, lint on final merged code
5. **Deployment check** — if the project deploys to Vercel/Netlify/etc., verify the build succeeds locally (`npm run build` or equivalent) before committing
6. **Cleanup** — remove losing worktrees and branches

## Run Logging

Log every execution to `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`:

```yaml
---
date: {date}
repo: {repo}
mode: {single-pass|parallel-3|parallel-5|debug-escalation}
winner: {draft number or n/a}
scores: {draft: score, ...}
debug_cycles: {count, if debug-escalation}
session_safety: {clean|stashed|warned}
---
```

## Learning Sync

Weekly (configurable): analyze run logs and post-merge diffs. Update a `learnings` section capped at 30 bullets. Prioritize learnings about:

- Recurring bug patterns in specific repos
- Which project types benefit from parallel vs single-pass
- Debug escalation success rate
- Common language-confusion errors
