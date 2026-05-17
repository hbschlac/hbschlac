---
name: session-safety
description: >
  Prevents sessions from silently deleting or overwriting each other's work.
  Always active. Includes branch scan to detect duplicated work (Groundhog Day
  prevention), sandbox-scoped session guidance, and merge readiness checklist.
  Runs passively alongside any other skill.
---

# session-safety

Prevents Claude Code sessions from silently deleting or overwriting each other's work. Activates automatically at the start of every session and before any file modification.

## Activation

Always active. This skill runs passively alongside any other task.

## Session Start Check

At the beginning of every session that will modify files:

1. **`git status`** — Check for uncommitted changes. If any exist:
   - Print: `session-safety: uncommitted changes detected in {N} files`
   - List the changed files
   - Ask: "These changes may be from another session. Should I stash them, commit them, or work around them?"
   - **Never silently proceed** past uncommitted changes

2. **`git stash list`** — Check for stashed work. If any exist:
   - Print: `session-safety: {N} stashes found`
   - List stash descriptions
   - The user may want to pop a stash before you start

3. **`git log --oneline -5`** — Check recent commits. Note the author/session of each. If the most recent commit was from a different session and touched files relevant to the current task, flag the overlap.

4. **Branch scan for duplicated work.** Run `git branch -a | head -30` and scan for branches with similar names or recent dates. If the current task looks like something that was already attempted on another branch (e.g., "update README" and 5 branches have README changes), tell the user:
   ```
   session-safety: similar work may exist on other branches:
   - {branch}: {commit message} ({date})
   - {branch}: {commit message} ({date})
   Consider building on existing work rather than starting fresh.
   ```
   This directly prevents the Groundhog Day pattern (17 branches, zero merges).

## Before Modifying Files

Before editing or deleting any file:

1. **Check if the file has uncommitted changes** (it may have been modified by a concurrent session). If yes, warn before overwriting.
2. **Never delete a file without checking `git log` for it first.** If the file was recently added by another session/commit, confirm with the user before removing.
3. **Never remove a component, function, or import** that was added in a recent commit unless the current task explicitly requires it. "Cleaning up unused code" is not a valid reason to remove something another session added minutes ago.

## Conflict Recovery

If you discover that work was lost (user says "that was deleted" or "where did X go"):

1. **`git reflog`** — Find the commit where the work existed
2. **`git show {sha}:{path}`** — Recover the specific file content
3. **`git cherry-pick`** or manual restoration — bring it back
4. **Commit the restoration** with message: `restore: re-add {description} (deleted by prior session)`

## Multi-Session Coordination

When the user is running multiple Claude Code sessions on the same repo:

- Each session should work on distinct files when possible
- If file overlap is unavoidable, the session that started later should pull/rebase before starting work
- Never force-push or reset shared branches
- Prefer creating feature branches for parallel work, merging when both sessions are done

## Sandbox-Scoped Sessions (Claude Code on the Web)

Web sessions are scope-locked to a single repo. They CANNOT push to other repos the user owns. When a session needs to change code that lives in another repo:

1. Write the changes as patch files or full file contents in the current repo
2. Include clear instructions for the user to apply from their laptop
3. Never assume "Hannah will figure it out later" — provide exact commands:
   ```bash
   # Apply to target repo:
   cd ~/path/to/target-repo
   git checkout -b improvement-from-session
   # Then paste/apply the changes
   ```
4. Flag this constraint explicitly so the user knows the work isn't done until they apply it

## Merge Readiness Checklist

Before ending a session that created improvements on a branch:

- [ ] Changes are committed (not just staged)
- [ ] Branch is pushed to remote
- [ ] If changes need to land in another repo, instructions are written
- [ ] CLAUDE.md is updated if project context changed
- [ ] No orphaned analysis files (AUDIT.md, REVIEW.md) that should be in CLAUDE.md instead

## What This Skill Prevents

- Components or files silently deleted by a session that didn't know about them
- Uncommitted work overwritten without warning
- Merge conflicts from concurrent sessions that could have been avoided
- "restore:" commits that indicate work was lost and had to be recovered
- Groundhog Day: repeated work across isolated branches that never merge
- Orphaned improvements that die on throwaway branches
