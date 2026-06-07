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

## Stacked PR Workflow (Detailed)

When building a feature that decomposes into 3+ sequential PRs (common for greenfield projects):

### Creating the stack

```bash
# PR #1: scaffold (targets main)
git checkout -b hannah/scaffold-nextjs main
# ... work, commit, push ...
# Create PR #1 targeting main

# PR #2: schema (targets PR #1's branch)
git checkout -b hannah/schema-and-routes hannah/scaffold-nextjs
# ... work, commit, push ...
# Create PR #2 with base=hannah/scaffold-nextjs
# PR body: "Depends on #1 (scaffold)"

# PR #3: auth (targets PR #2's branch)
git checkout -b hannah/supabase-auth hannah/schema-and-routes
# ... work, commit, push ...
# Create PR #3 with base=hannah/schema-and-routes
# PR body: "Depends on #2 (schema + routes)"
```

### When a base PR merges

After PR #1 merges to main:
1. GitHub offers to retarget PR #2 to main — accept it
2. If there are conflicts, rebase: `git rebase main` on PR #2's branch
3. Push the rebased branch: `git push --force-with-lease`
4. Repeat down the stack

### Review order

- Review PRs in dependency order (#1 before #2 before #3)
- Don't block a later PR on comments in an earlier one — fix the earlier PR first
- CI may only run on the latest PR in the stack — verify each PR builds independently

### When NOT to stack

- 2 independent features → parallel branches, not a stack
- Feature + unrelated bug fix → separate branches
- Stack depth > 5 → consider combining some PRs (the rebase cascade becomes painful)

---

## Handoff Documentation

When a PR or session requires human action (dashboard config, deploys, external service setup):

### Pattern: end every PR that needs human action with a numbered list

```markdown
## What you need to do (N quick things)

1. **Activate the Resend webhook:**
   - Resend -> Webhooks -> endpoint `https://kindle.schlacter.me/api/webhooks/resend`
   - Enable `email.delivered` + `email.bounced`
   - Copy the `whsec_...` secret
   - Vercel -> Settings -> Env Vars -> add `RESEND_WEBHOOK_SECRET=<whsec_...>` -> redeploy
   - Verify: unsigned POST to endpoint returns 401 (was 503)

2. **Set Google Books API key (recommended):**
   - Set `GOOGLE_BOOKS_API_KEY` in Vercel env vars
   - Works without it for light use, but prod is more reliable with a key
```

### Rules

- **Be specific.** "Set the env var" is not enough. Say which dashboard, which field name, which value format.
- **Include verification steps.** "After setting X, do Y and expect Z." The human needs to know it worked.
- **Separate required from recommended.** "(required)" vs "(recommended)" in the heading.
- **Don't mix human actions with completed work.** The handoff section is ONLY for things Claude couldn't do.
- **For k8s/non-Vercel deploys:** state the exact command. `git pull && ./deploy.sh` or "Needs a rebuild + redeploy of the k8s image (cc @sam)."

---

## Branch Naming and Hygiene

- **Web sessions**: Use the auto-assigned `claude/*` branch name. Don't rename.
- **Feature work**: `feature/{short-description}` for human-initiated branches.
- **After merge**: Delete the remote branch. Orphaned branches are noise.
  ```bash
  git push origin --delete {branch-name}
  ```
- **Stale branch threshold**: Any branch not updated in 14 days with no PR is likely orphaned. Flag it.

---

## Changelog

- **2026-06-07 — v8: Stacked PR workflow detail, handoff documentation patterns**
  - ADDED: Detailed stacked PR workflow (create, rebase when base merges, review order, when not to stack)
  - ADDED: Handoff documentation pattern (numbered human-action lists, verification steps, required vs recommended)
  - Evidence: recs.community stacked PRs #1-7, kindle-schlacter-me handoff sections, kindle-connector deploy instructions
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
