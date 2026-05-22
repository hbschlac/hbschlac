# mcp-contributor: Targeted Improvements

Audit date: 2026-05-22
Last skill update: 2026-04-16 (v0.2.3) — 36 days stale

## Status

- **29 covered** URLs in sources.yml
- **0 gap-high** (good — all critical pages covered)
- **26 gap-med** URLs not yet synthesized into SKILL.md
- **Weekly refresh workflow** (weekly-refresh.yml) — no evidence of successful runs since creation
- **Session log** — 1 entry (inspector#832 dry-run)

## Issues Found

### 1. Drift risk (HIGH)
36 days since last update. MCP governance moves fast — the spec, SEP process, SDK tiers, and contributor ladder may have changed. The refresh.sh script exists but there's no evidence the GitHub Actions workflow has ever fired successfully.

**Fix:** Run `./refresh.sh` immediately and address any drift. Verify the GitHub Actions workflow is enabled on the repo (Actions may need to be manually enabled after initial push).

### 2. Gap-med coverage (MEDIUM)
26 gap-med URLs represent useful contributor context that's missing:
- SDK documentation (build-server, build-client)
- Inspector docs
- Tutorials
- Spec pages for tools/resources/prompts/sampling/elicitation/roots
- Extensions and registry pages

**Fix:** Prioritize the 5 most contributor-relevant gap-med pages:
1. `build-server` — most contributors will build servers
2. `build-client` — second most common contribution type
3. Inspector docs — primary debugging tool
4. Tools spec page — most common capability to implement
5. Resources spec page — second most common capability

### 3. Session log underutilized (LOW)
Only 1 entry in the session log. The log was designed to track real-world usage for learning, but it's empty after the initial dry-runs.

**Fix:** Add a prompt at the end of the skill: "If this session involved a real MCP contribution attempt, append a one-liner to the Session log section."

### 4. Stale repo references in sources.yml
sources.yml `index_fetched: 2026-04-16` and `skill_version: 0.1.0` — both stale. The skill is at v0.2.3 but sources.yml still references v0.1.0.

**Fix:** Update `skill_version` to `0.2.3` and re-fetch the llms.txt index to check for new MCP pages added since April 16.

## Proposed Changes (for next PR to mcp-contributor repo)

```diff
# sources.yml header
- skill_version: 0.1.0
+ skill_version: 0.2.3

# SKILL.md — add session log reminder at end of Step 10
+ **Session tracking:** If this session involved a real MCP contribution (PR opened, issue filed, SEP drafted, Discord post), append a one-liner to the Session log at the bottom of this file.

# CHANGELOG.md — add under [Unreleased]
+ ### Changed
+ - Updated sources.yml skill_version to 0.2.3
+ - Added session log reminder after Step 10
+ ### Fixed
+ - Verified GitHub Actions workflow is enabled
+ - Ran refresh.sh to detect 36 days of potential drift
```
