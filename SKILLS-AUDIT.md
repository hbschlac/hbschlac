# Skills Audit — May 2026

Cross-skill review based on all recent deployments, open issues, and usage patterns.

## Executive Summary

Three skills built, one actively running (mcp-contributor), one dormant (code-builder), one opening PRs but not closing them (vibe-improver). The biggest systemic issue: **detection without remediation** — drift gets flagged but never fixed, PRs get opened but stay in draft, stubs get created but never completed.

---

## mcp-contributor

### What's working
- Weekly automated drift detection via `refresh.sh` + GitHub Actions
- 39 source URLs tracked with coverage status
- Clean separation: `sources.yml` as the coverage map, `SKILL.md` as the skill, `refresh.sh` as the detector

### What's broken

**11 anchor misses repeating for 6+ weeks (issues #4–#9).** `sources.yml` references `§Step 11.1` through `§Step 11.11` but those headings no longer exist in `SKILL.md`. Every weekly run reports the same 11 misses. Nobody fixes them.

**New MCP pages accumulating unaddressed:**
- Apr 19: 0 → Apr 26: 3 → May 3: 3 → May 10: 6 → May 17: 11 → May 24: 16
- These are real gaps: new SDK charters, client best practices, SEPs for sessionless MCP, task extensions, spec deprecation lifecycle

**Issues #1–#3 (filed Apr 17) still open:**
- #1: No cross-reference from §1 to §11.7 lifecycle (easy fix)
- #2: §6 repo map missing Inspector, Registry, ext-* repos (medium fix)
- #3: §4 titled "SDK workflow" but applies to all non-spec repos (naming fix)

### Fixes needed

1. **Auto-fix anchor misses:** `refresh.sh` should detect when an anchor target is a simple renumber/remap and submit a PR to fix `sources.yml`, not just report it
2. **Auto-triage new pages:** New pages from `llms.txt` should be auto-added to `sources.yml` as `gap-low` with a single consolidating PR, not N separate issues
3. **Consolidate issues:** Replace weekly duplicate issues with one rolling issue that updates in-place, or auto-close when a newer refresh supersedes
4. **Fix the 3 real issues (#1–#3):** These are substantive improvements, not drift — they should be prioritized over the mechanical refresh reports
5. **Add gap-high page ingestion:** 20 medium-priority gap URLs (SDK docs, debugging, security, specification details for tools/resources/prompts) should be triaged — some are now contributor-critical given MCP's growth

---

## code-builder

### What's working
- Architecture is sound: judgment gate, parallel worktrees, scoring rubric, learning logs

### What's broken

**Zero activity since creation (Apr 14).** Either it never triggers, or it triggers and fails silently.

### Fixes needed

1. **Add activation logging:** Every trigger (or failed trigger) should append to a log so you can see if it's activating at all
2. **Reduce default parallelism:** 5 drafts is expensive. Default to 3 for tasks under 100 lines, 2 for tasks under 50 lines
3. **Add a fast path:** For well-scoped tasks (single file, clear spec), skip parallel drafts entirely — do 1 draft with self-review
4. **Test it:** Run 5 real tasks through it and record outcomes. Without usage data, the rubric and scoring weights are untested assumptions

---

## vibe-improver

### What's working
- Metric targeting is smart: identifies `broken_in_prod`, computes a Vibe Score, picks the highest-leverage fix
- PR quality is high: the muse-shopping PR has a clear test plan, revert instructions, and scoped CI workflow
- Revert-safe design: "Close this PR + delete the branch. No code on main has changed."

### What's broken

**The loop doesn't close.** The PR was opened May 22 as a draft and is still a draft 4 days later. An autonomous improvement engine that opens work but doesn't push it to completion is a glorified issue tracker.

### Fixes needed

1. **Auto-check CI after PR creation:** If CI passes, convert from draft to ready-for-review and notify you
2. **Track PR lifecycle as a metric:** Time-to-merge should be a vibe metric. If a vibe-improver PR stays open > 48h, escalate
3. **Connect to insights-dashboard:** Use session/commit data to validate whether the improvement actually improved anything

---

## claude-code-insights-dashboard

### What's broken
- `insight-detector.py` is a stub — the "intelligence" layer was never built
- Raw metrics (hours, sessions, commits) exist but no pattern detection or actionable alerts

### Fixes needed
1. Implement basic anomaly detection: zero-commit sessions, unusually long sessions, project switching spikes
2. Feed detected patterns into vibe-improver targeting

---

## Cross-Skill Integration Gaps

| From | To | Missing link |
|------|----|-------------|
| insights-dashboard | vibe-improver | Insights should feed vibe score calculation |
| code-builder | mcp-contributor | SEP implementations should use parallel-draft scoring |
| vibe-improver | insights-dashboard | PR outcomes should flow back as data |
| mcp-contributor | code-builder | Drift fixes could use code-builder for SKILL.md rewrites |

---

## Blind Spots — Not Covered by Any Skill

1. **Portfolio/site maintenance:** hannah-portfolio is the most active repo (updated May 23) with no skill guiding content, deployment, or project page updates
2. **PM workflow:** No skill for writing specs, PRDs, synthesizing user research — despite having workspace-ai-research and twitch-community-research repos that prove the pattern
3. **Cross-repo health monitoring:** 27 repos, no skill checking for stale deps, failing CI, or unpinned secrets
4. **Build log automation:** build-log repo exists but isn't connected to any skill that auto-captures what you ship

---

## Priority Order

| Priority | Action | Impact | Effort |
|----------|--------|--------|--------|
| 1 | Fix mcp-contributor anchor misses + close stale issues | Stops noise, makes real issues visible | Low |
| 2 | Add auto-triage for new MCP pages in refresh.sh | Stops gap from growing | Medium |
| 3 | Add CI-check + draft-to-ready flow in vibe-improver | Closes the autonomous loop | Medium |
| 4 | Test code-builder with 5 real tasks, calibrate | Validates or kills the skill | Medium |
| 5 | Implement insight-detector.py basics | Enables data-driven vibe scoring | Medium |
| 6 | Build cross-skill integration (insights → vibe → code-builder) | Force multiplier | High |
| 7 | New skill: cross-repo health monitor | Prevents rot across 27 repos | High |
