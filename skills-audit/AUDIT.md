# Skills Audit — June 2026

Covers: **code-builder**, **mcp-contributor**
Analysis window: April 13 – May 31, 2026 (last sync → today)
Data sources: commit history (915 commits searched), open issues, SKILL.md definitions, sources.yml, recent session patterns

---

## Executive Summary

Both skills are well-designed but underutilized. code-builder hasn't been invoked during the heaviest coding period (May 2026: kindle-connector, kindle-schlacter-me, hannah-portfolio, recs.community). mcp-contributor's drift detection works but generates unresolved noise (7 open weekly issues). The gap isn't skill quality — it's **activation friction** and **environment mismatch**.

---

## 1. code-builder

### 1a. What wasn't used (and should have been)

| Recent task | Why code-builder should have fired | Outcome without it |
|---|---|---|
| Torrent title parser (kindle-connector, May 29) | Design-space task: 3 heuristic approaches for ambiguous "Title - Author" splits. Parallel drafts would have explored regex vs. NLP vs. rule-based. | Single implementation with a fragile heuristic that admits it can't handle all cases |
| Middleware rewrite for jamiesbach subdomain (May 26) | Debugging task that went through 2 commits (next.config rewrite → middleware fallback). Parallel could have tried both approaches simultaneously. | Serial trial-and-error across 2 commits |
| "Stuff" read-it-later app (May 28) | Greenfield prototype — hard signal for parallel per the skill's own rules | Single-pass. 1 commit. No alternatives explored. |
| kindle-connector bridge API design (May 29) | 3 new endpoints (/search, /prepare-file, /file) — multi-file, design-space decisions | Single-pass |

### 1b. Why it wasn't used

1. **Environment mismatch.** Many recent sessions appear to be Claude Code on the web (remote execution). The skill's `isolation: "worktree"` requirement fails in environments where cwd isn't the project repo or worktree support is limited.
2. **Token cost.** SKILL.md is ~350 lines. It loads into context on every coding task, even single-line fixes. The "when uncertain, default to activating" rule means it fires on everything.
3. **Sync is dead.** "Last synced: 2026-04-13" — 7 weeks of coding without a single sync. The cron-based sync design assumes a local always-on machine. The learnings section is frozen.
4. **Stale project references.** Examples reference "662-calmar-portfolio" which doesn't appear in current repos. Cross-repo mining targets outdated paths.
5. **5 drafts is overkill for most tasks.** Looking at the May commits: most are targeted bug fixes, config tweaks, or incremental features. N=5 is right for greenfield; N=3 would be better as the default for modifications.

### 1c. Learnings that should exist but don't

From May 2026 commits, these patterns should have been captured:

- **Vercel host-based rewrites in next.config don't fire on deployed builds** — use middleware instead (jamiesbach subdomain, 2 commits to discover)
- **Torrent search results are non-deterministic** — can't re-search to find a result by ID; encode enough state in the ID to reconstruct (kindle-schlacter-me, 2 commits)
- **Silent null returns mask real errors** — throw with diagnostic messages instead of returning null (kindle-schlacter-me torrent source)
- **Timeout constants need production headroom** — pullpush.io 8s → 20s (false alarm health checks)
- **Cross-repo API contracts need to be versioned** — kindle-connector and kindle-schlacter-me are tightly coupled; bridge API changes require coordinated deploys
- **OG image generation needs metadataBase for absolute URLs** — Next.js opengraph-image.tsx won't unfurl on iMessage/Slack without it

### 1d. Structural problems

1. **No graceful degradation for web/remote environments.** Should detect `CLOUD_ENVIRONMENT` or equivalent and skip worktree attempts.
2. **The log format requires `~/.claude/skills/code-builder/runs/` to exist locally.** Web sessions don't persist local state.
3. **The scoring rubric is load-bearing dead weight for single-pass runs.** The 100-point framework only matters for parallel; it shouldn't be in context for single-pass.
4. **Cross-repo mining in the sync reads git history from repos that may not be cloned locally.** Doesn't account for web-only workflows.

### 1e. What worked well

- The judgment gate (parallel vs. single) is well-calibrated with clear signals
- The rubric catches real quality dimensions (nullable guards, hook rules, env var trimming)
- The learnings section from the April backfill identified genuine cross-repo patterns
- The "Claude picks the winner" design saves review time

---

## 2. mcp-contributor

