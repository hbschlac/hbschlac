# Skill Audit — 2026-05-14

Reviewed: code-builder, mcp-contributor, Claude Skills site (skills-roan.vercel.app)
Data sources: 27 GitHub repos, 20+ Vercel deployments (schlacter.me), commit history, open issues, skill file contents

---

## 1. code-builder

### What it does
Spawns 5 parallel git worktree implementations of the same coding task, scores them on a 100-point rubric, merges the winner. Weekly sync mines run logs to update a "Current learnings" section (capped at 30 bullets).

### What's wrong

| Finding | Evidence | Impact |
|---------|----------|--------|
| **Never updated since creation** | 1 commit (April 14). Zero iteration in 30 days | Skill is frozen at v1; no learnings incorporated from real usage |
| **Sync hasn't run** | "Last synced: 2026-04-13" — over a month stale | The self-improvement loop (the skill's core value prop) is broken |
| **Only 12/30 learnings** | Learnings section is 40% capacity | Missing a month of patterns from active development |
| **Parallel path rarely triggers** | Recent work: content updates, bug fixes, copy rewrites, admin panels — all fall below the judgment gate's "30+ LOC changed" threshold | The 5-draft workflow is designed for greenfield features but the actual workload is incremental |
| **Scoring rubric assumes test infra** | "Tests pass = 15 points" but many portfolio projects lack test suites | 15% of the rubric is ungraded for the most common projects |
| **No content/copy awareness** | Activation says "Do NOT activate for: Writing, design, planning" | Excludes the single largest category of recent work (case study content, page copy, research writeups) |
| **gitDirty deploys not caught** | 14 of 20 recent Vercel deploys show `gitDirty: "1"` | Uncommitted changes shipping to production — merge validation should flag this |
| **Duplicate deployments** | Same commit deployed 2-4x (kindle-libby content = 4 deploys, job-tracker fix = 3 deploys) | No pre-push validation or deploy-once guard |

### What should change → See `skills/code-builder/SKILL.md`

1. **Expand activation to include content-heavy work** — new "content mode" for case studies, copy, research pages (single-pass with content-specific checklist)
2. **Lower parallel threshold for familiar repos** — if repo has been worked on in last 7 days, threshold drops (context is warm)
3. **Add deploy validation step** — check `git status` clean before push; fail if dirty
4. **Make test scoring conditional** — if project has no test command, redistribute 15 points to other criteria
5. **Force sync catchup** — if last sync > 14 days, trigger sync before next run
6. **Add learnings from recent sessions** — 8 new patterns from April-May work
7. **Track duplicate deploy pattern** — learning: always `git stash` or commit before deploy

---

## 2. mcp-contributor

### What it does
Operational playbook for contributing to the Model Context Protocol governance org — spec PRs, SDK patches, SEP drafts. Includes triage decision tree, governance structure, and automated drift detection.

### What's wrong

| Finding | Evidence | Impact |
|---------|----------|--------|
| **4 consecutive drift issues ignored** | Issues #4-#7 (April 19 – May 10), all open, all auto-filed by GitHub Actions | Skill content has been drifting from MCP source docs for a month — the information may now be wrong |
| **3 feature issues unresolved since day 1** | #1 (missing navigation), #2 (repo map gaps), #3 (§4 title scope) | Known defects filed at creation, never fixed |
| **Zero actual contributions logged** | Session log at bottom: only initial scaffolding comment from April 16 | The skill has never been used for its intended purpose |
| **Repo map is incomplete** | Issue #2: missing Inspector, Registry, ext-* repos | Users following the map will miss repositories |
| **§4 titled "SDK workflow" but applies to all non-spec repos** | Issue #3 | Misleading section title creates confusion |
| **No pointer from capability questions to §11.7 lifecycle** | Issue #1 | Users asking "can MCP do X?" won't find the lifecycle docs |

### What should change → See `skills/mcp-contributor/SKILL.md`

1. **Fix all 3 feature issues** — rename §4 to "Repository contribution workflow", add missing repos, add capability→lifecycle pointer
2. **Add a staleness guard** — if drift issues > 2 without resolution, skill announces "⚠ Content may be outdated — run refresh.sh before relying on governance details"
3. **Add "first contribution" fast path** — current skill optimizes for SEP-level contributions but good-first-issues are the realistic entry point
4. **Wire session logging** — append to session log automatically on any contribution action

---

## 3. Blindspot: No skill for the actual primary workload

### The gap
Looking at 20+ recent Vercel deployments and 80+ commits across repos, the dominant work pattern is:

- **Portfolio case study creation** (research → data → dashboard → content → deploy)
- **Feature addition to schlacter.me** (job tracker, jamie-bach admin, claude-code stats)
- **Content iteration** (copy rewrites, screenshot wiring, section tightening)
- **Research data pipelines** (Reddit scraping, feedback analysis, visualization)

None of this work has a skill. code-builder explicitly excludes writing/content. The most-repeated workflow has zero skill support.

### Evidence from deployment patterns
```
May 12  — Add Network tab to job tracker
May 4   — Re-skin jamie-bach: East Coast sail palette
May 4   — Retire old static jamie-bach guide HTML  
May 4   — Add jamie-bach admin: todos, flights, rooms, survey, expenses
May 1   — Rebuild jamie-bach-2026 with admin path + Vercel KV
Apr 28  — Tighten Tinker Flywheel 'so what' section
Apr 23  — Fix job-tracker: checkbox completion and artifact title editing
Apr 17  — add claude-code stats page + homepage teaser
Apr 14  — content(kindle-libby): wire in 2 existing screenshots
Apr 14  — content(claude-wishlist): rewrite copy to match what actually shipped
Apr 14  — content(ldor): populate Prototype section with 4 existing screenshots
Apr 14  — fix(reddit-pulse): actually make GitHub PUTs sequential
```

Every single deployment is portfolio/content work. Zero deployments triggered by code-builder's parallel workflow.

### What should exist → See `skills/portfolio-builder/SKILL.md`

New skill: **portfolio-builder** — optimized for the schlacter.me development cycle.

---

## 4. Claude Skills site (skills-roan.vercel.app)

### Status: Dormant
- 1 deployment ever (from a fork commit by Allen Zhou, not original work)
- Zero updates since creation
- Listed in portfolio as a project but the site itself is stale

### Recommendation
Either sunset the listing or rebuild it as a showcase for the actual skills (code-builder, mcp-contributor, portfolio-builder). The current framing ("Makes Claude's persistent instruction system understandable for non-engineers") is outdated now that Anthropic has shipped native skill support.

---

## 5. Profile README (this repo)

### What's wrong
- Lists only 3 projects (Muse, Claude Skills, Kindle × Libby) but there are now 18 portfolio projects and 27 repos
- "Claude Skills" link points to dormant site
- No mention of code-builder, mcp-contributor, or the research work that dominates recent activity

### What should change → See updated `README.md`
- Lead with the strongest recent work
- Link to live portfolio projects, not dormant sites
- Reflect the actual builder identity shown by deployment history
