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

### Skill precedence (when multiple skills trigger)

code-builder is the execution engine. Domain skills provide context. They co-activate, not compete:

| Task type | Active skills | Who does what |
|---|---|---|
| Portfolio feature | code-builder + portfolio-dev | portfolio-dev: conventions, data model. code-builder: mode selection, execution. |
| Deploy failure | vercel-ship (primary) | vercel-ship owns debugging. code-builder activates only if the fix requires code changes. |
| CSS/styling | code-builder (visual mode) + portfolio-dev | code-builder runs 3 visual drafts. portfolio-dev constrains the design system. |
| User-facing text in code | code-builder + content-quality | code-builder runs Step 6 content check. content-quality validates the text. |
| Production incident | debug-escalation (primary) | debug-escalation owns triage. code-builder's debug loop activates only for the fix itself. |
| Cross-repo coordination | session-safety (primary) | session-safety owns the workflow. code-builder handles per-repo code changes. |

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
| Task outputs files for external systems? | Validate format compliance before the point of no return. Check: file structure, required metadata, size plausibility. See LEARNINGS.md "File Format Compliance." |
| Task builds a multi-step pipeline? | Map all steps, add validation between them. See LEARNINGS.md "Pipeline Hardening." |
| Task adds an optional enhancement to an existing feature? | Make it fail gracefully — try/catch with degradation, don't let it break the core path. See LEARNINGS.md "Graceful Degradation." |
| Task consumes content from external/untrusted sources? | Validate format, authenticity, plausibility, integrity, safety. See LEARNINGS.md "Untrusted Source Validation." |
| Task sends data to a third party (email, API, payment)? | Assume silent failure. Build "sent, not confirmed" UX. Add webhook idempotency. See LEARNINGS.md "Third-Party Integration." |
| Task involves multiple concurrent long-running operations? | Model per-operation state machine in server, not client memory. Add per-op timeouts, per-item status UI, cancellation. See LEARNINGS.md "Async Operation Queue Management." |

### 1C-2. Claude Code Environment (web sessions)

| Check | Action |
|---|---|
| Running in ephemeral container? | No persistent filesystem between sessions. Anything worth keeping must be committed and pushed. |
| Need to search/fetch external info? | Use subagents (`Agent` tool with `subagent_type: "Explore"`) for broad searches. Use `WebFetch`/`WebSearch` for specific URLs. Don't shell out to `curl` for APIs when MCP tools exist. |
| Using MCP tools (GitHub, Vercel, etc.)? | MCP tools can timeout or fail silently. Always verify the result — don't assume success. If a tool returns an error, retry once, then fall back to an alternative approach or flag the user. |
| Need to work across repos? | Check `mcp__claude-code-remote__list_repos` first. If the repo is available, use `add_repo`. If not, send a PushNotification with exact commands — don't write laptop instructions in CLAUDE.md that sit unread. |
| Spawning subagents for parallel work? | Use `Agent` tool with `run_in_background: true` for independent tasks. For research: specify "report in under 200 words" to keep context lean. For code changes: use `isolation: "worktree"`. Never spawn more than 3 subagents for one task. |
| Session nearing context limits? | Conversation gets auto-compressed. Keep skill activations minimal after the first 3 — suppress announcements. Prefer direct tool calls over subagent delegation for simple tasks. |
| Considering parallel mode (Step 4a)? | **Skip it in web sessions.** Worktrees don't work in ephemeral containers. Use single-pass or debug loop. |

### 1C-3. MCP Integration Tools

Web sessions have access to powerful MCP integrations beyond GitHub. Use `ToolSearch` to load schemas before calling. Key tools by category:

| Category | Tools | Use for |
|---|---|---|
| **GitHub** | `mcp__github__search_pull_requests`, `pull_request_read`, `merge_pull_request`, `create_pull_request`, `list_issues` | PR management, code search, issue triage. `search_pull_requests` works across repos even when not in session scope. |
| **Vercel** | `mcp__Vercel__list_deployments`, `get_deployment_build_logs`, `get_runtime_logs`, `get_project` | Deploy verification, runtime debugging, env var checks. Faster than the dashboard. |
| **Google Drive** | `mcp__Google-Drive__search_files`, `read_file_content`, `create_file` | Read/write docs, access shared files, store analysis outputs. |
| **Gmail** | `mcp__Gmail__search_threads`, `create_draft` | Check for relevant emails, draft notifications. |
| **Canva** | `mcp__Canva__generate-design`, `search-designs`, `export-design` | Generate social images, OG images, design assets for portfolio. |

**MCP tool patterns:**
- Always load schemas via `ToolSearch` before calling — direct calls fail with InputValidationError.
- Chain calls: `list_pull_requests` → `pull_request_read` → check status → `merge_pull_request`.
- Large results: MCP search tools can return >100KB. Use specific queries and pagination to keep results manageable.
- Cross-repo: `mcp__github__search_pull_requests` with `owner:hbschlac` works even for repos not in session scope. Use it for status checks before deciding what to work on.

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

