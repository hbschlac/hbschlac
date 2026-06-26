---
name: session-safety
description: >
  Prevents sessions from silently deleting or overwriting each other's work.
  Always active. Includes blocking Groundhog Day prevention, sandbox-scoped
  session guidance, and merge readiness checklist.
---

# session-safety

Prevents Claude Code sessions from silently overwriting each other's work. Always active.

---

## Session Start (mandatory, before any work)

### 1. Read CLAUDE.md

If the repo has a CLAUDE.md, read it FIRST. It contains session history, known issues,
and explicit "do not repeat" instructions. Do not skip this.

### 2. Check for uncommitted changes

```bash
git status
git stash list
```
If uncommitted changes exist: list them, ask "Stash, commit, or work around them?"
Never silently proceed.

### 3. Note recent commits

```bash
git log --oneline -5
```
Flag overlap if the last commit was from a different session and touched relevant files.

### 4. Groundhog Day scan (BLOCKING)

```bash
git fetch origin --prune 2>/dev/null
git branch -a --sort=-committerdate | head -30
```

If branches with similar commit messages exist (e.g., multiple "skill audit," "consolidate,"
"improve code-builder" branches):

```
SESSION BLOCKED: Groundhog Day detected.

{N} branches already attempted this exact task:
- {branch}: {commit message} ({date})
- {branch}: {commit message} ({date})

This work has been done. Do NOT start over.

Options:
1. Read the most recent branch and EDIT its files (don't rewrite)
2. Ask what specifically needs to change
3. Focus on merging existing work rather than creating more
```

**This is blocking.** Do not proceed with a task that duplicates existing branch work
unless explicitly confirmed "yes, start fresh."

---

## Step 0: Do Productive Work First (before anything else)

Every session should start by doing the highest-value work available, not by reviewing skills. Run this BEFORE any other task analysis:

**Priority 1: Unblock stuck PRs (try MCP merge NOW)**

```bash
# Find all open PRs across repos
```
Use `mcp__github__search_pull_requests` with `is:open author:hbschlac` to find stuck PRs. For each one: `mcp__github__pull_request_read` to check CI. If CI is green → `mcp__github__merge_pull_request`. This is always the highest-value action.

**Priority 2: Clean up orphaned branches**

```bash
git fetch origin --prune 2>/dev/null
git branch -r --merged origin/main | grep -v 'main$' | sed 's|origin/||' | head -20
```
For each merged branch: `git push origin --delete {branch}`. For unmerged branches older than 14 days with no open PR: delete them too. 50+ orphaned branches in this repo are pure noise.

**Priority 3: Disable broken automation**

Check CLAUDE.md for noisy crons or false-positive alerts. If a cron files identical issues weekly, disable it or fix the detection logic.

**Priority 4: Build features or fix bugs in actual projects**

Read CLAUDE.md "What to work on" section. Pick the top unblocked item. If the target repo isn't in scope, use `mcp__github__search_pull_requests` (works across repos) to check its state.

**Priority 5: Add monitoring to deployed projects**

Use Vercel MCP tools (`mcp__Vercel__list_deployments`, `mcp__Vercel__get_runtime_logs`) to check deployment health. Create a GHA cron that pings production URLs.

**Never do:** another skill review, another gap analysis, another audit of this repo. Read the circuit breaker below.

---

## Meta-Review Circuit Breaker (BLOCKING)

If the task is "review skills," "audit skills," "improve skills," or "consolidate sessions" — OR if a scheduled routine's task description mentions reviewing, auditing, or improving skills:

```bash
git log --oneline --since="7 days ago" origin/main | grep -i "improve.*skill\|skill.*review\|gap analysis\|blindspot\|coverage gap"
```

If ANY skill-review commit exists in the last 7 days:

```
SESSION BLOCKED: Review addiction detected.

{count} skill review commits in the last 30 days. The skills have been reviewed
and improved continuously since Jun 4. They are comprehensive.

This session WILL NOT do a full skill review. Options:
1. State ONE specific gap you encountered in real work — make a targeted edit
2. Do productive work (see Step 0 above — the priorities are concrete)
3. If the user explicitly insists on a full review, proceed — but log this override
```

