# code-builder

Auto-activates when Hannah writes, changes, or debugs code. Raises the floor of every coding task by picking the right mode, running build gates, and learning from outcomes.

## Activation

Trigger on any explicit code task ("build this", "fix this bug", "refactor X", "add this feature") or implicit signal (error logs, broken tests, failing deploy, git repo context).

Also trigger on rapid content/UI iteration tasks ("change the copy", "swap this image", "update the data", "fix the layout") — these use quick mode.

Do NOT activate for pure research, brainstorming, or design discussions with no code output.

Announce activation:

```
⚡ code-builder activated — [quick|parallel]. [one-line reason]
```

## Mode selection

Before doing any work, classify the task into one of two modes:

### Quick mode (default for most tasks)

Use when ANY of these are true:
- Content/copy change (text, images, data, config)
- Single-file fix or tweak
- CSS/layout adjustment
- Bug fix with obvious cause
- Task likely under ~50 changed lines
- User is in a rapid iteration session (3+ changes in the last hour)

Quick mode workflow:
1. Make the change directly
2. Run the build gate (see below)
3. If gate passes, commit and push
4. If gate fails, fix and re-run

### Parallel mode (for meaningful features)

Use when ALL of these are true:
- New feature, significant refactor, or complex bug with unclear root cause
- Likely touches 3+ files or 100+ changed lines
- Not a content/copy/config change
- Working directory is a git repository

Parallel mode workflow:
1. Scope the task — state the goal, constraints, and success criteria
2. Spawn 5 Agent worktrees in parallel, each with a different bias:
   - **Minimal**: smallest possible diff, fewest new abstractions
   - **Idiomatic**: follows existing codebase patterns exactly
   - **Readable**: optimizes for clarity and self-documenting code
   - **Robust**: prioritizes error handling, edge cases, types
   - **Free**: best judgment, no assigned bias
3. Each draft must pass the build gate independently
4. Score all 5 against the rubric (see below)
5. Pick the winner. Gap-check: if a rejected draft caught an edge case or wrote a better test, cherry-pick that into the winner
6. Merge the winner, run the build gate one final time

## Build gate (ALWAYS runs before push)

This is the single most important part of the skill. Every push must pass these checks. Never skip them — ERROR deploys to Vercel cost time and break the site for users.

```bash
# 1. TypeScript (if tsconfig.json exists)
npx tsc --noEmit

# 2. Lint (if eslint config exists)
npx eslint . --max-warnings 0

# 3. Build (if package.json has a build script)
npm run build

# 4. Tests (if test script exists and tests are relevant)
npm test -- --passWithNoTests
```

If any check fails:
- Fix the issue
- Re-run the failing check
- Do NOT push until all checks pass
- Do NOT use --no-verify or skip hooks

Common build failures to watch for (from actual deployment history):
- TypeScript literal type narrowing (`count: 1` compared to `0` fails)
- Next.js `export const dynamic` conflicts with Turbopack `cacheComponents`
- Missing imports after moving/renaming files
- Floating UI `position: fixed` needed inside overflow parents

## Scoring rubric (parallel mode only)

Score each draft 0-100 across 9 criteria:

| Criterion | Weight | What to check |
|-----------|--------|---------------|
| Correctness | 25 | Does it work? Does it handle edge cases? |
| Tests | 15 | Are new behaviors tested? Do existing tests pass? |
| Typecheck | 10 | Does `tsc --noEmit` pass? |
| Lint | 5 | Does eslint pass with 0 warnings? |
| Minimal diff | 15 | Smallest change that solves the problem? |
| No new deps | 5 | Avoids adding packages when existing code suffices? |
| Reuses utilities | 10 | Uses existing helpers, components, patterns? |
| Conventions | 10 | Matches existing codebase style? |
| Scope | 5 | Stays within the task boundary? |

Winner = highest total score. Log ties and the tiebreaker reasoning.

## Environment validation

Before starting any task in a new repo, check:

```bash
# Verify env vars are set and trimmed (trailing \n is a known issue)
node -e "Object.entries(process.env).filter(([k]) => k.match(/KEY|SECRET|TOKEN|URL/i)).forEach(([k,v]) => { if(v && v !== v.trim()) console.warn('⚠️ ' + k + ' has whitespace — trim it') })"
```

