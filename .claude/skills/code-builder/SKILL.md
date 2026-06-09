---
name: code-builder
description: >
  Improves code quality through four execution modes: single pass (fast, obvious),
  parallel (N isolated drafts scored on rubric, winner merged), debug loop
  (hypothesis-test-learn for integration failures), and visual (3 drafts for
  CSS/styling). Self-improving via learning sync.
---

# code-builder

## Activation

Auto-triggers on coding tasks. Explicit: `/code-builder`, "build this," "fix this bug."
Implicit: working in a git repo while describing a coding task, sharing error messages.

Do NOT activate for: pure code reading, research, writing prose, design, planning, meta-tasks.

Default: when uncertain, activate. Single-pass costs nothing; missing a dev task is worse.

**Conflict:** If `mcp-contributor` is active (guiding a PR to the MCP org), code-builder defers. code-builder handles only code tasks mcp-contributor doesn't claim.

## Announcement

> **code-builder activated** — [parallel, N drafts | single pass | debug loop | visual, 3 drafts]. [reason.]

Suppress after 3rd consecutive single-pass in the same session.

---

## Step 0 — Pre-flight Research Gate

Before writing any code, answer three questions silently:

1. **Is the domain well-understood?** Standard web dev, API integration, DB queries → yes. Binary formats (plists, Shortcuts, protocol buffers), undocumented vendor APIs, hardware protocols → no. If no: tell the user before coding. Propose a spike: a throwaway prototype that validates the approach in <30 minutes. Don't commit spike output.

2. **Is there an established library or pattern?** Search npm/PyPI/crates.io for existing solutions. If a maintained library exists, use it instead of hand-rolling.

3. **Has this been attempted before in this repo?** Check git log for prior attempts:
   ```bash
   git log --all --oneline --grep="fix\|revert" -- {files}
   ```
   If 3+ prior attempts found: **stop.** Print the failure history. Suggest either a fundamentally different approach, an external library, or scoping down the feature. Do not iterate on the same strategy.

---

## Step 1 — Pre-flight Checks

Runs in ALL modes before writing code.

### 1A. Git Repo Gate (BLOCKING)

```bash
git rev-parse --git-dir 2>/dev/null
```

If not a git repo: offer `git init`. If declined, force single-pass mode — parallel requires git worktrees. Do NOT proceed with parallel mode in a non-git directory.

### 1B. Language & Framework Detection

Detect the project's stack before assuming commands. Check in order:

| Indicator | Stack | Test cmd | Lint cmd | Type cmd |
|---|---|---|---|---|
| `package.json` + `next.config.*` | Next.js | from scripts | from scripts | `tsc --noEmit` |
| `package.json` + `vite.config.*` | Vite | from scripts | from scripts | `tsc --noEmit` |
| `package.json` (other) | Node.js | from scripts | from scripts | `tsc --noEmit` if tsconfig |
| `Cargo.toml` | Rust | `cargo test` | `cargo clippy` | `cargo check` |
| `go.mod` | Go | `go test ./...` | `go vet ./...` | — |
| `pyproject.toml` / `requirements.txt` | Python | `pytest` | `ruff check .` or `flake8` | `mypy .` if configured |
| `Gemfile` | Ruby | `bundle exec rspec` | `rubocop` | — |
| `pom.xml` / `build.gradle` | Java/Kotlin | `mvn test` / `gradle test` | — | — |
| `.github/workflows/*.yml` | GH Actions | per workflow | per workflow | — |
| `supabase/` dir + `package.json` | Next.js + Supabase | from scripts | from scripts | `tsc --noEmit` |

Read from `package.json` scripts when available — don't assume `npm test` exists.

### 1C. Claude Process Failures

| Check | Action |
|---|---|
| Task touches `process.env.*`? | Validate + trim at read-site. Check `NEXT_PUBLIC_` exposure — ships to browser. |
| Task adds a `useEffect`? | Must return cleanup if it subscribes, starts timer, or sets state. |
| Task uses floating UI (tooltip, dropdown, popover)? | Use `position: fixed` + portal, not `absolute` inside scroll parents. |
| Task destructures API/KV response? | Guard nullable response before destructuring. Render `<EmptyState />` or early-return. |
| Task could duplicate existing utility? | `grep -r` for similar helpers before writing new ones. |
| Task adds conditional logic around a hook? | No conditional calls, no hooks in callbacks/effects. |
| Task adds user-facing text? | Run content-quality checks. |

