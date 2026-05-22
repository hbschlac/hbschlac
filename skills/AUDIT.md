# Skills Audit — 2026-05-22

## Scope

Reviewed 2 skills (code-builder, mcp-contributor) against:
- build-log: 221 entries across 5+ production projects (Apr–May 2026)
- hannah-portfolio: 403.6 hours Claude Code, 187 sessions, 17 projects, 24 API endpoints
- Recent commits: 11 portfolio commits in last 30 days
- mcp-contributor: 9 commits, all April 16

---

## code-builder: Changes Implemented

### New: Infrastructure mode (Step 4c)
**Problem:** ~30% of build-log entries are infrastructure tasks (R2 migration, GHA workflows, Playwright automation, auth flows, cron debugging). code-builder was treating these as coding tasks — either spawning unnecessary parallel drafts or doing single-pass with no safety net.

**Evidence:** Vercel Blob suspension required emergency R2 migration with no rollback plan. GitHub API parallel PUTs caused data loss. OAuth edge cases (missing DB columns, trust proxy, OAuth-only accounts) surfaced only in production.

**Change:** New routing path in the judgment gate. Infrastructure tasks now get a pre-flight checklist (affected services, rollback plan, environment parity, concurrent access, data backup) instead of parallel drafts. Tasks are executed sequentially with verification after each step.

### New: Post-merge verification (Step 6.5)
**Problem:** code-builder declared "done" after tests + typecheck passed, but the build log shows many bugs caught only in production or dev server. "Tests pass" ≠ "feature works."

**Evidence:** Build log documents Playwright timeouts, auth redirect failures, broken image placeholders, and cron double-fires — none caught by test suites.

**Change:** New required step after merge: load the affected page/endpoint, test the golden path, verify auth flows end-to-end. If verification isn't possible, state explicitly what couldn't be verified.

### Changed: Rubric rebalanced
**Problem:** Original rubric had no security or data integrity dimensions. A draft that hardcoded a secret in client code lost 0 points. A draft that added lodash lost 3 points.

| Criterion | Old Weight | New Weight | Rationale |
|-----------|-----------|-----------|-----------|
| Security | 0 | 10 | §A2 already documented a secret exposure incident; rubric should catch it |
| Data integrity | 0 | 5 | Race conditions, null crashes documented 6× in build log |
| No new deps | 10 | 5 | Over-penalized; adding a well-maintained dep is often correct |
| Scope containment | 5 | 0 | Merged into "minimal diff" (redundant) |

### Changed: Learnings expanded (12 → 24 bullets)
**Added §C: Infrastructure patterns (6 bullets):**
- Playwright cold-start timeouts (4min+ on GHA)
- iOS Shortcuts multipart body validation (13 iterations documented)
- Cron idempotency guards (double-fire incidents)
- Storage migration integrity checks (R2 broken placeholders)
- Auth end-to-end testing (OAuth edge case compounding)
- Env var deployment target parity (4× trim fixes)

**Added to §A (2 bullets):**
- Serialize writes to shared state (GitHub API race condition)
- Always have migration/rollback path for cloud storage (Blob suspension)

### Changed: Cross-repo mining targets updated
Replaced stale repo names (`662-calmar-portfolio`) with current repos (`hannah-portfolio`, `interior-designer-portfolio`, `kindle-schlacter-me`). Added `migrate|rollback` to grep patterns.

---

## mcp-contributor: Issues Found (not yet implemented)

| Issue | Severity | Fix |
|-------|----------|-----|
| 36 days without refresh | HIGH | Run `./refresh.sh`, verify GHA workflow enabled |
| sources.yml version stale (0.1.0 vs 0.2.3) | MEDIUM | Update header |
| 26 gap-med pages uncovered | MEDIUM | Prioritize 5 most contributor-relevant |
| Session log has 1 entry | LOW | Add reminder prompt at end of skill |

---

## Blindspots: Skills That Don't Exist But Should

### 1. Portfolio project shipping (HIGH value)
17 projects all follow the same pattern: create slug, add to `content/projects.ts`, create page route, add screenshots, wire API endpoints. This has been done 17 times manually. A skill could scaffold the entire structure from a one-liner.

### 2. Scheduled job reliability (MEDIUM value)
24 API endpoints, many on cron. Build log shows double-fire, cold-start failures, and staleness detection issues. A skill could enforce idempotency, health checks, and monitoring for any new scheduled endpoint.

### 3. Cross-project coordination (MEDIUM value)
Shipping a new project requires updates across: portfolio site, build log, GitHub profile, claude-code-stats. Currently manual and often incomplete. A skill could checklist + automate the cross-repo updates.

---

## Weekly Sync: Resurrection Plan

The code-builder weekly sync (Sunday 6pm cron) has never run. This is the skill's most important feedback loop — without it, learnings stagnate and the rubric never recalibrates.

**To fix:**
1. Verify the cron job exists: `crontab -l | grep code-builder`
2. If missing, add: `0 18 * * 0 cd ~ && claude -p "code-builder sync"`
3. Create a test run log manually to verify the sync pipeline works
4. After 3 real parallel runs accumulate, revisit the deferred evaluations (holdout-commit, precision/recall, citation lint)
