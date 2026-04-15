---
name: startup-hook-skill
description: Creating and developing startup hooks for Claude Code on the web. Use when the user wants to set up a repository for Claude Code on the web, create a SessionStart hook to ensure their project can run tests and linters during web sessions.
---

# Startup Hook Skill for Claude Code on the web

Create SessionStart hooks that install dependencies so tests and linters work in Claude Code on the web sessions.

## Hook Basics

### Input (via stdin)
```json
{
  "session_id": "abc123",
  "source": "startup|resume|clear|compact",
  "transcript_path": "/path/to/transcript.jsonl",
  "permission_mode": "default",
  "hook_event_name": "SessionStart",
  "cwd": "/workspace/repo"
}
```

### stdout vs stderr

In sync mode (default), the hook's **stdout is parsed for JSON control directives**. Write human-readable logs to **stderr** so they don't get interpreted.

```bash
echo "Installing dependencies..." >&2   # log
npm install >&2                          # log install output too
```

### Async mode

```bash
#!/bin/bash
set -euo pipefail

echo '{"async": true, "asyncTimeout": 300000}'  # stdout: directive

npm install >&2
```

Async mode lets the session start immediately while install continues in the background. **Trade-off**: if the user's first turn needs installed tools (running tests, executing code, reading files that depend on generated artifacts), they may hit a race. Rule of thumb: sync unless the user explicitly opts in.

### Environment variables available to the hook

- `$CLAUDE_PROJECT_DIR` — repository root path
- `$CLAUDE_ENV_FILE` — path to write shell exports persisted to the session
- `$CLAUDE_CODE_REMOTE` — `"true"` if running in Claude Code on the web

Persist variables for the session by appending to `$CLAUDE_ENV_FILE`:
```bash
echo 'export PYTHONPATH="."' >> "$CLAUDE_ENV_FILE"
echo 'export PATH="$CLAUDE_PROJECT_DIR/node_modules/.bin:$PATH"' >> "$CLAUDE_ENV_FILE"
```

Gate remote-only behavior:
```bash
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi
```

## Workflow

Make a todo list for all the tasks in this workflow and work on them one after another.

### 1. Analyze the project

Find every signal that tells you how to install, lint, and test. **Check all of these, not just the README.**

