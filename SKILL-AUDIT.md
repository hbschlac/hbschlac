# Skill Audit — 2026-04-23

Cross-referenced both skills (code-builder, mcp-contributor) against 220 commits in the build-log, 4 open GitHub issues, source coverage data, and observed project patterns across 6+ active repositories.

---

## Skills reviewed

| Skill | Repo | Last updated | Status |
|-------|------|-------------|--------|
| code-builder | hbschlac/code-builder | 2026-04-14 | 1 commit, no issues |
| mcp-contributor | hbschlac/mcp-contributor | 2026-04-17 | 4 open issues, drift detected |

---

## code-builder: Findings

### What worked well
- The 5-draft parallel system with worktree isolation is architecturally sound
- The 100-point scoring rubric is objective and measurable
- The judgment gate correctly defaults to single-pass for small tasks
- The learning system concept (weekly sync, cross-repo mining, citation thresholds) is strong
- Run logging creates an auditable trail

### Pain points and unmet use cases

#### 1. No security awareness in the rubric
**Evidence:** Build-log shows OAuth implementations (Muse), Amazon auth flows (Libby), Stripe routing, Gmail API integration. The rubric scored correctness, tests, lint, conventions — but never checked for XSS, secrets in client code, missing auth guards, or injection risks.

**Impact:** High. Every web app Hannah ships handles user data, payments, or authentication. A draft that passes all tests but leaks an API key in client JS would score 95/100 under the old rubric.

**Fix applied:** Added 5-point Security criterion. Reduced Follows repo conventions from 10→5 to keep total at 100. Added explicit security check as Step 6.3 in merge validation.

#### 2. No smoke test after merge
**Evidence:** Build-log shows 220 commits across production apps deployed to Vercel. The old skill declared "done" after tests + typecheck + lint passed. But tests verify code correctness, not feature correctness — a component can pass all tests and still render broken in the browser.

**Impact:** High. Hannah ships frontend-heavy products (portfolio, interior-designer, Muse). The gap between "tests pass" and "feature works in browser" is where bugs hide.

**Fix applied:** Added smoke test step (Step 6.5). Frontend changes: start dev server, verify in browser. API changes: hit the endpoint. If smoke test can't run, must explicitly note why.

#### 3. Flat, unstructured learnings
**Evidence:** The 12 existing learnings were split into just 2 categories: "Claude process failures" (6) and "Concrete code-level patterns" (6). But the build-log shows work across very different domains — frontend (React, Next.js, CSS), API integrations (Gmail, OAuth, Stripe), deployment (Vercel, Cloudflare R2, GitHub Actions), and automation (Playwright, iOS Shortcuts). A single "code patterns" bucket forces Claude to scan all 30 bullets on every task instead of pulling domain-relevant ones.

**Impact:** Medium. As the learning list grows toward the 30-bullet cap, domain tagging becomes the difference between learnings that get applied and learnings that get ignored.

**Fix applied:** Split into 4 domains: §A Process, §B Frontend, §C API & Integration, §D Deployment & Infrastructure. Added 6 new learnings mined from the build-log activity.

#### 4. Static bias hints that don't adapt
**Evidence:** The 5 draft biases (simplest, idiomatic, readable, performant, free choice) are the same regardless of task type or accumulated learnings. If the learnings show that "OAuth token refresh must be atomic," draft 4 (correctness-focused) should know that for auth tasks — but it didn't.

**Impact:** Medium. The parallel system's value comes from diversity. If drafts don't use accumulated knowledge, the skill's learning system is partially wasted.

**Fix applied:** Added "Adapt from learnings" column to bias hints table. Each draft now pulls domain-matched learnings from the current learnings section.

#### 5. Weekly sync with no fallback
**Evidence:** The sync relies on `cron 0 18 * * 0`. If cron isn't set up (new machine, cloud environment, different OS), learnings never update. There's no way to detect this failure.

**Impact:** Medium. The learning system is the skill's long-term value. A silently broken sync means the skill stops improving.

**Fix applied:** Added in-session fallback: if `Last synced` date is >14 days old, run a lightweight sync (10 most recent run logs only) at session start.

#### 6. No cost awareness for parallel runs
**Evidence:** 5 parallel drafts use ~5x the tokens of a single pass. In a long session with many coding tasks, this adds up. The judgment gate helps, but there's no session-level throttle.

**Impact:** Low-medium. Matters more in long sessions with many tasks.

**Fix applied:** Added cost-awareness rule: if ≥3 parallel builds have already run in the current session, default subsequent tasks to single pass unless Hannah explicitly requests parallel.

#### 7. No domain tagging in run logs
**Evidence:** Run logs captured the task, judgment, scores, and cherry-picks — but not the domain (frontend, API, auth, etc.). This makes the learning sync's cross-referencing harder because it has to re-classify every historical run.

**Fix applied:** Added `domain` field to run log frontmatter. Also added `runner_up_score` and `security_findings` fields.

