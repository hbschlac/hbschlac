# code-builder

> Raises the floor of code quality by generating parallel implementations, self-scoring them, and merging the winner — then verifying the result is actually deployable.

---

## Activation

### Explicit triggers
- `/code-builder`
- "build this", "fix this bug", "add feature X", "refactor Y"

### Implicit triggers (all must be true)
- Working in a git repository
- Task involves writing, changing, or fixing code
- NOT pure research, design, planning, or meta-discussion

### Skip
- Questions about how something works
- Planning/architecture discussions (until "go build it")
- Non-code tasks (copy, docs, content)

---

## Workflow

### Step 0 — Announce
Always state: "Activating code-builder — [1-sentence task summary]"

### Step 1 — Scope
- Identify affected files, test surface, and deployment target
- Detect project type: Next.js (Vercel), Node/Express, static, monorepo
- Identify entry points: if project has separate dev/prod entries (e.g., `src/app.js` vs `api/index.js`), flag for dual-path validation

### Step 2 — Judgment gate
Escalate to parallel (N=5) if **≥2 soft signals fire** OR **any hard signal**:

| Signal | Type |
|--------|------|
| Greenfield file/feature | Hard |
| Explicit user override ("try multiple approaches") | Hard |
| ≥3 files touched | Soft |
| Unfamiliar domain/library | Soft |
| Performance-sensitive path | Soft |
| Multiple valid architectural approaches | Soft |
| Error with unclear root cause | Soft |

Single-path: proceed normally with steps 4–7 still applied.

### Step 3 — Parallel execution (if triggered)
- Spawn N=5 agents in isolated git worktrees
- Each gets a distinct bias hint (e.g., "minimize diff", "maximize test coverage", "prefer stdlib", "optimize perf", "prioritize readability")
- Each must independently pass Step 5 (deploy gate) or be disqualified

### Step 4 — Score (100-point rubric)

| Category | Points | What it measures |
|----------|--------|-----------------|
| Correctness | 25 | Does it work? Edge cases handled? |
| Tests | 20 | New/updated tests pass, coverage delta ≥0 |
| Type safety | 15 | `tsc --noEmit` clean, no `any` escapes, props match |
| Lint & format | 10 | Zero new warnings, matches project style |
| Minimal diff | 10 | Smallest change that solves the problem |
| Deploy readiness | 10 | All imports resolve, no missing files, env vars valid |
| No new deps | 5 | Prefers existing packages/utils |
| Conventions | 5 | Matches project patterns (naming, structure, error handling) |

Disqualifiers (score → 0):
- `tsc --noEmit` fails
- Any import references a file not tracked in git
- Test suite regresses
- Hardcoded secrets in client-side code

### Step 5 — Deploy gate (REQUIRED, every merge)

Run these checks before declaring success:

```
1. tsc --noEmit (or project-equivalent type check)
2. Import resolution scan:
   - grep all import/require statements in changed files
   - verify each referenced local file exists AND is tracked in git
   - flag dynamic imports referencing non-existent paths
3. Dual-entry validation:
   - if project has api/index.js (or similar Vercel serverless entry) AND src/app.js (local entry):
     ensure middleware, error handlers, and route registrations match
4. Env var audit:
   - grep for process.env.* in changed files
   - verify each referenced var exists in .env.example or .env.local
   - flag any var used without fallback in server-only code
5. Test suite: npm test (or equivalent) — must pass
6. Build check: npm run build (or next build) — must succeed
```

If any check fails: fix it before reporting success. Do not skip.

### Step 6 — Merge validation
- Gap-check: did the winning draft miss anything from the task spec?
- Redundancy sweep: remove dead code introduced by the change
- Re-run full test suite after merge conflict resolution

### Step 7 — Log
Write run summary to `~/.claude/skills/code-builder/runs/{date}-{slug}.md`:
```
## {date} — {task-slug}
- Path: single | parallel (N=5)
- Winner score: {score}/100
- Deploy gate: pass | fail → fix
- Key decision: {why this draft won}
- Failure patterns caught: {list}
```

