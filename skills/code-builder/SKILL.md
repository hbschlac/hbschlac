# code-builder

> Claude Code skill that raises the floor of code quality by generating parallel implementations, self-scoring them against a measurable rubric, and merging the winner — with circuit breakers, integration checks, and deploy verification that the original lacked.

---

## Triggers

**Explicit:** "build this", "fix this bug", "add a feature", "implement", "refactor", "code-builder"

**Implicit:** coding tasks in git repos, error messages, broken features, new projects

**Do NOT activate:** pure research, design work, meta tasks, writing docs with no code

---

## Step 0 — Pre-flight research gate

Before writing any code, answer three questions silently:

1. **Is the domain well-understood?** Standard web dev, API integration, database queries → yes. Binary formats (plists, Shortcuts, protocol buffers without tooling), undocumented vendor APIs, hardware-adjacent protocols → no.

2. **Is there an established library or pattern?** Search npm/PyPI/crates.io for existing solutions. If a maintained library exists, use it instead of hand-rolling.

3. **Has this been attempted before in this repo?** Check git log for prior attempts at the same feature. If 2+ prior failed attempts exist, do NOT proceed with another variation — instead surface a diagnostic to the user: what failed, why, and what fundamentally different approach might work.

**If domain is NOT well-understood:** Tell the user before coding. Propose a spike: a throwaway prototype that validates the approach in <30 minutes. Do not commit spike output. Only proceed to full implementation after the spike succeeds.

**If 3+ prior attempts found:** Stop. Print the failure history. Suggest either (a) a fundamentally different approach, (b) an external tool/library, or (c) scoping down the feature. Do not iterate on the same strategy.

---

## Step 1 — Judgment gate: single-pass vs. parallel

Default to **single-pass** execution. Escalate to **5-draft parallel** only when the task warrants it.

### Parallel signals (need ≥2 to fire, or 1 hard signal)

| Signal | Example |
|--------|---------|
| Multiple files touched | Feature spans 4+ files |
| Design space is wide | "add auth" has many valid architectures |
| Novelty | No prior art in this repo |
| Risk | Breaking change or production-facing |
| Scope | >100 lines of net-new code |
| **Hard: explicit override** | User says "run parallel" |
| **Hard: greenfield prototype** | New project, no existing patterns |

### Single-pass triggers (override parallel signals)

- Simple bug fix in 1-2 files
- Mechanical rename/refactor
- Config change
- Live debugging requiring rapid iteration
- Task with exactly one correct implementation (fix a typo, update a version)

---

## Step 2 — Single-pass execution

1. Read relevant code
2. Implement the change
3. Run type checker, linter, tests
4. If any fail, fix and re-run (max 3 cycles)
5. Proceed to Step 5 (integration check)

---

## Step 3 — Parallel execution (5 drafts)

Spawn 5 isolated git worktrees, each with a different optimization bias:

| Draft | Bias |
|-------|------|
| A | Simplest possible — fewest lines, least abstraction |
| B | Most idiomatic to this repository's existing patterns |
| C | Optimized for readability and maintainability |
| D | Optimized for edge cases and defensive correctness |
| E | Best overall instinct — no constraint |

Each draft must independently pass type checking, linting, and existing tests.

---

## Step 4 — Scoring rubric (100 points)

| Criterion | Weight | What it means |
|-----------|--------|---------------|
| Correctness | 25 | Does it actually work? All paths, not just happy path |
| Tests | 15 | Does it add/update tests covering the change? |
| Type safety | 10 | No `any`, no unsafe casts, no suppressed errors |
| Lint clean | 5 | Zero new warnings |
| Minimal diff | 10 | Smallest change that solves the problem |
| No new dependencies | 5 | Avoids adding packages; if adding, justified |
| Reuses existing utilities | 5 | Uses repo's helpers instead of reinventing |
| Matches repo conventions | 10 | Naming, file structure, patterns consistent |
| Scope discipline | 5 | No drive-by refactors, no unrelated changes |
| Integration safety | 10 | Works with adjacent systems — env vars, APIs, deploy config |

**Winner selection:** Highest score wins. If gap <5 points, prefer the simpler draft. Cherry-pick improvements from runners-up only if they fill a gap the winner missed, not for marginal polish.

Clean up all rejected worktrees after merge.

---

## Step 5 — Integration check (NEW — runs after every merge)

Before reporting the task as complete, verify these:

1. **Build passes:** Run the project's build command. Not just type-check — full production build.
2. **Dev server starts:** If this is a web project, start the dev server and confirm it loads without errors.
3. **Affected routes/endpoints respond:** If the change touches an API route or page, hit it once.
4. **Environment variables are present:** If the change references any env var, confirm it exists in `.env`, `.env.local`, or the deployment platform's config. Do not guess values — flag missing vars.
5. **No import cycles:** If the change adds new imports, verify no circular dependency was introduced.

If any check fails, fix it before reporting done. If the fix introduces another failure, you are in a **cascade** — proceed to Step 6.

---

## Step 6 — Cascade circuit breaker (NEW)

