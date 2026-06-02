# Skills Audit — June 2, 2026

Comprehensive review of all Claude Code skills across the hbschlac org, based on:
- Full content of both SKILL.md files (code-builder, mcp-contributor)
- 10 open issues on mcp-contributor (7 automated drift reports + 3 manual)
- 9 PRs across repos (recs.community, muse-shopping, libby-hold-monitor)
- 132 commits on hannah-portfolio
- 29 repos in the org, 16 portfolio projects
- Weekly GitHub Actions drift detection logs (April 19 – May 31)

---

## Skill 1: code-builder

**What it does:** Spawns 5 parallel code implementations in isolated worktrees, scores them 0–100 on a rubric, merges the winner, cherry-picks gaps from rejected drafts.

### What's working
- Clear activation triggers and decision logic (parallel vs. single-pass)
- Smart threshold: <10 LOC gets single pass, >30 LOC gets parallel drafts
- Five distinct biases (simplest, idiomatic, readable, performant, instinct) produce real variety
- Scoring rubric is concrete and weighted

### Pain points / unmet use cases

| # | Finding | Evidence | Severity |
|---|---------|----------|----------|
| 1 | **No evidence of logged runs** | `runs/` directory exists but no `.md` logs found in the repo | High |
| 2 | **Learning sections are static** | §A and §B contain hardcoded patterns ("guard nullable responses", "Rules of Hooks") but no mechanism to append from actual sessions | High |
| 3 | **Not activated during largest coding sessions** | recs.community (7 PRs in one night with schema, auth, RLS, and server actions) and hannah-portfolio (132 commits) show no code-builder fingerprints | Critical |
| 4 | **No support for multi-PR workflows** | The recs.community session produced 7 stacked PRs — code-builder only thinks in terms of single tasks, not PR chains | Medium |
| 5 | **No pre-merge validation step** | The scoring rubric checks correctness/tests/linting but doesn't enforce "run the dev server and verify in browser" for UI work | High |
| 6 | **No integration with CI** | muse-shopping's vibe-improver shows autonomous PRs are possible, but code-builder doesn't know how to wait for / react to CI results | Medium |
| 7 | **Rubric doesn't weight security** | RLS policies, auth wiring, CSRF prevention — these showed up in recs.community PRs but the rubric has no security dimension | High |
| 8 | **No project-specific tuning** | A Next.js App Router project has very different "idiomatic" patterns than a Python automation (libby-hold-monitor) — the skill is project-agnostic | Medium |
| 9 | **Sync mechanism never ran** | "Optional weekly learning syncs require scheduling `code-builder-sync`" — no evidence this was ever set up | High |

### What couldn't be done
- The skill can't actually enforce itself. If Claude doesn't pick it up from `~/.claude/skills/`, it silently doesn't activate. No fallback, no "hey, should I run code-builder?"
- Can't operate in Claude Code on the web (this session) because worktree isolation requires local git

### Blindspots
- **No post-merge tracking**: Did the winning draft actually work in production? No feedback loop
- **No diff-size awareness**: The skill should know that its 5-draft approach adds significant token cost and wall-clock time — worth it for greenfield, not for a 3-line bug fix where the threshold is borderline
- **No abort/escalate**: If all 5 drafts score below 40, the skill should flag that the task may need human design input rather than picking the least-bad option

---

## Skill 2: mcp-contributor

**What it does:** Guides contributors through MCP governance — triage, fork-to-PR workflows, SEP lifecycle, SDK contribution patterns, communication protocols.

