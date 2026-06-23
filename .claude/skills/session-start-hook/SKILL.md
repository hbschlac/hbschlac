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

Runs in background while the session starts. Race condition risk: the agent might
try tests before deps install. Mitigation: write a sentinel file at the end
(`touch .claude-deps-ready`) or stay synchronous (slower but guaranteed).

### Environment Variables

- `$CLAUDE_PROJECT_DIR` — Repository root path
- `$CLAUDE_ENV_FILE` — Path to write environment variables for the session
- `$CLAUDE_CODE_REMOTE` — Set to "true" in remote environments

## Workflow

### 1. Analyze Dependencies

Find dependency manifests:

**JavaScript/TypeScript:** `package.json` (npm), `pnpm-lock.yaml` (pnpm), `yarn.lock` (yarn), `bun.lockb` (bun)

**Python:** `pyproject.toml` (pip/Poetry/PDM), `requirements.txt` (pip), `Pipfile` (pipenv)

**Other:** `Cargo.toml` (Rust), `go.mod` (Go), `Gemfile` (Ruby), `build.gradle`/`pom.xml` (Java)

**Tool versions:** `.nvmrc`, `.python-version`, `.tool-versions`, `.ruby-version`

Read documentation (README.md, CONTRIBUTING.md) for setup context.

### 2. Detect Project Architecture

Check for:

- **Monorepo:** separate `frontend/`+`backend/` with own `package.json`, workspace configs
- **Vercel:** `vercel.json` with multiple builders, separate serverless entry points
- **Existing Claude config:** `.claude/settings.json` (don't overwrite), `CLAUDE.md`
- **CI config:** `.github/workflows/*.yml`, `Dockerfile` — mine for setup clues

The hook must install deps for ALL entry points, not just root.

- **Monorepo workspaces:** Check for `pnpm-workspace.yaml`, `package.json` workspaces field, `turbo.json`, `nx.json`. Install at root level — workspace-aware package managers handle sub-packages.
- **Database migrations:** If `prisma/`, `drizzle.config.*`, or `migrations/` exist, add `npx prisma generate` or equivalent to the hook. Don't run `migrate deploy` in hooks — that's destructive.
- **Python projects with system deps:** Some Python packages need system-level libraries. Check for `apt-get` instructions in README. Add to hook: `sudo apt-get update && sudo apt-get install -y {deps}` before pip install.

### 3. Design Hook

Key principles:
- Synchronous by default (switch to async only if user asks)
- Web-only unless user asks otherwise (`$CLAUDE_CODE_REMOTE` guard)
- Prefer `npm install` over `npm ci` (container caches state after hook)
- Idempotent, non-interactive

**Retry logic for web environments:**
```bash
install_with_retry() {
  local max_attempts=3
  local attempt=1
  while [ $attempt -le $max_attempts ]; do
    if "$@"; then return 0; fi
    echo "Attempt $attempt failed. Retrying in ${attempt}s..." >&2
    sleep "$attempt"
    attempt=$((attempt + 1))
  done
  echo "All $max_attempts attempts failed for: $*" >&2
  return 1
}
```

**Python projects:**
```bash
python3 -m venv .venv
echo 'export PATH=".venv/bin:$PATH"' >> "$CLAUDE_ENV_FILE"
source .venv/bin/activate
pip install -r requirements.txt  # or pip install -e ".[dev]"
```

### 4. Create Hook File

```bash
mkdir -p .claude/hooks
cat > .claude/hooks/session-start.sh << 'EOF'
#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Install dependencies here
EOF

chmod +x .claude/hooks/session-start.sh
```

### 5. Register in Settings

Add to `.claude/settings.json` (merge with existing, don't overwrite):
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

### 6. Validate Hook

```bash
CLAUDE_CODE_REMOTE=true CLAUDE_ENV_FILE=/tmp/test-env-file ./.claude/hooks/session-start.sh
```

If `$CLAUDE_ENV_FILE` was written to: `source /tmp/test-env-file` and verify.

### 6B. Debug Hook Failures

When a hook fails silently or tests/linters don't work after session start:

| Symptom | Check | Fix |
|---|---|---|
| Hook didn't run | `cat .claude/settings.json` — is `hooks.SessionStart` registered? | Add the hook registration. Use `$CLAUDE_PROJECT_DIR` prefix. |
| Hook ran but deps missing | Run the hook script manually: `bash -x .claude/hooks/session-start.sh` | The `-x` flag shows each line as it executes. Look for silent failures. |
| `npm install` fails in hook | Check if `package-lock.json` exists. Network issues in web sessions? | Try `npm install --prefer-offline --no-audit`. Check network policy. |
| Python venv not activated | `$CLAUDE_ENV_FILE` must be written to — `echo 'export PATH=...' >> "$CLAUDE_ENV_FILE"` | Verify the env file path is correct and the file is sourced by the session. |
| Hook runs on laptop (unwanted) | Missing `$CLAUDE_CODE_REMOTE` guard | Add `[ "${CLAUDE_CODE_REMOTE:-}" != "true" ] && exit 0` as first line. |
| Hook timeout | Hook takes >5min (default async timeout) | Set `"asyncTimeout": 300000` or optimize the install step. Use `npm ci` if lockfile exists. |

**Cross-reference:** When bootstrapping a new repo, `project-bootstrap` (Step 4B) generates the hook alongside CLAUDE.md. Use that for new repos instead of creating from scratch.

### 7. Validate Linter

Run the linter on a single file. Common commands:
- `npx eslint src/index.ts` / `npx tsc --noEmit` (JS/TS)
- `ruff check src/main.py` / `flake8 src/main.py` (Python)
- `cargo clippy` (Rust) / `go vet ./...` (Go)

### 8. Validate Tests

Run a single test. Common commands:
- `npx jest --testPathPattern=example` / `npx vitest run src/example.test.ts`
- `pytest tests/test_example.py -x`
- `cargo test -- --test-threads=1` / `go test ./pkg/example/...`

### 9. Validate Build

Run the build command:
- `npm run build` / `next build` / `npx tsc --noEmit`
- `cargo build` / `go build ./...`

If Vercel multi-builder: verify the serverless entry point resolves its imports.

### 10. Bootstrap CLAUDE.md

If no `CLAUDE.md` exists, create one with `/init`. Verify it includes:
build command, test command, lint command, project architecture, deploy target.

### 11. Commit and push

## Wrap up

Provide summary with:
- Changes made
- Project architecture detected
- Dependencies installed
- Validation results (hook, linter, tests, build, CLAUDE.md)
- Hook execution mode (synchronous) with trade-offs
- Note: merge to default branch for all future sessions to use it

---
