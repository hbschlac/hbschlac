---
name: code-builder
description: >
  Raises the floor of code quality by generating up to 5 parallel implementations
  of the same dev task, self-scoring them against a measurable rubric, and merging
  the winner. For content-heavy and incremental work, runs a streamlined single-pass
  with a fit-for-purpose checklist.
---

# code-builder

## 0. Announcement (every activation)

```
🔧 code-builder activated — [parallel 5x | single-pass | content-mode]. [one-line reason].
```

Always state mode chosen and why before doing anything else.

---

## 1. Activation triggers

### Explicit
- `/code-builder` slash command
- "build this," "fix this bug," "add a feature," "write me a function"
- "5x this" → force parallel
- "just fix it" → force single

### Implicit — code work
- Working directory is a git repo AND Hannah describes coding work
- Hannah shares error stacks or failing logs
- Hannah pastes code requesting changes
- Known project repos receiving modification requests
- "something broke," "this page is broken," "test is failing"

### Implicit — content work (NEW)
- Hannah asks to add/edit/rewrite case study content, page copy, or research writeups
- Hannah asks to wire in screenshots, GIFs, or media to existing pages
- Phrases: "update the copy," "add this section," "tighten the writeup," "populate the page"
- Working in a portfolio or content-heavy repo (hannah-portfolio, build-log, research repos)

### Do NOT activate
- Pure research questions ("how does X work?")
- Brainstorming or planning with no implementation ask
- Meta tasks ("what are my TODOs?")

**Default:** activate when uncertain.

---

## 2. Staleness guard (NEW)

Before entering the judgment gate, check `Last synced:` date below.