## Step 4a — Parallel Path (laptop only — skip in web sessions)

**SKIP in web sessions.** Parallel mode requires git worktrees, which don't work in ephemeral containers. Fall back to single-pass immediately.

**Status:** Untested after 8 versions and 50+ sessions. Requires laptop with persistent filesystem. When first used: run N=3, log full score breakdown, commit the run log. Spawn N `Agent` calls with `isolation: "worktree"` and differentiated biases (simplest, most idiomatic, most readable). Score with the rubric in Step 5. See git history for the full parallel mode spec.

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

## Rapid Shipping Mode

When building 5+ features in a single session (e.g., kindle-schlacter-me shipped 20 PRs in 2 sessions), normal single-pass mode is correct but needs scoping discipline.

### Activation

- User provides a feature list, PRD, or backlog with 5+ items
- Multiple related features share a codebase and deploy target
- Features can be shipped incrementally (each PR is independently deployable)

### Sequencing rules

1. **Build the core path first.** The feature that everything else depends on ships first. Don't build the error UI before the happy path works.
2. **Validation before polish.** PR order: core feature → input validation → error handling → edge cases → UX polish → escape hatches. kindle-schlacter-me: send (PR#1) → EPUB validation (PR#7) → failure visibility (PR#13) → fake detection (PR#17) → stuck status fix (PR#18).
3. **Group by pipeline stage, not by feature type.** Don't do "all search features, then all send features." Do "search happy path + send happy path, then search edge cases + send edge cases."
4. **Ship after each PR, not after the batch.** Each PR should be deployed and smoke-tested before starting the next. This surfaces real-world failures that inform the next PR.

### Scope management (when to stop iterating)

Rapid iteration on a pipeline (search → download → validate → send) generates a growing backlog of discovered issues. Without boundaries, this becomes unbounded:

| Signal | Action |
|---|---|
| New issue is in the same pipeline step you just fixed | You're churning. Escalate to debug-escalation. |
| New issue is a different failure mode you haven't seen | Healthy iteration. Keep going. |
| You've shipped 10+ PRs and the core path works reliably | Declare the pipeline "hardened." Remaining issues go to a backlog, not the current session. |
| Edge case affects <5% of users | Add it to the backlog. Don't optimize for rare cases during initial shipping. |
| You're adding UX polish to a feature that has unhandled errors | Stop polishing. Fix the errors first. |

### Post-ship UX discovery (before moving to the next feature)

After shipping each core feature PR, run the UX discovery checklist (LEARNINGS.md "Post-Ship UX Discovery Checklist") BEFORE starting the next feature. This takes 10 minutes and prevents 10+ reactive PRs. Key checks: real device, state persistence across reload, failure paths, deep links, user correction flows.

If running in a web session where you can't test the UI directly, write the checklist into the PR body and ask the user to test before you continue building on top of that feature.

### File validation audit (before shipping any file-output feature)

When your feature generates, transforms, or relays files to an external system, build a validation function BEFORE shipping the feature — not after 4 reactive PRs:

1. **Format compliance:** Does the file match the spec? (zip structure, required entries, encoding, magic bytes)
2. **Content integrity:** Is this real content or a stub/placeholder? (file size, page count, structure)
3. **Structural validity:** Is it well-formed? (no broken internal references, DRM-free, parseable)
4. **Feature isolation:** Can optional enhancements (AI summaries, metadata enrichment) corrupt the base file? If yes, gate them separately.
5. **Deliverability:** Will the receiving system's undocumented rules accept this?

Write the validation function as a single pre-send gate. Run all 5 layers before the point of no return (send, upload, write to DB). Fail with a user-facing error, not silently.

Evidence: kindle-schlacter-me PRs #7, #8, #9, #14, #15, #17 — 6 PRs discovering these layers one at a time. A single upfront validation function would have caught 5 of 6 in one PR.

### Anti-pattern: the 15-PR pipeline

kindle-schlacter-me PRs #6-20 hardened the download→validate→send pipeline over 15 iterations. A pipeline audit (see debug-escalation's pipeline hardening) at PR #6 would have identified format compliance (#7), content integrity (#17), delivery confirmation (#18), and fallback sources (#11) in 3-4 comprehensive PRs instead of 15 reactive ones.

**Rule:** After 5 PRs targeting the same pipeline, STOP. Run debug-escalation's pipeline hardening audit (map all steps, audit each for failure modes, prioritize by blast radius). Then batch the remaining fixes into 2-3 comprehensive PRs.

---

## Learnings Reference

Patterns from real projects are in `LEARNINGS.md` (same directory). Read it when you need reference patterns for a specific domain (Supabase, API resilience, testing, CI, performance, etc.).

Last synced: 2026-06-17. GH Action deployed at `.github/workflows/code-builder-sync.yml`.

---
