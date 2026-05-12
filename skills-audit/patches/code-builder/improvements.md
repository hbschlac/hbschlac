# code-builder Improvements

Concrete patches for edge cases, missing error handling, and operational gaps.

---

## 1. mkdir -p for run log directory

**Problem:** Step 7 logs to `~/.claude/skills/code-builder/runs/{date}-{slug}.md`
but never ensures the directory exists. First run in a fresh environment fails.

**Fix in SKILL.md Step 7:**

Add before the write instruction:
```markdown
Before writing the log, ensure the directory exists:
`mkdir -p ~/.claude/skills/code-builder/runs`
```

---

## 2. Worktree cleanup verification

**Problem:** Step 6 says "Clean up worktrees. Delete losing branches." but has no
verification. Orphaned worktrees accumulate silently.

**Fix in SKILL.md Step 6 (Merge validation), after cleanup:**

```markdown
6. Clean up worktrees and verify:
   ```bash
   git worktree remove <path> --force  # for each losing draft
   git branch -D draft-2 draft-3 draft-4 draft-5  # losing branches
   ```
   Verify cleanup:
   ```bash
   git worktree list
   ```
   If any drafts remain, retry removal. If stuck, report to user:
   "Worktree cleanup failed for <path> — manual `git worktree remove` needed."
```

---

## 3. Token budget awareness in judgment gate

**Problem:** The judgment gate has no cost awareness. 5 parallel agents on a
large feature can burn 500K+ tokens without the user realizing.

**Fix in SKILL.md Step 3 — add to the judgment gate table:**

```markdown
| Gate | Parallel threshold | Single threshold |
|---|---|---|
| ... existing rows ... |
| Token budget | Estimated <100K tokens per draft | Estimated >100K per draft → reduce to N=3 |
| Task size | <500 LOC estimated output total | >500 LOC → force single (too large for parallel) |
```

Add a note after the table:
```markdown
**Cost guardrail:** If the estimated total output across all drafts exceeds
300K tokens, reduce to N=3 drafts. If >500K tokens, force single pass.
Announce the downgrade: "Reduced to N=3 — estimated token budget exceeded."
```

---

## 4. Stale learning warning

**Problem:** Learnings freeze silently. After the initial backfill on April 13,
no sync has run. The skill should warn when learnings are old.

**Fix in SKILL.md Step 1 (read learnings), add:**

```markdown
Check the `Last synced:` date in Current learnings. If >14 days ago:
- Add to the activation banner: `⚠ learnings stale ({N} days) — run /code-builder sync`
- Continue using existing learnings (stale > none)
```

---

## 5. Graceful git init for non-repo directories

**Problem:** The skill forces single-pass when not in a git repo. But many
projects start as prototypes before `git init`.

**Fix in SKILL.md Step 4a, item 1:**

```markdown
1. Confirm working dir is a git repo via `git rev-parse --git-dir`.
   If not a git repo:
   - Ask: "This directory isn't a git repo. Want me to `git init` so I can
     use parallel drafts, or proceed with single pass?"
   - If user agrees: `git init && git add -A && git commit -m "initial commit"`
   - If user declines or no response in 5s: downgrade to single pass.
```

---

## 6. Handle all-drafts-fail scenario

**Problem:** Step 4a says "Score survivors if any fail/timeout" but doesn't
handle the case where ALL 5 drafts fail.

**Fix in SKILL.md Step 4a, after waiting for completion:**

```markdown
If all 5 drafts fail or timeout:
- Report: "All 5 parallel drafts failed. Falling back to single pass."
- Log the failure in the run log with `winner_draft: none`, `notes: "all drafts failed"`
- Execute the task as a single pass (Step 4b).
```

---

## 7. Add conflict/precedence declaration

**Problem:** code-builder and mcp-contributor can both activate on the same task
(e.g., writing code for an MCP contribution). No precedence is declared.

**Fix in SKILL.md frontmatter, add:**

```yaml
conflicts:
  - mcp-contributor  # If mcp-contributor is active and guiding a specific
                     # PR workflow, defer to it for the overall process.
                     # code-builder can still activate for the implementation
                     # substep within mcp-contributor's workflow.
```

And in the "When this skill activates" section:
```markdown
**Conflict resolution:** If mcp-contributor is already active and managing
a contribution workflow, code-builder activates only for the implementation
substep (Step 3 or Step 4 of mcp-contributor), not for the overall flow.
```
