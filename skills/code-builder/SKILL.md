# code-builder

Raises the floor of Claude's dev output by running **5 parallel implementations**, **self-scoring them against a measurable rubric**, and merging the winner.

---

## When this skill activates

**Any time Hannah is writing, changing, or fixing code, activate.**

### Explicit triggers
- `/code-builder` command
- "build this", "fix this bug", "add a feature", "implement X"

### Implicit triggers
- Git repo + coding task detected
- Error / stack trace pasted with request for changes
- Code pasted with modification request

### Does NOT activate
- Pure research / questions
- Design or planning conversations (no code output)
- Meta tasks (repo setup, config changes, README edits)

**Default behavior:** When uncertain, activate. Single-pass costs almost nothing.

---

## Announcement (required, every activation)

Before doing anything else, print exactly this one-line banner:

```
🔧 **code-builder activated** — [parallel, 5 drafts | single pass]. [≤15-word reason.]
```

---

## Workflow

### Step 1 — Scope
State the task in one line.

### Step 2 — Identify targets
List files likely to change.

### Step 3 — Judgment gate

Decide: **parallel (5 drafts)** vs. **single pass**.

**Default is single.** Escalate to parallel only when ≥2 parallel signals fire OR any hard signal fires.

| Gate | Parallel threshold | Single threshold |
|---|---|---|
| LOC estimate | >30 lines changed | <10 lines |
| Files touched | >1 file OR creates new file | Exactly 1 existing file |
| Design space | Multiple valid architectures | One obviously correct path |
| Novelty | New pattern in repo | Variation of existing pattern |
| Risk | Touches critical path (auth, checkout, payments, data) | Contained to leaf component |
| Task type | Feature / refactor / greenfield | Targeted bug fix (known root cause) |
| Phrasing | Open-ended ("build X", "add a feature for Y") | Specific ("change line 42 to...") |
| Domain complexity | Cross-cutting (API + frontend + DB) | Single-layer change |

**Hard signals (any one decides):**
- Hannah explicit override → obey
- Not a git repo → force **single** (worktrees require git)
- Live debugging with rapid iteration → force **single**
- Greenfield prototype → force **parallel**

### Step 4a — Parallel path (N=5)

**Prerequisite:** Claude's primary working directory must be the project git repo (verify via `git rev-parse --git-dir`).

Spawn **5 Agent calls in parallel**, each with:
- `isolation: "worktree"` (isolated branch per draft — no file collisions)
- `run_in_background: true`

**Bias hints for differentiation:**

| Draft | Bias | Adapt from learnings |
|-------|------|---------------------|
| 1 | **Simplest possible** — fewest lines, no abstractions | If learnings show simpler approaches consistently win in this repo, weight correctness over cleverness |
| 2 | **Most idiomatic to repo** — match existing patterns exactly | Pull specific patterns from `§B Current learnings` for this repo's stack |
| 3 | **Optimize for readability** — clearest naming, smallest functions | If frontend task: prioritize component decomposition and prop clarity |
| 4 | **Optimize for correctness + edge cases** — handle errors, nulls, auth edge cases | If API/auth task: add rate-limit handling, token refresh, error boundaries |
| 5 | **Free choice** — go with best instinct | If learnings show a recurring failure mode for this task type, specifically avoid it |

Each draft agent prompt **must include:**
- The full task description
- List of files to change
- Repo conventions detected (naming, imports, file structure)
- Relevant learnings from `## Current learnings` section (domain-matched)
- Instruction to run tests + typecheck + lint after implementation

### Step 4b — Single pass

Implement directly. Still run tests + typecheck + lint after.

### Step 5 — Self-evaluate and pick the winner (parallel only)

**Claude picks. Do NOT ask Hannah to review 5 diffs.**

Score each draft out of 100 points:

