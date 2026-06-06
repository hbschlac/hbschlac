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
| code-builder | v7.3 | Parallel drafts, self-scoring, debug loop, visual mode |
| vercel-ship | v1.2 | Pre-deploy validation for Next.js + Vercel |
| mcp-contributor | v4.1 | MCP governance contribution workflow (FROZEN) |
| content-quality | v5 | Anti-AI-slop, voice matching, hallucination prevention |
| session-safety | v7 | Groundhog Day prevention, cross-session conflict detection |
| portfolio-dev | v3.1 | schlacter.me / Next.js portfolio patterns |
| session-start-hook | v5 | SessionStart hook creation for Claude Code on the web |
| project-bootstrap | v1.2 | Auto-generate CLAUDE.md for repos |
| debug-escalation | v4 | Fix-churn cycle breaker |
| research-pipeline | v1 | Scrape, classify, analyze, present research data |

## Sandbox constraint

Web sessions can only push to `hbschlac/hbschlac`. To change other repos, write full file contents under `.claude/skills/` here, then use GitHub MCP tools to create a PR and merge it to main. If MCP merge isn't available, add laptop instructions below.

## Laptop instructions (pending)

```bash
# Copy skills to Claude Code runtime
cp -r ~/hbschlac/.claude/skills/* ~/.claude/skills/

# Fix mcp-contributor anchor bug (5 min)
cd ~/mcp-contributor
# In refresh.sh: change heading grep from "## Step N.N:" to "### N.N"
# Then: git commit -am "fix: anchor grep pattern" && git push
# Then: gh issue close 4 5 6 7 8 -c "Fixed anchor pattern"

# Run first-ever code-builder sync
cd ~/.claude/skills/code-builder && code-builder sync

# Clean orphaned branches
cd ~/hbschlac
git branch -r | grep 'claude/eloquent-euler' | xargs -I{} basename {} | xargs -I{} git push origin --delete {}
```

## Known issues

1. **code-builder learning sync has never run.** 52+ days since initial backfill. No GH Action exists.
2. **mcp-contributor refresh.sh anchor bug.** Grep expects `## Step 11.1:` but SKILL.md uses `### 11.1`. Creates false-positive issues weekly.
3. **mcp-contributor has zero real-world usage** despite extensive maintenance.
4. **No skill for PM workflows** (specs, experiment design, data analysis). recs.community was built from a PRD but no skill codifies PRD-to-code translation patterns.
5. ~~**No skill for the research pipeline**~~ **RESOLVED**: research-pipeline v1 created 2026-06-05.
6. **mcp-contributor is FROZEN** — over-invested (v4.1 across 30+ sessions, zero real contributions). No further iteration until: anchor bug fixed, stale issues closed, one real MCP contribution made.
7. **Supabase patterns are uncovered.** recs.community uses Supabase heavily (RLS, migrations, auth triggers, security-definer functions). code-builder and vercel-ship now include Supabase learnings (v7.3 and v1.2 respectively).
8. **No testing strategy skill.** kindle-schlacter-me has 71 tests, recs.community has CI but no tests yet. No guidance on what to test, test patterns, or when to add tests.
9. **Non-Vercel deployment is barely covered.** kindle-connector deploys to k8s. Only vercel-ship exists for deployment patterns.

## README editing rules

- Tone: direct, concise, evidence over adjectives. Hannah writes like a builder, not a marketer.
- Every project claim must be verifiable (live site, repo, or deployment).
- Don't add projects that aren't shipped. Don't inflate descriptions.
