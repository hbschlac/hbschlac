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

### Async Mode
```bash
#!/bin/bash
set -euo pipefail

echo '{"async": true, "asyncTimeout": 300000}'

npm install
```

The hook runs in background while the session starts. Using async mode reduces latency but introduces a race condition: the agent loop might try to run tests or linters before the hook completes.

**Mitigation for async race conditions:**
- Write a sentinel file at the end of the hook: `touch .claude-deps-ready`
- In CLAUDE.md, note: "If tests fail with 'module not found', wait for startup hook to complete (check for `.claude-deps-ready`)"
- Alternatively, stay synchronous (the default) — it's slower but guarantees readiness.

### Environment Variables

Available environment variables:
- `$CLAUDE_PROJECT_DIR` - Repository root path
- `$CLAUDE_ENV_FILE` - Path to write environment variables
- `$CLAUDE_CODE_REMOTE` - If running in a remote environment (i.e. Claude Code on the web)

Use `$CLAUDE_ENV_FILE` to persist variables for the session:
```bash
echo 'export PYTHONPATH="."' >> "$CLAUDE_ENV_FILE"
```

Use `$CLAUDE_CODE_REMOTE` to only run a script in a remote env:
```bash
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi
```

## Workflow

Make a todo list for all the tasks in this workflow and work on them one after another.

### 1. Analyze Dependencies

Find dependency manifests and analyze them:

**JavaScript/TypeScript:**
- `package.json` / `package-lock.json` → npm
- `pnpm-lock.yaml` → pnpm
- `yarn.lock` → yarn
- `bun.lockb` → bun

**Python:**
- `pyproject.toml` → pip/Poetry/PDM (check `[build-system]` for which)
- `requirements.txt` / `requirements-dev.txt` → pip
- `Pipfile` / `Pipfile.lock` → pipenv
- `setup.py` / `setup.cfg` → pip

**Other languages:**
- `Cargo.toml` → cargo (Rust)
- `go.mod` → go (Go)
- `Gemfile` → bundler (Ruby)
- `build.gradle` / `pom.xml` → gradle/maven (Java/Kotlin)
- `mix.exs` → mix (Elixir)

**Tool version files:**
- `.nvmrc` / `.node-version` → Node version constraint
- `.python-version` → Python version constraint
- `.tool-versions` → asdf version manager
- `.ruby-version` → Ruby version constraint

Additionally, read through any documentation (README.md, CONTRIBUTING.md, docs/) to get context on how the environment setup works.

### 2. Detect Project Architecture

Before designing the hook, understand the project shape. Check for:

**Monorepo / multi-directory layouts:**
- Separate `frontend/` and `backend/` (or `src/` and `api/`) directories with their own `package.json`
- Workspace configs (`workspaces` in root `package.json`, `pnpm-workspace.yaml`, `turbo.json`, `nx.json`)
- Multiple dependency manifests at different paths

**Vercel configuration:**
- `vercel.json` — check for multiple `builds` entries (e.g. Express API + Next.js frontend sharing one deploy)
- Separate serverless entry points (commonly `api/index.js` or `api/index.ts`) that construct their own Express app distinct from `src/app.js`
- Any `rewrites` or `routes` that map paths to different builders

**Existing Claude Code config:**
- `.claude/settings.json` — check for existing hooks to avoid overwriting
- `CLAUDE.md` — check if project documentation already exists

**CI configuration (mine for setup clues):**
- `.github/workflows/*.yml` — CI often documents exact setup steps, system dependencies, and env vars
- `Dockerfile` / `docker-compose.yml` — system-level deps and setup order
- `.circleci/config.yml`, `Jenkinsfile`, etc.

Record what you find. The hook must install dependencies for ALL entry points, not just the root.

### 3. Design Hook

Create a script that installs dependencies.

**Key principles:**
- Don't use async mode in the first iteration. Only switch to it if the user asks for it.
- Write the hook only for the web unless user asks otherwise (see `$CLAUDE_CODE_REMOTE`).
- The container state gets cached after the hook completes, prefer dependency install methods that take advantage of that (i.e. prefer `npm install` over `npm ci`).
- Be idempotent (safe to run multiple times).
- Non-interactive (no user input).

**For monorepos / multi-directory projects:**
- Install dependencies in each directory that has its own manifest (e.g. `cd frontend && npm install && cd ../backend && npm install`)
- If using workspaces, a single root install is usually sufficient

**For Python projects:**
- Create a virtual environment if one doesn't exist: `python3 -m venv .venv`
- Activate it and persist for the session: `echo 'export PATH=".venv/bin:$PATH"' >> "$CLAUDE_ENV_FILE"`
- Install: `pip install -r requirements.txt` or `pip install -e .` or `poetry install`
- If `pyproject.toml` has `[project.optional-dependencies]`, install dev deps: `pip install -e ".[dev]"`

**For mixed-language projects:**
- Install each language's dependencies in sequence
- Set up PATH/env vars for each via `$CLAUDE_ENV_FILE`