| Criterion | Weight | Measurement |
|-----------|--------|-------------|
| Correctness | 25 | Walk each requirement; deduct per miss |
| Tests pass | 15 | Run `npm test` / `pytest` / project test cmd; 0 failures = 15, else 0 |
| Typecheck clean | 10 | `tsc --noEmit` / equivalent; 0 errors = 10 |
| Lint clean | 5 | Project's lint cmd; 0 warnings = 5 |
| Minimal diff | 10 | `10 × (min_LOC / this_LOC)` across all drafts |
| No unnecessary new deps | 10 | 0 new = 10; each new dep = −3 |
| Reuses existing utilities | 10 | Did it grep for and reuse existing helpers/utils? |
| Follows repo conventions | 5 | Naming, file structure, import style consistency |
| Scope containment | 5 | Deduct if unrelated files touched |
| Security | 5 | No XSS vectors, no secrets in client code, no SQL injection, inputs validated at boundaries |

**Total: 100 points.**

**Tiebreakers:** (1) smallest diff, (2) draft 2 (most idiomatic).

**Draft diversity check:** If ≥3 drafts converge on the same approach (identical file structure + logic flow), note this in the run log. Convergence is signal — it likely means the approach is correct. Divergence is opportunity — look for complementary strengths to cherry-pick.

### Step 6 — Merge validation (prevent loss + redundancy)

1. **Gap check** — Re-read the original task. Confirm winner covers every requirement. If gaps exist, cherry-pick specific hunks from rejected drafts (not wholesale branches).
2. **Redundancy check** — Scan for unused imports, dead code, debug logs, shadowed utilities. Strip any found.
3. **Security check** — Scan for:
   - Secrets or API keys in client-accessible code
   - Unsanitized user input rendered as HTML
   - Missing auth checks on new endpoints
   - `dangerouslySetInnerHTML` or `eval()` usage without justification
4. **Rerun validation** — Tests + typecheck + lint on the final merged diff. All must pass.
5. **Smoke test** — If the change is user-facing (UI component, page, API endpoint):
   - Frontend: start dev server, verify the feature renders and behaves correctly in browser
   - API: hit the endpoint with a test request, verify response
   - If smoke test cannot be run (no dev server, headless env), note explicitly: `⚠ Smoke test skipped — [reason]`
6. **Merge** — Merge winner's branch to working branch.
7. **Clean up** — `git worktree remove` all 5; delete losing branches; keep winner's branch ref for audit.
8. **Report in one line:**
   ```
   ✓ Merged draft {N}/5 (score {X}/100). {≤15-word reason}. {Cherry-picks: [files] | No gaps.} Tests ✓ Types ✓ Lint ✓ Security ✓. {Smoke: ✓ | ⚠ skipped}
   ```

### Step 7 — Log the run (required, always)

Write to `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`:

```markdown
---
date: YYYY-MM-DD
task_slug: kebab-case-summary
repo: owner/repo-name
judgment: parallel | single
override: none | hannah-forced-parallel | hannah-forced-single
winner_draft: N
winner_sha: abc1234
winner_score: XX
runner_up_score: XX
cherry_picks: [files] | none
security_findings: [items] | none
smoke_test: pass | skip | fail
domain: frontend | api | auth | data | infra | mixed
---

## Task
{verbatim task from Hannah}

## Judgment reasoning
{1-2 sentences on why parallel vs. single}

## Drafts
### Draft 1 — Simplest
- Approach: ...
- Files: ...
- LOC: ...
- Score: XX/100
- SHA: ...
- Notable: ...

{repeat for all 5}

## Cherry-picks
{what was taken from non-winners and why, or "None — winner was complete"}

## Security review
{any findings or "Clean — no issues detected"}

## In-session feedback
{anything Hannah said about the result, or "None"}

## Notes
{timeouts, worktree failures, diversity observations, etc.}
```

---

## Syncing learnings

### Scheduled sync
Cron: `0 18 * * 0` (Sunday 6pm)

### In-session fallback sync
If the cron hasn't run in >14 days (check last-synced date in `## Current learnings`), run a lightweight sync at the start of the next session: scan the 10 most recent run logs only.

### On-demand sync
Hannah says "sync learnings" → run full sync immediately.

### Sync procedure

**Sources (mine all 5):**
1. Run logs: `~/.claude/skills/code-builder/runs/*.md`
2. Post-merge git diffs: `git log` + `git diff` against `winner_sha` — what did Hannah change after merge? (signals a miss)
3. In-session feedback captured in run logs
4. Judgment overrides (Hannah forced parallel/single — was she right?)
5. Cross-repo mining: bounded to 50 most recent commits per repo, filtered by author + keywords (error, fix, revert, bug, hack, workaround)

