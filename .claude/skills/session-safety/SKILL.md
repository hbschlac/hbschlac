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
2. Do productive work from CLAUDE.md "What to work on next"
3. If the user explicitly insists on a full review, proceed — but log this override
```

**This is BLOCKING like Groundhog Day.** Do not proceed with a full review unless the user explicitly overrides. 7 consecutive sessions (Jun 10-16) violated the advisory version of this check. The problem was: advisory checks get ignored. Blocking checks force a redirect.

**Scheduled routine override:** If this session is a scheduled routine AND the task says "review skills" or similar, the circuit breaker still fires. Scheduled routines should NOT be configured to review skills — that's how the 12-day loop happened. Notify the user that their scheduled task is doing review work instead of productive work, and suggest reconfiguring.

### Productive Work Accelerator

When the circuit breaker fires, don't just say "do productive work." Execute this sequence:

**Step 1: Try to unblock stuck PRs RIGHT NOW** (not "suggest" — actually try):
```bash
grep -A5 "CRITICAL\|stuck\|unmerged\|open.*days" CLAUDE.md
```
If stuck PRs exist, attempt to merge them via MCP tools before doing anything else. This is the highest-value action.

**Step 2: If no PRs to merge, check for concrete feature work:**
```bash
grep -A3 "Build features\|TODO\|WIP\|in-progress" CLAUDE.md
```

**Step 3: Present the top 3 actionable items** with one-line descriptions. Don't list everything — pick what's unblocked NOW from this session.

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

Evidence: recs.community PRs #1-7 opened May 27, zero merged by June 9. 13 days of stale stacked PRs.

---

## Cross-Repo Management from Web Sessions

Web sessions are scope-locked to one repo's MCP tools. This is the #1 cause of stuck PRs — work gets created in other repos but can never be merged from subsequent web sessions.

### Check what repos are accessible

Before assuming you can't reach a repo:
```
mcp__claude-code-remote__list_repos → shows all repos available to add
```

If the target repo appears, add it to the session:
```
mcp__claude-code-remote__add_repo → adds repo to current session's MCP scope
```

After adding, you can use `mcp__github__merge_pull_request`, `mcp__github__list_pull_requests`, etc. on that repo.

### When a repo can't be added

If the repo isn't in `list_repos` or `add_repo` fails:

1. **Write a self-contained merge script** in CLAUDE.md under "Laptop instructions." Not "merge the PRs" — the exact commands:
   ```bash
   cd ~/recs.community
   gh pr merge 1 --squash
   gh pr edit 2 --base main && gh pr merge 2 --squash
   # Continue for each PR in the stack
   ```

2. **Track stuck PRs explicitly** in CLAUDE.md's known issues with: repo, PR numbers, days open, what's blocking.

3. **Don't create more stacked PRs if existing ones haven't merged.** A stack of 7 unmerged PRs is worse than no stack. Evidence: recs.community #1-7 (15+ days, zero merges).

### Stuck PR triage (extends stuck stack detection)

At session start, also check for PRs in known repos that aren't the current session's scope:
```bash
# Check CLAUDE.md for known stuck PRs
grep -A5 "stuck\|unmerged\|open.*days" CLAUDE.md
```

If stuck PRs exist, the FIRST action should be attempting to add that repo and merge — not building new features on top of the stuck foundation.

### Time-based escalation

PRs get staler and riskier over time. Escalate based on age:

| Age | Severity | Action |
|---|---|---|
| 7 days | Warning | Flag in session. Attempt `list_repos` → `add_repo` → merge. |
| 14 days | High | Block new PRs to that repo until existing ones merge. Attempt merge every session. |
| 21 days | Critical | The PR likely has merge conflicts now. Options: (1) rebase and force-push, (2) close and recreate from main, (3) squash the entire stack into one PR. |
| 30+ days | Abandon threshold | Close the PR. Cherry-pick salvageable work into a new branch from current main. The original branch has drifted too far. |

Evidence: recs.community PRs #4-7 open 17+ days, muse-shopping #1 open 22+ days. Both are now in "High" territory — conflicts likely, merge risk increasing daily.

### Execution over documentation

Cross-repo merge has been documented in session-safety v11, v13, v14, and v15. Four versions of guidance. Zero stuck PRs merged by these versions. The problem is not documentation — it's execution. When you detect stuck PRs:

1. **Try to merge RIGHT NOW, not "document for later."** Use `mcp__github__search_pull_requests` (works across repos even when `list_pull_requests` doesn't). If the PR has passing CI and is non-controversial, merge it.
2. **If MCP merge tools work:** merge immediately. Don't add to "Laptop instructions."
3. **If MCP tools can't reach the repo:** send a PushNotification with the exact commands. Don't write them in CLAUDE.md where they'll be read in 3 weeks — send them NOW.
4. **If you're in a scheduled/autonomous session and find stuck PRs:** the notification IS the action. Don't add another known issue.

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

### What autonomous sessions should NOT do

- **Don't make architectural decisions.** Refactoring, dependency upgrades, or design changes need interactive review.
- **Don't merge PRs without explicit prior authorization.** Check-and-report, don't check-and-act on shared resources.
- **Don't create new PRs for discovered issues.** Report findings via notification; let the user decide how to address them.
- **Don't do unbounded work.** Set a scope at the start. If the analysis balloons, notify with what you've found so far and stop.
- **Don't review skills unless the user explicitly asked for it.** The meta-review circuit breaker applies to scheduled sessions too. If a scheduled routine's task is "review skills" or "audit skills," notify the user that this task should be reconfigured to do productive work instead.

### Scheduled session anti-pattern: the review loop

12 consecutive scheduled sessions (Jun 4-16, 2026) each did "analyze PRs, find gaps, improve skills" despite CLAUDE.md explicitly saying "Do NOT do another full skill review." The advisory circuit breaker was ignored 7 times.

**Why it happened:** Each session independently decided to review skills because analyzing PRs is easy work that always produces output. Building features requires context, decisions, and risk — reviews don't.

**How to prevent:** The meta-review circuit breaker is now BLOCKING (not advisory). But if a scheduled routine keeps being configured to review skills, that's a human configuration problem. Notify once: "Your scheduled routine is doing skill reviews. The skills have been reviewed 12+ times. Reconfigure this routine to [specific productive task from CLAUDE.md]."

Evidence: hbschlac/hbschlac has scheduled routines running skill reviews and health checks. 12 sessions produced skill improvements nobody needed while stuck PRs aged from 7 to 25 days without action.

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

Evidence: mcp-contributor refresh.sh creates identical "11 anchor misses" issues weekly (May 3 - Jun 14, 7 issues). The anchor bug is known, documented in CLAUDE.md #2 and #17, but nobody fixes it because it requires laptop access. The cron should be disabled until the anchor pattern is fixed.

### Concrete cross-repo escalation (when list_repos is unavailable)

When `list_repos`/`add_repo` tools don't exist in the current session (confirmed: not all web sessions have them):

1. **Create a GitHub Action in hbschlac/hbschlac** that merges PRs in other repos:
   ```yaml
   name: Cross-Repo Merge
   on: workflow_dispatch
     inputs:
       repo: { required: true, type: string }
       pr_number: { required: true, type: number }
   jobs:
     merge:
       runs-on: ubuntu-latest
       steps:
         - run: gh pr merge ${{ inputs.pr_number }} --repo hbschlac/${{ inputs.repo }} --squash
           env:
             GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
   ```
2. **Or: open the web session directly in the target repo.** Each repo can have its own session — merge from there.
3. **Last resort: laptop instructions with exact commands.** The CLAUDE.md already has this, but if stuck >21 days, escalate to: email yourself the commands (via PushNotification), or schedule a reminder.

---

## Changelog

- **2026-06-17 — v17: Make meta-review circuit breaker BLOCKING, scheduled review loop prevention**
  - CHANGED: Meta-review circuit breaker upgraded from advisory to BLOCKING (like Groundhog Day scan). 7 sessions (Jun 10-16) violated the advisory version — blocking forces redirect to productive work.
  - ADDED: Productive work accelerator now tries to merge stuck PRs via MCP first, not just suggest them.
  - ADDED: Scheduled session anti-pattern: the review loop — explains the 12-session Jun 4-16 pattern and prevents recurrence.
  - ADDED: Prohibition on skill reviews in autonomous sessions unless explicitly requested.
  - Evidence: 12 consecutive sessions did skill reviews. 7 explicitly violated the "Do NOT review" instruction. 0 stuck PRs merged despite 4 versions of merge guidance. recs.community #4-7 aged from 7 to 21 days; muse-shopping #1 from 15 to 26 days.
- **2026-06-16 — v16: Cross-repo execution over documentation**
  - ADDED: "Execution over documentation" subsection to cross-repo management — 4 versions of merge guidance produced 0 merges, the problem is execution not docs. New rules: try to merge NOW via MCP tools, send PushNotification with exact commands if tools can't reach the repo, don't add more "Laptop instructions" that sit for weeks.
  - Evidence: session-safety v11-v15 all documented cross-repo merge patterns. recs.community PRs #4-7 are now 20+ days old. muse-shopping #1 is 25+ days old. Zero stuck PRs were resolved by the documentation — the guidance was correct but never executed.
- **2026-06-15 — v15: Scheduled/autonomous session patterns**
  - ADDED: Scheduled/autonomous session section — notification thresholds (notify on findings and failures, stay silent on all-clear), notification format (phone-banner first line, actionable detail in body), self-contained analysis rules, prohibited actions for autonomous sessions
  - Evidence: hbschlac/hbschlac runs scheduled routines for skill reviews and health checks. Prior autonomous sessions produced transcripts nobody read — the PushNotification is the only output that reaches the user. No skill covered when to notify vs. stay silent, or how to structure self-contained autonomous work.
- **2026-06-14 — v14: Automated system noise, draft PR triage, cross-repo escalation fallback**
  - ADDED: Automated system noise section — detecting and triaging noisy crons and abandoned automated PRs
  - ADDED: Draft PR triage rules (promote, merge, or close — draft limbo is worse than no PR)
  - ADDED: Noisy cron triage with disable-or-fix rule (3+ unactioned identical alerts → disable or fix)
  - ADDED: Concrete cross-repo escalation when `list_repos`/`add_repo` don't exist (GHA merge workflow, direct session, laptop escalation)
  - Evidence: mcp-contributor cron filed 7 identical "11 anchor misses" issues (May 3 - Jun 14), all ignored. muse-shopping #1 (vibe-improver draft) open 23+ days with no human action. This session confirmed `list_repos`/`add_repo` tools are NOT available in all web sessions.
- **2026-06-13 — v13: Time-based stuck PR escalation**
  - ADDED: Time-based escalation table for stuck PRs (7d warning → 14d high → 21d critical/rebase → 30d+ abandon threshold)
  - Evidence: recs.community PRs #4-7 (17+ days), muse-shopping #1 (22+ days). session-safety detected stuck PRs but had no escalation — a 7-day-old PR and a 30-day-old PR got the same treatment. Older PRs need stronger intervention (rebase, squash, or abandon).
- **2026-06-12 — v12: Productive work accelerator**
  - ADDED: Productive work accelerator — when meta-review circuit breaker fires, actively suggest top unblocked items from CLAUDE.md instead of just saying "do productive work"
  - Evidence: circuit breaker correctly prevents reviews but leaves the session directionless; 4+ sessions stopped reviewing but didn't start building
- **2026-06-11 — v11: Cross-repo management, rollback patterns**
  - ADDED: Cross-repo management from web sessions (list_repos → add_repo → merge workflow)
  - ADDED: Concrete guidance for when repos can't be added (merge scripts, stuck PR tracking)
  - ADDED: Rollback patterns for Vercel, k8s/Docker, and databases
  - Evidence: recs.community #1-7 stuck 15+ days, muse-shopping #1 stuck 20+ days — both because no session could reach them
- **2026-06-10 — v10: Meta-review circuit breaker**
  - ADDED: Meta-review circuit breaker — throttles "review all skills" sessions if a review was merged in the last 7 days
  - Evidence: 4 consecutive review sessions (Jun 5-9) all doing "analyze PRs, find gaps, add learnings" instead of building things
- **2026-06-09 — v9: Stacked PR management and stuck stack detection**
  - ADDED: Stacked PR management section (merge immediately, retarget, rebase, stuck detection)
  - Evidence: recs.community PRs #1-7 open for 13+ days with zero merges despite correct stacking
- **2026-06-08 — v8: Cross-repo coordination**
  - ADDED: Cross-repo coordination section (coupled repos, deploy order, sandbox limitation)
  - Evidence: kindle-schlacter-me + kindle-connector coupled PRs (PR#2 in both repos)
- **2026-06-06 — v7: Multi-developer coordination**
  - ADDED: Multi-developer coordination section (COORDINATION.md, PR stacking, self-onboarding)
  - Evidence: recs.community multi-Claude workflow (PRs #1-7)
- **2026-06-05 — v6: Concurrent session safety, branch naming/hygiene**
  - ADDED: Concurrent session guidance (check for recent branches, avoid shared file contention)
  - ADDED: Branch naming conventions and stale branch detection threshold
- **2026-06-04 — v5: Add PR-merge workflow to break Groundhog Day cycle**
  - Added: "Land Your Work" section with explicit PR creation + merge via MCP tools
  - Fixed: Groundhog Day scan now fetches remote branches first (web sessions start with no local branches)
  - Context: session #31 proved that pushing to branches without merging is the root cause of Groundhog Day
- **2026-05-29 — v4: Tightened anti-orphan rules, removed gendered assumptions**
  - Kept: all v3 blocking Groundhog Day behavior
  - Tightened: session end checklist (removed "tell Hannah to merge" — that's CLAUDE.md's job)
  - Carried forward: all v2/v3 improvements
- **2026-05-27 — v3: Groundhog Day prevention made blocking**
- **2026-05-24 — v2: consolidated from 25 session branches**
- **2026-05-16 — v1: initial version**