**This is BLOCKING like Groundhog Day.** Do not proceed with a full review unless the user explicitly overrides.

**Scheduled routines:** If a scheduled routine's task says "review skills" or similar, the circuit breaker fires AND you must send a PushNotification telling the user to reconfigure:

```
<routine_summary>
Your scheduled routine is configured to review skills — this is blocked by the circuit breaker
(15 skill-review PRs merged since Jun 4, 0 feature work PRs). Reconfigure this routine to do
one of: health check monitoring, PR hygiene sweep, or dependency freshness audit. See
session-safety's "Scheduled Routine Templates" section for ready-to-use templates.
</routine_summary>
```

---

## Before Modifying Files

1. Check if the file has uncommitted changes. Warn before overwriting.
2. Never delete a file without checking `git log` for it first.
3. Never remove a component/function/import added in a recent commit unless the task explicitly requires it.

---

## Conflict Recovery

If work was lost ("that was deleted", "where did X go"):

1. `git reflog` → find the commit where it existed
2. `git show {sha}:{path}` → recover file content
3. Cherry-pick or manual restore
4. Commit with message: `restore: {description} (deleted by prior session)`

---

## Sandbox-Scoped Sessions (Claude Code on the Web)

Web sessions are scope-locked to a single repo. When changes need to go to another repo:

1. Write changes as full file contents under `.claude/skills/` or a clear path in the current repo.
2. Include exact laptop commands in CLAUDE.md under "Laptop Instructions":
   ```bash
   cd ~/path/to/target-repo
   cp ~/hbschlac/.claude/skills/X/SKILL.md ./SKILL.md
   git commit -am "description" && git push
   ```
3. Be explicit — don't assume "she'll figure it out."

---

## Anti-Orphan Rules

1. **No standalone AUDIT.md, REVIEW.md, SKILLS-AUDIT.md, or analysis files.** Put findings inline in CLAUDE.md or in the relevant skill file.
2. **No rewriting skills from scratch.** Edit the existing file. If no version exists, create one. If a version exists, modify it.
3. **No redundant consolidation.** If CLAUDE.md says "Last consolidated: [date]", trust it. Make incremental changes.
4. **No version-inflating rewrites.** Don't claim "v7" if you rewrote the file from scratch instead of editing v6. Versions track evolution, not replacement.

---

## Session End Checklist

Before ending a session that created improvements:

- [ ] Changes are committed (not just staged)
- [ ] Branch is pushed to remote
- [ ] **Create a PR via MCP tools and merge it** (see below)
- [ ] If changes target another repo, laptop instructions are in CLAUDE.md
- [ ] CLAUDE.md is updated if project context changed
- [ ] No orphaned analysis files

## Land Your Work (CRITICAL — prevents Groundhog Day)

Pushing to a branch is NOT enough. 30 sessions pushed to branches. None merged. Do this:

1. Push your branch: `git push -u origin {branch}`
2. Create a PR via `mcp__github__create_pull_request`
3. Merge the PR via `mcp__github__merge_pull_request` (squash merge preferred)
4. If MCP merge tools aren't available, add explicit merge instructions to CLAUDE.md

If you skip this step, your work will be orphaned and the next session will redo it.

---

## Concurrent Session Safety

When multiple web sessions may be active on the same repo:

1. **Use unique branch names.** The auto-generated `claude/*` names handle this.
2. **Check for branches updated in the last hour before starting work on shared files.**
   ```bash
   git branch -r --sort=-committerdate | head -10
   git log --all --oneline --since="1 hour ago"
   ```
3. **Don't edit CLAUDE.md or shared config files unless that's the primary task.** These are high-contention files.
4. **If you see a recent branch touching the same files, ask before proceeding.** Two sessions editing the same component will create a merge conflict neither can resolve.

---

## Multi-Developer Coordination

When multiple humans (or their Claudes) work on the same repo:

