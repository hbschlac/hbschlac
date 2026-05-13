# Integration Playbook — Landing Orphaned Branch Work

14 session branches have accumulated improvements that need to be selectively
merged. This playbook is designed to be executed from the laptop where you have
access to all repos.

---

## Phase 1: Land this branch to main (~10 min)

This branch (`claude/eloquent-euler-6IX8U`) contains:
- `README.md` — Consolidated best version from 5+ attempts
- `CLAUDE.md` — Project memory that prevents future sessions from re-auditing
- `AUDIT.md` — Meta-audit with full findings
- `INTEGRATION-PLAYBOOK.md` — This file
- `SKILL.md` — code-builder v3 (consolidated from 5 iterations)

```bash
cd ~/hbschlac
git fetch origin
git checkout main
git merge origin/claude/eloquent-euler-6IX8U --no-ff -m "Land consolidated skill audit, README, CLAUDE.md, and code-builder v3"
git push origin main
```

---

## Phase 2: Fix mcp-contributor (~15 min)

### 2a. Fix the refresh.sh anchor bug (P0 — stops 4 weeks of noise)

The grep pattern expects `## Step 11.1:` but SKILL.md uses `### 11.1 Design Principles`.

```bash
cd ~/mcp-contributor
# Find the grep pattern in refresh.sh and update it to match actual heading format
grep -n "Step" refresh.sh
# Fix: change the heading regex to match ### N.N format instead of ## Step N.N:
# Test: ./refresh.sh --dry-run  (should show 0 anchor misses instead of 11)
git add refresh.sh
git commit -m "fix: update anchor grep pattern to match actual SKILL.md heading format"
git push
```

### 2b. Close noise issues #4-7

```bash
gh issue close 4 -c "Root cause: anchor grep pattern bug in refresh.sh. Fixed in $(git rev-parse --short HEAD)."
gh issue close 5 -c "Duplicate of #4 — same anchor bug."
gh issue close 6 -c "Duplicate of #4 — same anchor bug."
gh issue close 7 -c "Duplicate of #4 — same anchor bug."
```

### 2c. Fix structural issues #1-3

From the OdhHA branch audit (`skills/mcp-contributor/PATCHES.md`):

**Issue #1** — Add cross-reference from capability triage (S1) to S11.7 lifecycle:
```
In S1.5 (triage): Add "For protocol capability questions, see §11.7 Protocol Primer."
```

**Issue #2** — Add missing repos to S6 repo map:
```
Add: Inspector, Registry, ext-*, access, .github
```

**Issue #3** — Retitle S4 from "SDK workflow" to "Non-spec repo workflow":
```
S4 applies to Inspector, Registry, etc. — not just SDKs.
```

---

## Phase 3: Deploy code-builder v3 (~15 min)

The consolidated SKILL.md on this branch incorporates improvements from 5
separate sessions. Copy it to the code-builder repo:

```bash
# Get the v3 SKILL.md from this branch
cd ~/hbschlac
git checkout claude/eloquent-euler-6IX8U -- SKILL.md

# Copy to code-builder repo
cp SKILL.md ~/code-builder/SKILL.md
cd ~/code-builder

# Review the diff
git diff SKILL.md

# Commit
git add SKILL.md
git commit -m "code-builder v3: consolidated from 5 audit sessions

Key changes from v2:
- Token budget awareness (N=3 for medium tasks)
- mkdir -p for run log directory
- Worktree cleanup verification
- Stale learning detection (warns after 14 days without sync)
- Adaptive bias hints based on win-rate history
- Cross-skill conflict declaration
- Suppressible single-pass activation banner
- git init offer when not in a repo (instead of silent downgrade)
- Post-merge diff mining promoted from deferred to active
- Auto-discovery of repos from ~/.claude/projects/ (no hardcoded names)"
git push
```

### 3a. Set up the weekly sync runner

Create `.github/workflows/weekly-sync.yml` in the code-builder repo:

```yaml
name: Weekly Learning Sync
on:
  schedule:
    - cron: '0 23 * * 0'  # Sunday 6pm ET
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Trigger sync
        run: |
          echo "Weekly sync triggered at $(date)"
          echo "TODO: Implement sync.sh that reads run logs and updates learnings"
          # For now, create an issue as a reminder
      - name: Create reminder issue
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Weekly sync reminder — ${new Date().toISOString().split('T')[0]}`,
              body: 'Run `code-builder sync` manually or implement sync.sh.',
              labels: ['sync']
            });
```

---

## Phase 4: Deploy insight-detector.py (~5 min)

```bash
# Get the full implementation from the OdhHA branch
cd ~/hbschlac
git show origin/claude/eloquent-euler-OdhHA:skills/insights-dashboard/insight-detector.py > /tmp/insight-detector.py
git show origin/claude/eloquent-euler-OdhHA:skills/insights-dashboard/requirements.txt > /tmp/requirements.txt

# Copy to the actual repo
cp /tmp/insight-detector.py ~/claude-code-insights-dashboard/insight-detector.py
cp /tmp/requirements.txt ~/claude-code-insights-dashboard/requirements.txt
cd ~/claude-code-insights-dashboard

git add insight-detector.py requirements.txt
git commit -m "feat: implement insight-detector with 8 pattern detection algorithms

Replaces stub with: session length analysis, commit velocity tracking,
project concentration detection, cadence patterns, growth trajectory,
and transcript behavioral analysis."
git push
```

---

## Phase 5: Clean up orphaned branches (~5 min)

After landing the valuable work, delete the redundant branches:

```bash
cd ~/hbschlac

# Keep these (have unique valuable content):
# claude/eloquent-euler-6IX8U — this branch (merged to main in Phase 1)
# claude/eloquent-euler-TZDUi — code-builder v2 reference
# claude/review-code-skill-plan-5p6Yc — original plan reference

# Safe to delete (content superseded by this branch):
git push origin --delete claude/eloquent-euler-1YmCG
git push origin --delete claude/eloquent-euler-7gZPQ
git push origin --delete claude/eloquent-euler-8Exat
git push origin --delete claude/eloquent-euler-9BrkB
git push origin --delete claude/eloquent-euler-NZwjg
git push origin --delete claude/eloquent-euler-OCF48
git push origin --delete claude/eloquent-euler-OdhHA
git push origin --delete claude/eloquent-euler-Oiaxw
git push origin --delete claude/eloquent-euler-c2gJQ
git push origin --delete claude/eloquent-euler-fr1II
git push origin --delete claude/eloquent-euler-g9WhT
git push origin --delete claude/eloquent-euler-oZ6aD
```

---

## Phase 6: Future prevention

After landing all the above, future Claude Code web sessions on this repo will:
1. Read CLAUDE.md and see the full context
2. Know which branches have been merged vs. deleted
3. Know the sandbox constraint and write laptop-executable instructions
4. Not re-audit skills that have already been audited and fixed

**Time estimate for Phases 1-5: ~50 minutes total.**