**Retry logic for web environments:**
Network in web containers can be flaky. Wrap install commands with a retry:
```bash
install_with_retry() {
  local max_attempts=3
  local attempt=1
  while [ $attempt -le $max_attempts ]; do
    if "$@"; then
      return 0
    fi
    echo "Attempt $attempt failed. Retrying in ${attempt}s..." >&2
    sleep "$attempt"
    attempt=$((attempt + 1))
  done
  echo "All $max_attempts attempts failed for: $*" >&2
  return 1
}

install_with_retry npm install
```

### 4. Create Hook File

```bash
mkdir -p .claude/hooks
cat > .claude/hooks/session-start.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Only run in remote environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Install dependencies here
EOF

chmod +x .claude/hooks/session-start.sh
```

### 5. Register in Settings

Add to `.claude/settings.json` (create if doesn't exist):
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

If `.claude/settings.json` exists, merge the hooks configuration — don't overwrite existing settings (permissions, allowed tools, etc.).

### 6. Validate Hook

Run the hook script directly:

```bash
CLAUDE_CODE_REMOTE=true CLAUDE_ENV_FILE=/tmp/test-env-file ./.claude/hooks/session-start.sh
```

IMPORTANT: Verify dependencies are installed and script completes successfully.
If `$CLAUDE_ENV_FILE` was written to, source it and verify the variables are set:
```bash
source /tmp/test-env-file
echo $PATH  # should include .venv/bin for Python projects
```

### 7. Validate Linter

IMPORTANT: Figure out what the right command is to run the linters and run it for an example file. No need to lint the whole project. If there are any issues, update the startup script accordingly and re-test.

Common linter commands:
- `npx eslint src/index.ts` (JS/TS)
- `npx tsc --noEmit` (TypeScript type-check)
- `ruff check src/main.py` or `flake8 src/main.py` (Python)
- `cargo clippy` (Rust)
- `go vet ./...` (Go)

### 8. Validate Test

IMPORTANT: Figure out what the right command is to run the tests and run it for one test. No need to run the whole test suite. If there are any issues, update the startup script accordingly and re-test.

Common test commands:
- `npx jest --testPathPattern=example` or `npx vitest run src/example.test.ts` (JS/TS)
- `pytest tests/test_example.py -x` (Python)
- `cargo test -- --test-threads=1` (Rust)
- `go test ./pkg/example/...` (Go)

### 9. Validate Build

IMPORTANT: Run the project's build command to catch compilation and bundler errors that would fail on deploy. Common commands:
- `npm run build` / `next build` (Next.js)
- `npx tsc --noEmit` (TypeScript type-check only)
- `cargo build` (Rust)
- `go build ./...` (Go)
- `python -m py_compile src/main.py` (Python — basic syntax check)

If the project has a `vercel.json` with multiple builders or a separate serverless entry point (e.g. `api/index.js`), verify that entry point also resolves its imports correctly — a common failure mode is middleware or config registered in the dev server entry (`src/app.js`) but missing from the serverless entry.

If the build fails, fix the startup script (missing dependency, wrong Node version, etc.) and re-test.

### 10. Bootstrap CLAUDE.md

If the project does not already have a `CLAUDE.md` at the repo root, create one. Use the `/init` skill to generate it.

Minimum useful content to verify is in the CLAUDE.md:
- **Build command** (e.g. `npm run build`)
- **Test command** (e.g. `npm test` or `npm test -- --run` for vitest)
- **Lint command** (e.g. `npm run lint`)
- **Project architecture** (monorepo layout, key entry points, frontend vs backend)
- **Deploy target** (e.g. Vercel, with any relevant `vercel.json` notes)

If CLAUDE.md already exists, scan it to make sure build/test/lint commands are documented. If they're missing, add them.

### 11. Commit and push

Make a commit and push it to the remote branch.

## Wrap up

We're all done. In your last message to the user, provide a detailed summary with the format below:

* Summary of the changes made
* Project architecture detected (single project / monorepo / Vercel multi-builder / mixed-language / etc.)
* Dependencies installed (list package managers and counts)
* Validation results
  1. Hook execution
  2. Linter execution (include details if it failed)
  3. Test execution (include details if it failed)
  4. Build execution (include details if it failed)
  5. CLAUDE.md present and has build/test/lint commands
* Hook execution mode: Synchronous
  * Inform user that hook is running synchronous and the below trade-offs. Let them know that we can change it to async if they prefer faster session startup.
    * Pros: Guarantees dependencies are installed before your session starts, preventing race conditions where Claude might try to run tests or linters before they're ready
    * Cons: Your remote session will only start once the session start hook is completed
* Inform user that once they merge the session start hook into their repo's default branch, all future sessions will use it.

---

## Changelog

- **2026-05-24 — v2: improvements from deployment history analysis**
  - Added: Python project support (venv, pip, poetry, pyproject.toml)
  - Added: async race condition mitigation (sentinel file pattern)
  - Added: tool version file detection (.nvmrc, .python-version, .tool-versions)
  - Added: CI config mining for setup clues
  - Added: pnpm, yarn, bun detection
  - Added: mixed-language project support
  - Added: $CLAUDE_ENV_FILE validation step
  - Added: common linter/test/build commands per language
  - Fixed: settings.json merge note (don't overwrite existing settings)
  - Fixed: $CLAUDE_CODE_REMOTE guard in hook template
