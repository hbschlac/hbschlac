# hbschlac/hbschlac — GitHub Profile README

This repo contains Hannah Schlacter's public GitHub profile page (`README.md`)
and Claude Code skill definitions (`.claude/skills/`).

## Owner context

Hannah Schlacter — Senior PM at Walmart (BuyBox, ~400M daily product page views).
No CS degree. Builds consumer products and AI tools. Primary dev environment is
Claude Code (~800+ hours, 300+ sessions, 8 shipped projects).

## DO NOT REPEAT: The Groundhog Day Problem

Between April 14 and May 17, 2026, **18 separate sessions** audited the same
skills, proposed the same improvements, and pushed to isolated branches that
never merged to main. Main still has only 2 commits from March 2026.

**If you are about to:**
- Audit skills → STOP. Read this file. The audit is done (see Skills section below).
- Rewrite the README → STOP. Check existing branches first: `git branch -a | grep claude`
- Improve code-builder → STOP. v4 is in `.claude/skills/code-builder/SKILL.md` on this branch.
- Create an AUDIT.md or REVIEW.md → STOP. Put findings in this CLAUDE.md instead.

**The work exists. The problem was integration, not analysis.**

## Sandbox constraint

Web sessions are scope-locked to `hbschlac/hbschlac`. You CANNOT push to
`code-builder`, `mcp-contributor`, `claude-config`, or any other repo. If you
need to change those repos, write the changes here with explicit laptop
instructions for Hannah to apply.

## Skills inventory (current as of May 17, 2026)

| Skill | Location | Status | Purpose |
|-------|----------|--------|---------|
| **code-builder** | `.claude/skills/code-builder/SKILL.md` | v4 (this branch) | Parallel implementations, self-scoring, learning loop |
| **mcp-contributor** | `.claude/skills/mcp-contributor/SKILL.md` | v2 (this branch) | Contributing to MCP governance org |
| **content-quality** | `.claude/skills/content-quality/SKILL.md` | v2 (this branch) | Anti-slop, hallucination prevention, voice matching |
| **debug-escalation** | `.claude/skills/debug-escalation/SKILL.md` | v2 (this branch) | Root-cause analysis for fix churn |
| **session-safety** | `.claude/skills/session-safety/SKILL.md` | v2 (this branch) | Cross-session conflict prevention |

### Known issues (awaiting laptop execution)

1. **code-builder sync has never run** — No GH Action or cron exists. The learning
   loop (the skill's core differentiator) is inert since Apr 13 backfill.
2. **mcp-contributor refresh.sh anchor bug** — grep expects `## Step 11.1:` but
   SKILL.md uses `### 11.1 Design Principles`. Causes false-positive drift alerts.
3. **Skill files need to be copied to ~/.claude/skills/** — The canonical versions
   are in this repo but Claude Code reads from `~/.claude/skills/` at runtime.

## What matters for README edits

- Portfolio landing page. Tone: direct, concise, evidence over adjectives.
- Every project claim must be verifiable — link to live site, repo, or deployment.
- The "Skills arc" section tells a specific narrative: designed the concept before
  Anthropic shipped it, then built production skills. Keep this arc intact.
- Don't add projects that aren't shipped. Don't inflate descriptions.

## Related repos

| Repo | What | Status |
|------|------|--------|
| `code-builder` | Parallel-draft skill (public) | v1 in repo; v4 here |
| `mcp-contributor` | MCP governance skill (public) | anchor bug in refresh.sh |
| `claude-code-insights-dashboard` | Session analytics (public) | detector stub needs full impl |
| `hannah-portfolio` | schlacter.me (public) | Active |
| `muse-shopping` | E-commerce platform (public) | Active |
| `libby-hold-monitor` | Kindle x Libby automation | Active |
| `managed-agents-pulse` | Agents research collector (public) | Only skill actually running |

## Deployment

The README renders automatically on github.com/hbschlac. No build step, no CI.
