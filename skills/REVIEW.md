# Skills Review — May 2026

Analysis of all Claude Code skills against actual usage patterns from Vercel deployments, git history, and build log.

## Skills reviewed

| Skill | Status | Last updated | Usage evidence |
|-------|--------|-------------|----------------|
| code-builder | Active (but not firing) | Apr 2026 | 0 parallel-mode runs detected in recent deploys |
| mcp-contributor | Dormant | Apr 16-17 | 0 MCP contributions made; 9 open issues |
| interior-designer-skill | Active (private) | Apr 2026 | ~100 commits in April |
| claude-config | Config repo | May 12 | Central config |

## Gap 1: code-builder never activates on real work

**Evidence:** 60+ recent deployments all show single-pass commits. No commit messages reference parallel drafts, winner selection, or scoring. Every commit has `actor: claude-code_*_agent` metadata indicating standard single-pass execution.

**Root cause:** The skill requires "meaningful" work to trigger parallel mode, but the dominant workflow is rapid micro-iteration (10-30 small changes per session). Even feature work tends to be incremental — "add Network tab to job tracker" is one commit, not a 5-draft competition.

**Fix applied:** Added "quick mode" as the default for most tasks. Quick mode does single-pass + build gate (the most valuable part). Parallel mode reserved for genuinely complex features.

## Gap 2: No build gate prevents ERROR deploys

**Evidence:** 2 Vercel ERROR deployments in schlacter-me:
- TS type narrowing error (literal `1` vs `0`)
- Turbopack cacheComponents incompatibility

Both required follow-up fix commits. Users of the deployed site saw broken pages until the fix landed.

**Fix applied:** Mandatory build gate before every push — `tsc --noEmit`, `eslint`, `npm run build`, `npm test`. Gate runs in both quick and parallel modes.

## Gap 3: Double Vercel deploys from same commit

**Evidence:** kindle-schlacter-me shows same-SHA deployments created within 200-500ms of each other. Two triggers fire: GitHub push webhook + Vercel CLI deploy.

**Fix applied:** Added deployment awareness section — push triggers webhook automatically, do not also run Vercel CLI deploy.

## Gap 4: Env var issues recur across projects

**Evidence:**
- `RESEND_API_KEY` with trailing `\n` (kindle-schlacter-me)
- `SYNC_SECRET` with whitespace (hannah-portfolio)
- Both caused silent auth/send failures requiring multiple debug commits

**Fix applied:** Added environment validation step and specific learnings about trimming env vars.

## Gap 5: mcp-contributor is comprehensive but unused

**Evidence:** Created April 16-17, 9 open issues filed, no updates since. The skill has thorough coverage of MCP governance, SEPs, and workflows. sources.yml tracks 80+ URLs with coverage status. But zero MCP contributions have been made.

**Recommendation:** Either:
- Use the skill to make an actual MCP contribution (good first issues exist)
- Archive it and reclaim the cognitive overhead
- The skill itself is well-built — it's the activation that's missing, not the content

## Gap 6: No session continuity mechanism

**Evidence:** kindle-schlacter-me has a manual "Add CONTINUE.md handoff for next session" commit. This suggests session state doesn't carry between Claude Code web sessions.

**Fix applied:** Added session continuity section to code-builder — suggests CONTINUE.md creation when session winds down.

## Gap 7: No skill for content-heavy rapid iteration

**Evidence:** The top activity categories by deployment volume:
1. Jamie's bach party site (~30 deploys in May) — copy, photos, layout, subdomain routing
2. Interior designer portfolio (~100 commits in April) — gallery, journal, floor plan, shortcuts
3. Kindle tool stack (~20 deploys in May) — scraper fixes, search integration, auth

All are content-heavy rapid iteration. The code-builder skill explicitly excluded non-code tasks.

**Fix applied:** code-builder now activates on content/UI iteration tasks and routes them to quick mode.

## Gap 8: Learnings not captured from actual pain

**Evidence (from build log / deployment history):**
- Gmail SafeLinks defeating magic link tokens (3 attempts)
- iOS Shortcuts integration (v1 through v13+)
- LibGen scraper rewrites as mirrors went down
- R2 image migration with 1x1 placeholder corruption
- Torrent search non-determinism causing "result not found"

These hard-won insights weren't in the original 12 learnings.

**Fix applied:** Expanded learnings from 12 to 18, all derived from actual deployment data.

## Blindspots identified

1. **No mobile QA** — Interior designer portfolio has mobile-specific bugs (hamburger nav, sticky toolbar, cramped header) but no skill verifies mobile rendering
2. **No OG/social preview verification** — Multiple commits for OG cards ("custom OG card for iMessage/Slack/Twitter previews") but no automated verification they render correctly
3. **No dependency freshness tracking** — No skill monitors for outdated or vulnerable dependencies
4. **No cross-repo coordination** — kindle-connector + kindle-schlacter-me share an API contract but each session works in isolation
5. **No image optimization** — Many commits add/swap images ("add 9 attendee headshots", "re-crop daniella, abbey, gwenna") but no automated optimization or format conversion

## What was asked but couldn't be done

Based on the iteration patterns (multiple attempts at the same task), these categories required the most rework:

1. **iOS Shortcuts** (13+ versions) — Plist format quirks, Scriptable vs native Shortcuts, signing requirements
2. **Email delivery** (Gmail SafeLinks, Resend size limits, magic link consumption) — Email client behavior is hard to predict from code
3. **Scraper stability** (LibGen mirrors, torrent search non-determinism) — External service instability requires defensive patterns
4. **Storage migration** (Vercel Blob → R2, 1x1 placeholders, CDN suspension) — Data migration edge cases are invisible until they corrupt data

## Summary of changes made

The updated `code-builder/SKILL.md`:
- Adds **quick mode** (default) for rapid iteration, reserves parallel mode for complex features
- Adds **mandatory build gate** before every push (tsc, eslint, build, test)
- Adds **environment validation** step for env vars
- Adds **deployment awareness** (avoid double Vercel deploys)
- Adds **session continuity** (CONTINUE.md suggestion)
- Expands learnings from **12 → 18** with real deployment-derived insights
- Activates on **content/UI tasks** (routed to quick mode) instead of ignoring them