### 1D. Deployment & Integration

| Check | Action |
|---|---|
| Deploying to Vercel? | No `fs` in serverless. `trust proxy` if behind proxy. Invoke vercel-ship if available. |
| Custom server + Vercel? | **Diff dev entry (e.g. `server.ts`) against serverless entry (e.g. `api/index.ts`).** Middleware order, error handler placement, and body parser config must match. Silent 500s come from divergence between these two files. |
| Task changes auth/OAuth? | Verify redirect URLs for local AND production. Check cookie domain. |
| Task involves file storage? | Verify upload-store-retrieve end-to-end. Check URL format. |
| Task references external URLs? | Verify every URL exists. Never fabricate. Use `[TODO: add URL]` if unverified. |
| Monorepo or multi-directory? | Install deps in ALL entry points, not just root. |

### 1E. Cross-Session Safety

| Check | Action |
|---|---|
| Uncommitted changes? | `git stash list` + `git status`. Do NOT overwrite — ask first. |
| Files modified in last 2 hours by different commit? | Flag potential conflict. |
| Components imported by 3+ files? | Extra caution on deletion — verify all import sites. |
| Similar work on other branches? | `git branch -a --sort=-committerdate | head -20`. Build on existing work. |

Output: one-line summary of checks that fired, or "Pre-flight clean."

---

## Step 2 — Scope the Task

State the task in one line. Identify:
- Files likely to change
- Greenfield (new) or modification (fix/tweak)
- Design space: multiple valid approaches or one obvious path?
- Integration surface: external services, APIs, device-specific behavior?
- Estimated complexity: small (<30 LOC), medium (30-150 LOC), large (>150 LOC)
- Visual: is this primarily CSS/styling/layout?

---

## Step 3 — Judgment Gate (with task-size adaptation)

Four modes. Default is single pass.

### Quick-fix bypass

If ALL of these are true, skip directly to single-pass (Step 4b):
- <10 LOC change
- Single file
- Obvious fix (typo, missing import, off-by-one, rename)
- No design decisions

Skip the full rubric scoring for these. Just fix it.

### Parallel threshold (N=3 or N=5)

Escalate when >=2 soft signals fire OR any hard signal fires:

Soft signals: >30 LOC, >1 file, multiple valid architectures, new pattern to repo, touches critical path, feature/refactor/greenfield, open-ended phrasing.

**Draft count:**
- Large (>150 LOC, >3 files) → N=5
- Medium (30-150 LOC) → N=3
- Near rate limits or long session → N=3 regardless

### Visual mode threshold (N=3)

Escalate when the task is primarily CSS, styling, or layout:
- Adding/redesigning a visual component (card, hero, navigation, gallery)
- Color scheme, spacing, typography, or animation changes
- Responsive layout or mobile-specific styling
- ">60% of the change is CSS/Tailwind/styled-components"

### Debug loop threshold

Escalate when ANY fire:
- Attempt >=2 at the same task (prior failed/reverted)
- Error involves external integration (API, OAuth, device-specific)
- Reproduces in production but not locally (or vice versa)
- User says "this keeps breaking" or "I've tried X already"
- 3+ consecutive fix commits in same area in recent git log
- Current error matches a recently committed fix (regression)

### Single pass (default)

<30 LOC, 1 file, one obvious path, existing pattern, leaf component, known root cause.

### Hard overrides

- User explicit override → obey
- Not a git repo → force single (after offering `git init`)
- Live debugging with rapid iteration → force single
- Greenfield prototype from scratch → force parallel
- "This keeps failing" / integration failure → force debug loop

---

## Step 4a — Parallel Path

1. **Git repo gate (BLOCKING):** `git rev-parse --git-dir` must succeed. If not, abort parallel — do NOT silently fall back to single.

2. `mkdir -p ~/.claude/skills/code-builder/runs/`

3. Spawn **N `Agent` calls in parallel** (single message), each with:
   - `isolation: "worktree"`, `run_in_background: true`, `subagent_type: "general-purpose"`
   - Differentiation bias:
     - Draft 1: simplest possible — fewest lines, no abstractions
     - Draft 2: most idiomatic to this repo — match existing patterns exactly
     - Draft 3: optimize for readability — clearest naming, smallest functions
     - (N=5) Draft 4: optimize for edge cases and defensive correctness
     - (N=5) Draft 5: best instinct — free choice
   - Each prompt includes: the detected test/lint/typecheck commands from Step 1B (not hardcoded npm/pytest). "Before coding, `grep -r` for existing utilities. After coding, run [detected test cmd], [detected typecheck cmd], and [detected lint cmd]."

