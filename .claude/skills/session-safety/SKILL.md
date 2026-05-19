---
name: session-safety
description: >
  Prevents sessions from silently deleting or overwriting each other's work.
  Always active. Includes branch scan for duplicated work (Groundhog Day
  prevention), sandbox-scoped session guidance, and merge readiness checklist.
---

# session-safety

Prevents Claude Code sessions from silently overwriting each other's work. Always active.

---

## Session Start Check

At the beginning of every session that will modify files:

1. **`git status`** — Check for uncommitted changes.
   - If any: list changed files, ask "Stash, commit, or work around them?"
   - Never silently proceed past uncommitted changes.

2. **`git stash list`** — Check for stashed work. List stash descriptions if any exist.

3. **`git log --oneline -5`** — Note author/session of recent commits. Flag overlap if the last commit was from a different session and touched relevant files.

4. **Branch scan for duplicated work.**
   ```bash
   git branch -a | head -30
   ```
   If the current task resembles work on existing branches (e.g., "update README" with 5 branches having README changes), say:
   ```
   session-safety: similar work may exist on other branches:
   - {branch}: {commit message} ({date})
   Consider building on existing work rather than starting fresh.
   ```

---

## Before Modifying Files

1. Check if the file has uncommitted changes. Warn before overwriting.
2. Never delete a file without checking `git log` for it first. If recently added by another session, confirm before removing.
3. Never remove a component/function/import added in a recent commit unless the task explicitly requires it.

---

## Conflict Recovery

If work was lost ("that was deleted", "where did X go"):

1. `git reflog` — find the commit where it existed
2. `git show {sha}:{path}` — recover file content
3. Cherry-pick or manual restore
4. Commit with message: `restore: re-add {description} (deleted by prior session)`

---

## Multi-Session Coordination

- Each session should work on distinct files when possible.
- If overlap is unavoidable, the later session pulls/rebases first.
- Never force-push or reset shared branches.
- Prefer feature branches; merge when both sessions are done.

---

## Sandbox-Scoped Sessions (Claude Code on the Web)

Web sessions are scope-locked to a single repo. They CANNOT push to other repos.

When a session needs to change code in another repo:
1. Write the changes as full file contents in the current repo.
2. Include exact commands for the user to apply from their laptop:
   ```bash
   cd ~/path/to/target-repo
   git checkout -b improvement-from-session
   # paste/apply the changes
   ```
3. Flag this constraint explicitly. Don't assume "Hannah will figure it out."

---

## Session End Checklist

Before ending a session that created improvements:

- [ ] Changes are committed (not just staged)
- [ ] Branch is pushed to remote
- [ ] If changes target another repo, laptop instructions are in CLAUDE.md
- [ ] CLAUDE.md is updated if project context changed
- [ ] No orphaned analysis files (AUDIT.md, REVIEW.md) — put findings in CLAUDE.md
- [ ] **Tell Hannah to merge the branch.** Work on orphan branches is useless.

---

## What This Skill Prevents

| Problem | How |
|---------|-----|
| Files silently deleted by a session that didn't know about them | Pre-modification git log check |
| Uncommitted work overwritten | Session start check |
| Merge conflicts from concurrent sessions | Multi-session coordination rules |
| Work lost requiring "restore:" commits | Conflict recovery protocol |
| Groundhog Day: repeated work on isolated branches | Branch scan + merge checklist |
| Orphaned improvements dying on throwaway branches | Session end checklist with explicit merge instruction |

---

## Changelog

- **2026-05-19 — Consolidated from branches CT6lT + GpVa7**
  - Added sandbox-scoped session guidance (the #1 operational constraint)
  - Added session end checklist with explicit "tell Hannah to merge"
  - Added branch scan for Groundhog Day prevention
  - Merged the two slightly different versions from CT6lT (57 lines) and GpVa7 (102 lines)