**Dependency manifests (primary):**
- Node: `package.json` + (`package-lock.json` → npm, `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, `bun.lockb` → bun)
- Python: `pyproject.toml` (poetry/hatch/uv/rye), `requirements*.txt` (pip), `Pipfile` (pipenv), `environment.yml` (conda)
- Rust: `Cargo.toml`
- Go: `go.mod`
- Ruby: `Gemfile`
- JVM: `pom.xml` (maven), `build.gradle[.kts]` (gradle)
- .NET: `*.csproj`, `*.sln`
- PHP: `composer.json`
- Elixir: `mix.exs`
- Dart/Flutter: `pubspec.yaml`
- Deno: `deno.json[c]`

**Monorepo signals:** `pnpm-workspace.yaml`, `turbo.json`, `nx.json`, `lerna.json`, `workspaces` in `package.json`, `Cargo.toml` `[workspace]`, `go.work`. If present, install at the repo root with the workspace-aware command.

**Tool-version files (run before install):** `.nvmrc`, `.node-version`, `.python-version`, `.ruby-version`, `.tool-versions` (asdf/mise), `mise.toml`, `rust-toolchain[.toml]`. If the container already has the right version, skip; otherwise document the requirement — don't silently install a different version.

**Canonical commands — prefer these over guessing:**
- `.github/workflows/*.yml`, `.gitlab-ci.yml`, `.circleci/config.yml` — CI usually has the real install/lint/test incantations
- `Makefile`, `justfile`, `Taskfile.yml` — target names like `install`, `lint`, `test`
- `package.json` `scripts` — look for `test`, `lint`, `typecheck`, `check`
- `pyproject.toml` `[tool.*]` sections — pytest, ruff, mypy configs
- README / CONTRIBUTING.md

### 2. Check existing `.claude/` state

```bash
ls -la .claude/ 2>/dev/null
```

- If `.claude/hooks/session-start.sh` already exists, read it. Decide: extend it, or replace it after confirming with the user.
- If `.claude/settings.json` already has a `SessionStart` entry, merge into the existing array — don't overwrite.
- If the project uses `.claude/settings.local.json` (user-local), leave it alone; edit the checked-in `.claude/settings.json`.

### 3. Design the hook

**Principles:**
- **Sync by default.** Only switch to async if the user asks or install is demonstrably slow (>60s).
- **Remote-only by default.** Local devs usually have their own setup; don't interfere. Gate with `$CLAUDE_CODE_REMOTE`.
- **Leverage container caching.** The container state is cached after the hook completes. `npm install` / `pip install -r` are fine because they're fast on warm caches. Use `--prefer-offline` / `--cache` flags where available.
- **Idempotent.** Safe to run many times; use guards for expensive non-install steps.
- **Non-interactive.** No prompts. Pin `CI=true`, `DEBIAN_FRONTEND=noninteractive`, `npm_config_yes=true` as needed.
- **Logs to stderr.** Keep stdout clean for JSON directives.
- **Fail loudly.** `set -euo pipefail` is mandatory.

**What does NOT belong in the hook:** codegen that takes minutes, docker image pulls, DB migrations, fetching large fixtures. Move those to explicit user-triggered scripts.

### 4. Create the hook file

Template (sync, remote-only, Node example — adapt for the stack you found):

```bash
mkdir -p .claude/hooks
cat > .claude/hooks/session-start.sh <<'EOF'
#!/bin/bash
set -euo pipefail

# Remote-only
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

echo "[session-start] installing dependencies" >&2
npm install --prefer-offline --no-audit --no-fund >&2

# Persist PATH so node_modules/.bin is available in shells
echo 'export PATH="'"$CLAUDE_PROJECT_DIR"'/node_modules/.bin:$PATH"' >> "$CLAUDE_ENV_FILE"

echo "[session-start] done" >&2
EOF

chmod +x .claude/hooks/session-start.sh
```

**Idempotency examples for non-install work:**
```bash
# Skip if already built
[ -f dist/index.js ] || npm run build >&2

# Skip tool install if on PATH
command -v ruff >/dev/null || pip install ruff >&2
```

### 5. Register in settings

Edit `.claude/settings.json`. If the file or hooks key is absent, create them. If a `SessionStart` array already exists, **append** to the array — do not replace.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh"
          }
        ]
      }
    ]
  }
}
```

If there are multiple matchers, keep them as separate entries in the outer array.

### 6. Validate the hook

Run the script with the same env the hook runtime provides:

```bash
CLAUDE_CODE_REMOTE=true \
CLAUDE_PROJECT_DIR="$PWD" \
CLAUDE_ENV_FILE="$(mktemp)" \
  ./.claude/hooks/session-start.sh
```

Check all three:
1. Exit code is 0 (`echo $?`).
2. Install artifacts exist (`node_modules/`, `.venv/`, `target/debug/`, etc. — stack-specific).
3. Shell exports in `$CLAUDE_ENV_FILE` look correct.

If it fails, read the stderr output — don't guess.

### 7. Validate the linter

Find the lint command from step 1 (package.json script, `ruff`/`eslint` on PATH, `make lint`, CI config). Run it on **one file** — not the whole repo:

```bash
npx eslint path/to/one/file.js
# or
ruff check path/to/one/file.py
```

Exit code 0 means the tool is installed and usable. If it fails because a dep is missing, update the hook and re-run step 6.

### 8. Validate the tests

Find the test command the same way. Run **one test** — not the whole suite:

```bash
npx jest path/to/one.test.js
# or
pytest path/to/one_test.py::test_name -q
```

Same rule: green means the hook set things up correctly.

### 9. Commit and push

Commit `.claude/hooks/session-start.sh` and `.claude/settings.json`. Do not commit `.claude/settings.local.json` (user-local).

## Wrap up

In your final message to the user, use this format:

* **Summary** of the changes made
* **Validation results**
  1. ✅/‼️ Hook execution (include stderr excerpt if it failed)
  2. ✅/‼️ Linter execution (include the command run and the file you ran it on)
  3. ✅/‼️ Test execution (include the command run and the test you ran)
* **Execution mode: Synchronous** (default)
  * Pros: guarantees dependencies are installed before the session starts — no race conditions when Claude immediately runs tests or linters.
  * Cons: the remote session won't start until the hook finishes. Offer to switch to async if install is slow.
* **Heads up**: once merged to the default branch, all future web sessions on this repo use the hook. Local sessions are unaffected (gated by `CLAUDE_CODE_REMOTE`).
