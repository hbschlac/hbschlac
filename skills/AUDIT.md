# Skill Audit — 2026-05-05

Cross-skill review of all public Claude Code skills: **code-builder**, **mcp-contributor**, **claude-code-insights-dashboard**. Identifies pain points, unmet use cases, blind spots, and concrete improvements.

---

## Skills Inventory

| Skill | Repo | Commits | Last Update | Open Issues |
|-------|------|---------|-------------|-------------|
| code-builder | hbschlac/code-builder | 1 | Apr 14 | 0 |
| mcp-contributor | hbschlac/mcp-contributor | 6 releases (v0.2.3) | Apr 17 | 6 |
| claude-code-insights-dashboard | hbschlac/claude-code-insights-dashboard | 4 | Apr 17 | 0 |
| claude-config | hbschlac/claude-config | private | Apr 14 | unknown |
| skills-gallery | hbschlac/skills-gallery | private | Apr 14 | unknown |
| interior-designer-skill | hbschlac/interior-designer-skill | private | Apr 14 | unknown |

---

## A. code-builder — Findings

### What works well
- 5-draft parallel approach is sound — the probability argument holds
- 100-point scoring rubric is concrete and measurable
- Learning system with weekly sync is genuinely novel
- Judgment gate with worked examples prevents over-parallelizing trivial tasks
- Cherry-pick gap-filling from rejected drafts captures value from losers

### Pain points / unmet needs

1. **Post-merge diff mining is deferred (highest-value signal missing).** The sync documents this as "the skill's highest-value learning signal" but it's not implemented. When you silently edit code after a merge, those edits are the strongest signal about what the skill got wrong. Every week this stays deferred, learning data is lost.

2. **No bias-hint performance tracking.** The 5 drafts each have a bias (simplest, idiomatic, readable, performance, free choice). But the skill never tracks which bias wins most often per task type. After 20+ runs, this data would let the skill skip consistently poor performers or weight scoring. Example: if "simplest" wins 70% of bug fixes, the skill should know that.

3. **Hardcoded repo names in cross-repo mining.** The sync step (2e) references `662-calmar-portfolio`, `schlacter.me`, `muse-shopping`, `libby-hold-monitor` by name. If repos are renamed, moved, or new ones created, mining breaks silently. Should auto-discover from `~/.claude/projects/`.

4. **No automated sync runner.** The skill documents `code-builder-sync` but provides no shell script, GitHub Action, or launchd plist. Users have to set up the cron job themselves. Compare: mcp-contributor ships `refresh.sh` + `.github/workflows/weekly-refresh.yml`.

5. **Token budget enforcement deferred.** 5 parallel agents on a large feature (>200 LOC each) could blow through rate limits. No guardrail.

6. **12 learnings out of 30 after ~1 month — but sync hasn't run since Apr 13.** That's 22 days of accumulated learning signal sitting unprocessed.

7. **Learning evaluation is qualitative only.** "repeated >=2 times = candidate" is the threshold. No measurement of whether learnings actually improve draft quality. The deferred holdout-commit eval (section 12a) and live-task precision/recall (section 12b) would close this gap.

8. **Non-git fallback is abrupt.** Worktree isolation fails outside git repos. The skill downgrades to single pass but the user experience is jarring — "restart from the project repo" mid-task.

### Improvements implemented (see `skills/code-builder/SKILL.md`)
- Added bias win-rate tracking to run log format and sync workflow
- Replaced hardcoded repo list with auto-discovery from `~/.claude/projects/`
- Added token budget awareness section to parallel path
- Promoted post-merge diff mining from deferred to sync step 2b with concrete implementation
- Added cross-skill integration notes (insights-dashboard data can inform learning)

---

## B. mcp-contributor — Findings

### What works well
- Comprehensive coverage of MCP governance (89 source URLs tracked)
- Automated drift detection via refresh.sh + GitHub Actions is excellent infrastructure
- Source provenance tracking (sources.yml with status, fetched date, anchor mapping)
- Clean versioning via CHANGELOG.md with dry-run validation
- SEP lifecycle coverage is thorough

### Pain points / unmet needs