### Blindspots (things that weren't asked about but matter)

#### A. No E2E / integration test distinction
The rubric treats "tests pass" as binary (15 points). But there's a meaningful difference between unit tests passing and E2E tests (Playwright) passing. For the Libby Hold Monitor (which uses Playwright extensively), unit test pass ≠ working automation.

**Recommendation for future iteration:** Split "Tests pass" into "Unit tests" (10) and "Integration/E2E tests" (5) if the repo has both. Keep at 15 total for repos with only unit tests.

#### B. No accessibility checking
Hannah builds user-facing web apps. None of the rubric criteria check for accessibility (ARIA labels, keyboard navigation, color contrast, semantic HTML). This is a gap that becomes more important as the apps gain users.

**Recommendation for future iteration:** Add `axe-core` or `eslint-plugin-jsx-a11y` results as a bonus criterion (not scored, but flagged in run logs).

#### C. No deployment-specific validation
The skill validates code quality but not deployability. A Next.js app can pass all local checks and then fail Vercel build due to output mode mismatch, missing env vars, or static export limitations.

**Recommendation for future iteration:** If the repo has a Vercel config or `vercel.json`, run `vercel build --dry-run` (or equivalent) as part of merge validation.

---

## mcp-contributor: Findings

### What worked well
- Comprehensive 11-step contributor journey from intent to merged PR
- Automated drift detection with `refresh.sh` + SHA-256 hashing
- Source coverage tracking via `sources.yml` with coverage tiers
- Governance model coverage is thorough (6-tier ladder, WGs, IGs)

### Open issues (all addressed in IMPROVEMENTS.md)

| Issue | Title | Root cause | Fix |
|-------|-------|-----------|-----|
| #1 | No path from capability questions → §11.7 lifecycle | Missing cross-reference index | Add quick-find index table after §0.5 |
| #2 | §6 repo map missing Inspector, Registry, ext-* | Repo map only covers spec + SDKs | Add 6 missing repos + dynamic inventory command |
| #3 | §4 titled "SDK workflow" but applies broadly | Misleading section title | Retitle to "Non-spec repository workflow", broaden guidance |
| #4 | Drift detected (2026-04-19) | Upstream docs changed | Run refresh.sh, update drifted sections, commit new hashes |

### Additional gaps identified

1. **No small-change worked example** — §6.6 shows a SEP example but nothing for the more common typo/docs fix path. New contributors start small.
2. **17 GAP-MED sources unprocessed** — Inspector docs, SDK CONTRIBUTING.md files, transport spec details, and registry docs would help contributors but aren't ingested.
3. **Stale source inventory** — `sources.yml` indexed 2026-04-16. No mechanism to detect new pages added to modelcontextprotocol.io since then.
4. **No contribution tracking across sessions** — Session log placeholder exists but has no format. Contributors lose context between sessions.

### Blindspots

#### A. No local development setup validation
The skill lists prerequisites (Node 24+, npm 11+, Git) but doesn't verify them. A contributor could follow the workflow and fail at step 3 because their Node version is wrong. Adding a prerequisite check script (or even a checklist) would prevent wasted effort.

#### B. No CI expectations documentation
The skill walks through PR creation but doesn't explain what CI checks the PR will face. A contributor's PR might pass local validation but fail MCP's CI due to checks they didn't know about (schema validation, cross-SDK compatibility, etc.).

---

## Cross-skill observations

### Tasks that could have been done faster
- **Frontend iteration cycles** — The code-builder skill runs 5 drafts but doesn't shortcut when the task is a known pattern (e.g., "add a new page to the portfolio" is structurally identical each time). A pattern cache of "template tasks" could skip the judgment gate entirely and go straight to single-pass with a known recipe.
- **Auth/OAuth flows** — These are complex but follow well-documented patterns. The skill should recognize auth tasks and inject OAuth-specific learnings into every draft, not just draft 4.

### Tasks that could have had stronger outcomes
- **Security-sensitive features** — Stripe routing, OAuth, Gmail API integration all shipped without explicit security review in the rubric. The improved rubric fixes this.
- **Cross-cutting features** — Features that touch both frontend and backend (e.g., Muse checkout flow) would benefit from the judgment gate having a "cross-cutting" signal. Added.

### Things Claude couldn't do
- **Visual regression testing** — No ability to screenshot before/after and diff. The smoke test step is a partial mitigation.
- **Real user testing** — Can't simulate actual user flows in production. The skill correctly stays within dev-environment boundaries.
- **Deploy validation** — Can't verify Vercel deployments succeed post-merge. The deployment learnings help prevent known failure modes.

---

## Files in this audit

| File | Purpose |
|------|---------|
| `SKILL-AUDIT.md` | This document — full analysis and rationale |
| `skills/code-builder/SKILL.md` | Improved code-builder skill with all changes applied |
| `skills/mcp-contributor/IMPROVEMENTS.md` | Specific fixes for all 4 open issues + 4 additional gaps |
