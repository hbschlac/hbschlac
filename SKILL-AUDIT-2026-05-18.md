# Skill Ecosystem Audit — 2026-05-18

Comprehensive review of all Claude Code skills, recent deployment activity, and improvement plan.

## Skills Reviewed

### 1. code-builder

**What it does**: Auto-activates on coding tasks. Judgment gate decides parallel (5 isolated worktree drafts, scored on 100-point rubric, winner merged) vs single pass. Self-improving via weekly learning sync from run logs.

**Strengths**:
- Sophisticated judgment matrix avoids wasting parallel runs on trivial tasks
- 5 bias hints (simplest, most idiomatic, readability, performance, free choice) create genuine diversity
- Cherry-pick from rejected drafts captures edge-case coverage the winner missed
- Run logs create a structured audit trail

**Issues found**:
- **Learning loop appears dormant**: Changelog has one entry (Apr 13 initial backfill). 12 learnings, all static. No evidence the weekly cron sync has ever run.
- **Deferred features never shipped**: holdout-commit eval, N=5 precision/recall, citation lint, token budget caps, stale-rule audit, cross-skill conflict scan — all listed as future work with no progress.
- **No failure handling**: What happens when worktree creation fails? When all 5 drafts score identically? When the winner has merge conflicts?
- **No usage telemetry**: Can't answer "how often does parallel path trigger?" without manually scanning transcripts.
- **No tests**: The judgment gate, rubric scoring, and merge logic have no automated validation.

