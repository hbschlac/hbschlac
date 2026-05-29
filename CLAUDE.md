# hbschlac/hbschlac — Skills Repository

This repo is the canonical source for Claude Code skills. Main branch should always have the latest consolidated versions.

**Last consolidated:** 2026-05-29 (from 30 session branches, 100+ Vercel deployments, 29 repos analyzed)

## DO NOT RE-AUDIT

30 prior sessions audited these skills. The audit is done. If your task involves "review skills," "audit skills," or "consolidate sessions," the work is on this branch. Edit the existing files — don't create new audit documents.

## Skills inventory

| Skill | Path | Version | Status |
|-------|------|---------|--------|
| code-builder | `.claude/skills/code-builder/SKILL.md` | v7 | Active — 7 critical gaps fixed (git gate, quorum, language detection, task-size adaptation) |
| vercel-ship | `.claude/skills/vercel-ship/SKILL.md` | v1 | **NEW** — covers 40% of real work (Next.js + Vercel deployment) |
| mcp-contributor | `.claude/skills/mcp-contributor/SKILL.md` | v4 | Active — staleness patches applied, auth section expanded |
| content-quality | `.claude/skills/content-quality/SKILL.md` | v4 | Active — "Claude voice" failure mode added |
| session-safety | `.claude/skills/session-safety/SKILL.md` | v4 | Active — Groundhog Day prevention is blocking |
| portfolio-dev | `.claude/skills/portfolio-dev/SKILL.md` | v2 | Active — covers 65% of actual usage |
| session-start-hook | `.claude/skills/session-start-hook/SKILL.md` | v4 | Stable — no changes needed |
| project-bootstrap | `.claude/skills/project-bootstrap/SKILL.md` | v1 | **NEW** — auto-generates CLAUDE.md for any repo |
| debug-escalation | `.claude/skills/debug-escalation/SKILL.md` | v3 | Active — stops fix-churn cycles |

## What changed in this consolidation (v29→v30)

### New skills
- **vercel-ship:** Pre-deploy validation built from 100+ real Vercel deployments and 13 documented build failures. Key insight: 100% of build failures are TypeScript type errors from interface changes not propagated to all callers. This single check (`tsc --noEmit` before push) would have prevented every failure.
- **project-bootstrap:** Auto-generates CLAUDE.md + .claude/ config from repo analysis. Addresses the fact that muse-shopping (65K LOC), interior-designer-portfolio, and other active repos have zero Claude config.
- **debug-escalation:** Stops fix-churn cycles by forcing root-cause analysis when 3+ fix attempts fail.

### Improved skills
- **code-builder v7:** Git repo check is now a BLOCKING gate (was a suggestion). Added quorum/failure handling for parallel mode. Language/framework detection replaces hardcoded npm/pytest. Quick-fix bypass for <10 LOC changes. Cherry-pick has rollback strategy.
- **mcp-contributor v4:** Replaced all hardcoded values (protocol version, SEP counts, working groups, Discord link) with "check the source" instructions. Added missing repos to repo map. Expanded auth section. Added sponsor-finding playbook.
- **content-quality v4:** Added "Claude voice" failure mode, expanded banned phrases.
- **portfolio-dev v2:** Added vercel-ship cross-references, subdomain documentation, tsc pre-deploy check.

## Sandbox constraint

Web sessions are scope-locked to `hbschlac/hbschlac`. You CANNOT push to other repos. When changes need to land elsewhere, write full file contents here and add copy commands to the laptop instructions below.

## Laptop instructions (after merging this branch to main)

```bash
# Step 1: Merge this branch to main
cd ~/hbschlac && git fetch origin
git merge origin/claude/eloquent-euler-AdUlM --no-ff -m "Land v30 skills consolidation: 9 skills, 3 new, 6 improved"
git push origin main

# Step 2: Copy skills to Claude Code runtime
cp -r .claude/skills/* ~/.claude/skills/

# Step 3: Fix mcp-contributor anchor bug (in the mcp-contributor repo)
cd ~/mcp-contributor
# In sources.yml: change "## Step 11.1:" to "### 11.1"
# Then run: git commit -am "fix: anchor grep pattern in sources.yml" && git push
# Then close noise issues: gh issue close 4 5 6 7 8 -c "Fixed anchor pattern — false positives resolved"

# Step 4: Run mcp-contributor refresh (6+ weeks overdue)
cd ~/mcp-contributor && ./refresh.sh

# Step 5: Add CLAUDE.md to active repos that are missing it
# Use project-bootstrap skill in each repo:
# cd ~/muse-shopping && claude "/project-bootstrap"
# cd ~/interior-designer-portfolio && claude "/project-bootstrap"

# Step 6 (optional): Clean up orphaned branches
cd ~/hbschlac
git branch -r | grep 'claude/eloquent-euler' | grep -v AdUlM | xargs -I{} basename {} | xargs -I{} git push origin --delete {}
```

## Related repos

| Repo | What | Needs |
|------|------|-------|
| hannah-portfolio | schlacter.me (most active, ~40% of work) | CLAUDE.md via project-bootstrap |
| muse-shopping | Shopping platform (65K LOC) | CLAUDE.md via project-bootstrap |
| mcp-contributor | MCP governance skill | Anchor bug fix + refresh.sh run |
| code-builder | Parallel-draft skill | Copy updated SKILL.md from this repo |
| claude-config | Central config (private) | Copy all skills |
| interior-designer-portfolio | Design portfolio | CLAUDE.md via project-bootstrap |
| recs.community | New shared project | CLAUDE.md via project-bootstrap |
| kindle-schlacter-me | Kindle delivery | CLAUDE.md via project-bootstrap |