### 2a. Drift detection works, resolution doesn't

7 consecutive weekly "[refresh] drift or gaps detected" issues (#4–#10) are open with zero resolution. The automation creates the alert; nothing acts on it. This is pure noise — worse than no detection, because it trains the user to ignore the signal.

### 2b. Manual issues are real gaps

- **#3** (§4 scope): SDK workflow section applies to all non-spec repos, not just SDKs. Misleading title causes the skill to give wrong guidance for docs/registry contributions.
- **#2** (§6 repo map): Missing Inspector, Registry, and ext-* repos. Contributors asking "where does this go?" get incomplete answers.
- **#1** (capability → lifecycle navigation): No way to get from "can MCP do X?" to the lifecycle spec. Common first question from contributors goes unanswered.

### 2c. Sources.yml is healthy but aging

All sources were fetched 2026-04-16. The MCP ecosystem moves fast (new SEPs, SDK updates, governance changes). 6+ weeks without a refresh means the skill may be giving outdated advice on:
- SDK tier classifications
- Active Working Groups
- Specification version (still references 2025-11-25)

### 2d. What's missing

1. **No auto-resolution workflow.** refresh.sh detects drift but doesn't propose patches. It should output a diff suggestion.
2. **No issue deduplication.** 7 identical "drift detected" issues is 6 too many — should reopen/update a single tracking issue.
3. **No activation evidence.** No way to know if the skill has ever been used for a real MCP contribution.

---

## 3. Cross-skill gaps (blindspots)

### 3a. No deployment/infrastructure skill
Heavy work on Docker (kindle-connector), Vercel (hannah-portfolio), Oracle VM, Tailscale — but no skill captures deployment patterns. Every deployment debugging session starts from zero.

### 3b. No multi-repo coordination skill
kindle-connector ↔ kindle-schlacter-me are tightly coupled. commits need coordination. hannah-portfolio serves multiple subdomains. No skill helps Claude reason about cross-repo dependencies.

### 3c. No project planning skill
recs.community went through a structured PRD → open questions → stack decision → scaffold flow. This is a repeatable pattern with no skill coverage.

### 3d. code-builder's sync and mcp-contributor's refresh are both broken feedback loops
Both skills have mechanisms to stay current (sync, refresh.sh) that aren't running. The pattern: automate detection, forget resolution.

---

## 4. Recommended changes

### code-builder (implemented in `skills-audit/code-builder/SKILL.md`)

1. **Add remote/web environment detection** with graceful single-pass fallback
2. **Reduce default N from 5 to 3** — 5 is for greenfield; 3 covers the design space for modifications with less overhead
3. **Split SKILL.md into core + appendix** — scoring rubric and log template only load for parallel runs
4. **Update project references** to current repos (kindle-connector, kindle-schlacter-me, recs.community, hannah-portfolio)
5. **Add May 2026 learnings** — 6 new patterns from recent commits
6. **Replace cron sync with on-demand + post-session trigger** — sync when the user says "sync" or at session end
7. **Add "couldn't-do" capture** — when parallel fails, log why for future improvement
8. **Tighten activation** — don't fire on config changes, content edits, or sub-10-LOC fixes unless explicitly asked

### mcp-contributor (detailed in `skills-audit/mcp-contributor/improvements.md`)

**SEVERITY: HIGH** — MCP underwent its largest revision since launch (stateless protocol, MCP Apps, extensions framework, conformance suite requirements) between April–May 2026. The skill is now materially incorrect on protocol mechanics.

1. **Re-fetch all sources immediately** — every section touching protocol mechanics is stale
2. **Add coverage for 6 new concepts** — stateless core, MCP Apps, Tasks extension, JSON Schema 2020-12, extensions framework, conformance suites
3. **Collapse 7 drift issues into 1 tracking issue** — the weekly automation is correct but the issue accumulation is unactionable
4. **Fix §4 scope** (issue #3) — rename to "Repository contribution workflow"
5. **Add missing repos to §6** (issue #2) — Inspector, Registry, ext-*, Apps
6. **Add capability → lifecycle navigation** (issue #1)
7. **Deduplicate drift issue automation** — update/reopen a single issue instead of creating new ones
8. **Split SKILL.md** to stay under token budget — core workflow (200 lines) + on-demand reference files
9. **Increase refresh cadence** to twice-weekly during the RC validation window (through July 28, 2026)
