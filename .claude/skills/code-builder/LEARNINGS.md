# code-builder Learnings Reference

Reference patterns extracted from real projects. Loaded on-demand, not on every skill activation.

Last synced: 2026-06-13 (manual, from 40+ PRs across kindle-schlacter-me, kindle-connector, recs.community, muse-shopping, hbschlac)

---

## Process

- **Trim all `process.env` at the read-site.** Pattern: `process.env.X?.trim()`. (5 citations across schlacter.me, muse)
- **Verify BOTH dev server AND serverless entry middleware order.** Silent 500s when error handler is before routes in one but not the other. (muse `d01750d`)
- **Set `trust proxy` behind any reverse proxy.** Broke OAuth in muse, session validation in calmar. (muse `0c92c13`, `3a83f67`)
- **Don't iterate on the same strategy 3+ times.** If it didn't work twice, the approach is wrong, not the execution.
- **Guard nullable API responses before destructuring.** KV/API calls return null on miss.
- **Check for existing utilities before writing new ones.** Duplicated helpers across 3 repos.

## Python

- **Always create and activate a venv before installing.** `python3 -m venv .venv && source .venv/bin/activate`. Never install globally.
- **Use `if __name__ == "__main__":` in every entry point.** Prevents double-execution when imported by tests.
- **Pin deps with `pip freeze > requirements.txt` after install.** Unpinned deps break on next session/deploy.
- **Use `pathlib.Path` over `os.path`.** Consistent cross-platform, fewer string manipulation bugs.
- **For scheduled automation, validate the happy path AND the "nothing to do" path.** Cron jobs that crash on empty input generate noise.
- **Check `sys.exit()` codes in GH Actions.** Non-zero exits fail the workflow. Intentional "nothing to do" should exit 0.

## Integration

- **Offload Playwright/puppeteer to GHA instead of serverless.** Cold starts on Vercel/Render exceed 30s. (libby-hold-monitor)
- **Register both www and non-www OAuth redirect URIs.** Google treats them as different. (muse `68d29d4`)
- **Handle OAuth-only accounts in password login flow.** `bcrypt.compare(input, null)` crashes. (muse `3a83f67`)

## Automation / Scheduling

- **GitHub Actions cron syntax uses UTC.** `schedule: cron: '0 6 * * *'` is 6am UTC, not local.
- **Always add `workflow_dispatch` alongside `schedule`.** Enables manual re-runs during debugging.
- **For long-running automations, add a timeout.** `timeout-minutes: 10` prevents hung jobs from consuming quota.
- **Log the "last successful run" timestamp.** Without this, debugging "it stopped working" means reading days of logs.

## Merge Safety

- **Never force-push without checking other sessions' branches.** 3 incidents of code loss from merge conflicts in calmar.
- **Check `git branch -a --sort=-committerdate` before starting.** Build on existing branch work, don't start over.

## Supabase

- **Enable RLS on every table, then write policies.** Forgetting RLS exposes the table to any authenticated user.
- **Security-definer functions need `SET search_path = public`.** Prevents schema shadowing attacks.
- **Use triggers for cross-table consistency, not application code.** Profile creation on signup, admin membership on community creation — must succeed atomically.
- **Nullable FK on user delete preserves data.** `ON DELETE SET NULL` keeps content, shows "Former member."
- **Test RLS policies with positive AND negative cases.** Verify both access and denial.
- **Supabase auth middleware must refresh the session on every request.** Use `@supabase/ssr` three-file pattern (server, client, middleware).
- **Migration files are append-only.** Never edit a deployed migration. Name format: `YYYYMMDDNNNNNN_description.sql`.

## API Resilience

- **Cross-source fallback with deadline budgets.** Try primary source first with per-attempt timeout, fall back through alternatives. Hard outer deadline prevents total timeout. (kindle-schlacter-me `resilientDownload.ts`)
- **Dead-resource fast-fail.** Zero progress + zero speed for ~90s → abort early. (kindle-connector)
- **Charge quota only after success.** Failed attempts shouldn't consume rate limits. (kindle-schlacter-me)
- **Parallel fan-out with per-target timeout.** Query sources in parallel with individual timeouts. (kindle-connector, 30s→3s)
- **Negative caching for metadata.** Cache "not found" with TTL to avoid re-querying. (kindle-schlacter-me)

## KV / Caching

- **Key design: `namespace:entity:identifier:qualifier`.** Example: `kindle:devicestate:{email}`. Consistent structure prevents collisions.
- **Event-time monotonic guards for state updates.** Store event timestamps; only update if new event is chronologically newer.
- **Shared cache across features.** Single cache key, not feature-specific duplicates.

## Testing Strategy

- **Test resilience logic, not happy paths only.** Test: happy path, each fallback trigger, exclusion rules, timeout cutoff, "nothing works" path. (kindle-schlacter-me `resilientDownload.test.ts`)
- **Gate PRs on tests + lint + typecheck.** Add `.github/workflows/pr-tests.yml`. Use `paths:` filter to skip unrelated changes.
- **Use `continue-on-error: true` for gradual adoption.** Gate what you can enforce today; flip to required after cleanup.
- **Test at the boundary, not the implementation.** Test public functions and security boundaries (RLS, auth gates), not internal helpers.
- **Add a test with the bug fix.** Write the failing test BEFORE writing the fix.
- **No tests for glue code.** Don't test: pass-through components, config files, one-line utilities, framework boilerplate.