1. **Maintain COORDINATION.md.** Track: who's working on what, review queue, blocked items. Update it at session start and end.
2. **Stack PRs with explicit dependencies.** Use `base` branches: PR #2 targets PR #1's branch, not main. State "Depends on #N" in the PR body.
3. **Don't review-bomb.** If there are 6 stacked PRs, review in order. Don't leave comments on PR #6 about issues that should be caught in PR #2.
4. **Separate CI from content PRs.** CI setup (workflows, hooks) should be its own PR so it doesn't block feature review.
5. **Self-onboarding documentation.** When onboarding another developer's Claude, create a PR with CLAUDE.md, review checklist, and coordination doc. The other Claude should be able to `git clone` and start working without a handoff message.

---

## Cross-Repo Coordination

When a product spans multiple repos (e.g., a frontend + backend bridge, or a web app + Python service):

1. **Identify coupled repos early.** If your change touches an API contract, deployment sequence, or shared data format, the other repo needs a coordinated change.
2. **Reference the other repo's PR in your PR body.** "Requires kindle-connector PR#2 to be deployed first" prevents half-deployed states.
3. **Deploy order matters.** Backend/API changes usually deploy before frontend changes that depend on them. Document the deploy sequence in the PR body.
4. **Sandbox limitation:** Web sessions can only push to one repo. For cross-repo changes, complete one repo's work and note the other repo's changes in CLAUDE.md under "Laptop instructions."
5. **Shared env vars.** When two repos share an API endpoint or secret, changes to the value must be coordinated. List affected repos in the PR body.

Evidence: kindle-schlacter-me (Vercel frontend) + kindle-connector (k8s Python bridge) are a coupled system. kindle-connector PR#2 (infohash lookup) was paired with kindle-schlacter-me PR#2 (resilient download). Both PRs reference each other.

---

## Stacked PR Management

Creating stacked PRs is not enough — they must actually merge. A stack of 7 open PRs is worse than no stack.

### Merge stacked PRs immediately

1. **Merge PR #1 as soon as CI passes.** Don't wait for the whole stack to be reviewed.
2. **After #1 merges, retarget #2 to main.** GitHub offers the button, or: `gh pr edit 2 --base main`.
3. **Repeat for each PR in the stack.** The goal is to land work incrementally, not batch-review everything.
4. **If a PR is blocked on review:** ping the reviewer. If no response in 24h, merge if CI is green and the change is low-risk.
5. **If a PR is blocked on CI:** fix CI first. CI failures block the entire downstream stack.

### Rebasing stacked PRs

When a base PR merges and the next PR has conflicts:
```bash
git checkout feature-branch-2
git rebase main
git push --force-with-lease
```

Use `--force-with-lease` (not `--force`) to avoid overwriting concurrent changes.

### Stuck stack detection

At session start, check for stale open PRs:
```bash
# PRs open for more than 7 days with no activity
gh pr list --state open --json number,title,createdAt,updatedAt
```

If a PR stack has been open for >7 days with no merges, flag it:
```
STUCK STACK DETECTED: {repo} has {N} open PRs from {date}.
None have merged. Options:
1. Merge #1 now if CI is green
2. Close the stack and create a single combined PR
3. Ask the owner what's blocking
```

---

## Cross-Repo Management from Web Sessions

Web sessions are scope-locked to one repo. Before assuming you can't reach another repo, check `mcp__claude-code-remote__list_repos` and `add_repo`.

### Time-based escalation for stuck PRs

| Age | Action |
|---|---|
| 7 days | Flag. Attempt `list_repos` → `add_repo` → merge. |
| 14 days | Block new PRs to that repo until existing ones merge. |
| 21 days | Rebase and force-push, close and recreate from main, or squash the stack into one PR. |
| 30+ days | Close the PR. Cherry-pick salvageable work into a new branch from current main. |

### Execution over documentation

When you detect stuck PRs, try to merge NOW:
1. Use `mcp__github__search_pull_requests` (works across repos) to find and merge them.
2. If MCP tools can't reach the repo, send a PushNotification with exact commands.
3. Don't write laptop instructions that will sit unread. Notifications reach the user; CLAUDE.md doesn't.

