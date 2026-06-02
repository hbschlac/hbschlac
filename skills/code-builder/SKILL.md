# code-builder

> 5 parallel drafts · self-scored · winner merged · learnings accumulate

## §0 — Activation

**Triggers** (any of these):
- Explicit: `/code-builder`, "use code-builder", "parallel drafts"
- Implicit: coding task in a git repo (write, fix, refactor, add feature, resolve bug)
- Error logs pasted with a repo context
- Greenfield file or feature request

**Does NOT activate for:** reading/analyzing code, design discussions, documentation-only, meta questions about the skill itself.

**On activation, announce:**
`⚡ code-builder activated — [parallel | single-pass]. [one-line reason].`

---

## §1 — Decision: parallel vs. single-pass

Evaluate every coding task against these signals before writing any code.

### Parallel (5 drafts) when ANY is true:
- Estimated diff > 30 LOC
- Touches 3+ files
- Multiple valid design approaches exist
- Greenfield component/module/endpoint
- Security-critical path (auth, RLS, payments, user data)
- User explicitly requests parallel

### Single-pass when ALL are true:
- Estimated diff < 10 LOC
- Single file
- One obvious correct approach
- Known root cause (for bug fixes)
- Not security-critical

### Gray zone (10–30 LOC): default to parallel unless the path is unambiguous.

