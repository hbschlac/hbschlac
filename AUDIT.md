# Skills Audit — May 13, 2026

Meta-audit of all Claude Code skills built by @hbschlac, cross-referenced against
14 Claude Code web sessions (Apr 14 – May 12), two prior audit documents, the
full code-builder SKILL.md (v2), the backfill plan, and commit history across
all branches.

---

## The #1 Finding: The Groundhog Day Problem

**Every session re-audits the same skills, produces improvements on an isolated
branch, and nothing ever merges.** Main has 2 commits from March 2026. Zero PRs
exist. 14 branches of work are orphaned.

| Date | Branch | Work done | Merged? |
|------|--------|-----------|---------|
| Apr 14 | `review-code-skill-plan` | 19K-word backfill plan | No |
| Apr 15 | `oZ6aD` | Rewrote session-start-hook skill | No |
| Apr 21 | `9BrkB` | Improved session-start-hook (deployment patterns) | No |
| Apr 22 | `NZwjg` | Added CLAUDE.md, updated README | No |
| Apr 23 | `OCF48` | Audited code-builder + mcp-contributor | No |
| Apr 25 | `1YmCG` | Updated README skills section | No |
| Apr 28 | `Oiaxw` | code-builder: deploy gate + 26 learnings | No |
| May 1 | `c2gJQ` | README: full portfolio + Claude Code stats | No |
| May 3 | `g9WhT` | code-builder: deploy gate (duplicate of Oiaxw) | No |
| May 4 | `fr1II` | README: real Claude Code usage | No |
| May 5 | `OdhHA` | Cross-skill audit + insight-detector.py | No |
| May 9 | `TZDUi` | code-builder v2: debug loop + pre-flight | No |
| May 11 | `7gZPQ` | Skills arc narrative + CLAUDE.md | No |
| May 12 | `8Exat` | Full skills audit + portfolio-dev skill | No |

**Root cause:** Each web session is sandbox-scoped to `hbschlac/hbschlac`. It
cannot push to the actual skill repos (`code-builder`, `mcp-contributor`,
`claude-config`). So improvements are written as proposals in THIS repo on
throwaway branches. Without a merge step executed from the laptop, the work dies.

**Cost:** ~30 hours of Claude Code time producing duplicated analysis. The same
finding ("code-builder sync never ran") appears in 3+ sessions. The same README
was rewritten 5+ times independently.

---

## Skills Inventory

| Skill | Repo | Status | Core problem |
|-------|------|--------|-------------|
| **code-builder** | `hbschlac/code-builder` | v2 on branch, v1 in repo | Sync never ran; 18 learnings frozen since Apr 13 |
| **mcp-contributor** | `hbschlac/mcp-contributor` | Active but rotting | 7 open issues, 4 weeks of unresolved drift alerts |
| **session-start-hook** | `hbschlac/claude-config` | Improved twice, never landed | Two independent rewrites on orphaned branches |
| **insights-dashboard** | `hbschlac/claude-code-insights-dashboard` | Stub detector | insight-detector.py written on branch, never merged |
| **portfolio-dev** | proposed (8Exat branch) | Never created | Covers 65% of actual usage but doesn't exist |
| **managed-agents-pulse** | `hbschlac/managed-agents-pulse` | Active | Only skill that's actually running |

---

## 1. Use Cases / Pain Points Not Met

### 1a. No skill covers the primary workflow
65% of April usage was personal portfolio/tools work (schlacter.me, hannah-portfolio).
No skill exists for this. code-builder activates generically but doesn't encode:
Next.js App Router patterns, the projects.ts data model, case study page workflow,
Vercel deployment specifics, or the warm-neutral design system.

### 1b. code-builder's learning loop has never executed
The weekly sync — the skill's entire differentiator ("gets sharper over time") — has
never run after the initial April 13 backfill. 30 days of coding signals are unprocessed.
The skill claims 18/30 learnings but hasn't learned anything new since inception.

### 1c. mcp-contributor creates noise without resolution
Automated drift detection fires weekly via GitHub Actions, creates issues, but nobody
resolves them. Issues #4–7 are 4 consecutive weeks of the same 11 anchor misses caused
by a grep pattern bug in `refresh.sh` (expects `## Step 11.1:` but SKILL.md uses
`### 11.1 Design Principles`). The automation detects but doesn't remediate.

### 1d. No skill for non-code PM workflows
Specs, experiment design, stakeholder communication, data analysis — none have skills
despite being a significant portion of Claude usage for a PM who codes.

### 1e. Research pipeline pattern has no skill
4 research projects (workspace-ai-research, twitch-community, managed-agents-pulse,
claude-wishlist) follow the same pattern: scrape → classify → dashboard. No skill
encodes this reusable pipeline.

---

## 2. Tasks Done That Could Be Faster/Better

### 2a. README was rewritten 5+ times independently
Five branches each rewrote the README from scratch without seeing each other's work.
The best version (7gZPQ, May 11) adds the Skills arc narrative, but earlier versions
had elements it dropped (Claude Code stats table, "How I build" section). A CLAUDE.md
with "here's the current README direction" would have prevented all 4 redundant rewrites.

### 2b. Audit work was duplicated 3 times
- Apr 23 (OCF48): Audited code-builder + mcp-contributor
- May 5 (OdhHA): Audited code-builder + mcp-contributor + insights-dashboard
- May 12 (8Exat): Audited code-builder + mcp-contributor + managed-agents-pulse

