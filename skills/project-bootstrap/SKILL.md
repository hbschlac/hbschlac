---
name: project-bootstrap
description: >
  Auto-generates CLAUDE.md and .claude/ config for any repo by analyzing its
  actual structure, dependencies, and conventions. Solves the problem where
  65K-LOC projects (muse-shopping) and actively-developed apps
  (interior-designer-portfolio) have zero Claude Code configuration. Trigger
  phrases: "bootstrap this project", "set up Claude for this repo",
  "generate CLAUDE.md", "init claude config", "add claude config",
  "this repo has no CLAUDE.md", "project-bootstrap", "configure claude
  for this project". Also activates implicitly when entering a repo with
  no CLAUDE.md for the first time in a session.
---

# project-bootstrap

Generates a proper `CLAUDE.md` and `.claude/` config for any repo by analyzing what's actually there — not guessing from templates. Solves the config debt problem: most repos have zero Claude Code configuration despite heavy Claude usage.

**Not for:** creating new projects from scratch (use `create-next-app`, `cargo init`, etc.). This is for existing repos that are missing Claude config.

---

## Announce activation

> **project-bootstrap activated** — analyzing {repo-name} to generate Claude config.

---

## Step 1: Analyze the repo

Run all of these in parallel to build a complete picture:

### 1A. Project identity
```bash
# Repo name and remote
basename $(git rev-parse --show-toplevel)
git remote get-url origin 2>/dev/null

# Recent commit patterns (conventions, authors, frequency)
git log --oneline -20
git shortlog -sn --since="3 months ago" | head -5
```

### 1B. Language and framework detection
```bash
# Package manager and dependencies
for f in package.json Cargo.toml go.mod pyproject.toml setup.py requirements.txt Gemfile pom.xml build.gradle composer.json; do
  [ -f "$f" ] && echo "FOUND: $f"
done

# Framework detection
[ -f "next.config.js" ] || [ -f "next.config.mjs" ] || [ -f "next.config.ts" ] && echo "FRAMEWORK: Next.js"
[ -f "vite.config.ts" ] || [ -f "vite.config.js" ] && echo "FRAMEWORK: Vite"
[ -f "nuxt.config.ts" ] && echo "FRAMEWORK: Nuxt"
[ -f "svelte.config.js" ] && echo "FRAMEWORK: SvelteKit"
[ -f "angular.json" ] && echo "FRAMEWORK: Angular"
grep -q "express" package.json 2>/dev/null && echo "FRAMEWORK: Express"
grep -q "fastapi\|flask\|django" requirements.txt pyproject.toml 2>/dev/null && echo "FRAMEWORK: Python web"
```

### 1C. Commands detection
```bash
# Extract scripts from package.json
[ -f "package.json" ] && node -e "
  const pkg = JSON.parse(require('fs').readFileSync('package.json'));
  const s = pkg.scripts || {};
  const relevant = ['dev','start','build','test','lint','typecheck','format','check'];
  relevant.forEach(k => { if(s[k]) console.log(k + ': ' + s[k]); });
"

# Python commands
[ -f "pyproject.toml" ] && grep -A5 "\[tool.pytest" pyproject.toml 2>/dev/null
[ -f "Makefile" ] && grep "^[a-z].*:" Makefile | head -10

# Rust/Go/Ruby commands
[ -f "Cargo.toml" ] && echo "test: cargo test" && echo "lint: cargo clippy" && echo "check: cargo check"
[ -f "go.mod" ] && echo "test: go test ./..." && echo "vet: go vet ./..."
```

### 1D. Project structure
```bash
# Key directories (depth 2, ignore node_modules/.git/.next)
find . -maxdepth 2 -type d \
  ! -path './node_modules*' ! -path './.git*' ! -path './.next*' \
  ! -path './dist*' ! -path './build*' ! -path './.vercel*' \
  ! -path './target*' ! -path './__pycache__*' \
  | head -40

# Key config files
ls -la tsconfig.json .eslintrc* .prettierrc* tailwind.config* \
  vercel.json .env.example .env.local jest.config* vitest.config* \
  playwright.config* cypress.config* docker-compose* Dockerfile \
  .github/workflows/*.yml 2>/dev/null
```

### 1E. Existing Claude config
```bash
[ -f "CLAUDE.md" ] && echo "CLAUDE.md EXISTS" && cat CLAUDE.md
[ -d ".claude" ] && echo ".claude/ EXISTS" && ls -la .claude/
[ -f ".claude/settings.json" ] && cat .claude/settings.json
```