### Hard overrides:
- `--single` flag → always single-pass
- `--parallel` flag → always parallel
- No git repo available → single-pass (can't create worktrees)
- Claude Code on the web (no local git) → single-pass with explicit note

---

## §2 — Single-pass workflow

1. Read relevant code
2. Implement the change
3. Run available checks (typecheck, lint, tests)
4. If UI change: start dev server and verify in browser before reporting done
5. Present the result

---

## §3 — Parallel workflow

### 3.1 — Spawn 5 agents

Each agent works in an isolated git worktree. Assign distinct biases:

| Agent | Bias |
|-------|------|
| A | Simplest possible — fewest lines, least abstraction |
| B | Most idiomatic for this project's stack and conventions |
| C | Readability-first — clearest names, most self-documenting |
| D | Performance-optimized — fewest allocations, fastest path |
| E | Best instinct — no constraint, just write what feels right |

Each agent receives:
- The task description
- Relevant file contents
- Project context (see §7)
- Its assigned bias
- The scoring rubric (§4)

### 3.2 — Collect and score

Wait for all 5 agents. Score each 0–100 using the rubric in §4.

### 3.3 — Abort check

If ALL drafts score below 40:
- Do NOT pick the least-bad option
- Report: "All 5 drafts scored below 40. This task likely needs human design input or a clearer spec before code-builder can produce quality output."
- List the top failure modes across drafts
- Ask for direction

### 3.4 — Select winner

Pick the highest-scoring draft. In case of ties (within 3 points), prefer the draft with the higher correctness sub-score.

### 3.5 — Cherry-pick gaps

Review rejected drafts for:
- Test cases the winner missed
- Edge-case handling the winner skipped
- Documentation/comments that clarify non-obvious behavior

Merge these into the winner if they improve the score without introducing conflicts.

### 3.6 — Validate

Run the full check suite on the merged result:
- `tsc --noEmit` (TypeScript projects)
- Linter
- Test suite
- If UI change: start dev server, verify golden path and edge cases in browser

### 3.7 — Log the run

Write a log entry to `runs/{date}-{slug}.md`:

```markdown
# {date} — {task slug}

**Decision:** parallel | single-pass
**Reason:** {why}
**Scores:** A={n} B={n} C={n} D={n} E={n}
**Winner:** {letter} ({bias})
**Cherry-picked from:** {letters, or "none"}
**Final score:** {n}/100
**Learned:** {one-line takeaway, or "nothing new"}
```

---

## §4 — Scoring rubric

| Dimension | Weight | 0 | 50 | 100 |
|-----------|--------|---|----|----|
| Correctness | 30 | Doesn't compile/run | Works for golden path | Handles all edge cases |
| Tests | 15 | No tests | Tests golden path | Tests edges + failure modes |
| Type safety | 10 | `any` / type errors | Compiles clean | Types document intent |
| Lint / format | 5 | Lint errors | Clean | Follows project conventions |
| Minimal diff | 10 | Rewrites unrelated code | Some extra changes | Touches only what's needed |
| Security | 15 | Introduces vulnerability | No obvious issues | Validates inputs, safe defaults, principle of least privilege |
| Dependencies | 5 | Adds unnecessary deps | Uses existing deps | Zero new deps |
| Code reuse | 5 | Duplicates existing helpers | Uses some existing code | Maximizes reuse |
| Conventions | 5 | Ignores project patterns | Mostly follows patterns | Indistinguishable from existing code |

**Security scoring (detail):**
- Auth/RLS work: Does it enforce authorization on every path? Are there bypasses?
- User input: Is it validated/sanitized at the boundary?
- Secrets: Are they in env vars, never in client bundles or committed code?
- SQL/queries: Parameterized? RLS enabled?
- CSRF: POST-only for mutations? No GET side effects?

---

## §7 — Project context detection

Before spawning agents, detect the project's stack and conventions:

1. **Read project signals:**
   - `package.json` → framework, dependencies, scripts
   - `tsconfig.json` / `pyproject.toml` / `Cargo.toml` → language and config
   - `CLAUDE.md` → project-specific instructions
   - `.claude/settings.json` → permissions, hooks
   - Recent git log (last 10 commits) → commit style, active patterns

2. **Set context for agents:**
   - Framework: Next.js App Router / Express / Flask / etc.
   - Styling: Tailwind / CSS modules / styled-components
   - Data: Supabase / Prisma / raw SQL / REST
   - Testing: Jest / Vitest / Pytest / none
   - Deployment: Vercel / Render / Docker

3. **Pass to each agent:** "This is a {framework} project using {styling} and {data layer}. Follow the patterns in the existing codebase."

---

## §8 — Learning accumulation

### Automatic (after every run):
If the winning draft reveals a pattern not in §A, append it:
- "What went wrong in lower-scoring drafts?" → add as anti-pattern
- "What made the winner score highest?" → add as positive pattern
- Only append if the pattern is generalizable (not project-specific)

### Manual:
User says "code-builder learned: {insight}" → append to §A.

### Pruning:
If §A exceeds 30 entries, during the next sync:
- Remove entries that duplicate each other
- Remove entries that are now obvious (incorporated into the rubric)
- Keep entries that prevent recurring mistakes

---

## §9 — Post-merge tracking

After a code-builder run is merged (detected via git log or PR merge):
- Note in the run log: `**Merged:** {date}`
- If a follow-up fix is needed within 48 hours on the same area:
  - Note: `**Post-merge fix needed:** {date} — {what broke}`
  - Add the failure mode to §A if it's generalizable
  - Reduce confidence in the draft bias that introduced the issue

---

## §A — Learned patterns

_Patterns discovered from actual runs. Auto-appended by §8._

1. Never hardcode secrets in client-side JS — use env vars with `NEXT_PUBLIC_` prefix only for public values
2. Resolve merge conflicts by running the test suite, not by eyeballing diffs
3. Guard nullable API responses before destructuring — `data?.field` not `data.field`
4. Validate environment variables at startup, not at first use
5. React Rules of Hooks: never call hooks conditionally or in loops
6. `useEffect` cleanup: always return a cleanup function for subscriptions, timers, event listeners
7. Floating UI: position calculation must account for scroll offset and viewport bounds
8. Supabase RLS: always test both the positive case (authorized user sees data) AND negative case (unauthorized user is denied)
9. Security-definer functions must set `search_path` to prevent path injection
10. POST-only for mutations — never use GET for state changes (CSRF)

## §B — Anti-patterns

_Things that caused low scores in past runs._

1. Adding `// removed` comments for deleted code — just delete it
2. Wrapping simple operations in unnecessary abstractions
3. Re-exporting unused types for "backwards compatibility"
4. Catching errors silently (`catch {}`) instead of logging or re-throwing
5. Using `any` to "fix" type errors instead of understanding the type
