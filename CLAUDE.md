# hbschlac/hbschlac

This repo is Hannah Schlacter's GitHub profile README and the canonical staging area for Claude Code skills.

## STOP -- Read this before doing anything

Between April 14 and June 23, 2026, **45+ Claude Code web sessions** audited and improved these skills. 30 sessions (Apr-Jun 4) produced orphaned branches. 13 sessions (Jun 4-17) merged daily review PRs. 2 sessions (Jun 17-23) trimmed 584 lines of bloat. The skills are comprehensive. They do not need more review.

**If your task involves "review skills," "audit skills," "improve skills," or "consolidate sessions":**
1. **Do not do a full review.** The meta-review circuit breaker in session-safety is BLOCKING.
2. If you found ONE specific gap in real work, make a targeted edit.
3. EDIT existing skill files. Do not rewrite from scratch.
4. When done, create a PR via MCP tools and merge it.

## Skills inventory

| Skill | Version | What it does |
|-------|---------|-------------|
| code-builder | v8.9 | Execution engine: single-pass, debug loop, visual mode, rapid shipping. MCP integration patterns. Parallel mode collapsed to stub. Learnings in LEARNINGS.md |
| vercel-ship | v1.8 | Pre-deploy validation for Next.js + Vercel + Docker/k8s + concrete MCP deployment workflows |
| content-quality | v11 | Anti-AI-slop, voice matching, hallucination prevention, UX copy, wizard flow copy |
| session-safety | v19 | Groundhog Day prevention, BLOCKING review circuit breaker, Step 0 productive work routing, branch cleanup, scheduled routine templates |
| debug-escalation | v12.1 | Fix-churn breaker, cross-skill routing, pipeline hardening, scheduled routine failure handling |
| portfolio-dev | v3.2 | schlacter.me / Next.js portfolio patterns + end-to-end new project workflow |
| session-start-hook | v6 | SessionStart hook creation + hook debugging |
| project-bootstrap | v1.3 | Auto-generate CLAUDE.md + session-start hooks for repos |
| research-pipeline | v1.3 | Scrape, classify, analyze, present research data + Claude Code session research with WebSearch/WebFetch |
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
- Clean up orphaned branches (54 across hbschlac/hbschlac — commands now in session-safety)
- Reconfigure scheduled routines from "review skills" to health checks/PR hygiene

## Active known issues

1. **mcp-contributor anchor bug.** refresh.sh grep expects `## Step 11.1:` but SKILL.md uses `### 11.1`. Creates false-positive issues weekly. Fix: update sources.yml anchors (requires laptop, 5 min).
2. **mcp-contributor cron noise.** 8+ identical "11 anchor misses" issues filed, all unactioned. Disable the cron or fix the bug.
3. **code-builder parallel mode collapsed.** Stub-only in SKILL.md (full spec in git history). Laptop-only, never tested.
4. **No project has monitoring configured.** Incidents are discovered reactively. Use Vercel MCP tools + WebFetch in scheduled routines for health checks.
5. **muse-shopping #1 draft PR.** Created by vibe-improver, 50+ days in draft limbo. Close or merge.
6. **100% of sessions since Jun 4 did skill reviews, 0% did feature work.** Productive Work Accelerator moved to Step 0 (first thing sessions see). Circuit breaker now sends PushNotification when routines are misconfigured.
7. **Scheduled routines misconfigured.** Routines configured to "review skills" hit the circuit breaker every time. Reconfigure to: health check, PR hygiene, or dependency freshness.
8. **54 orphaned branches.** Branch cleanup commands now in session-safety. Run them.
9. **recs.community 4 stacked PRs open 30+ days.** PRs #4-7 in dependency chain, none merged. Merge #4 first.

## Sandbox constraint

Web sessions can only push to `hbschlac/hbschlac`. To change other repos, use GitHub MCP tools to create a PR. If MCP tools can't reach the repo, send a PushNotification with exact commands instead of writing laptop instructions.

## README editing rules

- Tone: direct, concise, evidence over adjectives. Hannah writes like a builder, not a marketer.
- Every project claim must be verifiable (live site, repo, or deployment).
- Don't add projects that aren't shipped. Don't inflate descriptions.
