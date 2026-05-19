# hbschlac/hbschlac — GitHub Profile README

This repo contains Hannah Schlacter's public GitHub profile page (`README.md`)
and Claude Code skill definitions (`.claude/skills/`).

## Owner context

Hannah Schlacter — Senior PM at Walmart (BuyBox, ~400M daily product page views).
No CS degree. Builds consumer products and AI tools. Primary dev environment is
Claude Code.

## The Integration Rule

Between April 14 and May 19, 2026, **20 separate sessions** audited the same
skills, proposed the same improvements, and pushed to isolated branches that
never merged to main. Main had only 2 commits from March 2026.

**This branch fixes that.** All skill files now live on main.

### Before modifying skills

1. Check `git log --oneline -10` — your changes build on the consolidated work.
2. Do not create AUDIT.md, REVIEW.md, or SKILL-AUDIT.md files. Put findings here.
3. Do not rewrite skills from scratch. Edit the existing files.
4. **Commit to a branch and tell Hannah to merge.** The work is useless on an orphan branch.

### Before ending a session

- [ ] Changes are committed and pushed
- [ ] If changes need to land in another repo, exact commands are written below in "Laptop Instructions"
- [ ] No orphaned analysis files

## Sandbox constraint

Web sessions are scope-locked to `hbschlac/hbschlac`. You CANNOT push to
`code-builder`, `mcp-contributor`, `claude-config`, or any other repo. Write
changes here with explicit laptop instructions for Hannah to apply.

## Skills inventory

| Skill | Path | Purpose |
|-------|------|---------|
| **code-builder** | `.claude/skills/code-builder/SKILL.md` | Parallel implementations, self-scoring rubric, debug loop, learning sync |
| **mcp-contributor** | `.claude/skills/mcp-contributor/SKILL.md` | Contributing to MCP governance org |
| **content-quality** | `.claude/skills/content-quality/SKILL.md` | Anti-slop, hallucination prevention, voice matching |
| **session-safety** | `.claude/skills/session-safety/SKILL.md` | Cross-session conflict prevention, Groundhog Day guard |

### Known issues requiring laptop execution

1. **mcp-contributor anchor bug** — `refresh.sh` in the mcp-contributor repo
   greps for `## Step 11.1:` but SKILL.md uses `### 11.1 Design Principles`.
   Fix: update `sources.yml` anchors to match actual headings.
2. **code-builder sync cron does not exist** — No GH Action or cron runs the
   weekly learning sync. The skill's self-improvement loop is inert.
3. **Skill files should be copied to `~/.claude/skills/`** — Claude Code reads
   from `~/.claude/skills/` at runtime, not from this repo.

## Laptop instructions (pending)

```bash
# Copy skills to Claude Code runtime location:
cp -r .claude/skills/* ~/.claude/skills/

# Fix mcp-contributor anchors (in the mcp-contributor repo):
cd ~/path/to/mcp-contributor
# Update sources.yml: replace "## Step 11.1:" with "### 11.1"
# Then commit and push
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
| `claude-code-insights-dashboard` | Session analytics (public) | detector stub needs implementation |
| `hannah-portfolio` | schlacter.me (public) | Active |
| `muse-shopping` | E-commerce platform (public) | Active |
| `libby-hold-monitor` | Kindle x Libby automation (private) | Active |
| `claude-config` | Central config, skills, memory (private) | Active |
