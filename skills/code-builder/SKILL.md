---
name: code-builder
description: >
  Raises the floor of code quality by generating 5 parallel implementations
  of the same dev task, self-scoring them against a measurable rubric, and
  merging the winner. Includes UI/visual, mobile-responsiveness, accessibility,
  and security criteria alongside correctness and convention adherence.
trigger:
  - /code-builder
  - "build this"
  - "fix this bug"
  - "add a feature"
  - "something broke"
  - "this page is broken"
  - Creating components, functions, modules, pages, or layouts
  - Pasting code requesting changes
  - Sharing errors or stack traces
---

# code-builder

## 1 — Activation

Before any work, print:

```
🔧 code-builder activated — [parallel | single pass | visual]. [reason ≤15 words]
```

### DO activate for

- Bug fixes, feature builds, refactors, component creation
- Styling / layout / responsive design tasks
- Page or route creation
- Migration or upgrade tasks

### Do NOT activate for

- Pure reading, research, or exploration
- Writing, design docs, planning, or strategy
- Meta-tasks (summarize session, update build log)
- Tasks the user explicitly says to do quickly / without parallel

---

## 2 — Decision Gate

### Parallel (5 drafts) when

- \>30 lines expected to change
- Multiple files or new files involved
- Multiple valid design approaches exist
- Greenfield prototype from scratch
- Open-ended task phrasing ("make this page look better")
- UI/layout task with subjective design space

### Single pass when

- <10 lines changed
- Exactly one file, one obviously correct path
- Targeted bug fix with known root cause
- Not in a git repo (worktree requirement)

### Visual mode (3 drafts) when

- Task is primarily CSS/styling/layout
- 10-30 lines expected to change
- Design is subjective but scope is contained
- Single-component visual refinement

Visual mode spawns 3 drafts (not 5) to save tokens while still
exploring the design space: (1) minimal/clean, (2) match existing patterns,
(3) best instinct.

---

## 3 — Scoring Rubric (100 points)

### Core criteria (60 pts)

| Criterion | Weight | Measurement |
|-----------|--------|-------------|
| Correctness | 25 pts | Walk task requirements; deduct for gaps |
| Tests pass | 15 pts | Run project test suite; pass=15, fail=0 |
| Typecheck clean | 10 pts | Zero errors on `tsc --noEmit` or equivalent |
| Lint clean | 5 pts | Zero warnings on project lint command |
| Scope containment | 5 pts | Deduct if unrelated files touched |

### Craft criteria (25 pts)

| Criterion | Weight | Measurement |
|-----------|--------|-------------|
| Minimal diff | 8 pts | LOC efficiency across drafts |
| Reuses existing utilities | 7 pts | Grep for helpers before writing new ones |
| Follows repo conventions | 5 pts | Naming, structure, import style alignment |
| No unnecessary deps | 5 pts | Zero new deps=5; each new dep costs -2 |

### UI & UX criteria (15 pts — applied when task touches UI)

| Criterion | Weight | Measurement |
|-----------|--------|-------------|
| Mobile responsiveness | 5 pts | Check breakpoints: 375px, 768px, 1024px. No overflow, no cramped text, no hidden content |
| Visual consistency | 5 pts | Matches existing design tokens (colors, spacing, fonts, border-radius). No magic numbers |
| Accessibility baseline | 5 pts | Semantic HTML, alt text on images, sufficient color contrast, keyboard navigability |

When a task does NOT touch UI, redistribute the 15 pts: +5 correctness, +5 minimal diff, +5 tests.

### Security overlay (deductions, not scored)

Deduct 10 pts per violation found:
- Hardcoded tokens/secrets in client-side code
- Unsanitized user input rendered as HTML (XSS)
- Missing auth checks on protected routes/endpoints
- Secrets in git-committed files
- eval() or dangerouslySetInnerHTML without justification

Security floor: any draft scoring <50 after deductions is disqualified.

---

## 4 — Parallel Workflow

### Step 4a — Spawn drafts

Spawn all drafts simultaneously with `isolation: "worktree"` and
`run_in_background: true`.

**5-draft mode bias hints:**
1. Simplest possible implementation
2. Most idiomatic to repo patterns
3. Optimize for readability and maintainability
4. Optimize for performance and edge-case coverage
5. Best instinct — unconstrained

**3-draft visual mode bias hints:**
1. Minimal/clean — fewest lines, simplest selectors
2. Match existing design patterns — reuse tokens, mirror sibling components
3. Best instinct — optimize for user delight

Each draft reports: approach summary, files touched, LOC added/removed,
commit SHA.

### Step 4b — Pre-flight checks (before scoring)

For each draft, before scoring:
1. Run tests (`npm test` / project test command)
2. Run typecheck (`tsc --noEmit` or equivalent)
3. Run lint (`npm run lint` or equivalent)
4. If task touches UI: check for responsive issues by reviewing CSS/Tailwind at mobile breakpoints

### Step 5 — Evaluate

Score all drafts against rubric. Record full breakdown.

**Tiebreakers (in order):**
1. Smallest diff
2. Draft 2 (repo idiom match)
3. Better mobile handling

### Step 6 — Merge & validate

