# code-builder

Raises the floor of Claude's dev output by running **parallel implementations**, **self-scoring them against a measurable rubric**, and merging the winner. Five parallel drafts + objective scoring pushes the floor much higher than single-pass.

**Claude picks the winner, not Hannah.**

---

## When this skill activates

**Any coding task — build, fix, refactor, debug.** Default to activating on code changes. Skip for pure research, writing, planning, or meta-tasks.

**Do NOT activate on:**
- Config-only changes (env vars, package.json fields, CI yaml)
- Content edits (copy, images, data files)
- Sub-5-LOC mechanical changes (rename, import fix, typo) unless Hannah says "5x this"

**When uncertain, activate in single-pass mode.** Costs almost nothing; missing a real dev task is worse.

---

## Announcement (required, every activation)

> 🔧 **code-builder activated** — [parallel, N drafts | single pass]. [≤15-word reason.]

Hannah can override: "5x this" → parallel, "just fix it" → single.

---

## Step 1 — Scope the task

State the task in one line. Identify: files likely to change, greenfield vs. modification, design space (multiple valid approaches or basically fixed?).

---

## Step 2 — Judgment gate

**Default is single.** Escalate to parallel only when **≥2 signals fire** OR **any hard signal fires.**

| Signal | → Parallel | → Single |
|---|---|---|
| LOC estimate | >30 lines | <10 lines |
| Files touched | >1 file or new file | 1 existing file |
| Design space | Multiple valid architectures | One obvious path |
| Novelty | New pattern in this repo | Variation of existing |
| Risk | Critical path (auth, checkout, data) | Leaf component |
| Task type | Feature / refactor / greenfield | Targeted bug fix |
| Phrasing | Open-ended ("build X") | Specific ("change line 42") |

**Hard signals:**
- Hannah override → obey
- Not a git repo → force **single**
- Live debugging / rapid iteration → force **single**
- Greenfield prototype → force **parallel**

**Parallel draft count:**
- Greenfield / high design-space → **N=5**
- Modification with multiple approaches → **N=3**

---

## Step 3a — Parallel path

### Environment check

Run `git rev-parse --git-dir` to confirm git repo. If it fails, downgrade to single with explanation.

### Spawn drafts

Spawn **N Agent calls in a single message**, each with:
- `isolation: "worktree"` — each draft gets its own worktree branch
- `run_in_background: true`
- `subagent_type: "general-purpose"`

**Draft differentiation (N=5):**
1. Simplest possible — fewest lines, no abstractions
2. Most idiomatic to this repo — match existing patterns exactly
3. Optimize for readability — clearest naming, smallest functions
4. Optimize for performance / correctness on edge cases
5. Free choice — best instinct

**Draft differentiation (N=3):**
1. Simplest possible — fewest lines
2. Most idiomatic to this repo
3. Free choice — best instinct

Each draft instruction: "You are one of N parallel drafts. Commit your work on the worktree branch. Report: approach summary (2 lines), files touched, LOC added/removed, commit SHA, edge cases handled."

Wait for all to complete. Score survivors if any fail.

### Score each draft (100 points)

| Criterion | Weight | How to measure |
|---|---|---|
| Correctness | 25 | Walk each requirement; deduct for misses |
| Tests pass | 15 | Run project's test command. Pass=15, fail=0. No tests → redistribute to Correctness (40 total) |
| Typecheck clean | 10 | `tsc --noEmit` or equiv. 0 errors = 10 |
| Lint clean | 5 | Project's lint command. 0 warnings = 5 |
| Minimal diff | 10 | `10 × (min_LOC / this_LOC)` |
| No new deps | 10 | 0 new = 10; each new = −3 unless required |
| Reuses existing utils | 10 | Did it grep for and reuse existing helpers? |
| Repo conventions | 10 | Naming, file structure, import style |
| Scope containment | 5 | Deduct if unrelated files touched |

**Tiebreakers:** (1) smallest diff, (2) most-idiomatic draft.

### Merge validation

1. **Gap check.** Re-read original task. Walk each requirement against winner's diff. Cherry-pick from losers if any solved a gap the winner missed.
2. **Redundancy check.** Strip unused imports, dead code, debug logs, duplicate helpers.
3. **Rerun tests + typecheck + lint.**
4. **Merge** winner's branch (fast-forward if possible).
5. **Clean up** all worktrees. Delete losing branches. Keep winner's branch.
6. **Report:**
   > ✓ Merged draft {N}/{total} (score {X}/100). {≤15-word reason.} Tests ✓ Types ✓ Lint ✓.

## Step 3b — Single path

Do the task. Skip to Step 4.

---

## Step 4 — Log the run

Write `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`:

```md
---
date: YYYY-MM-DD
task_slug: dark-mode-journal-editor
repo: hannah-portfolio
judgment: parallel | single
judgment_override: null | "single → parallel"
winner_draft: 3
winner_score: 82
cherry_picks_from: [1]
environment: local | web
---

## Task
> verbatim task description

## Judgment
[Why parallel or single. 1-2 sentences.]

## Drafts (parallel only)
### Draft N — [bias] ⭐ WINNER (if applicable)
- Approach: [2 lines]
- Files: [list] (LOC count)
- Score: X/100 (breakdown)
- SHA: abc1234

## In-session feedback from Hannah
- [verbatim quotes]

## Notes
[Anything unusual — timeouts, environment issues, override reasons]
```

**If running in a web/remote environment** where `~/.claude/skills/` doesn't persist: log to `{repo}/.claude/code-builder-runs/{date}-{slug}.md` instead and note in the log that it's repo-local.

---

## Syncing learnings