- If last sync > 14 days ago AND run logs exist: announce "⚠ Learnings are stale ({N} days). Running catch-up sync first." Then execute §8 (Sync protocol) before proceeding.
- If last sync > 30 days ago: announce staleness but proceed without sync (don't block the task).

---

## 3. Judgment gate

### Mode selection: parallel vs. single-pass vs. content-mode

| Gate | Parallel (N=5) | Single-pass | Content-mode |
|------|----------------|-------------|--------------|
| **Task type** | Feature, refactor, greenfield | Bug fix, targeted change | Copy, content, media wiring |
| **Lines of code** | >30 changed | <10 lines | Any (content-driven) |
| **Files touched** | >1 file OR new file | Exactly 1 existing | Content/page files only |
| **Design space** | Multiple valid architectures | One obviously correct path | Tone/framing choices |
| **Novelty** | New pattern in repo | Existing pattern variation | New section in existing pattern |
| **Risk** | Touches critical paths | Confined to leaf component | Visual/copy only |
| **Phrasing** | Open-ended ("build X") | Specific ("change line 42") | "Rewrite," "add section," "tighten" |

### Warm-context adjustment (NEW)
If the repo was worked on within the last 7 days (check recent git log), lower the parallel threshold:
- Lines: >20 (not >30)
- Rationale: context is warm, iteration is faster, more value from exploring alternatives

### Hard overrides
- Explicit Hannah override → obey
- Not a git repo → force single
- Live debugging with rapid iteration → force single
- Greenfield prototype from scratch → force parallel
- Content-only changes (no logic) → force content-mode

---

## 4. Parallel execution (N=5)

### Prerequisites
- Confirm git worktree support: `git worktree list`
- Confirm project has a working test/build command
- Create 5 isolated worktrees from current HEAD

### Execution
1. Brief each draft identically: full task spec, no hints about other drafts
2. Each draft works in its own worktree
3. No communication between drafts
4. Each draft must reach "done" independently: passing build + tests + typecheck + lint (where available)

### If a draft fails to complete
- Score it as-is with deductions
- Do not discard — partial solutions may have cherry-pickable elements

---

## 5. Single-pass execution

Standard Claude Code workflow. No worktrees. Apply the scoring rubric as a self-check after completion.

---

## 6. Content-mode execution (NEW)

For content-heavy work (case studies, copy, research pages). No worktrees.

### Content checklist (applied after draft)
- [ ] **Accuracy**: claims match source data; no hallucinated stats
- [ ] **Tone consistency**: matches existing page/site voice
- [ ] **Link integrity**: all URLs resolve; no broken internal links
- [ ] **Media wired**: screenshots/GIFs referenced actually exist in public/ or are committed
- [ ] **Mobile readability**: no lines > 80 chars in prose; responsive-friendly markup
- [ ] **SEO basics**: page has title, description, OG meta (if applicable)
- [ ] **No orphan content**: new page is linked from navigation/index

Report: "✓ Content-mode complete. Checklist: {N}/7 passed. {issues if any}."

---

## 7. Scoring rubric

| Criterion | Weight | Measurement | Conditional |
|-----------|--------|-------------|-------------|
| Correctness | 25 | Walk each task requirement; deduct for misses | Always |
| Tests pass | 15 | Project test command; pass=15, any fail=0 | Only if project has test command; otherwise redistribute: +5 correctness, +5 conventions, +5 minimal diff |
| Typecheck clean | 10 | `tsc --noEmit` or equivalent; 0 errors=10 | Only if project uses TypeScript or typed language |
| Lint clean | 5 | Project lint command; 0 warnings=5 | Only if linter configured |
| Minimal diff | 10 | `10 × (min_LOC / this_LOC)` | Always |
| No unnecessary deps | 10 | 0 new=10; each new dep=−3 if not required | Always |
| Reuses existing utilities | 10 | Did draft grep and reuse helpers? | Always |
| Follows repo conventions | 10 | Naming, file structure, import style | Always |
| Scope containment | 5 | Deduct if unrelated files touched | Always |

**Conditional scoring (NEW):** If a criterion doesn't apply (no tests, no TypeScript, no linter), redistribute its points equally across the remaining criteria. Always announce the adjusted rubric: "Rubric adjusted: no test command → +5 correctness, +5 conventions, +5 minimal diff."

### Tiebreakers
1. Smallest diff
2. Draft 2 (most idiomatic by convention)

---

## 7b. Deploy validation (NEW)

Before any `git push` to a branch that triggers Vercel/CI deployment:

1. **Clean working tree**: `git status` must show nothing dirty. If `gitDirty`, stop and ask: "Uncommitted changes detected. Commit or stash before deploying?"
2. **Single push**: Do not push the same commit multiple times. If push succeeded, do not retry.
3. **Post-deploy check**: If Vercel URL is known, wait 60s then confirm deployment state is READY (not ERROR or BUILDING).

Rationale: 14 of 20 recent deploys had gitDirty=1. Multiple commits were deployed 2-4x.

---

## 8. Merge validation (parallel mode)

1. **Gap check:** Walk original task requirements; confirm winner covers each. Cherry-pick from rejected drafts for gaps.
2. **Redundancy check:** Scan for unused imports, dead code, commented-out blocks, debug logs, duplicate helpers; strip findings.
3. **Rerun validation:** Tests + typecheck + lint on final diff.
4. **Deploy validation:** Run §7b checks.
5. **Merge:** Fast-forward if possible; else `--no-ff`.
6. **Clean up:** `git worktree remove` all 5; delete losing branches; keep winner's branch.
7. **Report:** "✓ Merged draft {N}/5 (score {X}/100). {reason}. {Cherry-picks from {Y} | No gaps.} Tests ✓ Types ✓ Lint ✓."

---

## 9. Run log

After every activation, write a log to `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`:

```yaml
---
date: YYYY-MM-DD
repo: owner/repo
mode: parallel | single | content
task: one-line summary
score_winner: N/100
score_range: [low, high]
judgment_override: null | "Hannah said X"
duration_minutes: N
deploy_clean: true | false
---
```

Followed by freeform notes on what went well, what broke, what was surprising.

---

## 10. Sync protocol

**Trigger:** Scheduled cron `0 18 * * 0` (Sundays 6pm) OR on-demand via "code-builder sync" OR forced by staleness guard (§2).

**Window:** Read `Last synced:` date; collect data from that date forward.

**Sources (5):**
1. Run logs (`~/.claude/skills/code-builder/runs/*.md`)
2. Post-merge git diffs (reveals edits made after merge)
3. In-session feedback captured in logs
4. Judgment overrides (`judgment_override` field)
5. Cross-repo mining (bounded: `--max-count=50`, author filter, `--since` window)

**Processing:**
- Pass 1: Count patterns; candidates repeat ≥2 times
- Pass 2: Refine existing learnings (don't blindly append); handle duplicates, contradictions, strengthening
- Pass 3: Prune to hard cap of 30 bullets (remove oldest, fewest citations, superseded)

**Write:** Update `## Current learnings` section. Set `Last synced:` to today. Do not commit automatically.

**Announce:** "🔧 code-builder sync complete — added {N}, refined {M}, pruned {P}. Total learnings: {X}/30."

---

## Current learnings

**Last synced:** 2026-05-14

### §A. Claude Process Failures

1. "Never call `Skill()` from inside a scheduled-task body. Circular dispatch re-triggers on each tick, burning rate limit." (1 citation)

2. "No hardcoded tokens or secrets in client JS — even for internal tools. Anything imported into a `"use client"` module ships to the browser." (1 citation)

3. "Done requires green tests + typecheck, not 'looks right.' Compile-pass alone forces rework loops." (2 citations)

4. "Resolve merge conflicts by re-running tests, not eyeballing. Code was lost 3× in calmar." (1 citation)

5. "Guard nullable KV/API responses before destructuring. Render `<EmptyState />` instead of crashing on null." (3 citations)

6. "Grep for existing helpers before writing new ones. Duplicated utilities drift and compound." (1 citation)

7. "Always check `git status` before pushing. 14/20 recent deploys shipped with uncommitted changes (gitDirty=1), causing inconsistent builds and duplicate deployments." (NEW — deploy audit May 2026, 14 citations)

8. "Do not push the same commit multiple times. If Vercel deploy triggered, wait for it — re-pushing creates duplicate deployments that waste build minutes and create confusion about which is canonical." (NEW — deploy audit May 2026, 6 citations)

### §B. Concrete Code-Level Patterns

9. "Validate + trim `process.env.X` at the read-site. Whitespace variance causes silent misconfiguration." (4 citations)

10. "Floating UI inside scroll/overflow parents needs `position: fixed` + portal, not absolute positioning." (1 citation)

11. "Rules of Hooks, full form: no conditional calls, no hooks in callbacks/effects, no early returns before any hook." (Agent mining, 2026-04-13)

12. "`useEffect` subscriptions/timers/state mutations must return cleanup functions." (Agent mining, 2026-04-13)

13. "Unscale `getBoundingClientRect()` values when an ancestor has CSS transform." (2 citations)

14. "Save editor selection before DOM-mutating modals; restore on close to avoid caret/selection loss." (2 citations)

15. "When wiring screenshots into content pages, verify the file exists in public/ before referencing. Missing images cause silent 404s that only show on deploy." (NEW — content work May 2026, 3 citations)

16. "Vercel KV operations in server actions need explicit error boundaries. KV timeouts return undefined, not errors, causing silent data loss." (NEW — jamie-bach KV rebuild May 2026, 2 citations)

17. "For content rewrites, always read the existing copy first and match the existing voice/tone. Rewrites that shift register feel jarring even if the new copy is technically better." (NEW — tinker-flywheel tightening April 2026, 2 citations)

### §C. Content & Portfolio Patterns (NEW)

18. "Case study pages need a 'so what' — problem→built→learned is a story, not a portfolio piece, unless the learning is specific enough to be falsifiable." (NEW — tinker-flywheel April 2026, 1 citation)

19. "Research dashboards should show methodology before data. Readers who don't trust the collection won't trust the analysis." (NEW — managed-agents-pulse, workspace-ai patterns, 2 citations)

20. "When adding admin features to portfolio sub-apps (job-tracker, jamie-bach), use the same auth pattern as the main site. Inconsistent auth UX confuses the user even when technically correct." (NEW — jamie-bach admin May 2026, 1 citation)
