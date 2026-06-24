# hbschlac/hbschlac

This repo is Hannah Schlacter's GitHub profile README and the canonical staging area for Claude Code skills.

## STOP -- Read this before doing anything

Between April 14 and June 23, 2026, **57+ Claude Code web sessions** worked on this repo. 30 (Apr-Jun 4) produced orphaned branches. 14 (Jun 4-23) merged daily skill review PRs. Every PR across all 5 repos has been analyzed. The skills are comprehensive and do not need more review.

**If your task involves "review skills," "audit skills," "improve skills," or "consolidate sessions":**
1. **BLOCKED.** The meta-review circuit breaker in session-safety is BLOCKING. Do not proceed.
2. Execute the Productive Work Accelerator in session-safety instead.
3. If you found ONE specific gap in real work, make a targeted edit (1-3 lines). No full reviews.
4. When done, create a PR via MCP tools and merge it.

## Skills inventory

| Skill | Version | What it does |
|-------|---------|-------------|
| code-builder | v8.8 | Execution engine: parallel drafts, debug loop, visual mode, rapid shipping. Learnings in LEARNINGS.md |
| vercel-ship | v1.7 | Pre-deploy validation for Next.js + Vercel + Docker/k8s + escalation to debug-escalation |
| content-quality | v11 | Anti-AI-slop, voice matching, hallucination prevention, UX copy, wizard flow copy |
| session-safety | v18 | Groundhog Day prevention, BLOCKING review circuit breaker, inline learning capture, productive work routing |
| debug-escalation | v12 | Fix-churn breaker, cross-skill routing, pipeline hardening, invisible downstream failures |
| portfolio-dev | v3.2 | schlacter.me / Next.js portfolio patterns + end-to-end new project workflow |
| session-start-hook | v6 | SessionStart hook creation + hook debugging |
| project-bootstrap | v1.3 | Auto-generate CLAUDE.md + session-start hooks for repos |
| research-pipeline | v1.2 | Scrape, classify, analyze, present research data + Claude API integration |
| mcp-contributor | v4.1 | FROZEN -- zero usage, anchor bug unfixed. Do not iterate. |

## What to work on (not another skill review)

**P0 — Stuck work (oldest first, last updated 2026-06-24):**
- recs.community: 4 open PRs (#4, #5, #6, #7) stuck since May 27 (28 days). Merge or close.
- muse-shopping #1: draft PR stuck since May 22 (33 days). Merge, close, or promote.
- mcp-contributor: 8 identical bot issues (#6-#13, May 3 - Jun 21), all open, zero comments. Disable the weekly cron in `.github/workflows/` or fix the anchor bug in `sources.yml`.

**P1 — Feature work:**
- Build features on kindle-schlacter-me, kindle-connector, or recs.community
- Update the portfolio site (schlacter.me) with new projects (kindle PRs #21-25 shipped Jun 20)
- Set up monitoring/health checks for any deployed project

**P2 — Structural (only if specifically asked):**
- First real code-builder parallel mode run with N=3 and full logging
- Clean up orphaned branches (35+ across hbschlac/hbschlac)

## Active known issues (updated 2026-06-24)

1. **mcp-contributor cron noise (P0).** 8 identical "11 anchor misses" issues (#6-#13, May 3 - Jun 21), all open, zero comments. Root cause: `sources.yml` references `## Step 11.1:` but SKILL.md uses `### 11.1`. Fix: update anchors in `sources.yml` OR disable the cron in `.github/workflows/`. Every session since Jun 5 has documented this; none has fixed it.
2. **recs.community stuck PRs (P0).** PRs #4, #5, #6, #7 open since May 27. #2 and #3 merged Jun 12 (16 days late). The remaining 4 need merge or close.
3. **muse-shopping #1 draft PR (P0).** Created by vibe-improver May 22, now 33 days old. Merge, close, or promote to ready-for-review.
4. **code-builder parallel mode untested.** 9 versions, zero production runs. Requires laptop (web sessions can't do worktrees).
5. **No project has monitoring configured.** Incidents are discovered reactively. Documented since Jun 11 (PR #7), never addressed.

## Sandbox constraint

Web sessions can only push to `hbschlac/hbschlac`. To change other repos, use GitHub MCP tools to create a PR. If MCP tools can't reach the repo, send a PushNotification with exact commands instead of writing laptop instructions.

## README editing rules

- Tone: direct, concise, evidence over adjectives. Hannah writes like a builder, not a marketer.
- Every project claim must be verifiable (live site, repo, or deployment).
- Don't add projects that aren't shipped. Don't inflate descriptions.