**Priority fixes**:
1. Actually schedule the weekly sync cron job (the skill's most powerful differentiator is disabled)
2. Add a fallback path: if worktree creation fails, degrade to single pass with a warning rather than failing silently
3. Add a tiebreaker log entry when drafts score within 5 points of each other — this reveals whether the rubric has enough discriminating power
4. Surface activation counts in run logs to track parallel-vs-single ratio

### 2. mcp-contributor

**What it does**: LLM-ingestible synthesis of MCP governance docs. Automated weekly drift detection via GitHub Actions + refresh.sh. Covers triage, SEP lifecycle, contributor ladder, working groups, communication, licensing.

**Strengths**:
- Automated drift detection is genuinely impressive — weekly SHA-256 hash comparison with structured issue filing
- Coverage tier system (covered / gap-high / gap-med / gap-low / sep-ref) is well-designed
- Source pinning via sources.yml creates a maintainable audit trail
- Real dry-run validation (inspector#832) proved the skill works on actual contributions

**Issues found**:
- **11 anchor misses for 5 consecutive weeks** (issues #4-#8, Apr 19 - May 17): sources.yml references Step 11.1-11.11 headings that don't exist in SKILL.md. Never fixed despite being flagged every single week.
- **Growing un-triaged page backlog**: 0 new pages (Apr 19) → 3 (Apr 26, May 3) → 6 (May 10) → 11 (May 17). New MCP pages accumulate with no triage.
- **3 manual issues from dry-run** (#1-#3, Apr 17) all unaddressed:
  - #1: No cross-reference from capability questions → §11.7 lifecycle
  - #2: §6 repo map missing Inspector, Registry, ext-* repos
  - #3: §4 titled "SDK workflow" but applies to all non-spec repos
- **Refresh automation creates issues but no follow-through pressure**: No assignee, no due date, no escalation. Issues are fire-and-forget.

**Priority fixes**:
1. Fix the 11 anchor misses — either rename the SKILL.md headings to match Step 11.x or update sources.yml to reference the actual heading names
2. Triage the 11 new pages from issue #8: classify each as covered / gap-high / gap-med / gap-low / sep-ref in sources.yml
3. Address issues #1-#3 (§4 rename, §6 repo map expansion, §1.5 cross-reference)
4. Add auto-close logic to refresh.sh: if a refresh finds zero drift AND zero new pages, close the issue automatically instead of accumulating clean reports
5. Add staleness escalation: if the same anchor miss appears in 3+ consecutive reports, label it `stale` and add a TODO comment in the issue

### 3. insights-dashboard

**What it does**: Parses JSONL session transcripts into monthly stats (hours, sessions, commits, active days, top projects). Outputs JSON for a Next.js dashboard.

**Strengths**:
- Clean, functional pipeline from transcripts to public stats page
- Social card generation for LinkedIn sharing
- 6-hour session cap is a smart filter for idle periods

**Issues found**:
- **insight-detector.py is a stub**: The strategically most valuable piece (pattern mining) was started and abandoned. Currently just adds `suggestions: []` to the JSON.
- **No pattern detection**: Can't identify "70% of sessions are frontend TypeScript" or "you re-explain the same context in 15% of sessions" or "tasks involving X take 3x longer than average"
- **Commit counting is naive**: Regex-matching `git commit` in bash invocations misses amended commits, interactive rebases, and commits via MCP tools
- **No connection to code-builder learnings**: Session data could feed code-builder's learning sync but there's no pipeline

**Priority fixes**:
1. Implement insight-detector.py with at least 3 pattern detectors:
   - Task-type distribution (frontend / backend / config / docs / debugging)
   - Re-explanation detection (similar prompts across sessions)
   - Time-per-task-type analysis
2. Add a `--learnings` output mode that formats detected patterns as candidate bullets for code-builder's learning sync
3. Fix commit counting to also capture `git commit -m`, `git commit --amend`, and MCP-tool commits

### 4. Claude Skills (concept product)

**What it does**: Concept site pitching "persistent AI instruction sets" framed as "skills" for non-engineers. Live at skills-roan.vercel.app.

**Issues found**:
- **Self-described as "a pitch, not a product"** — but the actual skills you've built (code-builder, mcp-contributor) ARE the product. The concept site and the real skills are disconnected.
- **No bridge between the gallery and your working skills**: skills-gallery shows pre-built examples for non-engineers, but doesn't reference or install actual skills.

**Priority fix**:
1. Add code-builder and mcp-contributor as featured examples in the skills gallery — they're the strongest proof that the concept works

### 5. claude-config

**Status**: Private, inaccessible to this session. Cannot audit.

**Recommendation**: Grant Claude Code web sessions access to this repo so future audits can review the central skill configuration.

---

## Cross-Cutting Blindspots

### No skill orchestration layer
code-builder and mcp-contributor don't know about each other. When working in an MCP repo, both should activate — mcp-contributor for governance context, code-builder for implementation quality. A simple cross-reference in each SKILL.md ("if also working in an MCP repo, see mcp-contributor") would help.

### No skill usage telemetry
Across 187 sessions and 404 hours, there's no data on:
- How often each skill activates
- Whether code-builder's parallel path ever triggers (vs always falling to single pass)
- What the average rubric score is across runs
- Whether mcp-contributor's guidance actually results in successful MCP contributions

### Automation without follow-through
mcp-contributor's drift detection is a solved problem. The unsolved problem is: what happens after detection? Issues pile up because there's no mechanism to close the loop — no assignee, no SLA, no escalation.

### Self-improvement loops are designed but not running
code-builder's weekly sync is the skill's most differentiated feature. If it's not running, the skill degrades to a static prompt with no advantage over a well-written CLAUDE.md.

---

## Implementation Priority (ordered)

| # | Action | Skill | Effort | Impact |
|---|--------|-------|--------|--------|
| 1 | Fix 11 anchor misses in sources.yml / SKILL.md | mcp-contributor | 30 min | Stops 5 weeks of duplicate noise |
| 2 | Schedule code-builder weekly sync cron | code-builder | 15 min | Activates the self-improving flywheel |
| 3 | Triage 11 new MCP pages in sources.yml | mcp-contributor | 45 min | Clears the backlog |
| 4 | Address issues #1-#3 (naming, repo map, cross-ref) | mcp-contributor | 2 hrs | Fixes real gaps found in dry-run |
| 5 | Add worktree failure fallback | code-builder | 30 min | Prevents silent failures |
| 6 | Implement insight-detector.py pattern mining | insights-dashboard | 3 hrs | Unlocks data → learning pipeline |
| 7 | Add cross-skill references | code-builder + mcp-contributor | 15 min | Enables skill orchestration |
| 8 | Add activation telemetry to code-builder run logs | code-builder | 1 hr | Answers "is this actually being used?" |
| 9 | Add auto-close for clean refresh reports | mcp-contributor | 30 min | Stops issue accumulation |
| 10 | Connect insights → code-builder learning pipeline | insights + code-builder | 2 hrs | Closes the data flywheel |
