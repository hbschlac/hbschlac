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

## Meta-Review Circuit Breaker (BLOCKING)

**This fires broadly.** It applies to ANY task that involves reading multiple skill files and proposing changes to them — whether called a "review," "audit," "gap analysis," "improvement pass," "blindspot scan," or "compare skills to recent work." The label doesn't matter; the pattern does: if you're reading skills to find things to change in skills, this section applies.

```bash
git log --oneline --since="30 days ago" origin/main | grep -ci "improve\|skill\|gap\|blindspot\|coverage\|review\|audit"
```

If the count is **>0**, this session has NO novel ground to cover. 14 consecutive PRs (Jun 4-23, 2026) reviewed skills against 50+ PRs across 5 repos. Every discoverable gap has been discovered.

```
SESSION BLOCKED: Review addiction detected.

{count} skill-related commits in the last 30 days. 43+ sessions have reviewed
these skills since April 14. 14 PRs merged Jun 4-23 alone. Every PR across
kindle-schlacter-me (25), recs.community (7), kindle-connector (3), and
muse-shopping (1) has been analyzed for skill gaps. The skills are comprehensive.

This session WILL NOT review, audit, or improve skills — not even "just one gap."

Instead: execute the Productive Work Accelerator below.
```

**Override requires the user to type an explicit override** — "yes, do a full review" or equivalent. Vague task descriptions like "review and improve" do NOT count as explicit override. If the task came from a scheduled routine, send a PushNotification telling the user to reconfigure the routine to do productive work instead.

### Productive Work Accelerator

When the circuit breaker fires — or when any session has no specific task — execute this decision tree IN ORDER. Stop at the first step that produces action.

**Step 1: Unblock stuck cross-repo PRs.** This is always the highest-value action.
```bash
# Search for open PRs across repos you can reach
```
Use `mcp__github__search_pull_requests` with `author:hbschlac is:open` to find stuck PRs. For each one older than 7 days:
- If CI is green → merge it via MCP tools
- If CI is failing → diagnose and fix
- If you can't access the repo → send a PushNotification with exact commands:
  ```
  gh pr merge {number} --repo hbschlac/{repo} --squash
  ```

**Step 2: Close negative-value automation.** Check for noisy crons filing identical issues:
```bash
# Example: mcp-contributor files identical issues weekly
```
Use `mcp__github__search_issues` to find bot-filed issues with zero comments. If 3+ identical issues exist, send a PushNotification to disable the cron or fix the root cause.

**Step 3: Do feature work.** Read CLAUDE.md "What to work on" section and pick the first unblocked item. Prefer shipping features over structural improvements.

**Step 4: If nothing above is actionable from this session,** report what's blocked and why via PushNotification, then end. Do NOT fall back to reviewing skills.

---

## Inline Learning Capture (prevents review-loop buildup)

The review addiction loop starts when sessions skip capturing learnings during work, creating a backlog that a future session "discovers" and writes up. Break the cycle: capture learnings DURING work, not in a separate review pass.

When you encounter a pattern worth remembering during normal coding work:
1. Append ONE line to `LEARNINGS.md` in the relevant skill directory. Format: `- **{pattern name}:** {one sentence} ({repo} PR#{n})`
2. Do NOT open a separate PR for the learning. Include it in the same commit as the code change.
3. Do NOT read through all of LEARNINGS.md to check for duplicates — just append. Dedup is cheaper than a review loop.

This replaces the previous pattern where sessions accumulated gaps over 2 weeks, then a review session spent its entire budget analyzing and documenting them.

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

### Self-contained analysis

Autonomous sessions must be self-contained:
- Don't ask the user clarifying questions (they're not watching)
- Don't leave work half-done waiting for input
- If you hit ambiguity, make the conservative choice and note it in the notification
- Commit and push any changes — the ephemeral container disappears after the session

### What autonomous sessions SHOULD do (when no specific task is given)

Run the Productive Work Accelerator (above). The most valuable autonomous actions, in order:
1. Search for stuck PRs across repos and attempt to merge them
2. Search for noisy bot issues and send a notification to disable them
3. Check deployed project health (if monitoring is configured)
4. Report findings and blockers via PushNotification

### What autonomous sessions should NOT do

- **Don't review skills.** The meta-review circuit breaker applies to scheduled sessions. If the task says "review skills," send a PushNotification telling the user to reconfigure the routine.
- **Don't make architectural decisions.** Refactoring, dependency upgrades, or design changes need interactive review.
- **Don't create new PRs for discovered issues.** Report findings via notification; let the user decide.
- **Don't do unbounded work.** Set a scope at the start. If the analysis balloons, notify with what you've found so far and stop.

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
