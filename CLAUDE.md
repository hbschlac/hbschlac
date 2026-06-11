# hbschlac/hbschlac

This repo is Hannah Schlacter's GitHub profile README and the canonical staging area for Claude Code skills.

## STOP — Read this before doing anything

Between April 14 and June 4, 2026, **30+ Claude Code web sessions** audited these skills, produced improvements on isolated branches, and none ever merged to main. This is called the **Groundhog Day problem**. You are reading this because session #31 finally landed a CLAUDE.md on main to break the cycle.

**If your task involves "review skills," "audit skills," "improve skills," or "consolidate sessions":**
1. The skills in `.claude/skills/` are the consolidated output of 30 iterations. They are good.
2. Do NOT create new audit/review documents (AUDIT.md, REVIEW.md, SKILLS-AUDIT.md).
3. EDIT the existing skill files. Do not rewrite from scratch.
4. When done, create a PR via MCP tools and merge it — do not just push to a branch.

## Skills inventory

| Skill | Status | What it does |
|-------|--------|-------------|
| code-builder | v8.1 | Parallel drafts, self-scoring, debug loop, visual mode. Skill precedence table. Learnings in LEARNINGS.md |
| vercel-ship | v1.5 | Pre-deploy validation for Next.js + Vercel + Docker/k8s + post-deploy observability |
| mcp-contributor | v4.1 | MCP governance contribution workflow (FROZEN) |
| content-quality | v7 | Anti-AI-slop, voice matching, hallucination prevention, commit/PR quality, profile README |
| session-safety | v11 | Groundhog Day + cross-repo management + rollback patterns + stacked PR management |
| portfolio-dev | v3.1 | schlacter.me / Next.js portfolio patterns |
| session-start-hook | v5 | SessionStart hook creation for Claude Code on the web |
| project-bootstrap | v1.2 | Auto-generate CLAUDE.md for repos |
| debug-escalation | v7 | Fix-churn cycle breaker + production incident response + proactive monitoring |
| research-pipeline | v1 | Scrape, classify, analyze, present research data |

## Sandbox constraint

Web sessions can only push to `hbschlac/hbschlac`. To change other repos, write full file contents under `.claude/skills/` here, then use GitHub MCP tools to create a PR and merge it to main. If MCP merge isn't available, add laptop instructions below.

## Laptop instructions (pending)

```bash
# Copy skills to Claude Code runtime
cp -r ~/hbschlac/.claude/skills/* ~/.claude/skills/

# Fix mcp-contributor anchor bug + close stale issues (5 min)
cd ~/mcp-contributor
# In refresh.sh: change heading grep from "## Step N.N:" to "### N.N"
# Then: git commit -am "fix: anchor grep pattern" && git push
# Then: gh issue close 4 5 6 7 8 9 10 11 -c "Fixed anchor pattern"
# OR: Disable the cron entirely if mcp-contributor remains FROZEN:
#   Delete/disable .github/workflows/refresh.yml

# Merge recs.community stacked PRs (open 15+ days!)
cd ~/recs.community
gh pr merge 1 --squash  # scaffold
gh pr edit 2 --base main && gh pr merge 2 --squash  # schema
gh pr edit 3 --base main && gh pr merge 3 --squash  # auth
# Continue for PRs 4-7, retargeting each to main after its base merges

# Merge muse-shopping PR (open 20+ days!)
cd ~/muse-shopping
gh pr merge 1 --squash  # PR test gate

# Run first-ever code-builder sync
cd ~/.claude/skills/code-builder && code-builder sync

# Clean orphaned branches
cd ~/hbschlac
git branch -r | grep 'claude/eloquent-euler' | xargs -I{} basename {} | xargs -I{} git push origin --delete {}
```

## Known issues