## Scheduled / Autonomous Sessions

When running as a scheduled routine (no user watching), the session has different constraints than interactive sessions. The user set this up to run while they're away — the push notification is the deliverable, not the transcript.

### When to notify (PushNotification)

| Situation | Action |
|---|---|
| Found something the user set up this routine to catch | **Notify immediately** with what you found. Don't wait until you've investigated everything — timely > thorough. |
| Routine couldn't run (access denied, tool failure, repo not reachable) | **Notify** — a silent failure is worse than a noisy one. Say what broke and what they need to do. |
| Everything looks normal, nothing changed since last run | **Stay silent.** Don't notify "all clear" — that trains them to ignore notifications. |
| Found something interesting but not actionable | **Stay silent.** Only notify if they should do something in response. |
| Made changes and pushed (code fixes, PR comments) | **Notify** with what you changed and why. They need to know the repo state changed. |

### Notification format

Lead with the one sentence they'd read on a phone lock screen. Then include enough detail for them to act without opening the session:

```
<routine_summary>
{One sentence: what happened and what to do about it.}
{2-3 sentences: supporting detail — numbers, PR links, specific files.}
{If action needed: what specifically to do next.}
</routine_summary>
```

### Scheduled Routine Templates

Most scheduled routines fall into one of these patterns. Pick the closest match and adapt.

**Health Check Routine (deployment monitoring)**
1. Load Vercel MCP tools via ToolSearch. Run `mcp__Vercel__list_projects` to get projects, then `mcp__Vercel__list_deployments` for each to check recent deploy status.
2. For each project, hit the production URL with `WebFetch` and verify a 200 response.
3. Check `mcp__Vercel__get_runtime_logs` for any 500 errors in the last 24h.
4. Notify only if: a deployment failed, a site is down, or runtime errors are spiking. Stay silent if all healthy.

**PR Hygiene Routine (stuck work detection)**
1. Use `mcp__github__search_pull_requests` with `is:open author:hbschlac` to find all open PRs across repos.
2. For each PR open >7 days: check CI status with `mcp__github__pull_request_read` (method: `get_check_runs`).
3. If CI is green and PR is >14 days old: notify with the PR link and recommend merging or closing.
4. If CI is red: note which check failed. Notify if it's a simple fix the user could unblock quickly.
5. Check for draft PRs >30 days old — these should be closed or promoted.

**Dependency/Freshness Routine**
1. Check if portfolio README projects table matches what's deployed (compare README links to Vercel projects).
2. Look for repos with no commits in 30+ days that have open issues or PRs.
3. Notify if the portfolio is missing a shipped project, or if a project has gone stale with unresolved work.

**Cross-Repo Status Routine**
1. For each repo in the user's portfolio (kindle-schlacter-me, kindle-connector, recs.community, muse-shopping, hannah-portfolio):
   - Use `mcp__github__search_pull_requests` to check for open PRs
   - Use `mcp__github__list_issues` (if repo is in scope) to check for open issues
2. Aggregate: total open PRs, oldest PR age, repos with stuck work.
3. Notify with a summary if any repo has stuck work. Include the specific PR numbers and ages.

### Self-contained analysis

Autonomous sessions must be self-contained:
- Don't ask the user clarifying questions (they're not watching)
- Don't leave work half-done waiting for input
- If you hit ambiguity, make the conservative choice and note it in the notification
- Commit and push any changes — the ephemeral container disappears after the session

### What autonomous sessions should NOT do

- **Don't make architectural decisions.** Refactoring, dependency upgrades, or design changes need interactive review.
- **Don't merge PRs without explicit prior authorization.** Check-and-report, don't check-and-act on shared resources.
- **Don't create new PRs for discovered issues.** Report findings via notification; let the user decide how to address them.
- **Don't do unbounded work.** Set a scope at the start. If the analysis balloons, notify with what you've found so far and stop.
- **Don't review skills unless the user explicitly asked for it.** The meta-review circuit breaker applies to scheduled sessions too. If a scheduled routine's task is "review skills" or "audit skills," notify the user that this task should be reconfigured to do productive work instead.