Known env var issues from deployment history:
- `RESEND_API_KEY` stored with trailing `\n` — caused silent send failures
- `SYNC_SECRET` with whitespace — caused auth comparison failures
- `KINDLE_BRIDGE_URL` — verify reachable before attempting bridge calls

## Deployment awareness

After pushing to a Vercel-connected repo:
- Note that GitHub push webhook will auto-trigger a Vercel deploy
- Do NOT also run `vercel deploy` or similar — this causes double deployments of the same SHA within milliseconds (seen repeatedly in kindle-schlacter-me)
- If the user asks about deployment status, suggest checking Vercel dashboard

## Session continuity

When the session is winding down or the user signals they're done:
- If there's meaningful context that a future session needs, suggest creating or updating a `CONTINUE.md` at the repo root with:
  - What was accomplished
  - What's in progress
  - Known issues or next steps
  - Any decisions made and why

## Run logging

Every parallel-mode run logs to `runs/{date}-{slug}.md`:

```markdown
## {date} — {slug}
Mode: parallel
Winner: Draft {N} ({bias})
Score: {score}/100
Runner-up: Draft {M} ({bias}) — {score}/100
Gap-picks: [list any cherry-picked improvements]
Build gate: [pass/fail — what failed]
Time: {duration}
```

Quick-mode runs don't need individual logs, but learnings from them should still feed the weekly sync.

## Weekly sync

Cadence: Sunday 6 PM (or user's configured schedule).

Process:
1. Mine `runs/` logs and post-merge diffs since last sync
2. Mine git history across all repos for patterns (build failures, reverted commits, multi-attempt fixes)
3. Extract new learnings — things that went wrong, patterns that worked, recurring issues
4. Update `## Current learnings` below (hard cap: 30 bullets)
5. Prune learnings that are stale or duplicated

## Current learnings

1. Guard nullable API/DB responses before destructuring — `const { data } = await fetch()` will throw if response is `undefined`
2. Validate `process.env` values at read-site: trim whitespace, check for trailing `\n`, verify non-empty before using
3. Missing `useEffect` cleanup is the #1 post-merge correction — always return a cleanup function for subscriptions, timers, and event listeners
4. Floating UI inside overflow parents needs `position: fixed` + portal — `position: absolute` clips
5. Grep for existing helpers before writing new ones — `grep -r "function\|const.*=.*=>" src/lib src/utils` to find reusable code
6. TypeScript literal types bite when comparing: `count: 1` means `typeof count` is `1`, not `number` — comparison to `0` fails type-check. Use `count: number` in interfaces
7. Next.js `export const dynamic = "force-dynamic"` conflicts with Turbopack's `cacheComponents` setting — use route segment config or middleware instead
8. Gmail SafeLinks prefetches GET links before the user clicks — magic link tokens consumed on prefetch. Use POST-based verification (render a button that POSTs) instead of GET-based token consumption
9. Torrent/scraper search results are non-deterministic (seeder counts shift between calls) — encode enough data in the result ID to reconstruct the item without re-searching
10. LibGen mirror domains rotate unpredictably (`.is` goes down, `.li`/`.la`/`.bz` come up) — implement mirror rotation with fallback, not a single hardcoded domain
11. HTML anchor tooltips can contain `<br>` tags inside `title="..."` attributes — regex patterns using `[^>]` will break on these. Use `[\s\S]*?` lazy match instead
12. Vercel Blob public URLs can be CDN-suspended — when migrating storage, use the private URL with `BLOB_READ_WRITE_TOKEN` to bypass suspension
13. iOS Shortcuts have quirks: `WFJSONValues` must be inlined, not referenced; plutil binary format differs from XML plist; multipart form uploads need specific Content-Type boundaries
14. When working across two repos that talk to each other (e.g. kindle-connector bridge + kindle-schlacter-me frontend), verify the API contract in both directions before pushing either side
15. Resend email API has a ~22 MB practical limit after base64 encoding (~30 MB binary) — add a size guard before calling, and use noimages variants of EPUBs when available
16. `window.close()` is blocked by browsers when the window wasn't opened by script — redirect to `/` or show a "safe to close" page as fallback
17. Git SHA race conditions happen when writing multiple files to GitHub API in parallel — write posts and runs sequentially to avoid conflicts
18. R2 image migration can create 1x1 placeholder files if the source fetch fails silently — add a HEAD size check to verify the migrated file is real
