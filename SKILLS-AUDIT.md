# Skills Audit — 2026-05-20

Systematic review of all Claude Code skills created by @hbschlac. Covers gap analysis, pain points, blind spots, and concrete improvements shipped in this commit.

---

## Skills Reviewed

| Skill | Repo | Last Updated | Status |
|-------|------|-------------|--------|
| code-builder | hbschlac/code-builder | 2026-04-14 | 1 commit, never iterated |
| mcp-contributor | hbschlac/mcp-contributor | 2026-04-17 (v0.2.3) | 8 open issues, 5 weeks of unaddressed drift |
| skills-gallery | hbschlac/skills-gallery | 2026-04-14 | Static showcase, no skill logic |
| claude-code-insights-dashboard | hbschlac/claude-code-insights-dashboard | 2026-04-17 | Tracks sessions, not skill activations |

---

## Findings: code-builder

### What works
- The parallel-draft concept is sound — 5 isolated implementations with objective scoring genuinely raises the floor on code quality
- The scoring rubric (100-point, 9 criteria) is well-calibrated and measurable
- The learning loop design (weekly sync from run logs + post-merge diffs) is the right architecture for skill improvement over time
- Cherry-picking from losing drafts is a smart gap-filling mechanism

### Pain points not met
1. **Ephemeral environments break the skill entirely.** The skill assumes `~/.claude/skills/` persists across sessions. In Claude Code on the web (ephemeral containers), run logs are lost, learnings can't accumulate, and worktree isolation fails because the container may not have the project repo checked out at cwd.
2. **Worktree prerequisite fails silently in practice.** The skill documents that `isolation: "worktree"` fails when cwd isn't a git repo, but only discovers this *after* attempting to spawn 5 agents. Wasted tokens and time.
3. **No actual parallel runs have happened.** The repo has 1 commit. The "Current learnings" section was backfilled from session summaries, not from real code-builder runs. The learning loop has never been validated end-to-end.
4. **Cross-repo mining hardcodes repo names.** The sync references `662-calmar-portfolio`, `hannah-portfolio`, `muse-shopping`, `libby-hold-monitor` — some of these may not exist or may have moved.

### Tasks that could have been done faster
- **Environment detection should happen first, not after spawning agents.** A single `git rev-parse --git-dir` check before any agent spawning would save the cost of 5 failed spawns.
- **Single-pass mode is underpowered.** When code-builder falls back to single pass, it's just "do the task normally." There's no quality gate, no rubric check, no self-review. The rubric should apply to single-pass output too.

### Things asked that couldn't be done
- Parallel drafts in web/ephemeral sessions (no persistent worktrees)
- Persistent learning accumulation across sessions without a git-backed store
- Cross-repo mining when the session only has access to one repo

### Blind spots
1. **No skill self-test.** No way to verify code-builder is working after installation.
2. **Token budget unaccounted for.** SKILL.md is ~300 lines of dense instruction. With the "Current learnings" section, it consumes significant context window on every activation — even for a one-line typo fix.
3. **Scoring is unvalidated.** The same model generates code AND scores it. No holdout evaluation, no calibration check. A draft could score 90/100 and still be wrong.
4. **No inter-skill awareness.** If working on MCP code, both code-builder and mcp-contributor could activate simultaneously with no coordination.
5. **The 6 deferred evaluations from meta notes have stalled** — holdout-commit eval, N=5 precision/recall, citation-validity lint, token-budget enforcement, stale-rule audit, cross-skill conflict scan. None have been revisited.

---

## Findings: mcp-contributor

### What works
- Comprehensive coverage of MCP governance, SEP lifecycle, and contribution workflows
- The automated `refresh.sh` drift detection with weekly GitHub Actions is excellent infrastructure
- `sources.yml` coverage map with 89 URLs and tiered priorities is well-structured
- Release discipline (6 versions, semantic, with changelogs) is strong
- Dry-run validation before publishing caught real issues

### Pain points not met
1. **5 weeks of drift alerts are piling up unaddressed.** Issues #4-#8 are automated weekly alerts, all open, none triaged. The monitoring works — the response loop doesn't.
2. **11 broken anchor references.** `sources.yml` references headings §11.1-§11.11 that no longer exist in SKILL.md. Every refresh flags the same broken anchors.
3. **Issue #1 unfixed since April 17** — capability questions don't route to §11.7 lifecycle, causing contributors to misclassify existing-capability work as needing SEPs.
4. **Issue #3 unfixed** — §4 is titled "SDK workflow" but actually covers all non-spec repos (Inspector, Registry, etc.).
5. **Issue #2 unfixed** — §6 repo map is missing Inspector, Registry, ext-* repos.
6. **19 medium-priority gaps** in sources.yml remain uncovered.

### Tasks that could have been done better
- **Drift triage should be semi-automated.** The refresh script creates issues but doesn't suggest resolution actions. It could auto-classify new pages by comparing to existing coverage tiers and propose `sources.yml` updates as PRs.
- **Anchor references should be validated at commit time**, not discovered weekly. A pre-commit hook or CI check would catch §11.x reference breakage immediately.

### Blind spots
1. **No usage tracking.** No way to know if anyone (including Hannah) has actually used this skill in a real MCP contribution.
2. **The skill is extremely long.** It covers protocol fundamentals, 7 SEP statuses, 6-tier contributor ladder, 10 SDKs, Working Groups, Interest Groups, Discord rules, licensing, and more. Token cost per activation is very high even for a simple typo PR.
3. **No quick-start path.** A contributor wanting to fix a typo must load the entire governance model, SEP lifecycle, and protocol primer. The skill doesn't tier its content by task complexity.
4. **refresh.sh only checks for drift — not for skill effectiveness.** It validates that SKILL.md matches upstream docs but not that the skill actually helps someone contribute.

---

## Findings: Cross-Skill Systemic Issues

1. **No shared infrastructure.** Each skill independently defines activation banners, logging, syncing. No common patterns.
2. **No skill manifest.** No central registry of installed skills, versions, health status.
3. **No graceful degradation strategy.** Skills either fully activate or fail. No lightweight mode for constrained environments.
4. **No skill-activation metrics.** The insights-dashboard tracks sessions and commits but not skill activations, success rates, or learning velocity.
5. **Portfolio disconnect.** skills-gallery showcases skills conceptually but doesn't distribute them or link to actual SKILL.md files.

---

## Changes Implemented

### code-builder improvements (`.claude/skills/code-builder/SKILL.md`)
- **Environment detection moved to Step 0** — checks git repo + worktree capability before any agent spawning
- **Ephemeral-environment fallback** — detects web/container sessions and adapts (git-backed logging, reduced-scope learning)
- **Single-pass quality gate added** — rubric self-review applies to single-pass output too (subset: correctness, tests, lint, scope)
- **Token budget awareness** — skill now tiers its own content, loading full rubric only for parallel mode
- **Dynamic repo discovery** — cross-repo mining uses `find` and git config instead of hardcoded names
- **Self-test command** — `/code-builder test` validates installation and reports health

### mcp-contributor improvements (`.claude/skills/mcp-contributor/PATCHES.md`)
- **Fixes for all 3 manually-filed issues** (#1, #2, #3)
- **Anchor reference fix plan** for the 11 broken §11.x references
- **Triage recommendations** for the 11 new pages detected in latest refresh
- **Tiered content loading** proposal — load only relevant sections based on task type

### New: Skill manifest (`.claude/skills/manifest.yml`)
- Central registry of all skills with version, health, and activation triggers
- Environment compatibility flags
- Cross-skill conflict declarations
