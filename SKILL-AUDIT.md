# Skill Audit — June 3, 2026

Comprehensive review of all Claude Code skills across 29 repositories, cross-referenced against 35+ recent commits, Vercel deployments, and open issues.

---

## Skills Inventory

| Skill | Repo | Last Updated | Status |
|-------|------|-------------|--------|
| **code-builder** | hbschlac/code-builder | Apr 13, 2026 | 1 commit, never iterated |
| **mcp-contributor** | hbschlac/mcp-contributor | Apr 17, 2026 | 9 commits, 10 open issues (7 unresolved drift) |
| **interior-designer-skill** | hbschlac/interior-designer-skill | Apr 14, 2026 | Private, unknown state |
| **claude-config** | hbschlac/claude-config | May 12, 2026 | Central config, private |
| *(none)* | hbschlac/hannah-portfolio | **Today** | Most active repo — 138 commits, no skill |
| *(none)* | hbschlac/kindle-connector | **Today** | Active Python project, no skill |

---

## 1. code-builder — Critical Findings

### What happened in practice

The portfolio (hannah-portfolio) is where code-builder should fire most — 35+ commits in the last 2 weeks, all co-authored with Claude. Two major features shipped:

- **"Stuff" read-it-later app** — mockup → full backend with KV sync, AI summaries, server-side auth in 4 days (May 29 – Jun 2)
- **Jamie's bach** — bachelorette party site with subdomain routing, OG cards, itinerary, cost pages (May 22 – Jun 3)

**Evidence the parallel path rarely (if ever) fired:** Commits are rapid and sequential — the cadence shows single-pass development with fix-up commits immediately after, not the pattern of a 5-draft evaluation.

### Pain points not addressed (bugs that shipped, then got fixed)

| Fix commit | What went wrong | What the skill should have caught |
|-----------|-----------------|----------------------------------|
| `42ed362` "treat empty v2 blob as missing" | KV returned empty string instead of null | Edge-case: Vercel KV empty-blob behavior |
| `4fddb3f` "recover pre-Phase-2 localStorage items" | Migration left orphaned localStorage data | Data migration completeness check |
| `a09048c` "proxy preview images so hotlink-blocked CDNs load" | Social preview images broken | External CDN hotlink-blocking is common |
| `d96fdfa` "hoist icon.tsx out of (app) route group" | Icons not served due to route group scoping | Next.js route group layout inheritance quirk |
| `71eb748` "fix TS build for lodging suites" | TypeScript errors in production build | Type-check before committing (rubric says this but weight is only 10/100) |
| `6bb5d83` "middleware rewrites subdomain root" | Subdomain routing broken | Middleware + subdomain pattern is non-trivial |

### Root causes

1. **Judgment gate is too conservative.** Default is "single pass." The parallel signals table requires >= 2 signals to escalate. Real multi-file feature work (like Stuff Phase 2) should hit parallel but the LOC/files thresholds are set high.

2. **Scoring rubric underweights correctness.** Correctness = 25 points. Tests + Typecheck + Lint = 30 points combined. Edge-case coverage isn't a separate dimension — it's folded into "Correctness" which becomes subjective when the skill self-evaluates.

3. **No project-specific knowledge.** The skill doesn't know that:
   - Vercel KV returns empty strings (not null) for missing keys
   - Next.js route groups don't inherit all parent layouts
   - CDN images need proxying for OG/social preview generation
   - Middleware subdomain routing has specific patterns
   - `next/og` has iMessage vs Slack vs Twitter quirks

4. **Weekly sync is dead.** Learnings frozen at April 13. The cron-based sync requires local machine setup that isn't running. 50+ days of coding sessions with zero learning updates.

5. **No post-merge signal.** When you fix code right after the skill merged it, that's the strongest learning signal. The skill has no mechanism to detect or learn from your follow-up fixes.

6. **Remote session gap.** Claude Code on the web runs in ephemeral containers. The `runs/` logging directory and weekly cron don't work there. Most of your recent sessions appear to be web-based.

### What you asked Claude to do that it couldn't / didn't

Based on the fix-commit pattern, Claude repeatedly shipped initial implementations that missed platform-specific edge cases. The skill's architecture (5 parallel drafts evaluated on a rubric) doesn't help when all 5 drafts make the same wrong assumption about how Vercel KV or Next.js route groups work. The skill needs **domain knowledge injection**, not just parallel exploration.

### Blindspots missed

- **No deployment verification.** 100% Vercel deployment success rate, but zero mechanism to verify the deployed result works. The skill stops at "tests pass" but the real bugs were runtime/platform behavior.
- **No migration testing.** v1→v2 data migration was incomplete. The skill has no concept of data migration safety.
- **Token budget unawareness.** Running 5 parallel drafts with `isolation: "worktree"` in a complex repo could blow context limits. No guardrail exists.