## CI / GitHub Actions

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
- **Separate CI setup from feature PRs.** CI changes should be their own PR. (recs.community PR#5)
- **For Python projects, use a matrix for version testing** if supporting multiple versions. Otherwise, pin to `.python-version`.

## Multi-Developer

- **PR stacking for greenfield projects.** Stacked PRs with explicit `base` branches. Each PR body states its dependency. (recs.community PRs #1-6)
- **COORDINATION.md for multi-agent repos.** Track: active work, review queue, blocked items, parking lot.
- **Review checklists are persistent, not per-PR.** `docs/review-checklist.md` lets any reviewer apply consistent standards.
- **Self-onboarding PRs.** Make repos self-orienting: CLAUDE.md with session-start checklist, review checklist, coordination doc.

## Performance Optimization

- **Profile before parallelizing.** `console.time()`/`timeEnd()` around each section. (kindle-connector: 30s→3s by identifying sequential I/O bottleneck)
- **Per-source timeout budgets within an overall deadline.** Individual timeouts + hard overall deadline. Don't set per-source = overall.
- **Benchmark before AND after, with the same dataset.** Include numbers in the PR body.
- **Sequential → parallel is the highest-leverage refactor for I/O-bound code.** Convert `for await` to `Promise.allSettled()`.

## Async Multi-Step Workflows

- **Model state transitions explicitly.** Define states as union types with valid transitions. Store current state + last transition timestamp. (kindle-schlacter-me send stages)
- **Event-time ordering, not arrival-time ordering.** Webhooks arrive out of order. Only update state if new event is chronologically newer.
- **Idempotent event handlers.** Check if state transition already happened before applying. Return 200 regardless.
- **Separate the trigger from the work.** Webhook handlers acknowledge quickly (200), queue the actual work.

## Feature Batching

- **Group features into deployable rounds.** Group by dependency, not type. Each round independently deployable. (kindle-schlacter-me R0-R10)
- **Preview-first for multi-feature PRs.** Test golden path through all features before merging.
- **List what's in each round in the PR body.** One-line summary per feature with identifier.

## PRD-to-Code

- **Decompose the PRD into stacked PRs before writing code.** Plan: scaffold → schema → auth → core loop → CI → docs. (recs.community 7 PRs)
- **Implement the first product loop first.** Build vertically: signup → core action → result.
- **Schema migrations before application code.** Get data model right before UI.
- **Out-of-scope lists prevent scope creep.** Every PR lists what's intentionally NOT included.
- **Unblock stacked PRs proactively.** Merge #1 immediately if CI passes, retarget #2 to main, repeat.

## Test Framework Setup

When a project has no test infrastructure, set it up before writing tests:

**Jest (Next.js / Node.js):**
```bash
npm install -D jest @types/jest ts-jest
# For Next.js: npm install -D @testing-library/react @testing-library/jest-dom jest-environment-jsdom
```
Config: `jest.config.ts` with `preset: 'ts-jest'`. For Next.js, use `nextJest()` from `next/jest`.

**Vitest (Vite projects):**
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom
```
Config: `vitest.config.ts` — Vitest reads from `vite.config.ts` by default. Add `test: { environment: 'jsdom' }` for React.

**pytest (Python):**
```bash
pip install pytest pytest-cov
# For async: pip install pytest-asyncio
```
Config: `pyproject.toml` under `[tool.pytest.ini_options]`. Set `testpaths = ["tests"]`.

**Common mistakes:**
- Don't install test deps globally — always `--save-dev` or in venv
- Don't configure both Jest and Vitest — pick one per project
- Set up a single passing test before configuring CI — verify the runner works first
- For Supabase: mock `@supabase/supabase-js` in tests, don't hit real DB. Use `supabase start` only for integration tests.

## PWA / Mobile Web

- **Set font-size ≥16px on all inputs.** iOS Safari auto-zooms the viewport on focus for inputs <16px. This clips surrounding UI (buttons, icons). (kindle-schlacter-me PR#4)
- **Use `env(safe-area-inset-bottom)` for bottom-anchored UI.** Docks, modals, and FABs must account for the iOS home indicator. Pattern: `padding-bottom: calc(0.5rem + env(safe-area-inset-bottom))`. (kindle-schlacter-me PR#4)
- **Set `<meta name="viewport" content="..., viewport-fit=cover">`.** Required for `env(safe-area-inset-*)` to work. Without it, the values are always 0.
- **In-memory state dies on page reload.** Status chips, download progress, queue state — anything held in React state without persistence vanishes on navigation or PWA restart. Persist critical status to localStorage or server, reconcile on mount. (kindle-schlacter-me PR#13)
- **Handle lost HTTP responses.** The server completed the request but the client never got the 200 (network blip, tab switch, iOS background kill). Poll or use server-sent events for long operations. Don't assume "no response = failure." (kindle-schlacter-me PR#18)
- **Test on actual iOS Safari, not just Chrome mobile emulation.** The home indicator, auto-zoom, and `position: fixed` behavior differ. Chrome DevTools mobile mode doesn't reproduce them.

## Search Engineering

- **Parse "Title by Author" queries.** If the raw query fails, regex-split on ` by ` and search title + author separately. Try the full query first (it might be the actual title). (kindle-schlacter-me PR#5)
- **Multi-source result ranking.** When the same book/item appears from multiple sources, pick by: (1) format match, (2) source reliability, (3) file size plausibility. Don't just return the first hit. (kindle-schlacter-me PR#12)
- **Let the user override auto-pick.** Automatic source selection should have an escape hatch: "Find another version" that shows available alternatives. Don't force the "smart" choice. (kindle-schlacter-me PR#12)
- **Fan out across sources in parallel, not sequentially.** A 3-source search taking 2s each → 6s serial vs 2s parallel. Use `Promise.allSettled()` with per-source timeouts. (kindle-connector PR#1)

## File Format Compliance

- **Validate files against external specs before processing.** Amazon rejects EPUBs where `mimetype` is DEFLATED instead of STORED in the zip. The send succeeds (email goes out) but the book never appears. Validate BEFORE the point of no return. (kindle-schlacter-me PR#7)
- **Check for stub/placeholder content.** Fake ebook torrents contain locked placeholder EPUBs (often <10KB, single page, "VIP" markers in filename). Validate file size and content structure, not just format. (kindle-schlacter-me PR#17)
- **Pre-send validation checklist pattern:**
  1. Format compliance (zip structure, required entries, encoding)
  2. Content integrity (file size reasonable, not a stub, expected structure present)
  3. Deliverability (will the recipient system accept this?)
  4. Idempotency (is this a duplicate of something already sent?)
- **Fail at validation time, not delivery time.** A validation error shown before send is actionable. A silent delivery failure discovered hours later is not.

## Client-Server State Synchronization

- **Poll for completion on long operations.** If an API call can take >5s (downloads, conversions, email sends), return a job ID immediately and let the client poll for status. Don't hold the HTTP connection open. (kindle-schlacter-me PR#18)
- **Persist operation status server-side.** Client-side status (React state, session storage) is fragile — page reloads, tab switches, PWA restarts kill it. Store status in DB/KV with the operation ID. Client reconciles on mount. (kindle-schlacter-me PR#13)
- **Make failures visible and durable.** A failed download that disappears on page reload is a silent failure. Persist failure state with the error reason so the user can see it and retry. (kindle-schlacter-me PR#13)
- **Reconcile optimistic UI with server state.** When the client shows "Sending" but the server already completed, the next status poll should resolve the inconsistency. Don't require the user to refresh.

## Feature Gating

- **Gate risky features OFF by default.** If a feature works but reduces reliability of the core path (e.g., embedding AI summaries in ebooks reduces Amazon deliverability), ship it gated off. Let users opt in after the core path is proven solid. (kindle-schlacter-me PR#14)
- **Feature flags don't need a framework.** For small projects, a boolean in env vars or user settings is enough. Don't add LaunchDarkly for 2 flags.
- **Gate at the narrowest point.** Don't wrap the entire feature in a flag — gate only the part that causes risk. Keep the UI, API, and data model unconditional.

## Pipeline Hardening

When a pipeline (search → download → validate → send) has multiple failure modes discovered over time, don't fix them one at a time. Step back and audit the whole pipeline:

1. **Map every step in the pipeline.** List: input → transform → validation → output → confirmation.
2. **At each step, ask: what can go wrong?** Bad input, timeout, format error, external service down, partial success, silent failure.
3. **Add validation boundaries between steps.** Each step should validate its input (from the previous step) and its output (before passing to the next step).
4. **Make every failure visible.** No step should fail silently. If it can't proceed, it should produce an error the user can see and act on.
5. **Add escape hatches.** When the automatic path fails, give the user a manual alternative ("Find another version," "Try a different source," "Skip this step").

Evidence: kindle-schlacter-me PRs #6-#20 hardened the same pipeline over 15 iterations. A single upfront pipeline audit could have caught format compliance, content integrity, delivery confirmation, and fallback sources in 3-4 PRs instead of 15.

## Working on Large Existing Codebases

- **Read before changing.** For codebases >10K LOC, spend 15-30 minutes reading architecture before writing any code. Map: entry points, data flow, config, and the specific area you'll change.
- **Find the smallest change that solves the problem.** In a 65K LOC codebase, a 5-line fix is better than a 500-line refactor. Resist the urge to "fix everything while I'm in here."
- **Understand the implicit contracts.** Large codebases have conventions not documented anywhere. Check: how do existing tests work? What naming patterns exist? What's the import structure? Copy those patterns.
- **Incremental CI adoption.** Don't try to make all 200 TypeScript errors green at once. Gate what passes today, mark the rest `continue-on-error`, tighten incrementally.
- **Tech debt triage: severity × frequency.** Fix bugs that break production weekly before fixing code that's ugly but works. Document the rest in an issue, not in a cleanup PR nobody will review.