4. Each draft: commit on worktree branch, report approach (2 lines), files touched, LOC, SHA, edge cases.

5. **Quorum and failure handling:**
   - Wait for all N. Timeout: 5 minutes per draft.
   - If 1-2 drafts fail/timeout: continue with survivors. Score normally.
   - If 3+ drafts fail (N=5) or 2+ fail (N=3): **abort parallel.** Report which failed and why. Fall back to single-pass with the best surviving draft as starting point, or debug-loop if failures suggest an integration issue.
   - If ALL fail: do NOT retry parallel. Switch to debug-loop mode. The task likely has an environmental or integration issue that parallel drafts won't solve.

## Step 4b — Single Path

Execute normally. Skip to Step 7.

## Step 4c — Debug Loop

### Pre-Step 0: Failed Approach Scan (mandatory)

```bash
git log --all --oneline -20 -- {file}
git log --all --oneline --grep="fix" -- {file}
```

List prior attempts. These approaches are OFF LIMITS.

### Step 1: State the failure

> What happens: [exact error/behavior]
> What should happen: [expected behavior]
> Environment: [local/Vercel/GHA/device]

### Step 2: Read before writing

Do NOT write any code yet. Instead:
1. Read the full function, its callers, and dependencies — not just the error line.
2. Read the last 3-5 diffs touching this area: `git log -p -5 -- {file}`
3. Read error messages, stack traces, browser console output.
4. Check if the bug is environment-specific.

### Step 3: Hypothesize

Single-sentence hypothesis about ROOT CAUSE (not symptom):

```
debug-loop: hypothesis — {one sentence}
```

Root cause vs symptom:
- Symptom: "popup doesn't close" / Root: "window.close() blocked because reload() cleared opener reference"
- Symptom: "API returns 500" / Root: "trust proxy not set, rate limiter reads 127.0.0.1"

### Step 4: Prove it

Write a minimal diagnostic (NOT the fix):
- Single console.log at suspected root cause
- Failing test that reproduces the bug
- curl command demonstrating API behavior

### Step 5: Fix (only after proof)

Target the proven root cause. The fix must:
- Address root cause, not paper over symptom
- Not revert to an approach that already failed
- Include a guard or test preventing regression

### Step 6: Verify

Run the same diagnostic from Step 4. Check for side effects. Run detected test commands.

### Debug Loop Limits

- **5 hypothesis cycles max.** After 5, report what you've ruled out and what data would narrow it down.
- **Never change multiple variables simultaneously.**
- **Never repeat a failed approach.**
- **After 3+ attempts at the same integration, STOP and write what you've ruled out.**

## Step 4d — Visual Path (3 drafts)

For CSS/styling/layout tasks. Uses 3 drafts with visual-specific biases:

1. Spawn **3 `Agent` calls in parallel**, each with `isolation: "worktree"`:
   - Draft 1: minimal CSS — fewest properties, simplest selectors
   - Draft 2: match the repo's existing design language exactly
   - Draft 3: mobile-first, best accessibility

2. Score using the visual rubric variant (Step 5, visual criteria).

---

## Step 5 — Self-Evaluate and Pick Winner (Parallel/Visual Only)

### Standard rubric (100 points)

| Criterion | Weight |
|---|---|
| Correctness (walk each requirement) | 25 |
| Tests pass (using detected test cmd) | 15 (0 if any fail; redistribute to Correctness if no tests) |
| Typecheck clean (using detected type cmd) | 10 |
| Lint clean (using detected lint cmd) | 5 |
| Minimal diff (`10 * min_LOC / this_LOC`) | 10 |
| No unnecessary deps (0 new=10; each new=-3) | 10 |
| Reuses existing utilities | 10 |
| Follows repo conventions | 10 |
| Scope containment | 5 |

Tiebreak bonus: integration safety +5, pre-flight compliance +5, security +5.
Final tiebreak: (1) smallest diff, (2) draft 2 (most idiomatic).

### Visual rubric variant (replaces Tests/Typecheck/Lint with visual criteria)

