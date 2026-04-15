# Review notes — `startup-hook-skill` (session-start-hook)

Review of the skill at `~/.claude/skills/session-start-hook/SKILL.md`.

## Scope caveat

Only the current session was available in `~/.claude/projects/` at review time,
so this is a **content audit** of the skill itself — not a mining of past
deployment transcripts. If deployment-side logs become available later
(Claude Code on the web admin, centralized logging), re-run this review
against real user turns and tool traces.

## Bugs fixed

1. **Contradiction between design principle and template.** Step 2 said
   "don't use async mode in the first iteration", but the Step 3 template
   literally started with `echo '{"async": true, ...}'`. Rewrote the template
   to be sync-first; moved the async example to the "Hook Basics" section
   so it's reference material, not the default path.
2. **Typo.** `Syncronous` → `Synchronous` in the wrap-up format.
3. **stdout/stderr confusion.** The old version used `echo` inside scripts
   freely. In sync mode, stdout is parsed for JSON directives, so log output
   must go to stderr. Added an explicit "stdout vs stderr" subsection and
   redirected all log output in the template to `>&2`.

## Blindspots filled

4. **Dependency detection was Node/Python-centric.** Added JVM (maven,
   gradle), .NET, PHP (composer), Elixir (mix), Dart/Flutter (pubspec),
   Deno, Bun, and modern Python (uv, rye, hatch).
5. **No monorepo awareness.** Added pnpm/yarn workspaces, turborepo, nx,
   lerna, Cargo `[workspace]`, `go.work`.
6. **Tool-version files were ignored.** Added `.nvmrc`, `.python-version`,
   `.ruby-version`, `.tool-versions` (asdf/mise), `mise.toml`,
   `rust-toolchain.toml` — these routinely determine whether install works.
7. **CI/Make files weren't mined.** `.github/workflows/*`, `Makefile`,
   `justfile`, `Taskfile.yml`, `package.json` scripts, and `pyproject.toml`
   `[tool.*]` sections typically contain the canonical install/lint/test
   commands. Added a "prefer these over guessing" list.
8. **No pre-check of existing `.claude/` state.** Added a dedicated step
   (new Step 2) covering: reading an existing `session-start.sh`,
   merging into an existing `SessionStart` array instead of overwriting,
   leaving `.claude/settings.local.json` alone.
9. **Lint/test discovery was hand-waved.** Now lists concrete places to
   look for the canonical command before running it.
10. **Validation was weak.** Old step 5 said "verify dependencies are
    installed" without saying how. New step 6 requires checking all three:
    exit code is 0, install artifacts exist on disk, and `$CLAUDE_ENV_FILE`
    contents are correct. Steps 7 and 8 say to run lint/test on **one**
    file rather than the whole suite.
11. **`CLAUDE_ENV_FILE` was a footnote.** Promoted to a first-class pattern
    with a PATH-extension example in the template.
12. **Idempotency was asserted, not demonstrated.** Added concrete guards
    (`[ -f dist/index.js ] || ...`, `command -v ruff >/dev/null || ...`).
13. **Async trade-offs were thin.** Replaced "may cause a race condition"
    with a decision rule: sync unless install is demonstrably slow (>60s)
    or the user opts in.
14. **No "don't put X in the hook" guidance.** Added an explicit list:
    codegen, docker pulls, DB migrations, large fixture downloads don't
    belong in SessionStart.
15. **Safety posture underspecified.** `set -euo pipefail` is now called
    out as mandatory; non-interactive env hints (`CI=true`,
    `DEBIAN_FRONTEND=noninteractive`) added.

## Things I considered but did NOT change

- **`npm install` vs `npm ci`.** The original preference for `install` is
  defensible (cache-friendly, tolerant of partial container state), so kept
  it. Added `--prefer-offline --no-audit --no-fund` to the template to make
  the performance intent explicit.
- **Emoji in wrap-up (`✅`/`‼️`).** The global assistant guidance avoids
  emoji, but skills get to define their own output format and this one is
  narrow (six characters total), so kept it. Revisit if it reads as noisy
  in real output.
- **Splitting the skill into multiple files.** Considered extracting
  stack-specific templates (Node vs Python vs Rust) into sibling files,
  but at current length a single SKILL.md is easier to scan. Re-evaluate
  if more stacks get deep coverage.

## Follow-ups worth doing with real data

When deployment transcripts become available, look specifically for:

- How often async mode ends up being needed (are users hitting the >60s
  threshold?). If common, promote async to first-class with a decision
  matrix.
- How often the hook has to be re-edited after the first commit. Patterns
  there would surface missing defaults.
- Which ecosystems are most requested. The skill covers many now, but the
  examples are still Node-heavy.
- Whether users ask for local-machine hooks (non-remote) and the skill has
  to be re-read against that ask.