**Trigger:** Hannah says "code-builder sync" or `/code-builder sync`. No cron — syncs are on-demand only.

### Sync workflow

1. Read `Last synced:` date below. Read all `runs/*.md` since that date.
2. For each run's winner_sha, check post-merge diffs: `git log {sha}..HEAD --oneline -- <files>`. This reveals what Hannah silently edited after merge.
3. Count patterns (≥2 repetitions → candidate learning). Refine existing learnings (deduplicate, supersede contradictions, strengthen matches). Prune to **30 bullets max**.
4. Update the `## Current learnings` section. Update `Last synced:` date.
5. Announce: `🔧 code-builder sync — added {N}, refined {M}, pruned {P}. Total: {X}/30.`

---

## Current learnings

Last synced: 2026-06-01 (includes April backfill + May 2026 commit mining)

*If a repo's CLAUDE.md contradicts a rule below, the repo rule wins.*

### §A. Claude process failures

1. **Never call `Skill()` from inside a scheduled-task body.** Circular dispatch burns rate limit. (1×: summary:scheduled-tasks-bug-fixer-fix.md)
2. **No hardcoded tokens or secrets in client JS.** Anything in a `"use client"` module or `NEXT_PUBLIC_` ships to the browser. (1×: summary:calmar-upload-security.md)
3. **"Done" requires green tests + typecheck, not "looks right."** Declaring off a compile-pass forces rework 2–3 messages later. (2×: calmar, ramp-resume)
4. **Resolve merge conflicts by re-running tests, not eyeballing.** Code silently lost 3× in calmar. (1×: calmar ff5ac3a)
5. **Guard nullable API responses before destructuring.** Render `<EmptyState />` or early-return. Cross-repo ×3. (3×: calmar, schlacter.me, muse)
6. **Grep for existing helpers before writing a new one.** Calmar had 3× duplicate date-formatting utilities. (1×: calmar pattern mining)
7. **Silent null returns mask real errors — throw with diagnostic messages.** Returning null on failure paths surfaces as opaque errors 2 steps later; throw with the actual reason. (1×: kindle-schlacter-me 028dd3b)
8. **Verify deployed behavior, not just local.** Vercel host-based rewrites in next.config don't fire on deployed builds — use middleware. Config that works in `next dev` may not work in production. (2×: hannah-portfolio jamiesbach subdomain, 2 commits to discover)

### §B. Concrete code-level patterns

9. **Validate + trim `process.env.X` at the read-site.** Whitespace/quoting variance across Vercel/Render/local causes silent misconfig. Cross-repo ×2. (4×: schlacter.me, calmar)
10. **Floating UI inside scroll/overflow needs `position: fixed` + portal, not `absolute`.** Absolute clips inside gallery tiles, mobile sheets, modals. Cross-repo ×2. (1×: calmar, muse)
11. **Rules of Hooks: no conditional calls, no hooks in callbacks/effects, no return before hooks list.** Error surfaces one render later. Cross-repo ×2. (calmar, muse)
12. **`useEffect` with subscriptions/timers/setState must return cleanup.** Missing cleanup = #1 correction in calmar. (4×: calmar)
13. **Unscale `getBoundingClientRect()` when ancestor has CSS transform.** Measurements return in transformed frame. (2×: calmar)
14. **Save editor selection before DOM-mutating modal; restore on close.** Toolbar actions jump to wrong line after modal. (2×: calmar)
15. **Torrent/search results are non-deterministic — encode enough state in IDs to reconstruct.** Can't re-search to find a prior result; seeder counts shift between calls. Pack magnet+title into the ID. (2×: kindle-schlacter-me 6dbd275, 1b0ba87)
16. **Timeout constants need production headroom.** External services slow down; tight timeouts cause false alarms. 8s → 20s for pullpush.io health checks. (1×: hannah-portfolio de53215)
17. **OG images need `metadataBase` for absolute URLs.** Next.js opengraph-image.tsx won't unfurl on iMessage/Slack without it. (1×: hannah-portfolio a231a71)
18. **Cross-repo API contracts need coordinated deploys.** kindle-connector ↔ kindle-schlacter-me: bridge API changes broke the consumer until both were updated. Add back-compat fields; don't remove old fields until consumer is updated. (2×: kindle-connector/kindle-schlacter-me May 29 session)

### §C. Environment & tooling

19. **Worktree branch-name collisions (Claude Code issue #51596).** `isolation: "worktree"` derives branch names from agentId prefix. If a branch from a prior session exists, the worktree silently reuses stale files. Mitigate: delete `agent-*` branches before spawning parallel drafts.
20. **Web/remote sessions don't persist `~/.claude/skills/` state.** Log runs to `{repo}/.claude/code-builder-runs/` when running remotely.
21. **Skills share a 25,000-token budget after compaction.** This skill is ~250 lines loaded. Keep it under 300 to leave room for other skills.

## Meta notes

- N=5 → N=3 default for modifications (May 2026 analysis: most tasks had 2-3 viable approaches, not 5). N=5 preserved for greenfield.
- Cron sync removed. On-demand only — cron never ran in practice (7 weeks gap April–June).
- Activation narrowed: config-only, content-only, and sub-5-LOC changes excluded to reduce false activations.
- Stale project references updated: removed 662-calmar-portfolio, added kindle-connector, kindle-schlacter-me, recs.community.

## Changelog

- **2026-04-13** — Initial backfill. 12 learnings from 4 repos + 13 session summaries.
- **2026-06-01** — Audit + refresh. Added 9 learnings from May 2026 commits (§A7-A8, §B15-B18, §C19-C21). Reduced default N to 3. Removed cron sync. Added web/remote support. Tightened activation rules. Updated project references.