---

## Current learnings

### §A — Process failures (from deployment data)

1. Never skip `tsc --noEmit` — TypeScript type errors are the #1 cause of Vercel deployment failures across all projects
2. After creating a new component file, immediately verify it's staged in git — "Cannot find module './ComponentName'" failures come from forgetting `git add`
3. When adding a value to a union type, grep the entire codebase for that type definition — partial updates cause "Type X is not assignable to type Y" across multiple files
4. Vercel serverless entry (`api/index.js`) and local dev entry (`src/app.js`) can silently diverge — always propagate middleware/handler changes to both
5. Trim all environment variables at the read site: `process.env.VAR?.trim()` — trailing newlines in Vercel env vars have broken OAuth 5+ times
6. Never trust that a locally-working auth flow works in production — test OAuth redirects, callback URLs, and session handling against the deployed URL
7. If a deploy fails with a type error, check if the same error exists in other files using that type — batch-fix all occurrences, not just the one that errored
8. Avoid circular `Skill()` calls — they create infinite loops
9. Never hardcode secrets in client-side JavaScript
10. Require green tests, not just "looks right" — visual confirmation misses runtime errors

### §B — Code patterns (from post-merge diffs)

11. Validate env vars at startup with clear error messages, not silent undefined
12. Use `position: fixed` (not `absolute`) for floating UI in scrollable parents
13. Follow Rules of Hooks strictly — no conditional hooks, no hooks after early returns
14. Cleanup effects that create subscriptions (return teardown function)
15. When using CSS transforms, `getBoundingClientRect()` returns scaled values — divide by scale factor
16. Save editor selection/cursor position before opening modals that steal focus
17. Resolve merge conflicts via test outcomes, not visual diff comparison
18. Guard nullable API responses — upstream services return null for fields documented as required
19. Grep for existing utility helpers before writing new ones — most "I need a helper for X" already exist
20. When adding a new page/route to a nav type union, update ALL components that consume that type

### §C — Deployment patterns (new)

21. First deployment of a new project almost always fails — run `next build` locally before the initial push
22. If the same commit triggers multiple Vercel deployments, don't redeploy manually — wait for the webhook to settle
23. Auth-related environment variables (OAuth secrets, redirect URIs) must be tested against the production domain, not localhost
24. When migrating storage backends (e.g., Blob → R2), update BOTH the write path and all existing read references
25. Pre-push hook should run: `tsc --noEmit && npm run build` — catches 90% of deployment failures locally
26. If 3+ consecutive deploys fail on the same error, stop pushing fixes — read the full error, trace it to root cause, fix once

---

## Sync protocol

**Trigger**: Every Sunday 6pm (or after 10+ logged runs, whichever comes first)

**Process**:
1. Read all runs since last sync from `~/.claude/skills/code-builder/runs/`
2. Read post-merge diffs from git log
3. Check Vercel deployment logs for failures (if available)
4. Mine patterns: what broke? what was the root cause? what would have caught it earlier?
5. Update §A/§B/§C learnings (hard cap: 30 bullets total, rotate oldest unless still relevant)
6. If a learning has prevented 0 issues in 4 weeks, archive it

**Anti-patterns to watch for**:
- Same type of failure appearing 2+ times → missing learning bullet
- Deploy gate being skipped "because it's a small change" → never skip
- Learnings growing stale (referencing patterns no longer in codebase)

---

## Pre-push checklist (recommended git hook)

```bash
#!/bin/sh
# .git/hooks/pre-push
echo "Running deploy gate checks..."
npx tsc --noEmit || exit 1
npm run build || exit 1
npm test || exit 1
echo "All checks passed."
```

---

## Installation

Drop this file into `~/.claude/skills/code-builder/SKILL.md` for auto-discovery.

Optional: add the pre-push hook above to all active projects.

---

*Built by [@hbschlac](https://github.com/hbschlac) — fork and adapt.*
