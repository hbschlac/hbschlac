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

The hook runs in background while the session starts. Using async mode reduces latency, but introduces a race condition where the agent loop might depend on something that is being done in the startup hook before it completed.

### Environment Variables

Available environment variables:
- `$CLAUDE_PROJECT_DIR` - Repository root path
- `$CLAUDE_ENV_FILE` - Path to write environment variables
- `$CLAUDE_CODE_REMOTE` - If running in a remote environment (i.e. Claude code on the web)

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

Make a todo list for all the tasks in this workflow and work on them one after another

### 1. Analyze Dependencies

Find dependency manifests and analyze them. Examples:
- `package.json` / `package-lock.json` → npm
- `pyproject.toml` / `requirements.txt` → pip/Poetry
- `Cargo.toml` → cargo
- `go.mod` → go
- `Gemfile` → bundler

Additionally, read though any documentation (i.e. README.md or similar) to see if you can get additional context on how the environment setup works

### 2. Detect Project Architecture

Before designing the hook, understand the project shape. Check for:

**Monorepo / multi-directory layouts:**
- Separate `frontend/` and `backend/` (or `src/` and `api/`) directories with their own `package.json`
- Workspace configs (`workspaces` in root `package.json`, `pnpm-workspace.yaml`, `turbo.json`)
- Multiple dependency manifests at different paths

**Vercel configuration:**
- `vercel.json` — check for multiple `builds` entries (e.g. Express API + Next.js frontend sharing one deploy)
- Separate serverless entry points (commonly `api/index.js` or `api/index.ts`) that construct their own Express app distinct from `src/app.js`
- Any `rewrites` or `routes` that map paths to different builders

**Existing Claude Code config:**
- `.claude/settings.json` — check for existing hooks to avoid overwriting
- `CLAUDE.md` — check if project documentation already exists

Record what you find. The hook must install dependencies for ALL entry points, not just the root.

### 3. Design Hook

Create a script that installs dependencies.

**Key principles:**
- Don't use async mode in the first iteration. Only switch to it if the user asks for it
- Write the hook only for the web unless user asks otherwise (see $CLAUDE_CODE_REMOTE)
- The container state gets cached after the hook completes, prefer dependency install methods that take advantage of that (i.e. prefer npm install over npm ci)
- Be idempotent (safe to run multiple times)
- Non-interactive (no user input)

**For monorepos / multi-directory projects:**
- Install dependencies in each directory that has its own manifest (e.g. `cd frontend && npm install && cd ../backend && npm install`)
- If using workspaces, a single root install is usually sufficient

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

echo '{"async": true, "asyncTimeout": 300000}'
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

If `.claude/settings.json` exists, merge the hooks configuration.

### 6. Validate Hook

Run the hook script directly:

```bash
CLAUDE_CODE_REMOTE=true ./.claude/hooks/session-start.sh
```

IMPORTANT: Verify dependencies are installed and script completes successfully.

### 7. Validate Linter

IMPORTANT: Figure out what the right command is to run the linters and run it for an example file. No need to lint the whole project. If there are any issues, update the startup script accordingly and re-test.

### 8. Validate Test

IMPORTANT: Figure out what the right command is to run the tests and run it for one test. No need to run the whole test suite. If there are any issues, update the startup script accordingly and re-test.

### 9. Validate Build

IMPORTANT: Run the project's build command to catch compilation and bundler errors that would fail on deploy. Common commands:
- `npm run build` / `next build` (Next.js)
- `npx tsc --noEmit` (TypeScript type-check only)
- `cargo build` (Rust)
- `go build ./...` (Go)

If the project has a `vercel.json` with multiple builders or a separate serverless entry point (e.g. `api/index.js`), verify that entry point also resolves its imports correctly — a common failure mode is middleware or config registered in the dev server entry (`src/app.js`) but missing from the serverless entry.

If the build fails, fix the startup script (missing dependency, wrong Node version, etc.) and re-test.

### 10. Bootstrap CLAUDE.md

If the project does not already have a `CLAUDE.md` at the repo root, create one. This ensures future Claude Code sessions (and other contributors) have immediate context. Use the `/init` skill to generate it.

Minimum useful content to verify is in the CLAUDE.md:
- **Build command** (e.g. `npm run build`)
- **Test command** (e.g. `npm test` or `npm test -- --run` for vitest)
- **Lint command** (e.g. `npm run lint`)
- **Project architecture** (monorepo layout, key entry points, frontend vs backend)
- **Deploy target** (e.g. Vercel, with any relevant `vercel.json` notes)

If CLAUDE.md already exists, scan it to make sure build/test/lint commands are documented. If they're missing, add them.

### 11. Commit and push

Make a commit and push it to the remote branch

## Wrap up

We're all done. In your last message to the user, Provide a detailed summary to the user with the format below:

* Summary of the changes made
* Project architecture detected (single project / monorepo / Vercel multi-builder / etc.)
* Validation results
  1. ✅/‼️ Session hook execution (include details if it failed)
  2. ✅/‼️ linter execution (include details if it failed)
  3. ✅/‼️ test execution (include details if it failed)
  4. ✅/‼️ build execution (include details if it failed)
  5. ✅/‼️ CLAUDE.md present and has build/test/lint commands
* Hook execution mode: Syncronous
  * inform user that hook is running syncronous and the below trade-offs. Let them know that we can change it to async if they prefer faster session startup.
    * Pros: Guarantees dependencies are installed before your session starts, preventing race conditions where Claude might try to run tests or linters before they're ready
    * Cons: Your remote session will only start once the session start hook is completed
* inform user that once they merge the session start hook into their repo's default branch, all future sessions will use it.