---

## Rollback Patterns

When a merged PR breaks production:

### Vercel
1. **Instant rollback:** Vercel dashboard → Deployments → find last working deploy → "Promote to Production." This is faster than any code revert.
2. **Code revert:** `git revert {merge-commit-sha} && git push` creates a new commit undoing the merge.
3. **Don't force-push main.** Revert commits preserve history.

### k8s / Docker
1. **Roll back deployment:** `kubectl rollout undo deployment/{name}` reverts to previous revision.
2. **Pin to previous image tag:** `kubectl set image deployment/{name} {container}={image}:{previous-tag}`
3. **Check rollout status:** `kubectl rollout status deployment/{name}`

### Database
1. **Migrations are forward-only.** Write a new migration that undoes the change, don't edit the deployed one.
2. **For Supabase:** `supabase db reset` is destructive. Use a corrective migration instead.

## Branch Naming and Hygiene

- **Web sessions**: Use the auto-assigned `claude/*` branch name. Don't rename.
- **Feature work**: `feature/{short-description}` for human-initiated branches.
- **After merge**: Delete the remote branch. Orphaned branches are noise.
  ```bash
  git push origin --delete {branch-name}
  ```
- **Stale branch threshold**: Any branch not updated in 14 days with no PR is likely orphaned. Flag it.

---

## Branch Cleanup (batch)

When orphaned branches accumulate (30+ branches with no open PRs):

```bash
# List all remote branches merged into main — safe to delete
git fetch origin --prune
git branch -r --merged origin/main | grep -v 'main$' | sed 's|origin/||'

# Delete merged branches in bulk
git branch -r --merged origin/main | grep -v 'main$' | sed 's|origin/||' | xargs -I{} git push origin --delete {}

# For unmerged branches: check age and PR status before deleting
git for-each-ref --sort=-committerdate --format='%(refname:short) %(committerdate:short)' refs/remotes/origin/ | head -30
```

**Rules:**
- Delete merged branches without asking — they're noise.
- For unmerged branches >14 days old with no open PR: delete. The work was either abandoned or landed via a different branch.
- For unmerged branches with an open PR: leave them. The PR is the record.
- Never delete `main` or any branch with an active PR.
- Log how many branches were cleaned up in the commit message.

---

## Automated System Noise

Cron jobs and automated PR tools create work that needs human attention. When the human step doesn't happen, these systems generate noise instead of value.

### Symptoms

- Same bot issue filed weekly with identical content (mcp-contributor: 7 identical "drift detected" issues May-Jun 2026)
- Automated PRs stuck in draft indefinitely (muse-shopping #1: vibe-improver draft open 23+ days)
- Workflow runs succeeding but nobody acts on the output

### Draft PR triage

When automated tools create PRs (vibe-improver, Dependabot, Renovate):
1. If the PR is in draft: either promote to ready-for-review and merge, or close it. Draft limbo is worse than no PR.
2. If the PR has a passing preview deploy (Vercel bot shows success): merge it. The automation already validated it.
3. If nobody will review it within 7 days: close it with a comment explaining why, or merge if CI passes.

### Noisy cron triage

When a scheduled workflow creates the same issue/alert repeatedly:
1. **If the alert is accurate but nobody acts:** The problem isn't the cron — it's the missing human step. Either fix the underlying issue or disable the cron. Repeated accurate-but-ignored alerts train everyone to ignore all alerts.
2. **If the alert is a false positive:** Fix the detection logic. A cron that files 7 identical false-positive issues is negative-value automation.
3. **Disable-or-fix rule:** If 3+ identical alerts go unactioned, either fix the root cause or disable the automation. Don't let it keep running.

### When list_repos is unavailable

If `list_repos`/`add_repo` tools don't exist in the current session:
1. Open a web session directly in the target repo and merge from there.
2. Send a PushNotification with exact merge commands (don't write them in CLAUDE.md where they'll sit for weeks).

---
