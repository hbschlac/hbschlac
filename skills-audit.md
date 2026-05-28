# Skills Audit — 2026-05-28

Cross-cutting review of all Claude Code skills, usage patterns, and gap analysis based on:
- 6 public repos analyzed (code-builder, mcp-contributor, hannah-portfolio, muse-shopping, build-log, claude-code-insights-dashboard)
- 221 build-log commits (Mar 29 – Apr 28, 2026)
- 29 GitHub repos (9 public, 20 private)
- Recent activity through May 27, 2026

---

## 1. Skills Inventory

| Skill | Repo | Last Updated | Real Runs | Status |
|---|---|---|---|---|
| code-builder | hbschlac/code-builder | Apr 14 (1 commit) | 0 parallel runs | Dormant — never used in production |
| mcp-contributor | hbschlac/mcp-contributor | Apr 16 (9 commits) | 2 dry-runs only | Dormant — 6+ weeks stale |
| (none) | claude-config | May 12 | Unknown (private) | Central config — inaccessible |
| (none) | skills-gallery | Apr 14 | Unknown (private) | Gallery — inaccessible |

---

## 2. What You Actually Build (Where Time Goes)

Source: build-log commits + git history across all repos.

| Activity Category | % of Work | Repos | Skill Coverage |
|---|---|---|---|
| Full-stack web apps (Next.js/Vercel) | ~40% | hannah-portfolio, interior-designer-portfolio, recs.community | NONE |
| Bug fixes / debugging | ~25% | All repos | NONE |
| Auth / OAuth flows | ~10% | muse-shopping, interior-designer-portfolio | NONE |
| Infrastructure (Playwright, GHA, Vercel, R2) | ~10% | libby-hold-monitor, interior-designer-portfolio | NONE |
| Content / copy / event planning | ~10% | hannah-portfolio (Jamie's bach) | NONE |
| MCP contributions | ~0% | mcp-contributor (dry-runs only) | mcp-contributor |
| Parallel code generation | ~0% | None — never used | code-builder |

**The gap is stark:** 95%+ of your actual work has zero skill support. The two skills you built cover use cases that collectively represent <5% of your time.

---

## 3. Pain Points From Sessions (Not Addressed by Any Skill)

### 3A. Recurring infrastructure failures (build-log evidence)

| Pain Point | Evidence | Impact | Frequency |
|---|---|---|---|
| **Vercel Blob → R2 migration emergency** | 13+ commits across multiple days; built 4 admin endpoints | Multi-day outage | 1× (but catastrophic) |
| **iOS Shortcut integration** | 13 versions (v1–v13) of trial-and-error | Days of iteration | 1× |
| **OAuth flow debugging** | 7 auth-related commits in 2 days (muse-shopping) | Repeated across repos | 3+ repos |
| **Playwright timeout tuning on GHA** | Escalated from 30s→4min; eventually pivoted architecture | Wasted compute | 2× |
| **Merge conflicts losing code** | 3× in calmar; documented in code-builder learnings | Silent data loss | 3× |
| **process.env whitespace/trim** | 4 separate fixes across schlacter.me alone | Silent misconfig | 4+ times |

### 3B. Tasks Claude couldn't do or struggled with

| Task | What Happened | Root Cause |
|---|---|---|
| **Security audit of generated code** | Manifesto: "what came back was functional code I couldn't audit" | No skill for security review of Claude output |
| **Session handoff** | muse-shopping: explicit "session handoff doc" commit | No skill for context preservation between sessions |
| **Cross-repo coordination** | Portfolio + muse + calmar share patterns but each is independent | No skill for cross-repo pattern sync |
| **Vercel serverless debugging** | Trust proxy, middleware ordering, serverless entry points — repeated | No skill encoding Vercel deployment patterns |

### 3C. Blindspots (things that should have been caught)

| Blindspot | Evidence | Should Have Been |
|---|---|---|
| **No CLAUDE.md in muse-shopping** | 65K LOC, 120 API endpoints, 0 Claude config | CLAUDE.md with project conventions, test commands, deploy patterns |
| **hannah-portfolio CLAUDE.md is effectively empty** | Just `@AGENTS.md` which only warns about Next.js versions | Should encode design system, deployment, data scraping patterns |
| **No test commands in any skill** | code-builder references "project's test cmd" but never detects it | Skills should auto-detect test/lint/typecheck commands |
| **No pre-deploy checklist** | Vercel deploys frequently break on serverless config | Should have a pre-push validation skill |
| **Insights dashboard only counts commits** | Misses tool use patterns, error recovery, session complexity | `insight-detector.py` is a stub — never implemented |

---

## 4. code-builder: Detailed Gap Analysis

### What's strong
- Objective 100-point scoring rubric
- Parallel worktree isolation
- 5 differentiated draft biases
- Cherry-pick gap recovery from rejected drafts
- Embedded learnings with citation tracking
- Weekly sync design (on paper)

### What's broken or missing

**Critical (blocks real usage):**

1. **Zero real runs.** The skill has never been used for an actual parallel build. The initial backfill drew from session summaries, not real code-builder runs. Until it's battle-tested, the rubric weights and judgment gate are theoretical.

2. **Sync executor doesn't exist.** The weekly sync workflow (7 steps, 5 data sources, 3 passes) is documented but there's no script or automation to run it. Learnings will go stale.

3. **Git repo prerequisite not enforced upfront.** Step 4a says "confirm working dir is a git repo" but it's a suggestion, not a gate. If Claude forgets, all 5 agents fail silently.

**Robustness:**

4. **No quorum or retry strategy.** If 3+ drafts fail, what happens? If all 5 fail? No timeout duration specified.

5. **Language/framework detection missing.** Assumes npm test / pytest / tsc. Go, Rust, Ruby, Java repos would score incorrectly.

6. **Single-pass logging format ambiguous.** Does a single-pass run log 1 draft or 5 slots with 4 empty?

7. **Cherry-pick has no rollback.** If cherry-pick conflicts or breaks tests, no abort strategy defined.

**Optimization:**

8. **No task-size adaptation.** 1-LOC typo fix still runs full scoring rubric. 500-LOC refactor spawns 5 divergent agents.

9. **No success metrics.** No way to measure if parallel runs produce better code than single-pass would have.

10. **Repo-level config missing.** Different repos have different thresholds but the judgment gate is one-size-fits-all.

---

## 5. mcp-contributor: Detailed Gap Analysis

### What's strong
- Comprehensive 1,176-line guide covering the entire contributor lifecycle
- Machine-readable source map (sources.yml, 114 URLs)
- Automated drift detection (refresh.sh)
- Iterative quality (3 versions, 2 dry-runs)
- Good license handling (Apache 2.0 + CC-BY 4.0)

### What's broken or missing

**Staleness:**

1. **Dormant since April 16** — 6+ weeks with no updates despite weekly refresh being designed.

2. **Hardcoded snapshots rotting:**
   - Protocol version: `2025-11-25` (may have been superseded)
   - Active working groups: snapshot from April 16 (WGs form/dissolve)
   - SEP index: "27 Final / 2 Accepted / 1 Draft" (outdated)
   - Discord invite link: might have expired

3. **gap-med items never elevated.** 26 URLs waiting to be ingested — security/auth tutorials, extensions ecosystem, SDK tiers.

**Coverage:**

4. **Missing repos:** Inspector, Registry, ext-*, access, .github not in the repo map.

5. **§4 title misleading.** Says "SDK workflow" but applies to all non-spec repos.

6. **Auth section too shallow.** §11.9 is ~30 lines for OAuth 2.1 + DPoP + Workload Identity Federation.

7. **No "finding a sponsor" practical playbook.** §5.3 says "identify candidates" but doesn't teach how.

---

## 6. What's Missing Entirely (New Skills Needed)

### 6A. vercel-ship (highest impact based on usage patterns)

**Rationale:** ~40% of build-log work involves Next.js + Vercel. Repeated pain points: serverless entry config, trust proxy, middleware ordering, OAuth redirect URIs, Vercel Blob storage, R2 migration, OG image generation, subdomain routing.

**Would cover:**
- Pre-deploy validation checklist (env vars trimmed, middleware ordered, serverless entry correct)
- Vercel-specific debugging patterns (trust proxy, cold starts, function size limits)
- Image storage patterns (Blob vs R2 vs Cloudflare)
- OAuth flow patterns for Vercel serverless
- Subdomain routing + middleware rewrites

### 6B. auth-debug (second highest impact)

**Rationale:** 7+ auth-related commits in 2 days on muse, plus repeated OAuth issues across repos. Auth debugging is the most common "stuck" pattern.

**Would cover:**
- OAuth flow debugging checklist (redirect URIs, token validation, session handling)
- Common failure modes (missing privacy_consent column, trust proxy, envelope format)
- Per-provider patterns (Google, Meta, Apple)
- Environment-specific gotchas (local vs Vercel vs Render)

### 6C. project-bootstrap (for new repos)

**Rationale:** muse-shopping has 65K LOC with no CLAUDE.md. Interior-designer-portfolio is the most active project with no config. New repos (recs.community, kindle-connector) start from scratch.

**Would cover:**
- Auto-generate CLAUDE.md from repo analysis (package.json, tsconfig, test config)
- Detect and encode test/lint/typecheck commands
- Set up .claude/ directory structure
- Encode deployment target (Vercel, Render, GHA)

### 6D. session-handoff (addresses manifesto pain point)

**Rationale:** Explicit commit `f0ebcb5 "Add Claude session status handoff doc"` in muse-shopping. Manifesto identifies this: "Even together, you're building alone."

**Would cover:**
- End-of-session state capture (what was done, what's left, what broke)
- Context compression for next session
- Cross-session learning extraction

---

## 7. Implementation Priority

| # | Change | Impact | Effort | Target |
|---|---|---|---|---|
| 1 | **Patch code-builder** — enforce git check, add quorum, language detection, task-size heuristics | High (unblocks real usage) | Medium | code-builder/SKILL.md |
| 2 | **Create vercel-ship skill** | High (covers 40% of work) | Medium | New skill |
| 3 | **Patch mcp-contributor** — fix hardcoded values, add missing repos, rename §4 | Medium (prevents rot) | Low | mcp-contributor/SKILL.md |
| 4 | **Create project-bootstrap skill** | Medium (prevents config debt) | Low | New skill |
| 5 | **Create auth-debug skill** | Medium (saves debugging time) | Medium | New skill |
| 6 | **Build code-builder sync script** | Medium (unlocks learning loop) | High | code-builder/sync.sh |
| 7 | **Create session-handoff skill** | Low-Med (quality of life) | Medium | New skill |
| 8 | **Implement insight-detector.py** | Low (analytics) | Medium | claude-code-insights-dashboard |

---

## 8. Cross-Cutting Recommendations

1. **Use the skills you build.** code-builder has never run in parallel. Until it does, the rubric and judgment gate are untested theory. Force a parallel run on your next feature build, even if the judgment gate says single.

2. **Put CLAUDE.md in every active repo.** At minimum: test command, lint command, deploy target, key conventions. The portfolio and muse-shopping are both missing this.

3. **Run mcp-contributor refresh.sh.** It's been 6+ weeks. The weekly cron was designed but apparently never scheduled. Either schedule it or run it manually.

4. **Track skill activation in build-log.** Currently the build-log tracks commits but not skill invocations. Add a field: "skill: code-builder | mcp-contributor | none" to each entry.

5. **Cap skill scope to what you actually use.** mcp-contributor is 1,176 lines covering a workflow you've done 0 real times. vercel-ship covering patterns you hit weekly would deliver more value at 200 lines.