1. **Gap check** — confirm winner covers ALL task requirements
2. **Cherry-pick** — scan rejected drafts for edge cases, error handling, or visual polish the winner missed. Cherry-pick specific improvements, not wholesale code.
3. **Redundancy check** — remove unused imports, dead code, debug logs, console.logs
4. **Re-validate** — run tests + typecheck + lint on final diff
5. **Mobile spot-check** — if UI changed, confirm no overflow at 375px width
6. **Report** — one line: merge status, final score, files changed

---

## 5 — Post-Merge Verification

After merge, before reporting "done":

### For UI tasks
- Start dev server if not running
- Load the affected page/component in browser
- Check golden path + one edge case
- Check at mobile width (375px)
- Check for visual regressions in adjacent components

### For non-UI tasks
- Run full test suite
- Verify the specific behavior changed

### For deployment-targeted repos
- If repo has Vercel/Netlify preview: confirm build succeeds
- Note any deploy warnings

---

## 6 — Run Logging

Every execution: `~/.claude/skills/code-builder/runs/{YYYY-MM-DD}-{slug}.md`

```markdown
## {date} — {task-slug}

**Task:** {verbatim description}
**Mode:** parallel (5) | visual (3) | single
**Repo:** {repo name}

### Drafts
| # | Approach | Score | Key strength | Key weakness |
|---|----------|-------|-------------|-------------|
| 1 | ... | XX/100 | ... | ... |

### Winner: Draft {N} ({score}/100)
**Rationale:** {why this one}
**Cherry-picked from others:** {what, from which draft}

### Post-merge validation
- Tests: pass/fail
- Typecheck: clean/errors
- Mobile: checked/skipped/issues
- Browser verified: yes/no

### Learnings
- {anything new for the sync}
```

---

## 7 — Learnings Sync

**Schedule:** Sundays 6pm or on-demand via "code-builder sync"

**Sources:**
1. Run logs from new executions
2. Post-merge git diffs showing manual edits (what Claude got wrong)
3. In-session feedback
4. Judgment overrides
5. Cross-repo mining (50 recent commits per active repo)

**Rules:**
- Cap at 40 bullets (was 30 — increased to cover UI patterns)
- Remove bullets that haven't been relevant in 8+ weeks
- Group by category (Process, Code Patterns, UI/Visual, Framework-Specific)
- Each bullet must cite the source session or commit

### Current Learnings

**A — Process Failures**
- Never call Skill() from inside scheduled-task bodies (circular dispatch)
- "Done" requires green tests + typecheck + browser verification for UI tasks, not just compilation
- Resolve merge conflicts by re-running tests, not by inspection
- Grep for existing helpers before writing new ones
- When fixing a bug, write the reproduction test FIRST

**B — Code Patterns**
- Validate and trim `process.env.X` at read-site to handle whitespace variance
- Guard nullable API responses before destructuring
- `useEffect` subscriptions/timers must include cleanup functions
- Full Rules of Hooks enforcement in React code
- No hardcoded tokens/secrets in client JavaScript

**C — UI & Visual Patterns**
- Floating UI in scroll parents needs `position: fixed` + portal, not `position: absolute`
- Unscale `getBoundingClientRect()` values when CSS transforms apply
- Save/restore editor selection before DOM-mutating modals
- Always test at 375px width — "looks fine on desktop" is not done
- Use design tokens (CSS variables / Tailwind config) instead of magic hex values or pixel numbers
- Font stack changes affect line-height and spacing — check adjacent elements
- Image grids: use `object-fit: cover` with consistent aspect ratios, not variable heights
- Portrait/headshot images: consistent dimensions, border-radius, and spacing across grid
- Background color changes propagate — check header, footer, cards for contrast

**D — Next.js / React Specific**
- App Router: check if component needs `"use client"` before using hooks or browser APIs
- Dynamic imports for heavy components (image editors, rich text, maps)
- `next/image` requires explicit width/height or `fill` with sized parent
- Metadata exports in page.tsx for SEO on public-facing pages
- Tailwind responsive prefixes: design mobile-first, add `md:` and `lg:` overrides
- `localStorage` / `sessionStorage` access must be guarded with typeof window check

---

## 8 — Framework Awareness

When working in a detected framework, apply framework-specific checks:

### Next.js (App Router)
- Server vs Client component boundaries
- Metadata/SEO on public pages
- Image optimization via next/image
- Route groups and layouts
- Server actions for mutations

### React (general)
- Hooks rules enforcement
- Key prop on list items
- Controlled vs uncontrolled inputs
- Effect cleanup

### Tailwind CSS
- Mobile-first responsive design
- Design token consistency (extend theme, don't use arbitrary values when token exists)
- Dark mode support if repo uses it
- Purge/content config includes all template paths

---

## 9 — Error Recovery

### Worktree creation fails
→ Auto-downgrade to single pass. Log the failure.

### Agent timeout or crash
→ Score available drafts. If <2 completed, re-run as single pass.

### All drafts score <50
→ Do NOT merge any. Report the failure with top-scoring draft's issues. Ask user for guidance.

### Tests pass locally but CI fails
→ Check for env-specific issues (missing env vars, Node version, OS differences). Fix and re-validate.

### Merge conflicts
→ Re-run tests on merged result. Never resolve conflicts by inspection alone.
