# hbschlac/hbschlac

This repo is Hannah Schlacter's GitHub profile README and the canonical staging area for Claude Code skills.

## STOP -- Read this before doing anything

Between April 14 and June 17, 2026, **43+ Claude Code web sessions** audited and improved these skills. 30 sessions (Apr-Jun 4) produced orphaned branches. 13 sessions (Jun 4-17) merged daily review PRs. The skills are comprehensive. They do not need more review.

**If your task involves "review skills," "audit skills," "improve skills," or "consolidate sessions":**
1. **Do not do a full review.** The meta-review circuit breaker in session-safety is BLOCKING.
2. If you found ONE specific gap in real work, make a targeted edit.
3. EDIT existing skill files. Do not rewrite from scratch.
4. When done, create a PR via MCP tools and merge it.

## Skills inventory

| Skill | Version | What it does |
|-------|---------|-------------|
| code-builder | v8.7 | Execution engine: parallel drafts, debug loop, visual mode, rapid shipping. Learnings in LEARNINGS.md |
| vercel-ship | v1.7 | Pre-deploy validation for Next.js + Vercel + Docker/k8s + escalation to debug-escalation |
| content-quality | v11 | Anti-AI-slop, voice matching, hallucination prevention, UX copy, wizard flow copy |
| session-safety | v17 | Groundhog Day prevention, BLOCKING review circuit breaker, cross-repo execution |
| debug-escalation | v12 | Fix-churn breaker, cross-skill routing, pipeline hardening, invisible downstream failures |
| portfolio-dev | v3.2 | schlacter.me / Next.js portfolio patterns + end-to-end new project workflow |
| session-start-hook | v6 | SessionStart hook creation + hook debugging |
| project-bootstrap | v1.3 | Auto-generate CLAUDE.md + session-start hooks for repos |
| research-pipeline | v1.2 | Scrape, classify, analyze, present research data + Claude API integration |
| mcp-contributor | v4.1 | FROZEN -- zero usage, anchor bug unfixed. Do not iterate. |

## What to work on (not another skill review)

**High-priority (stuck work):**
- Merge or close muse-shopping #1 (draft PR, 30+ days old)
- Disable mcp-contributor cron (8+ identical unactioned issues) or fix the anchor bug

**Feature work:**
- Build features on kindle-schlacter-me, kindle-connector, or recs.community
- Update the portfolio site (schlacter.me) with new projects
- Set up monitoring/health checks for any deployed project

**Structural (only if specifically asked):**
- First real code-builder parallel mode run with N=3 and full logging
- Clean up orphaned branches (35+ across hbschlac/hbschlac)

## Active known issues

1. **mcp-contributor anchor bug.** refresh.sh grep expects `## Step 11.1:` but SKILL.md uses `### 11.1`. Creates false-positive issues weekly. Fix: update sources.yml anchors (requires laptop, 5 min).
2. **mcp-contributor cron noise.** 8+ identical "11 anchor misses" issues filed, all unactioned. Disable the cron or fix the bug.
3. **code-builder parallel mode untested.** 8 versions, zero production runs. First run should be N=3 on laptop where worktrees work.
4. **No project has monitoring configured.** Incidents are discovered reactively.
5. **muse-shopping #1 draft PR.** Created by vibe-improver, 30+ days in draft limbo.

## Sandbox constraint

Web sessions can only push to `hbschlac/hbschlac`. To change other repos, use GitHub MCP tools to create a PR. If MCP tools can't reach the repo, send a PushNotification with exact commands instead of writing laptop instructions.

## README editing rules

- Tone: direct, concise, evidence over adjectives. Hannah writes like a builder, not a marketer.
- Every project claim must be verifiable (live site, repo, or deployment).
- Don't add projects that aren't shipped. Don't inflate descriptions.