| Criterion | Weight |
|---|---|
| Correctness (matches design intent) | 20 |
| Mobile responsiveness | 15 |
| Visual consistency with existing design | 15 |
| Accessibility (contrast, focus states, screen reader) | 10 |
| Minimal diff | 10 |
| No unnecessary deps | 10 |
| Follows repo's CSS conventions (Tailwind/modules/styled) | 10 |
| Animation/transition smoothness | 5 |
| Scope containment | 5 |

Record full score breakdown in run log.

---

## Step 6 — Merge Validation

1. **Gap check:** Re-read original task. Cherry-pick from rejected drafts if a gap exists.
2. **Cherry-pick rollback:** If cherry-pick conflicts or breaks tests, abort the cherry-pick (`git cherry-pick --abort`) and note what couldn't be recovered. Do not force.
3. **Redundancy check:** Strip unused imports, dead code, debug logs, duplicated helpers.
4. **Rerun validation:** Detected test + typecheck + lint on merged diff.
5. **Deployment check:** No `fs` in serverless, env vars trimmed, auth redirects use production domain. If Vercel multi-builder, verify BOTH entry points.
6. **Content check:** If diff includes user-facing text, invoke content-quality skill.
7. **Data check:** Verify all external URLs/endpoints exist.
8. **Merge** winner's branch. Clean up: `git worktree list` then `git worktree remove`.
9. **Report:** `Merged draft {N}/{total} (score {X}/100). {reason.} Tests / Types / Lint.`

---

## Step 7 — Log the Run

Determine log location based on environment:
- **Laptop/persistent:** `~/.claude/skills/code-builder/runs/`
- **Web session (ephemeral container):** `.claude/runs/` in the current repo (survives via git push)

```bash
if [ -d "$HOME/.claude/skills/code-builder" ]; then
  LOG_DIR="$HOME/.claude/skills/code-builder/runs"
else
  LOG_DIR=".claude/runs"
fi
mkdir -p "$LOG_DIR"
```

Log entry (append to `{LOG_DIR}/{date}.jsonl`):

```json
{
  "date": "YYYY-MM-DD",
  "mode": "parallel|single|debug|visual",
  "task": "one-line summary",
  "drafts": 5,
  "winner": 2,
  "winner_bias": "idiomatic",
  "scores": [72, 89, 85, 78, 81],
  "cherry_picked": [4],
  "lang": "typescript",
  "framework": "nextjs",
  "repo": "repo-name",
  "loc_changed": 47,
  "files_changed": 3
}
```

---

## Current Learnings

Last synced: 2026-05-29 (manual consolidation from 28 session branches — automated sync has NEVER executed)

**WARNING:** The weekly sync (Sunday 6pm) is this skill's core differentiator but no cron/GH Action has ever been set up. These learnings are static since the initial backfill.

**To unblock:** Create `.github/workflows/code-builder-sync.yml` in this repo:
```yaml
name: code-builder learning sync
on:
  schedule:
    - cron: '0 1 * * 0'  # Sunday 1am UTC (6pm PT)
  workflow_dispatch:
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Collect run logs
        run: |
          mkdir -p .claude/skills/code-builder/runs
          # Aggregate .claude/runs/*.jsonl from recent sessions
          find .claude/runs -name '*.jsonl' -newer .claude/skills/code-builder/SKILL.md 2>/dev/null | while read f; do
            cat "$f" >> .claude/skills/code-builder/runs/aggregated.jsonl
          done
      - name: Commit if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add .claude/skills/code-builder/runs/
          git diff --cached --quiet || git commit -m "chore: code-builder learning sync $(date +%Y-%m-%d)" && git push
```
This is a starting point — the real sync should analyze run logs and update the learnings section.

### Process

- **Trim all `process.env` at the read-site.** 4 separate fixes across schlacter.me; also hit in muse OAuth. Pattern: `process.env.X?.trim()`. (5 citations)
- **Verify BOTH dev server AND serverless entry middleware order.** Silent 500s when error handler is before routes in one but not the other. (1 citation: muse `d01750d`)
- **Set `trust proxy` behind any reverse proxy.** Broke OAuth in muse, session validation in calmar. (2 citations: muse `0c92c13`, `3a83f67`)
- **Don't iterate on the same strategy 3+ times.** If it didn't work twice, the approach is wrong, not the execution. (build-log: 13 iOS Shortcut versions, Playwright timeout escalation)
- **Guard nullable API responses before destructuring.** KV/API calls return null on miss. (2 citations)
- **Check for existing utilities before writing new ones.** Duplicated helpers across 3 repos. (3 citations)