**Pass 1 — Count patterns:** A candidate learning needs ≥2 citations (distinct run logs, commits, or feedback instances).

**Pass 2 — Categorize and refine:**
- Assign each learning to a domain: `process`, `frontend`, `api`, `auth`, `data`, `deployment`, `testing`
- Update citation counts on existing learnings
- If new learning contradicts existing → supersede the old one (keep the newer, better-cited version)

**Pass 3 — Prune to cap:**
- Hard cap: **30 bullets** across all domains
- Prune by: (1) oldest last-cited date, (2) fewest citations, (3) superseded by newer learning
- Never prune a learning with ≥5 citations regardless of age

---

## Current learnings

Last synced: 2026-04-13 (initial backfill — 4 repos + 13 session summaries; 12 bullets)

### §A. Claude process failures
- Never call `Skill()` from inside a scheduled task — circular dispatch
- No hardcoded secrets in client JS — even internal tools ship to browser
- "Done" requires green tests + typecheck, not just compile-pass
- Resolve merge conflicts by re-running tests on the merge result, not eyeballing diffs
- Guard nullable API responses before destructuring (especially third-party APIs)
- Grep for existing helpers before writing new ones — duplicate utils are the #1 post-merge edit

### §B. Frontend patterns
- Floating UI inside scrollable parents needs `position: fixed` + portal
- Rules of Hooks: no conditional calls, no hooks in callbacks or effects
- `useEffect` subscriptions must return cleanup functions
- Unscale `getBoundingClientRect()` values when ancestor has CSS `transform`
- Save editor selection before modal open; restore on close

### §C. API & integration patterns
- Validate + trim `process.env.X` at read-site — whitespace and quoting variance across env managers
- OAuth token refresh must be atomic — never let two requests race on refresh
- Rate-limit API calls with exponential backoff; don't retry 4xx errors (except 429)
- Gmail/email API responses: always handle partial/empty payloads (messages without bodies, threads without messages)

### §D. Deployment & infrastructure
- Vercel builds: check `next.config` output mode matches deployment target (static vs. serverless)
- Playwright/E2E in CI: use `--headed` only locally; CI needs `--headless` + explicit viewport
- Cloudflare R2: presigned URLs expire — never cache them in client state beyond 1 request

---

## Meta notes

- **Worktree failures:** If `git worktree add` fails (dirty tree, locked worktree), fall back to single pass. Log the failure.
- **Deferred evaluation:** If tests take >60s per draft, run scoring criteria that don't require execution first (correctness walk, diff size, convention check). Only run tests for the top 2 candidates.
- **Source pinning:** This file is the single source of truth. Do not split into multiple files. The learnings section is the only mutable section; everything else is stable.
- **Cost awareness:** If a session has already run ≥3 parallel builds, default subsequent tasks to single pass unless Hannah explicitly requests parallel. Log accumulated parallel runs in the session.

---

## Changelog

- 2026-04-13: Initial backfill sanity test — mined 4 repos + 13 session summaries. 12 rules extracted, each with ≥2 citations.
- 2026-04-23: Skill audit improvements:
  - Added **security criterion** (5pt) to rubric; reduced conventions from 10→5 to keep total at 100
  - Added **smoke test** step after merge (Step 6.5) — frontend: dev server; API: test request
  - Added **security check** as explicit merge-validation substep
  - Split learnings into **4 domains** (process, frontend, API, deployment) from 2 (process, code)
  - Added **3 new learnings** from build-log mining: OAuth atomicity, Gmail partial payloads, Vercel output modes, R2 presigned URL expiry, Playwright CI headless, rate-limit backoff
  - Added **draft diversity check** — detect convergence vs. divergence across 5 drafts
  - Added **adaptive bias hints** — drafts now pull from domain-matched learnings
  - Added **in-session fallback sync** — if cron hasn't run in 14 days, auto-sync from last 10 runs
  - Added **cost awareness** — cap parallel runs per session at 3 unless overridden
  - Added **domain tag** to run log frontmatter for better learning categorization
  - Added **runner_up_score** and **security_findings** to run log frontmatter
  - Added **cross-cutting domain complexity** signal to judgment gate