### 1F. Deployment target
```bash
[ -f "vercel.json" ] && echo "DEPLOY: Vercel"
[ -f "render.yaml" ] && echo "DEPLOY: Render"
[ -f "fly.toml" ] && echo "DEPLOY: Fly.io"
[ -f "Dockerfile" ] && echo "DEPLOY: Docker"
[ -f ".github/workflows/"* ] && echo "CI: GitHub Actions" && ls .github/workflows/
[ -f "Procfile" ] && echo "DEPLOY: Heroku"
[ -f "netlify.toml" ] && echo "DEPLOY: Netlify"
```

### 1G. Database
```bash
# Detect database from deps or config
grep -l "pg\|postgres\|prisma\|drizzle\|mongoose\|sqlite\|mysql" package.json 2>/dev/null && echo "DB: detected in package.json"
[ -d "migrations" ] && echo "MIGRATIONS: $(ls migrations/ | wc -l) files" && ls migrations/ | tail -5
[ -d "prisma" ] && echo "ORM: Prisma" && cat prisma/schema.prisma | head -20
[ -f "drizzle.config.ts" ] && echo "ORM: Drizzle"
```

---

## Step 2: Generate CLAUDE.md

Based on analysis results, generate a `CLAUDE.md` that encodes the project's actual conventions. Structure:

```markdown
# {Project Name}

{One-line description from package.json/README or inferred from structure}

## Commands

- **Dev server:** `{detected dev command}`
- **Build:** `{detected build command}`
- **Test:** `{detected test command}`
- **Lint:** `{detected lint command}`
- **Typecheck:** `{detected typecheck command}`
- **Format:** `{detected format command}`

## Architecture

{Brief description of project structure based on Step 1D}

- `{dir}/` — {purpose}
- `{dir}/` — {purpose}

## Conventions

{Inferred from git log patterns, existing code, and config files}

- {Convention 1 — e.g., "App Router (not Pages Router)"}
- {Convention 2 — e.g., "Tailwind CSS for styling, no CSS modules"}
- {Convention 3 — e.g., "Server components by default, 'use client' only when needed"}

## Deployment

- **Target:** {Vercel | Render | GHA | Docker | etc.}
- **Branch:** {default branch from git}
- **Environment:** {env var management approach}

## Database

- **Type:** {PostgreSQL | SQLite | MongoDB | etc.}
- **ORM:** {Prisma | Drizzle | raw SQL | etc.}
- **Migrations:** `{migration command}`
```

**Rules for generation:**
- Only include sections where data was detected. Don't add empty sections.
- Commands must be verified as actually present in package.json/Makefile/etc.
- Conventions should be inferred from actual code, not assumed from framework defaults.
- Keep it concise. CLAUDE.md should be <100 lines for most projects.

---

## Step 3: Generate .claude/ config (if not present)

### settings.json

```json
{
  "permissions": {
    "allow": [
      "Bash({detected_test_cmd})",
      "Bash({detected_lint_cmd})",
      "Bash({detected_typecheck_cmd})",
      "Bash(git *)",
      "Bash(ls *)",
      "Bash(find *)",
      "Bash(grep *)"
    ]
  }
}
```

Only add commands that were actually detected. Don't add permissions for commands that don't exist in the project.

---

## Step 4: Validate

Before writing files:

1. **Verify commands work.** Run each detected command to confirm it doesn't error:
   ```bash
   {TEST_CMD} --help 2>/dev/null || {TEST_CMD} --version 2>/dev/null
   ```
   If a command doesn't exist, remove it from the generated config.

2. **Check for existing CLAUDE.md.** If one exists, show a diff of proposed changes rather than overwriting. Ask Hannah before modifying.

3. **Check for @-references.** If the project uses `@AGENTS.md` or other reference patterns, respect them. Don't overwrite references with inline content.

---

## Step 5: Write and report

1. Write `CLAUDE.md` to project root
2. Write `.claude/settings.json` if it doesn't exist
3. Report:
   > **project-bootstrap complete** — generated CLAUDE.md ({N} lines) + .claude/settings.json for {project-name}. Detected: {language}, {framework}, {deploy-target}. Commands: test={yes/no}, lint={yes/no}, typecheck={yes/no}.

---

## Anti-patterns (do NOT do these)

- **Don't generate generic CLAUDE.md from templates.** Every field must come from actual repo analysis.
- **Don't add commands that don't exist.** If there's no test script, don't add `npm test`.
- **Don't assume framework conventions.** Read the actual code. A Next.js project might use Pages Router, not App Router.
- **Don't include secrets or env values.** Reference `.env.example` patterns, not actual values.
- **Don't add skill references the user doesn't have.** Only reference skills that exist in `~/.claude/skills/`.
- **Don't bloat with every file path.** Architecture section should be 5-10 key directories, not a full tree.