1. ~~**code-builder learning sync has never run.**~~ **RESOLVED**: GH Action deployed at `.github/workflows/code-builder-sync.yml` (2026-06-10). Learnings extracted to `LEARNINGS.md`.
2. **mcp-contributor refresh.sh anchor bug.** Grep expects `## Step 11.1:` but SKILL.md uses `### 11.1`. Creates false-positive issues weekly.
3. **mcp-contributor has zero real-world usage** despite extensive maintenance.
4. ~~**No skill for PM workflows**~~ **RESOLVED**: code-builder v7.4 adds PRD-to-code section (stacked PR decomposition, vertical slicing, schema-first, out-of-scope patterns). Evidence: recs.community 7 PRs from PRD.
5. ~~**No skill for the research pipeline**~~ **RESOLVED**: research-pipeline v1 created 2026-06-05.
6. **mcp-contributor is FROZEN** — over-invested (v4.1 across 30+ sessions, zero real contributions). No further iteration until: anchor bug fixed, stale issues closed, one real MCP contribution made.
7. ~~**Supabase patterns are uncovered.**~~ **RESOLVED**: code-builder v7.3 and vercel-ship v1.2 include Supabase learnings.
8. ~~**No testing strategy skill.**~~ **RESOLVED**: code-builder v7.4 adds testing strategy section (what to test, test-with-bugfix, gradual CI adoption, CI workflow template). Evidence: kindle-schlacter-me 71 tests, muse-shopping CI gate.
9. ~~**Non-Vercel deployment is barely covered.**~~ **RESOLVED**: vercel-ship v1.4 adds Docker/k8s deployment checklists and debugging patterns. Evidence: kindle-connector deploys Python + Flask to k8s.
10. **No production incident response pattern existed.** debug-escalation v5 now covers production incident triage and resilient fix patterns. Evidence: kindle-schlacter-me PR#2 archive.org outage.
11. ~~**Cross-repo coordination was missing.**~~ **RESOLVED**: session-safety v8 now covers coupled repos (deploy order, shared env vars, sandbox limitations). Evidence: kindle-schlacter-me + kindle-connector coupled PRs.
12. ~~**No performance optimization patterns.**~~ **RESOLVED**: code-builder v7.5 adds performance optimization section (profile→parallelize→benchmark). debug-escalation v6 adds performance escalation. Evidence: kindle-connector PR#1 30s→3s.
13. ~~**No async workflow / state machine patterns.**~~ **RESOLVED**: code-builder v7.5 adds async multi-step workflow section (state transitions, event-time ordering, idempotent handlers). Evidence: kindle-schlacter-me send stages + Resend webhooks.
14. ~~**No domain migration guidance.**~~ **RESOLVED**: vercel-ship v1.3 adds domain migration checklist (repo rename, DNS, OAuth, webhooks, SEO). Evidence: recs.community PR#7 domain rename.
15. ~~**MCP deployment tools were a blindspot.**~~ **RESOLVED**: vercel-ship v1.3 adds MCP tools section for deployment verification. Evidence: every web session has Vercel MCP tools but no skill mentioned them.
16. **recs.community has 7 stacked PRs open for 15+ days with zero merges.** session-safety v9 adds stuck stack detection, v11 adds cross-repo merge workflow. PRs still need to be merged — requires laptop or adding repo to web session via `list_repos`/`add_repo`.
17. **mcp-contributor cron creates false-positive issues weekly.** 6 identical issues May-Jun 2026 (all reporting 11 anchor misses). The cron should be disabled or the anchor bug fixed — "FROZEN" doesn't stop the automation.
18. **muse-shopping #1 is open 20+ days (since May 22).** PR adds test gate for broken-in-prod. Not tracked previously — same stuck-PR pattern as recs.community.
19. **code-builder parallel mode has never been used in production.** 7 versions of the most complex execution mode with zero run logs. First real use should be N=3 with full logging.
20. **No project has monitoring/alerting configured.** Incidents are discovered reactively. debug-escalation v7 adds proactive monitoring patterns but no project has implemented them yet.
21. **Profile README is stale.** kindle-schlacter-me and recs.community are shipped/in-progress but not listed in README.md projects table.

## What to work on next (not another skill review)

The skills have been reviewed and improved 5 times in 6 days (Jun 4-10). They are comprehensive. Before doing another review, consider:

**Productive work that moves projects forward:**
- Merge the recs.community PR stack (#1-7, open 15+ days) — try `list_repos`/`add_repo` first, laptop if needed
- Merge muse-shopping #1 (open 20+ days) — same approach
- Build features on kindle-schlacter-me, kindle-connector, or recs.community
- Update the portfolio site (schlacter.me) with new projects
- Update README.md to reflect kindle-schlacter-me and recs.community
- Set up monitoring/health checks for any deployed project (see debug-escalation v7)
- Set up CI for repos that don't have it yet

**Remaining structural issues (only if specifically asked):**
- mcp-contributor: fix anchor bug or disable the cron (requires laptop, 5 min)
- mcp-contributor: make one real contribution to the MCP org to validate the skill
- First real code-builder parallel mode run with N=3 and full logging
- Clean up orphaned branches (35+ across hbschlac/hbschlac)

**Do NOT do:** another full skill review. If you found a specific gap, make a targeted edit.

## README editing rules

- Tone: direct, concise, evidence over adjectives. Hannah writes like a builder, not a marketer.
- Every project claim must be verifiable (live site, repo, or deployment).
- Don't add projects that aren't shipped. Don't inflate descriptions.