Each found similar issues. If the first audit had merged and the findings were in
CLAUDE.md, subsequent sessions could have jumped straight to implementation.

### 2c. code-builder was "upgraded" 5 times without landing
Oiaxw (Apr 28), g9WhT (May 3), OdhHA (May 5), TZDUi (May 9) — four separate sessions
improved code-builder, each branching from main (which has the original v1). The best
version (TZDUi) added debug loop + pre-flight + deployment validation. But it doesn't
include the bias win-rate tracking from OdhHA or the auto-discovery from OdhHA. No
single branch has the consolidated best version.

### 2d. 5-draft parallel always runs N=5
The judgment gate has no token budget awareness. A 200-line feature change spawning
5 agents could burn 500K+ tokens. Medium-complexity tasks should drop to N=3. Trivial
tasks shouldn't spawn agents at all.

### 2e. Run log directory creation not guaranteed
code-builder logs to `~/.claude/skills/code-builder/runs/` but never `mkdir -p`s.
First run in a clean environment fails.

---

## 3. Things Asked That Couldn't Be Done

### 3a. Landing changes to actual skill repos
Every session tried to improve skills but could only write to `hbschlac/hbschlac`.
The proxy is scope-locked. This is the fundamental constraint that causes Groundhog Day.

### 3b. Running the code-builder weekly sync
Can't execute the sync without access to `~/.claude/skills/`, the 4 source repo
clones, and git history. The plan (review-code-skill-plan) explicitly noted this:
"Execute §10 from the laptop where those constraints don't apply."

### 3c. Creating new GitHub repos
The backfill plan proposed creating `hbschlac/claude-config` as a private repo.
MCP `create_repository` returned 403 from the sandbox.

### 3d. Setting up GitHub Actions / cron
code-builder needs a sync runner (shell script + GH Action). Can't create workflows
in repos we can't access.

### 3e. Working outside git repos
code-builder forces single-pass when not in a git repo but could offer to `git init`
instead of silently degrading.

---

## 4. Blindspots

### 4a. No integration/merge process exists
The biggest blindspot across ALL prior sessions: nobody designed the process for
getting branch work into main or into the actual skill repos. Every session assumes
"Hannah will do it later" but provides no checklist, no priority order, no merge
instructions. This audit includes an integration playbook to fix this.

### 4b. Skills don't know about each other
code-builder and mcp-contributor can activate simultaneously with no coordination.
code-builder might spawn 5 parallel agents while mcp-contributor is guiding a specific
PR workflow. No skill declares conflicts or precedence.

### 4c. No quality gate on skill activation banners
"code-builder activated — single pass" appearing 50 times a day is noise. The banner
should be suppressible for single-pass mode or adaptive based on frequency.

### 4d. Stale learnings aren't flagged
After 30 days without a sync, code-builder should warn that its learnings may be
outdated. Currently it silently serves stale rules.

### 4e. No Vercel deployment skill
Everything deploys to Vercel, but no skill encodes: env var management, preview
deployment workflow, edge runtime patterns, build config. This is cross-cutting
across all projects.

### 4f. No testing/QA skill
code-builder scores on tests passing but doesn't help write or design tests.
A skill for test generation, coverage analysis, or regression detection is missing.

### 4g. Build-log entries are manual
221 commits of manual build-log entries. A skill could auto-generate entries from
git commits + session transcripts, saving 10-15 min per entry.

### 4h. insight-detector.py was implemented but never deployed
The May 5 session (OdhHA) wrote a complete implementation with 8 pattern detection
algorithms — but it's on an orphaned branch. The live dashboard still shows the stub.

---

## 5. Consolidated Improvement Plan

### Tier 0 — Break the Groundhog Day cycle (this session)
- [x] Write this meta-audit identifying the integration failure
- [x] Create CLAUDE.md that gives future sessions full context
- [x] Create INTEGRATION-PLAYBOOK.md with step-by-step laptop instructions
- [x] Consolidate best code-builder SKILL.md (v3) from all 5 iterations
- [x] Consolidate best README from all 5 branch attempts
- [x] Push to branch with merge-ready state

### Tier 1 — Land from laptop (Hannah, ~2 hours)
1. Merge this branch to main (README + CLAUDE.md + AUDIT.md)
2. Cherry-pick code-builder v3 SKILL.md into `hbschlac/code-builder`
3. Fix mcp-contributor refresh.sh anchor bug (the grep pattern — 5 min fix)
4. Close mcp-contributor issues #4-7 (all caused by the anchor bug)
5. Resolve mcp-contributor issues #1-3 (structural fixes documented in OdhHA)
6. Copy insight-detector.py from OdhHA branch into insights-dashboard repo
7. Set up code-builder sync runner (GH Action or launchd plist)

### Tier 2 — New skills (laptop, ~1 day)
1. Create portfolio-dev skill (proposed in 8Exat, covers 65% of usage)
2. Create Vercel deployment skill (cross-cutting, addresses 4e)

### Tier 3 — Systemic improvements (ongoing)
1. Add cross-skill conflict declarations
2. Implement token budget awareness in code-builder parallel path
3. Build auto-remediation into mcp-contributor drift detection
4. Run first code-builder weekly sync and validate learning loop
5. Evaluate skill effectiveness (holdout-commit eval, live-task precision/recall)