### Python

- **Always create and activate a venv before installing.** `python3 -m venv .venv && source .venv/bin/activate`. Never install globally. (Pattern: keep-sync, kindle-connector, libby-hold-monitor all use venvs)
- **Use `if __name__ == "__main__":` in every entry point.** Prevents double-execution when imported by tests. (Pattern: every Python CLI/automation project)
- **Pin deps with `pip freeze > requirements.txt` after install.** Unpinned deps break on next session/deploy. (Pattern: 3 repos had version drift)
- **Use `pathlib.Path` over `os.path`.** Consistent cross-platform, fewer string manipulation bugs.
- **For scheduled automation, validate the happy path AND the "nothing to do" path.** Cron jobs that crash on empty input generate noise. (Pattern: libby-hold-monitor, keep-sync)
- **Check `sys.exit()` codes in GH Actions.** Non-zero exits fail the workflow. Intentional "nothing to do" should exit 0.

### Integration

- **Offload Playwright/puppeteer to GHA instead of serverless.** Cold starts on Vercel/Render exceed 30s. (1 citation: libby-hold-monitor architecture pivot)
- **Register both www and non-www OAuth redirect URIs.** Google treats them as different. (1 citation: muse `68d29d4`)
- **Handle OAuth-only accounts in password login flow.** `bcrypt.compare(input, null)` crashes. (1 citation: muse `3a83f67`)

### Automation / Scheduling

- **GitHub Actions cron syntax uses UTC.** `schedule: cron: '0 6 * * *'` is 6am UTC, not local.
- **Always add `workflow_dispatch` alongside `schedule`.** Enables manual re-runs during debugging without waiting for the next cron tick.
- **For long-running automations, add a timeout.** `timeout-minutes: 10` prevents hung jobs from consuming quota.
- **Log the "last successful run" timestamp.** Without this, debugging "it stopped working" means reading days of GH Actions logs.

### Merge Safety

- **Never force-push without checking other sessions' branches.** 3 incidents of code loss from merge conflicts in calmar. (3 citations)
- **Check `git branch -a --sort=-committerdate` before starting.** Build on existing branch work, don't start over. (28 orphaned branches as evidence)

### Supabase

- **Enable RLS on every table, then write policies.** Default-deny means forgetting a policy locks out the app. But forgetting RLS exposes the table to any authenticated user. (Pattern: recs.community initial schema)
- **Security-definer functions need `SET search_path = public`.** Without it, a malicious user can shadow `public` tables with their own schema. (Pattern: recs.community `is_active_member`, `is_admin`)
- **Use triggers for cross-table consistency, not application code.** Profile creation on signup, admin membership on community creation — these must succeed atomically. Application-level inserts can fail between steps. (Pattern: recs.community `on_auth_user_created`, `on_community_created`)
- **Nullable FK on user delete preserves data.** `contributor_id UUID REFERENCES auth.users ON DELETE SET NULL` keeps the rec but shows "Former member." Don't CASCADE delete user-generated content. (Pattern: recs.community `recs` table)
- **Test RLS policies with positive AND negative cases.** "Can a member see their community's recs?" AND "Can a non-member see them?" Both must be verified. (Pattern: recs.community review checklist)
- **Supabase auth middleware must refresh the session on every request.** Use `@supabase/ssr` with the three-file pattern (server, client, middleware). The middleware calls `getUser()` which refreshes the cookie. (Pattern: recs.community auth PR)
- **Migration files are append-only.** Never edit a deployed migration. Create a new one to fix mistakes. Name format: `YYYYMMDDNNNNNN_description.sql`.

### API Resilience

- **Cross-source fallback with deadline budgets.** When downloading from multiple sources (archive.org, Gutenberg, Standard Ebooks), try the primary source first with a per-attempt timeout, then fall back through alternatives in priority order. Hard outer deadline prevents total timeout. (Pattern: kindle-schlacter-me `resilientDownload.ts`)
- **Dead-resource fast-fail.** If an external resource shows zero progress + zero speed + zero connectivity for ~90s, abort instead of polling for the full timeout. Reset the counter if any progress is detected. (Pattern: kindle-connector dead-torrent detection)
- **Charge quota only after success.** Failed attempts at an external service shouldn't consume the user's rate limit or quota. Move the quota increment after the success confirmation. (Pattern: kindle-schlacter-me send quota)
- **Parallel fan-out with per-target timeout.** When querying multiple external sources, query in parallel with individual timeouts. One slow source returns partial results instead of blocking everything. (Pattern: kindle-connector parallel indexer fan-out, 30s→3s latency improvement)
- **Negative caching for metadata.** Cache "not found" results with a TTL (e.g., 7 days) to avoid re-querying APIs for data that doesn't exist. (Pattern: kindle-schlacter-me book metadata cache)

