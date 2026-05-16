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

## What This Skill Prevents

- Components or files silently deleted by a session that didn't know about them
- Uncommitted work overwritten without warning
- Merge conflicts from concurrent sessions that could have been avoided
- "restore:" commits that indicate work was lost and had to be recovered
