# code-builder Skill Audit — 2026-05-31

## Methodology

Reviewed all public and accessible skill repos (`code-builder`, `mcp-contributor`, `skills-gallery`), 200+ build-log entries, 50+ recent Vercel deployments, and commit histories across `hannah-portfolio`, `interior-designer-portfolio`, `muse-shopping`, and `libby-hold-monitor`. Private repos (`claude-config`, `interior-designer-skill`, `skills-gallery`) were analyzed via metadata only.

---

## Finding 1: code-builder doesn't work in your most common environment

**Severity: Critical**

All recent development (35+ "Jamie's bach" commits, "Stuff" app, reddit-pulse fixes) was done via `claude-code_2-1-149_agent` — Claude Code on the web. The `isolation: "worktree"` parameter that code-builder depends on for parallel drafts requires a local git repo with worktree support. On web sessions, this silently downgrades to single-pass every time.

**Evidence:** Every Vercel deployment in May 2026 has `actor: "claude-code_2-1-149_agent"`. Zero deployments from local Claude Code.

**Fix in v2:** Added sequential-draft fallback that generates 3 drafts in-memory (apply → evaluate → revert → next) when worktrees are unavailable. Less isolated than worktrees but still captures the multi-draft benefit.

---

## Finding 2: Content/copy iteration is the #1 use case — and it's explicitly excluded

**Severity: Critical**

The skill says "Do NOT activate" for "Writing, design, planning, brainstorming." But 35+ of the last 40 commits are content work: copy tweaks, photo swaps, layout changes, itinerary edits. This is the highest-volume work pattern and gets zero skill support.

**Evidence:** Jamie's bach commits include copy-only changes like "fri games copy, sat subtitle, drop 'pastries' at Nitro" and "simpler CRU brunch publicNote" — small decisions where 2-3 variants would have been genuinely useful.

**Fix in v2:** Added "content mode" that activates for copy/design/layout tasks in code repos. Generates 2 content variants (concise vs. descriptive) instead of 5 code drafts. Scoring rubric adapted for content: accuracy, tone, completeness, mobile readability, link/reference correctness.

---

## Finding 3: No pre-push build validation — deployment failures shipped

**Severity: High**

Deployment `dpl_3xM1xmFHxTPv553zuhQsB4YA7wwe` ("lodging shows real 3-room layout") entered ERROR state on Vercel. The next commit was "fix TS build for lodging suites." The skill's scoring rubric includes typecheck/lint for parallel drafts, but single-pass tasks skip straight to logging with no build gate.

**Evidence:** ERROR deployment on 2026-05-26 followed immediately by a TS build fix commit.

**Fix in v2:** Added mandatory pre-commit build gate for ALL paths (single, parallel, and content). Runs `npm run build` / `next build` / project's build command. Blocks the commit if it fails.

---

## Finding 4: No rapid-iteration mode — 20 commits in one session with no batching

**Severity: Medium**

The Jamie's bach pattern: 15+ commits in a single day, each changing 1-3 lines of copy. Every change triggers a full code-builder evaluation cycle (scope → judgment gate → single pass → log). This is pure overhead — the user is iterating live and wants speed, not quality gates.

**Evidence:** 15 consecutive "Jamie's bach:" commits on 2026-05-26 alone, all single-line copy/photo changes.

**Fix in v2:** Added rapid-iteration detection. When ≥3 changes to the same file/page in one session, switch to "rapid mode": apply changes immediately, defer quality check to end-of-session or when the user says "done." Log one aggregate entry instead of 15 individual ones.

---

## Finding 5: Learnings are 7+ weeks stale

**Severity: Medium**

`Last synced: 2026-04-13 (initial backfill)`. The weekly Sunday 6pm sync has either not been set up or isn't running. 7 weeks of post-merge diffs, session patterns, and cross-repo mining signals have been lost.

**Evidence:** Learnings reference only calmar, schlacter.me, muse, and libby from the initial backfill. No entries from the Jamie's bach work, the interior-designer-portfolio work (which has 60+ build-log entries), or the "Stuff" app.

**Fix in v2:** Added staleness warning that fires on every activation when learnings are >14 days old. Simplified sync trigger — any phrasing like "sync" or "update learnings" works, not just the exact command.

---

## Finding 6: No deployment monitoring post-push

**Severity: Medium**

After pushing code, the skill logs the run and declares done. It never checks if the Vercel deployment actually succeeded. The ERROR deployment in Finding 3 would have been caught immediately with a 30-second post-push check.

**Fix in v2:** Added optional post-push deployment check. When Vercel MCP tools are available, polls deployment status for up to 2 minutes after push. Reports success/failure.

---

## Finding 7: No visual verification for UI changes

**Severity: Medium**

The learnings section documents 5+ visual bugs (crop tool zoom, floating UI clipping, white page crashes, drag-drop failures). All were caught by the user, not by the skill. The skill has no step for visual validation.

**Evidence:** §B learnings include "Floating UI inside scroll/overflow parent needs position: fixed + a portal" (2 repos), "Unscale getBoundingClientRect() values when ancestor has CSS transform" (2 citations), and "Guard nullable KV/API responses before destructuring" (3 citations — all crash-to-white-page bugs).

**Fix in v2:** Added visual verification step for UI-facing changes. Instructs Claude to use the `/run` or `/verify` skills if available, or to explicitly flag when visual verification wasn't possible.

---

## Finding 8: mcp-contributor drift issues accumulate without resolution

**Severity: Low (niche skill)**

