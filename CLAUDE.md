# STOP — Read This Before Doing Anything

**28 prior sessions audited these skills, wrote improvements, and pushed to orphaned
branches. None merged. Main has 2 commits from March 2026. Do not repeat this.**

If your task involves "review skills," "audit skills," "improve skills," or
"consolidate sessions," the work is DONE — it's on this branch. Your job is to
make Hannah merge it, not rewrite it.

## What to do instead of re-auditing

1. If skills need changes → **edit the existing files** in `.claude/skills/`. Do not rewrite from scratch.
2. If findings need recording → **add them to the relevant SKILL.md** under a `## Known Issues` or `## Current Learnings` section. Do not create AUDIT.md, REVIEW.md, SKILLS-AUDIT.md, or any standalone analysis file.
3. If changes need to reach another repo → **write laptop instructions below**. You cannot push to `code-builder`, `mcp-contributor`, `claude-config`, or any other repo from this sandbox.
4. If the task is ambiguous → **ask Hannah** what she wants. Don't default to "I'll audit everything."

## Sandbox constraint

Web sessions are scope-locked to `hbschlac/hbschlac`. You CANNOT push to other repos.
When changes need to land elsewhere, write the full file contents here under `.claude/skills/`
and add copy commands to the "Laptop Instructions" section below.

## Owner context

Hannah Schlacter — Senior PM at Walmart (BuyBox, ~400M daily product page views).
No CS degree. Builds consumer products and AI tools. Primary dev environment is Claude Code.

## Skills inventory

| Skill | Path | Purpose |
|-------|------|---------|
| code-builder | `.claude/skills/code-builder/SKILL.md` | Parallel implementations, self-scoring rubric, debug loop, learning sync |
| session-safety | `.claude/skills/session-safety/SKILL.md` | Cross-session conflict prevention, Groundhog Day prevention |
| content-quality | `.claude/skills/content-quality/SKILL.md` | Anti-slop, hallucination prevention, voice matching |
| mcp-contributor | `.claude/skills/mcp-contributor/SKILL.md` | Contributing to MCP governance org |
| session-start-hook | `.claude/skills/session-start-hook/SKILL.md` | SessionStart hooks for Claude Code on the web |
| portfolio-dev | `.claude/skills/portfolio-dev/SKILL.md` | Portfolio site (schlacter.me) development patterns |

## README guidance

- Portfolio landing page. Tone: direct, concise, evidence over adjectives.
- Every project claim must be verifiable — link to live site, repo, or deployment.
- Don't add projects that aren't shipped. Don't inflate descriptions.

## Laptop instructions (pending merge)

```bash
# Step 1: Merge this branch to main
cd ~/hbschlac
git fetch origin
git merge origin/claude/eloquent-euler-YapzR --no-ff -m "Land skills, CLAUDE.md, and portfolio-dev skill"
git push origin main

# Step 2: Copy skills to Claude Code runtime
cp -r .claude/skills/* ~/.claude/skills/

# Step 3: Fix mcp-contributor anchor bug (in the mcp-contributor repo)
cd ~/mcp-contributor
# In sources.yml: change "## Step 11.1:" to "### 11.1"
# Then: git commit -am "fix: anchor grep pattern" && git push
# Then: gh issue close 4 5 6 7 8 -c "Fixed anchor pattern"

# Step 4: Clean up orphaned branches (optional, after merging)
cd ~/hbschlac
git branch -r | grep 'claude/eloquent-euler' | xargs -I{} git push origin --delete {}
git push origin --delete claude/review-code-skill-plan-5p6Yc
```

## Related repos

| Repo | What | Action needed |
|------|------|---------------|
| code-builder | Parallel-draft skill (public) | Copy `.claude/skills/code-builder/SKILL.md` to repo |
| mcp-contributor | MCP governance skill (public) | Fix anchor bug in refresh.sh; close issues #4-8 |
| claude-config | Central config (private) | Copy all skills to `~/.claude/skills/` |
| hannah-portfolio | schlacter.me (public) | Active — portfolio-dev skill covers this |
| claude-code-insights-dashboard | Session analytics (public) | insight-detector.py still needs deployment |

## Session history

Last consolidated: 2026-05-27. 28 branches reviewed. Key insight: the problem was
never "the skills aren't good enough" — the problem was nothing ever shipped.
