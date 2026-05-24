# hbschlac/hbschlac — GitHub Profile README

This repo contains Hannah Schlacter's public GitHub profile page (`README.md`)
and the canonical Claude Code skill definitions (`.claude/skills/`).

## Owner context

Hannah Schlacter — Senior PM at Walmart (BuyBox, ~400M daily product page views).
No CS degree. Builds consumer products and AI tools. Primary dev environment is
Claude Code.

## The Groundhog Day Rule

Between April and May 2026, **25 separate sessions** audited the same skills,
proposed the same improvements, and pushed to isolated branches that never merged
to main. This cost ~40+ hours of duplicated Claude Code time.

**THIS BRANCH IS THE CONSOLIDATION. All skill files now live on main.**

### Before modifying skills

1. Check `git log --oneline -10` — your changes build on the consolidated work.
2. Do NOT create AUDIT.md, REVIEW.md, or SKILL-AUDIT.md files. Put findings in this file.
3. Do NOT rewrite skills from scratch. Edit the existing files in `.claude/skills/`.
4. Commit to a branch and tell Hannah to merge. Work on orphan branches is useless.

### Before ending a session

- [ ] Changes are committed and pushed
- [ ] If changes need to land in another repo, exact copy commands are in "Laptop Instructions" below
- [ ] No orphaned analysis files
- [ ] Hannah has been told to merge

## Sandbox constraint

Web sessions are scope-locked to `hbschlac/hbschlac`. You CANNOT push to
`code-builder`, `mcp-contributor`, `claude-config`, or any other repo. Write
changes here with explicit laptop instructions for Hannah to apply.

## Skills inventory

| Skill | Path | Purpose | Status |
|-------|------|---------|--------|
| **code-builder** | `.claude/skills/code-builder/SKILL.md` | Parallel implementations, self-scoring rubric, debug loop, learning sync | v5 — consolidated from 25 sessions |
| **mcp-contributor** | `.claude/skills/mcp-contributor/SKILL.md` | Contributing to MCP governance org | v2 — anchor bug documented |
| **content-quality** | `.claude/skills/content-quality/SKILL.md` | Anti-slop, hallucination prevention, voice matching | v2 |
| **session-safety** | `.claude/skills/session-safety/SKILL.md` | Cross-session conflict prevention, Groundhog Day guard | v2 |
| **session-start-hook** | `.claude/skills/session-start-hook/SKILL.md` | SessionStart hooks for Claude Code on the web | v2 — async race condition fix |

### Known issues requiring laptop execution

1. **mcp-contributor anchor bug** — `refresh.sh` greps for `## Step 11.1:` but
   SKILL.md uses `### 11.1 Design Principles`. Fix: update `sources.yml` anchors
   to match actual headings. Close issues #4-8.
2. **code-builder sync has never run** — No GH Action or cron executes the weekly
   learning sync. The skill's self-improvement loop is inert until a runner exists.
3. **Skills must be copied to `~/.claude/skills/`** — Claude Code reads from
   `~/.claude/skills/` at runtime, not from this repo.

## Laptop instructions (pending)

```bash
# 1. Copy skills to Claude Code runtime location:
cp -r .claude/skills/* ~/.claude/skills/

# 2. Fix mcp-contributor anchors (in the mcp-contributor repo):
cd ~/path/to/mcp-contributor
# Update sources.yml: replace "## Step 11.1:" with "### 11.1"
# Then: git commit -am "fix: anchor grep pattern" && git push
# Then: gh issue close 4 5 6 7 8 -c "Fixed anchor pattern"

# 3. Set up code-builder weekly sync (create GH Action or launchd plist)
```

## What matters for README edits

- Portfolio landing page. Tone: direct, concise, evidence over adjectives.
- Every project claim must be verifiable — link to live site, repo, or deployment.
- Don't add projects that aren't shipped. Don't inflate descriptions.

## Related repos

| Repo | What | Status |
|------|------|--------|
| `code-builder` | Parallel-draft skill (public) | v1 in repo; latest version here |
| `mcp-contributor` | MCP governance skill (public) | anchor bug in refresh.sh |
| `claude-code-insights-dashboard` | Session analytics (public) | detector stub needs deployment |
| `hannah-portfolio` | schlacter.me (public) | Active |
| `muse-shopping` | E-commerce platform (public) | Active |
| `libby-hold-monitor` | Kindle x Libby automation (private) | Active |
| `claude-config` | Central config, skills, memory (private) | Active |

## Session history (prevent re-auditing)

Last consolidated: 2026-05-24. 25 branches reviewed and merged into this version.
Key prior audit findings are incorporated into the skills themselves — do not
re-audit. Focus on net-new improvements only.