1. **3 weeks of unresolved automated drift issues (#4 Apr 19, #5 Apr 26, #6 May 3).** The detection creates issues but nobody resolves them. The automation detects drift but generates no remediation — no proposed SKILL.md patches, no diff of what changed. The skill should either auto-generate proposed edits or at minimum include the specific drift details in the issue body.

2. **Issue #3: section 4 titled "SDK workflow" but applies to all non-spec repos.** Misleading title causes contributors to skip the section when working on non-SDK repos like Inspector or Registry.

3. **Issue #2: repo map missing Inspector, Registry, ext-\*, access, .github repos.** These are active repos in the MCP org that contributors will encounter.

4. **Issue #1: No discoverable path from "can MCP do X?" to section 11.7 lifecycle.** Users asking capability questions get stuck because the triage in section 1 doesn't cross-reference the protocol primer.

5. **20 medium-priority gaps unfilled.** sources.yml has 20 URLs at `gap-med` covering SDK tutorials, security best practices, spec primitives (tools, resources, prompts, sampling, elicitation), and the MCP registry. These are exactly the pages SDK contributors need most.

6. **refresh.sh generates a report, not a patch.** When drift is detected, the output is human-readable markdown with "next steps." It should generate proposed SKILL.md edits — even rough ones — to reduce the time from detection to resolution.

### Improvements implemented (see `skills/mcp-contributor/PATCHES.md`)
- Specific SKILL.md text changes to resolve Issues #1, #2, #3
- refresh.sh improvement proposal to include proposed patches in drift issues
- Strategy for resolving the 3-week drift backlog

---

## C. claude-code-insights-dashboard — Findings

### What works well
- Clean aggregation pipeline (JSONL -> stats JSON -> Next.js page)
- 6-hour session cap is a smart methodological choice
- Project labeling for privacy-preserving public display
- Social image renderer for LinkedIn sharing

### Pain points / unmet needs

1. **insight-detector.py is a complete stub.** This is the skill's differentiator — the promise of pattern mining ("you refactor more than you build", "your longest sessions are on project X") is what makes this more than a simple counter. It's been a stub since the initial commit on Apr 17 (18 days).

2. **No requirements.txt.** Python dependencies (Pillow for render_social_image.py, pathlib standard lib) aren't documented. New users will hit ImportError on Pillow.

3. **No GitHub Action workflow.** README mentions automation but provides no `.github/workflows/` file. Compare: mcp-contributor includes `weekly-refresh.yml`.

4. **Hardcoded default paths.** `~/schlacter-me/public/claude-code-stats.json` is the default output — works only for you.

5. **No example output.** No sample `claude-code-stats.json` for users to see expected format before running the script.

### Improvements implemented (see `skills/insights-dashboard/`)
- Complete insight-detector.py with 8 pattern detection algorithms
- requirements.txt with dependencies
- Sample output format documentation

---

## D. Cross-Skill Blind Spots

These are gaps not addressed by any existing skill:

### 1. No skill interconnection
code-builder, mcp-contributor, and insights-dashboard are completely siloed. They don't share learnings, reference each other, or compose. Examples:
- When contributing to MCP, code-builder should auto-activate for the PR code
- insights-dashboard hours/sessions data could inform code-builder's learning (projects with more hours may have more post-merge edits)
- code-builder run logs are a richer data source than raw JSONL for insights

### 2. No deployment/DevOps skill
Build-log shows recurring pain around: Vercel deployments, Cloudflare R2 migrations, GitHub Actions optimization, Playwright timeouts, environment variable management. These patterns repeat across projects but no skill captures them.

### 3. No testing/QA skill
code-builder scores on tests passing but doesn't help write or design tests. "43 automated tests" for Muse suggests testing matters. A skill for test coverage analysis, test generation from API endpoints, or regression detection would fill this gap.

### 4. No build-log automation
The build-log repo has 221 commits of manual entries. A skill could auto-generate build-log entries from git commits + session transcripts, saving 10-15 minutes per entry.

### 5. No project-onboarding skill
With 26 repos and multiple active projects, switching between them mid-session is common. A skill that quickly loads project context (CLAUDE.md, recent commits, open issues, test status) would reduce ramp-up time.

---

## E. Things Done That Could Have Been Faster

| Pattern | Current | Faster approach |
|---------|---------|-----------------|
| Drift detection -> manual fix | 3-week backlog of unresolved issues | Auto-generate SKILL.md patches in the issue body |
| 5-draft bias hints are static | Same 5 biases every run | Adapt based on win-rate history per task type |
| Build-log entries | Manual writing per feature | Auto-generate from git log + session transcripts |
| insights-dashboard setup | Manual cron/GH Action setup | Ship a workflow file in the repo |
| Learning sync | Manual trigger / stale cron | Ship sync.sh alongside SKILL.md |

---

## F. Things Asked For But Not Completed

| Feature | Where | Status |
|---------|-------|--------|
| Pattern mining ("you refactor more than you build") | insight-detector.py | Stub only — **now implemented** |
| Post-merge diff learning | code-builder sync step 2b | Deferred — **now promoted with implementation** |
| Token budget enforcement | code-builder section 12c | Deferred — **now added as awareness section** |
| Learning precision/recall eval | code-builder section 12b | Still deferred (requires 20+ parallel runs) |
| Holdout-commit evaluation | code-builder section 12a | Still deferred (requires accumulated data) |