---

## 2. mcp-contributor — Critical Findings

### Maintenance debt is compounding

- **7 weekly "drift detected" issues** open since April 19 — the automation works but nobody resolves the drift
- **19 new MCP pages** appeared in llms.txt and aren't tracked in sources.yml
- **11 anchor references** in sources.yml point to SKILL.md headings that no longer exist
- **3 manually-filed issues** (#1, #2, #3) unresolved since April 17

### Structural problems

1. **Refresh workflow creates noise, not value.** Each week opens a NEW issue instead of updating the existing one. Result: 7 essentially identical issues cluttering the tracker.

2. **Detection without remediation.** The refresh script detects drift and new pages but can't fix anything. A Claude session could be triggered to actually update SKILL.md based on the refresh report.

3. **Issue #3 — misleading section title.** "§4 SDK workflow" actually applies to all non-spec repos, not just SDKs.

4. **Issue #2 — incomplete repo map.** Missing Inspector, Registry, and ext-* repos from the MCP org.

5. **Issue #1 — poor discoverability.** No pointer from capability questions to §11.7 lifecycle reference.

---

## 3. Cross-Cutting Gaps

### Your most active repo has no skill

hannah-portfolio has 138 commits and produces revenue (schlacter.me). It has a 2-line AGENTS.md that says "read the Next.js docs." A project-specific skill would encode:
- Vercel deployment patterns and KV quirks
- Next.js App Router + route group + middleware patterns
- Social preview / OG image generation gotchas
- Subdomain routing architecture
- The specific project structure (app/, components/, content/, lib/)

### Skills don't compose

If code-builder and mcp-contributor are both installed, what happens when you're coding in the mcp-contributor repo? Does code-builder try to run 5 parallel drafts of a SKILL.md edit? There's no composition or conflict-resolution mechanism.

### No skill effectiveness measurement

The claude-code-insights-dashboard tracks session metrics (hours, commits, active days) but not:
- How often code-builder's parallel path fires
- Win rate of draft selection (was the winner actually better?)
- Fix-commit frequency (how often does the user fix what the skill shipped?)
- Skill activation frequency per project

---

## 4. Changes Implemented

### code-builder (improved SKILL.md)

See `skills/code-builder/SKILL.md` in this repo. Key changes:

1. **Lowered parallel threshold** — default remains single-pass but the signal table now triggers parallel at a lower bar, and multi-file feature work is a hard signal
2. **Added edge-case coverage** as a separate 15-point scoring dimension (taken from over-weighted process metrics)
3. **Added project context step** — skill reads CLAUDE.md/AGENTS.md and recent git log to pick up project-specific patterns before coding
4. **Self-triggering sync** — checks learnings age at activation; if >14 days stale, runs inline sync before coding
5. **Post-merge learning signal** — after merging, diffs recent fix commits to detect what the skill got wrong
6. **Worktree failure fallback** — if isolation: "worktree" fails, falls back to single-pass with note
7. **Remote session awareness** — detects ephemeral environments and adjusts logging
8. **Updated learnings** from portfolio work (Vercel KV, Next.js route groups, CDN proxying, middleware patterns)
9. **Composition guard** — skips parallel path when operating on skill/config files

### mcp-contributor (refresh workflow fix)

See `skills/mcp-contributor/` in this repo. Key changes:

1. **Deduplicated refresh issues** — new workflow closes previous "drift" issue before opening a fresh one
2. **Added 19 missing pages** to sources.yml with priority classifications
3. **Fixed 3 manual issues** inline (section title, repo map, discoverability pointer)
4. **Added auto-remediation sketch** — when drift is detected, the workflow can trigger a Claude session to propose SKILL.md updates

---

## 5. Recommended Next Steps

1. **Copy improved SKILL.md files** from this repo to `~/.claude/skills/code-builder/` and the mcp-contributor repo
2. **Create a hannah-portfolio skill** — the biggest ROI improvement. Encode Next.js/Vercel/project-specific patterns
3. **Add fix-commit tracking** to claude-code-insights-dashboard — measure how often you fix what Claude shipped
4. **Close the 7 stale drift issues** in mcp-contributor and apply the deduplication workflow
5. **Test code-builder parallel path** — deliberately trigger it on a medium-complexity task and verify the worktree/scoring pipeline works end-to-end
6. **Archive unused repos** — newrepo-test, sync-test-e2e, desktop-scratch appear to be scaffolding artifacts