### What's working
- Extremely thorough governance synthesis (11 sections)
- Automated weekly drift detection via GitHub Actions + `refresh.sh`
- Source coverage map (`sources.yml`) with 89+ URLs categorized
- Real dry-run validation (tested against inspector#832)
- Proper open-source packaging (Apache 2.0, CONTRIBUTING.md, SECURITY.md)

### Pain points / unmet use cases

| # | Finding | Evidence | Severity |
|---|---------|----------|----------|
| 1 | **11 anchor misses have persisted for 7+ weeks** | Every weekly refresh (issues #4–#10) reports the same 11 broken `sources.yml → SKILL.md` heading references since April 19. Never fixed. | Critical |
| 2 | **New pages accumulating without triage** | Grew from 0 → 3 → 6 → 11 → 16 → 19 new MCP pages over 7 weeks. Detection works; remediation doesn't. | Critical |
| 3 | **3 manual issues from April 17 still open** | #1 (§1→§11.7 cross-ref), #2 (§6 repo map missing Inspector/Registry/ext-*), #3 (§4 "SDK workflow" misnaming). All actionable, none addressed. | High |
| 4 | **Drift detection creates issues but nobody acts on them** | 7 identical-structure issues, 0 comments on all of them. The automation loop is open — detect → file issue → ??? | Critical |
| 5 | **No auto-remediation** | `refresh.sh` could fix anchor misses and auto-triage new pages into categories, but it only reports | High |
| 6 | **Spec version frozen at 2025-11-25** | MCP has likely shipped newer spec revisions; references point to a potentially outdated version | Medium |
| 7 | **No actual contribution completed** | The skill was validated via dry-runs but there's no evidence of a real PR submitted to any MCP repo | Medium |
| 8 | **Feature lifecycle page appeared** | `community/feature-lifecycle` is a new page (first detected May 31) that likely supersedes or modifies the SEP process — not yet incorporated | High |

### What couldn't be done
- Can't auto-close stale refresh issues (the GH Action creates but doesn't deduplicate or close resolved ones)
- Can't actually submit PRs to MCP repos (skill only guides, doesn't execute)

### Blindspots
- **Issue noise is drowning signal**: 7 weekly issues with largely the same content. The latest issue should be the canonical one; older ones should auto-close when superseded.
- **No priority ranking of new pages**: `community/feature-lifecycle` is likely high-impact; `seps/2663-tasks-extension` is a reference. They're listed identically.
- **No changelog tracking**: The CHANGELOG.md stops at v0.2.1 but there have been 6 releases (latest v0.2.3)
- **SDK tier changes**: MCP has been adding/promoting SDKs — the skill's §6 repo map is stale

---

## Skill 3: skills-gallery (schlacter.me/projects/claude-skills)

**Status:** Concept product — a pitch for persistent AI instruction sets.

### Finding
This was built before Claude Code had native skills support. Anthropic has since shipped exactly what this concept described. The gallery is now a historical artifact, not an active tool. No changes needed — but the portfolio description should note that Anthropic validated the concept.

---

## Cross-cutting findings

### Sessions that should have been better

| Session | What happened | What code-builder should have done |
|---------|--------------|-----------------------------------|
| recs.community scaffold (May 27) | 7 PRs in one night — schema, auth, RLS, CI, community flow | Parallel drafts for the schema/RLS (security-critical). The migration SQL is one of the hardest things to get right and there's no undo. |
| hannah-portfolio Stuff app (May–June) | Phase 2 with real backend, AI summaries, server-side auth | Multi-file feature with design flexibility — exactly the parallel-draft sweet spot |
| muse-shopping vibe-improver (May 22) | Autonomous PR for CI gate — still in draft | Should have triggered a follow-up: "Draft PR created, CI passed, ready for merge?" |

### Missing skills entirely

| Gap | Why it matters |
|-----|---------------|
| **Portfolio builder** | hannah-portfolio is the most active repo (132 commits). A skill encoding the project schema, component patterns, and deployment flow would save massive context-rebuilding every session. |
| **Project scaffolder** | recs.community was bootstrapped from scratch with Claude generating 7 stacked PRs. A skill that encodes "Hannah's stack" (Next.js 16, Tailwind v4, Supabase, Vercel, App Router, TypeScript) with her conventions would make this repeatable and consistent. |
| **PR shepherd** | 7 open PRs on recs.community, 1 on muse-shopping, 0 merged. No automated review, no merge reminders, no stale-PR handling. |
| **Vibe improver / autonomous improvement** | The muse-shopping vibe-improver PR shows this pattern exists ad-hoc. Formalizing it as a skill that audits any repo for test coverage, CI gaps, dependency drift, and opens targeted PRs would be powerful. |

---

## Implementation plan

Changes are provided as ready-to-deploy files in this repo:

| File | Target repo | What changed |
|------|------------|-------------|
| `skills/code-builder/SKILL.md` | hbschlac/code-builder | Security rubric dimension, abort/escalate logic, post-merge tracking, project-context detection, auto-learning append, browser verification for UI work |
| `skills/mcp-contributor/SKILL.md` | hbschlac/mcp-contributor | Auto-close stale refresh issues, priority-rank new pages, fix §4 naming, expand §6 repo map, add §1→§11.7 cross-ref, update spec version references |
| `skills/mcp-contributor/refresh.sh` | hbschlac/mcp-contributor | Auto-remediate anchor misses, auto-triage new pages, deduplicate/close superseded issues |