### KV / Caching

- **Key design: `namespace:entity:identifier:qualifier`.** Example: `kindle:devicestate:{email}`, `kindle:bookmeta:{bookKey}`, `kindle:quota:send:{email}:{date}`. Consistent key structure prevents collisions and enables pattern-based cleanup. (Pattern: kindle-schlacter-me KV usage)
- **Event-time monotonic guards for state updates.** When multiple events (delivered, bounced) can arrive out of order, store the event timestamp and only update if the new event is newer. Prevents a late-arriving "delivered" from overwriting a more recent "bounced." (Pattern: kindle-schlacter-me per-address delivery banners)
- **Shared cache across features.** Book metadata fetched for the modal should be the same cache used for ratings display. Use a single cache key, not feature-specific duplicates. (Pattern: kindle-schlacter-me `kindle:bookmeta:{bookKey}`)

### Testing Strategy

- **Test resilience logic, not happy paths only.** For features with fallback/retry behavior, test: happy path, each fallback trigger, exclusion rules, timeout/deadline cutoff, and the "nothing works" path. (Pattern: kindle-schlacter-me `resilientDownload.test.ts` — 7 test cases covering cross-source fallback, archive.org single-attempt cap, libgen exclusion, deadline cutoff, empty-URL guard)
- **Gate PRs on tests + lint + typecheck.** Add `.github/workflows/pr-tests.yml` that runs `jest` (or detected test cmd), lint, and `tsc --noEmit` on every PR. Use `paths:` filter to skip unrelated changes. (Pattern: muse-shopping PR#1 — 63 existing tests, zero CI gate until automated)
- **Use `continue-on-error: true` for gradual adoption.** When adding CI to a project with pre-existing issues (TS errors, lint warnings), gate what you can enforce today and mark the rest `continue-on-error`. Flip to required after cleanup. (Pattern: muse-shopping typecheck gate)
- **Test at the boundary, not the implementation.** For API resilience, test the public function (`resolveAndDownload`) not internal helpers. For RLS, test "can member X see community Y's data?" and "can non-member Z see it?" — both positive and negative. (Pattern: recs.community review checklist, kindle-schlacter-me test structure)
- **Add a test with the bug fix.** When fixing a production incident, write the test that reproduces the bug BEFORE writing the fix. The test should fail first. (Pattern: debug-escalation Step 6 requirement)
- **No tests for glue code.** Don't test: simple pass-through components, config files, one-line utilities, framework boilerplate. Test: business logic, data transformations, resilience/fallback behavior, security boundaries (RLS, auth gates).

### CI / GitHub Actions

- **Minimal PR gate workflow template:**
  ```yaml
  name: PR Tests
  on:
    pull_request:
      branches: [main]
      paths: ['{src,lib,app}/**']
  jobs:
    check:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-node@v4
          with: { node-version-file: '.nvmrc' }
        - run: npm install
        - run: npm test
        - run: npx tsc --noEmit
        - run: npm run lint
  ```
- **Separate CI setup from feature PRs.** CI changes should be their own PR so they don't block feature review and can be tested independently. (Pattern: recs.community PR#5 — standalone CI PR)
- **For Python projects, use a matrix for version testing** if the project supports multiple Python versions. Otherwise, pin to the version in `.python-version`.

### Multi-Developer

- **PR stacking for greenfield projects.** When building a new project with dependencies between features (scaffold → schema → auth → features), use stacked PRs with explicit `base` branches. Each PR body should state its dependency. (Pattern: recs.community PRs #1-6)
- **COORDINATION.md for multi-agent repos.** When multiple Claude instances work on the same repo, maintain a coordination doc listing: active work, review queue, blocked items, and parking lot. (Pattern: recs.community COORDINATION.md)
- **Review checklists are persistent, not per-PR.** A `docs/review-checklist.md` lets any reviewer (human or Claude) apply consistent standards without re-deriving them each time. (Pattern: recs.community review checklist)
- **Self-onboarding PRs.** When another developer's Claude will work on the repo, create a PR that makes the repo self-orienting: CLAUDE.md with session-start checklist, review checklist, coordination doc. (Pattern: recs.community PR #4)

---

### Performance Optimization

- **Profile before parallelizing.** Identify whether the bottleneck is sequential I/O, CPU, or a single slow dependency. `console.time()`/`timeEnd()` around each section. For API fan-out: log per-source latency, not just total. (Pattern: kindle-connector went from 30s→3s by identifying that sequential indexer queries were the bottleneck, not any single slow indexer)
- **Per-source timeout budgets within an overall deadline.** When querying N sources in parallel, give each source its own timeout (e.g., 5s) plus a hard overall deadline (e.g., 15s). One hung source returns partial results instead of blocking everything. Don't set per-source timeout = overall timeout. (Pattern: kindle-connector parallel fan-out)
- **Benchmark before AND after, with the same dataset.** "It feels faster" is not evidence. Log wall-clock time for the same operation before the change and after. Include the numbers in the PR body. (Pattern: kindle-connector PR#1 reported 30s→3s)
- **Sequential → parallel is the highest-leverage refactor for I/O-bound code.** If you see `for (const x of items) { await fetch(x) }`, that's sequential I/O. Convert to `await Promise.allSettled(items.map(x => fetch(x)))`. Guard with per-item timeouts.

### Async Multi-Step Workflows

- **Model state transitions explicitly.** For workflows like send→email→delivered→bounced, define the states as a union type and the valid transitions. Store the current state and the timestamp of the last transition. (Pattern: kindle-schlacter-me send stages and Resend webhook delivery tracking)
- **Event-time ordering, not arrival-time ordering.** Webhooks arrive out of order. A "delivered" event may arrive after a "bounced" event. Store the event timestamp and only update state if the new event is chronologically newer. (Pattern: kindle-schlacter-me per-address delivery banners — already in KV/Caching section, but this is the workflow design principle)
- **Idempotent event handlers.** Webhooks can be delivered more than once. Process each event idempotently: check if the state transition already happened before applying it. Return 200 regardless. (Pattern: kindle-schlacter-me Resend webhook handler)
- **Separate the trigger from the work.** Webhook handlers should acknowledge quickly (return 200) and queue the actual work. Don't do heavy processing in the webhook handler — providers retry on timeout.

### Feature Batching

- **Group features into deployable rounds.** When shipping multiple features, group them by dependency (not by type). Round 1: foundational changes (data model, auth). Round 2: features that depend on Round 1. Each round should be deployable independently. (Pattern: kindle-schlacter-me R0-R10 shipped banners, book modal, library page, search, export, and send stages as one cohesive round because they all depended on the same data model changes)
- **Preview-first for multi-feature PRs.** Deploy to preview and test the golden path through all features before merging to main. Multi-feature PRs have more interaction bugs than single-feature PRs. (Pattern: kindle-schlacter-me "review on the Vercel preview, then merge to main")
- **List what's in each round in the PR body.** Each feature gets a one-line summary with its identifier (R0, R1, etc.). This makes review tractable for large PRs and lets the reviewer skip to what they care about.

### PRD-to-Code

- **Decompose the PRD into stacked PRs before writing code.** For greenfield projects built from a PRD, plan the PR sequence first: scaffold → data model/schema → auth → core feature loop → CI → coordination docs. Each PR should be independently deployable (or at least buildable). (Pattern: recs.community 7 PRs from PRD)
- **Implement the first product loop first.** Don't build horizontally (all pages, then all APIs). Build vertically: the first user journey that exercises signup → core action → result. For recs.community: signup → create community → land on admin page. Everything else comes after.
- **Schema migrations before application code.** Get the data model right (with RLS, triggers, FK rules) before writing UI. Schema mistakes are expensive to fix after data exists. (Pattern: recs.community PR#2 schema, PR#3 auth, PR#6 features)
- **Out-of-scope lists prevent scope creep.** Every PR body should list what's intentionally NOT included. "No invite-link generator yet" is a decision, not a gap. (Pattern: every recs.community PR body has an "Out of scope" section)
- **Unblock stacked PRs proactively.** Stacked PRs are only useful if they actually merge. After creating the stack: merge #1 immediately if CI passes, retarget #2 to main, repeat. If a PR is blocked on review, ping the reviewer. If blocked on CI, fix CI first — a stack of 7 open PRs is worse than no stack at all. (Evidence: recs.community PRs #1-7 all open for 13+ days with no merges)

---

## Changelog

- **2026-06-09 — v7.5: Performance optimization, async workflows, feature batching, stacked PR unblocking**
  - ADDED: Performance optimization learnings (profile before parallelize, per-source timeout budgets, benchmark before/after, sequential→parallel)
  - ADDED: Async multi-step workflow learnings (explicit state machines, event-time ordering, idempotent handlers, separate trigger from work)
  - ADDED: Feature batching learnings (deployable rounds, preview-first, list features in PR body)
  - ADDED: Stacked PR unblocking guidance (merge #1 immediately, retarget, don't let stacks rot)
  - Evidence: kindle-connector PR#1 (30s→3s parallel fan-out), kindle-schlacter-me PR#1 (R0-R10 feature rounds, send stage state machine, Resend webhooks), recs.community PRs #1-7 (stacked but unmerged for 13+ days)
- **2026-06-08 — v7.4: Testing strategy, CI/GH Actions, PRD-to-code learnings**
  - ADDED: Testing strategy section (what to test, test-with-bugfix, no-test-for-glue, gradual CI adoption)
  - ADDED: CI / GitHub Actions section (PR gate template, separate CI from features)
  - ADDED: PRD-to-code section (stacked PRs from PRD, vertical slicing, schema-first, out-of-scope lists)
  - Evidence: kindle-schlacter-me 71 tests + resilientDownload.test.ts, muse-shopping PR#1 CI gate, recs.community 7 PRs from PRD
  - Resolves CLAUDE.md known issues #4 (PM/PRD workflow) and #8 (testing strategy)
- **2026-06-06 — v7.3: Supabase, API resilience, KV/caching, multi-developer learnings**
  - ADDED: Supabase to framework detection table
  - ADDED: Supabase learnings section (RLS, migrations, security-definer, auth middleware, triggers)
  - ADDED: API resilience learnings (cross-source fallback, dead-resource fast-fail, parallel fan-out, quota-after-success)
  - ADDED: KV/caching learnings (key design, event-time monotonic guards, shared cache)
  - ADDED: Multi-developer learnings (PR stacking, COORDINATION.md, review checklists, self-onboarding)
  - Evidence: 14 PRs across kindle-schlacter-me, kindle-connector, recs.community, muse-shopping (May-Jun 2026)
- **2026-06-05 — v7.2: Python patterns, automation/scheduling learnings, GH Action template for sync**
  - ADDED: Python-specific learnings section (venv, pathlib, entry points, dep pinning)
  - ADDED: Automation/scheduling learnings (cron UTC, workflow_dispatch, timeouts)
  - ADDED: Concrete GH Action YAML template to unblock the learning sync (known issue #1)
  - ADDED: GH Actions to language/framework detection table
- **2026-06-04 — v7.1: Web-session run logging, sync staleness warning, dual-entry-point check**
  - FIXED: Run log path adapts to web (ephemeral) vs laptop (persistent) environments
  - FIXED: Sync staleness warning now explicitly states the automated sync has never run
  - ADDED: Explicit dual-entry-point diff check for custom server + Vercel deployments
- **2026-05-29 — v7: Critical gap fixes (git gate, quorum, language detection, task-size adaptation)**
  - FIXED: Git repo check is now a BLOCKING gate for parallel mode (was a suggestion)
  - FIXED: Added quorum/failure handling — 3+ draft failures abort parallel, switch to debug-loop
  - FIXED: Language/framework detection replaces hardcoded npm/pytest assumptions
  - FIXED: Quick-fix bypass skips full rubric for <10 LOC obvious fixes
  - FIXED: Cherry-pick has rollback strategy (`git cherry-pick --abort`)
  - FIXED: Parallel draft prompts use detected commands, not assumed ones
  - FIXED: Added timeout (5 min/draft) for parallel mode
  - Consolidated from v6 (YapzR) + audit findings (358hG)
- **2026-05-27 — v6: Four execution modes, visual path, pre-flight research gate**
- **2026-05-24 — v4: Consolidated from 25 session branches**
- **2026-04-14 — v1: Initial version**