A cascade is when fixing bug A introduces bug B, and fixing B introduces bug C.

**Rules:**
- Track the fix chain depth. After **3 cascading fixes** in a single session, stop.
- Print a diagnostic: what the original task was, what each fix changed, and where the chain is heading.
- Suggest to the user: (a) step back and rethink the approach, (b) commit what works and open an issue for the remainder, (c) pair on it interactively.
- Do NOT silently continue iterating. The user deserves to know the task is harder than it looked.

**Iteration cap on repeated failures:**
- If the same test/build/lint error recurs 3 times despite different fix attempts → stop, diagnose root cause, surface to user.
- If a feature requires >5 sequential commits to get working → flag it. This is a sign the approach is wrong, not that it needs one more tweak.

---

## Step 7 — Scope creep detection (NEW)

Before each commit, check:

- **File count:** If the change now touches 3x more files than the original task implied, pause and confirm with the user.
- **Unrelated changes:** If you're about to modify a file that has nothing to do with the stated task, don't. Note it as a separate follow-up.
- **Growing test surface:** If you need to mock 5+ new things to make tests pass, the change may be too coupled. Flag it.

---

## Step 8 — Session coordination (NEW)

Before starting work:

1. Run `git status` and `git stash list` to check for uncommitted work from other sessions.
2. If uncommitted changes exist that you didn't make, **do not discard them**. Stash them with a descriptive message and tell the user.
3. If the branch has recent commits you don't recognize, read them before proceeding. Another session may have made changes you'd overwrite.
4. After completing your work, run `git status` one final time. If new untracked files appeared that you didn't create, something else is running. Warn the user.

**Never run** `git checkout .`, `git clean -f`, or `git reset --hard` without explicit user confirmation. These destroy work from other sessions.

---

## Step 9 — Deploy verification guidance (NEW)

After merging, if the project has a deploy pipeline:

1. Check if there's a Vercel/Netlify/GitHub Actions deployment triggered.
2. Tell the user: "Change is merged. Deployment should be triggered — verify at [URL] once it's live."
3. If the project has a health check endpoint, suggest hitting it.

Do NOT assume deployment succeeded just because the code merged. Production is a different environment.

---

## Step 10 — Failure pattern library (NEW)

Known high-failure-rate patterns from prior sessions. When encountering these, apply extra caution:

### Binary/opaque format manipulation
**Pattern:** Generating iOS Shortcuts (.shortcut), binary plists, Protocol Buffers without codegen, PDF manipulation without a library.
**Rule:** Always use an established library. If no library exists, tell the user this is high-risk and propose alternatives. Do not hand-roll binary format generation.

### Auth redirect chains
**Pattern:** OAuth flows with multiple redirect hops (Google → app → callback → frontend).
**Rule:** Trace the full redirect chain on paper before coding. Verify every URL, every env var, every redirect_uri match. Test with the actual provider, not assumptions.

### Cloud storage migrations
**Pattern:** Moving from one storage provider to another (Vercel Blob → R2, S3 → GCS).
**Rule:** Always verify read access to the source before writing migration code. Check for CDN caching, auth headers, URL format differences. Build a rollback path.

### Multi-environment config drift
**Pattern:** Code works locally but fails in production because env vars, API keys, or URLs differ.
**Rule:** After any change involving env vars, print the full list of env vars the feature depends on. Let the user verify each one exists in production.

### Cascading CSS/layout regressions
**Pattern:** Fixing one component's layout breaks another component that shared implicit style dependencies.
**Rule:** When modifying shared styles or layout components, visually verify at least 3 pages, not just the one you changed.

---

## Run logging

Every execution creates a log entry in `runs/{date}-{slug}.md`:

```
## {date} — {slug}
**Task:** one-line summary
**Mode:** single-pass | parallel
**Pre-flight:** research gate outcome
**Draft scores:** (if parallel) A=XX B=XX C=XX D=XX E=XX
**Winner:** draft letter + reasoning
**Integration check:** pass | fail (details)
**Cascade depth:** 0-3
**Scope creep:** none | flagged (details)
**Failure pattern match:** none | matched (which pattern)
**Time:** approximate minutes
**Outcome:** shipped | needs-followup | blocked
```

---

## Weekly learning sync

Schedule: once per week (or after every 10 runs, whichever comes first).

Process:
1. Read all run logs since last sync
2. Read post-merge git diffs to see what actually shipped vs. what the skill produced
3. Identify:
   - Patterns where parallel was chosen but single-pass would've been fine (waste)
   - Patterns where single-pass was chosen but the fix cascaded (should've gone parallel)
   - New failure patterns to add to Step 10
   - Scoring criteria that consistently don't differentiate drafts (dead weight)
   - Integration check failures that could have been caught earlier
4. Update this skill file:
   - Adjust signal thresholds in Step 1
   - Add new entries to Step 10 failure pattern library (cap at 30)
   - Tune scoring weights if evidence supports it
5. Cap current learnings at 30 bullet points. Prune lowest-signal items.

### Current learnings

_Empty — populate after first weekly sync._
