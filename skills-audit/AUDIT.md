# Skills Audit — May 2026

Audit of all Claude Code skills built by @hbschlac, cross-referenced against 790 hours / 302 sessions of Claude Code usage (Feb–Apr 2026), 8 shipped projects, and open issues.

## Skills Inventory

| Skill | Repo | Status | Last Updated | Issues |
|-------|------|--------|-------------|--------|
| **code-builder** | `hbschlac/code-builder` | Stale — 1 commit, never iterated | Apr 14, 2026 | 0 |
| **mcp-contributor** | `hbschlac/mcp-contributor` | Active — weekly refresh running, but 7 open issues unfixed | Apr 17, 2026 (code); May 10 (auto-refresh) | 7 |
| **managed-agents-pulse collector** | `hbschlac/managed-agents-pulse/collection-agent/SKILL.md` | Active — collecting data | Apr 14, 2026 | 0 |

---

## 1. Use Cases / Pain Points Not Met

### code-builder never actually ran its learning loop
The weekly sync (the skill's core differentiator) requires manual cron setup. Unlike mcp-contributor, which has GitHub Actions running every Sunday, code-builder's sync has **never executed after the initial backfill**. The 12 learnings from April 13 are frozen. After 790 hours and 335 commits of coding work, the skill has learned nothing new. This defeats the entire "gets sharper over time" thesis.

### No skill covers your most-used workflows
Usage breakdown from your Claude Code stats:
- **65% of April** — personal portfolio & tools (schlacter.me, hannah-portfolio repo, 80+ commits)
- **21% of April** — interior design tool (100+ build log entries, private repo)
- **95% of March** — personal portfolio & tools

Yet **no skill exists for portfolio development** or interior design work. code-builder activates generically on coding tasks, but it doesn't encode patterns specific to your Next.js/Vercel/Tailwind stack, your content architecture (projects.ts data model, [slug] routing, case study pages), or your deployment workflow.

### mcp-contributor's open issues demonstrate skill rot
Issues #1–3 (filed manually from dry-run testing on Apr 17) identify real structural problems:
- S4 is titled "SDK workflow" but applies to all non-spec repos including Inspector (#3)
- S6 repo map is missing Inspector, Registry, ext-* repos (#2)
- No cross-reference from capability questions to S11.7 lifecycle (#1)

These have been open for **25 days** with no fix. Meanwhile, the automated refresh has detected the same 11 anchor misses **four consecutive weeks** (issues #4–7) without resolution.

### No skill for research/analysis workflows
You built 4 research-heavy projects (workspace-ai-research, twitch-community-research, managed-agents-pulse, claude-wishlist) that all follow the same pattern: scrape sources → classify/categorize → dashboard. No skill encodes this repeatable pipeline.

---

## 2. Tasks That Could Be Done Faster or Better

### code-builder's 5-draft approach burns tokens on trivial work
The judgment gate defaults to single-pass, which is correct. But the parallel-signal matrix has no **token budget awareness**. Running 5 parallel agents on a 200-line feature change could burn 500K+ tokens. The skill should factor estimated token cost into the judgment gate, and optionally reduce to N=3 for medium-complexity tasks instead of always N=5.

### code-builder doesn't verify worktree cleanup
Step 6 says "Clean up worktrees. Delete losing branches." but has no verification step. If cleanup fails silently (disk full, permission error, git lock), you accumulate orphaned worktrees. Should add a `git worktree list` check after cleanup.

### mcp-contributor's refresh.sh has a heading-format bug
The grep pattern in `refresh.sh` expects headings like `## Step 11.1:` but SKILL.md actually uses `### 11.1 Design Principles`. This causes 11 false-positive anchor misses every week. The bug is trivial to fix but has been firing for 4 consecutive automated runs, creating noise issues that obscure real drift signals.

### Run logging path may not exist
code-builder logs to `~/.claude/skills/code-builder/runs/{date}-{slug}.md` but never calls `mkdir -p` on that path. First run in a fresh environment will fail silently or error.

### managed-agents-pulse collector runs sequentially when it could parallel
The SKILL.md for the collection agent fetches Reddit (pullpush.io) then HN (Algolia) sequentially. These are independent API calls that could be parallelized, cutting collection time roughly in half.

---

## 3. Things Asked That Couldn't Be Done

### code-builder can't work outside git repos
Explicitly acknowledged in the skill — forces single-pass when not in a git repo. But many of your projects start as quick prototypes before `git init`. The skill should offer to initialize a repo rather than silently degrading.

### Cross-repo learning is bounded but never actually runs
code-builder's sync Source E ("cross-repo mining") uses `git fetch --all` with `--max-count=50` and author filter. But since the sync has never run beyond initial backfill, this cross-pollination has never happened. Your patterns from muse-shopping never informed your portfolio work, and vice versa.

### insight-detector.py is a stub
The Claude Code insights dashboard has `insight-detector.py` that "emits `suggestions[]` (empty). Intended for v2 pattern mining." This pattern-mining feature was never built, so the dashboard shows usage stats but no actionable insights about workflow patterns.

### No skill can help with non-code PM work
You're a PM who codes, but Claude Code skills only cover the coding side. Writing specs, experiment design, stakeholder communication, data analysis — none of these have skills, even though they're likely a significant portion of your Claude Code usage.

---

## 4. Blindspots

### The portfolio site is your primary product but has no dedicated skill
schlacter.me/hannah-portfolio has 80 commits, 20 route directories, and represents the majority of your Claude Code time. It has a CLAUDE.md and AGENTS.md, but no portable skill that encodes your:
- Content data model (projects.ts structure, case study template)
- Visual design system (warm neutral palette, Inter font, minimal UI)
- Deployment patterns (Vercel, App Router, server components)
- Page creation workflow (new case study = route dir + content entry + components)

A skill here would dramatically reduce the "explain my stack to Claude" overhead on every new session.

### code-builder and mcp-contributor don't know about each other
If you're contributing to MCP (mcp-contributor active) and writing code (code-builder should activate), there's no coordination. code-builder might try to spawn 5 parallel drafts while mcp-contributor is guiding a specific PR workflow. Skills should declare conflicts or precedence.

### No quality gate on skill activation announcements
Both skills require an activation banner, but neither tracks whether the banner was actually useful to you. If you're seeing "code-builder activated — single pass" 50 times a day, that's noise. The announcement should be suppressible or adaptive.

### Stale learnings aren't flagged
code-builder's learnings are frozen at April 13 with 12 bullets. There's no mechanism to flag that learnings are stale. After 30 days without a sync, the skill should warn that its learnings may be outdated.

### No skill for Vercel deployment patterns
You deploy everything to Vercel, but no skill encodes your Vercel-specific patterns: environment variables, preview deployments, edge runtime usage, build configuration. This is a cross-cutting concern across multiple projects.

### The Claude Skills concept product is disconnected from your actual skills
You built skills-roan.vercel.app to make Claude's instruction system accessible to non-engineers, but it's not connected to your actual Claude Code skill development workflow. There's no feedback loop between the concept product and the real skills you're building.

---

## Priority Fixes (Included in This Audit)

### P0 — Fix mcp-contributor refresh.sh anchor bug
**File:** `patches/mcp-contributor/refresh-anchor-fix.sh`
The grep pattern needs to match actual SKILL.md heading formats. Fixes issues #4–7 (4 weeks of false positives).

### P0 — Triage 6 new MCP pages
**File:** `patches/mcp-contributor/new-sources.yml`
6 pages detected by refresh but not yet added to sources.yml.

### P1 — Fix mcp-contributor structural issues (#1–3)
**File:** `patches/mcp-contributor/structural-fixes.md`
Specific edits for S1.5, S4 title, and S6 repo map.

### P1 — Add GitHub Actions to code-builder
**File:** `patches/code-builder/weekly-sync.yml`
Mirrors mcp-contributor's working cron pattern.

### P1 — Fix code-builder edge cases
**File:** `patches/code-builder/improvements.md`
mkdir -p for run logs, worktree cleanup verification, token budget awareness, stale learning warning.

### P2 — New portfolio-dev skill
**File:** `new-skills/portfolio-dev/SKILL.md`
Covers Next.js/Vercel/Tailwind stack patterns, content data model, case study workflow, deployment.