7 automated drift detection issues are open, all generated weekly by GitHub Actions. The `refresh.sh` script correctly identifies drift but creates undifferentiated issues. Nobody triages them because they all look the same.

**Evidence:** Issues #4-#10, all titled variations of "Content drift detected" with identical labels.

**Not fixed in code-builder v2** (different skill), but recommendation: Update `refresh.sh` to classify drift as editorial (auto-fix) vs. substantive (needs review) and only create issues for the latter.

---

## Finding 9: Judgment gate calibration — file-count threshold too high

**Severity: Low**

The learnings note "3 runs: Hannah overrode single → parallel when task touched ≥2 files → lower the file-count threshold." The current gate still says ">1 file" for parallel. The threshold should be lowered or the gate should weight multi-file changes more heavily.

**Fix in v2:** Lowered the file-count parallel signal from ">1 file OR creates new file" to "≥2 files (including new files)." Added "touches both code and content files" as a parallel signal.

---

## Finding 10: Multi-session conflicts — Claude Code sessions overwriting each other's work

**Severity: High**

Two "restore" entries in the build-log show one Claude Code session deleting components that another session created:
- `restore: re-add BugReportButton component (deleted by other session)` (Apr 5)
- `restore: re-apply bug-fixer types, KV key, middleware, and layout` (Apr 5)

The skill has no awareness of concurrent sessions or guidance on protecting work from being clobbered.

**Fix in v2:** Added learning §A9. When working in a project with active concurrent sessions, grep for recent commits by other authors/sessions before making structural changes.

---

## Finding 11: Fabricated data — Claude generated fake URLs that shipped

**Severity: High**

Build-log entry: `Replace fabricated curated URLs with verified Reddit posts` (Apr 12). Claude generated non-existent URLs that were committed and deployed. The skill's scoring rubric doesn't penalize hallucinated content.

**Fix in v2:** Added learning §C19. Verify all URLs, data references, and external links before committing. Never generate URLs from memory.

---

## Finding 12: AI slop — generated text needed explicit cleanup

**Severity: Medium**

Build-log entry: `Tinker Flywheel: rewrite memo copy to kill AI slop` (Apr 13). Claude's natural language output required manual cleanup to remove generic AI-sounding prose.

**Fix in v2:** Added to content mode rubric: tone consistency scoring penalizes generic/corporate/AI-sounding language. Content mode variants should match the user's voice, not Claude's default tone.

---

## Finding 13: iOS Shortcuts — 10+ iterations on a single integration task

**Severity: Medium (process insight)**

Build-log shows versions v3 through v13 of iOS shortcuts for photo upload, spanning April 1-3. Approaches tried: Scriptable scripts, PWA share targets, signed shortcut files, multipart form bodies, raw bytes, plutil round-trips, hand-written XML. Most failed silently.

This is exactly the type of task where parallel drafts would have compressed 10 serial attempts into 5 parallel ones, evaluated objectively. But the skill wasn't invoked (or couldn't differentiate the approaches structurally).

**Observation for v2:** The judgment gate should recognize "trying to integrate with an external platform/API with undocumented behavior" as a hard parallel signal.

---

## Finding 14: Image migration produced cascading failures

**Severity: Medium (process insight)**

Vercel Blob → Cloudflare R2 migration (Apr 1-2) required: CDN suspension bypass, 1×1 placeholder repair, restore-and-remigrate endpoints, purge-broken-r2 endpoint, debug-urls endpoint. Each fix revealed the next problem.

**Observation for v2:** Data migration tasks should be treated as high-risk in the judgment gate. Added as a parallel signal: "touches data migration or storage layer."

---

## Blindspots (things not asked about but missed)

1. **No skill for the interior-designer-portfolio** — the most feature-rich project (60+ build-log entries, journal editor, annotation system, iOS shortcuts). It likely has project-specific patterns that code-builder's generic learnings don't capture.

2. **No cross-project skill coordination** — code-builder and mcp-contributor operate independently. When working in a project that has both a CLAUDE.md and code-builder active, there's no defined precedence beyond "repo rule wins."

3. **No skill for non-code automation** — libby-hold-monitor (GitHub Actions + Playwright), kindle-connector (torrent→Kindle bridge), keep-sync all have operational patterns (cron health, auth flows, secret management) that no skill covers.

4. **skills-gallery is abandoned** — 1 deployment ever (2026-03-11). The educational site about Claude Skills for non-engineers hasn't been updated since the initial launch. If this is a portfolio piece, it's stale.

5. **No "undo last deploy" skill** — When a deployment fails (like the lodging TS error), there's no quick rollback workflow. The user has to debug and push a fix commit.

6. **Auth integration is a recurring pain cascade** — muse-shopping had 6 consecutive auth fixes in one day (Apr 14-16): missing middleware mount, trust proxy, OAuth-only accounts, env var trimming, backend envelope parsing, missing DB column. Each fix revealed the next issue. The skill could include an "auth checklist" learning for OAuth/session work.

7. **Fabricated content shipped to production** — Claude generated fake Reddit URLs that deployed. The skill needs an explicit "never generate URLs from memory" rule and a verification step for external references.

8. **AI-sounding prose ships without detection** — An explicit "kill AI slop" rewrite was needed for the Tinker Flywheel memo. The content mode rubric should penalize generic AI tone.

9. **The skills-gallery site is static HTML, not Next.js** — The README describes it as "Next.js · Vercel" but it's actually 3 plain HTML files with a `vercel.json` rewrite. The portfolio description is inaccurate.
