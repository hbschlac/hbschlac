---
name: project-bootstrap
description: >
  Auto-generates CLAUDE.md and .claude/ config for any repo by analyzing its
  actual structure, dependencies, and conventions. Solves the problem where
  large projects have zero Claude Code configuration despite heavy Claude usage.
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
basename $(git rev-parse --show-toplevel)
git remote get-url origin 2>/dev/null
git log --oneline -20
git shortlog -sn --since="3 months ago" | head -5
```

### 1B. Language and framework detection
```bash
for f in package.json Cargo.toml go.mod pyproject.toml setup.py requirements.txt Gemfile pom.xml build.gradle composer.json; do
  [ -f "$f" ] && echo "FOUND: $f"
done

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
[ -f "package.json" ] && node -e "
  const pkg = JSON.parse(require('fs').readFileSync('package.json'));
  const s = pkg.scripts || {};
  const relevant = ['dev','start','build','test','lint','typecheck','format','check'];
  relevant.forEach(k => { if(s[k]) console.log(k + ': ' + s[k]); });
"

[ -f "pyproject.toml" ] && grep -A5 "\[tool.pytest" pyproject.toml 2>/dev/null
[ -f "Makefile" ] && grep "^[a-z].*:" Makefile | head -10
[ -f "Cargo.toml" ] && echo "test: cargo test" && echo "lint: cargo clippy" && echo "check: cargo check"
[ -f "go.mod" ] && echo "test: go test ./..." && echo "vet: go vet ./..."
```

### 1D. Project structure
```bash
find . -maxdepth 2 -type d \
  ! -path './node_modules*' ! -path './.git*' ! -path './.next*' \
  ! -path './dist*' ! -path './build*' ! -path './.vercel*' \
  ! -path './target*' ! -path './__pycache__*' \
  | head -40
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
[ -f "Procfile" ] && echo "DEPLOY: Heroku"
[ -f "netlify.toml" ] && echo "DEPLOY: Netlify"
ls .github/workflows/*.yml 2>/dev/null && echo "CI: GitHub Actions"
```

### 1G. Database
```bash
grep -l "pg\|postgres\|prisma\|drizzle\|mongoose\|sqlite\|mysql" package.json 2>/dev/null
[ -d "prisma" ] && echo "ORM: Prisma" && head -20 prisma/schema.prisma
[ -f "drizzle.config.ts" ] && echo "ORM: Drizzle"
[ -d "migrations" ] && echo "MIGRATIONS: $(ls migrations/ | wc -l) files"
```

### 1H. Containerization
```bash
[ -f "Dockerfile" ] && echo "DOCKER: yes" && head -5 Dockerfile
[ -f "docker-compose.yml" ] || [ -f "docker-compose.yaml" ] && echo "COMPOSE: yes"
[ -f ".dockerignore" ] && echo "DOCKERIGNORE: yes"
```

### 1I. Linter / Formatter config
```bash
for f in .eslintrc .eslintrc.js .eslintrc.json eslint.config.js eslint.config.mjs \
         .prettierrc .prettierrc.json prettier.config.js \
         ruff.toml .ruff.toml pyproject.toml \
         .rubocop.yml rustfmt.toml .golangci.yml biome.json; do
  [ -f "$f" ] && echo "LINT_CONFIG: $f"
done
```

### 1J. Monorepo / Workspaces
```bash
[ -f "pnpm-workspace.yaml" ] && echo "WORKSPACE: pnpm" && cat pnpm-workspace.yaml
node -e "const p=JSON.parse(require('fs').readFileSync('package.json'));if(p.workspaces)console.log('WORKSPACE: npm',JSON.stringify(p.workspaces))" 2>/dev/null
[ -f "lerna.json" ] && echo "WORKSPACE: lerna"
[ -f "turbo.json" ] && echo "WORKSPACE: turborepo"
[ -f "nx.json" ] && echo "WORKSPACE: nx"
```

---

## Step 2: Generate CLAUDE.md

Based on analysis results, generate:

```markdown
# {Project Name}

{One-line description from package.json/README or inferred from structure}

## Commands

- **Dev server:** `{detected dev command}`
- **Build:** `{detected build command}`
- **Test:** `{detected test command}`
- **Lint:** `{detected lint command}`
- **Typecheck:** `{detected typecheck command}`

## Architecture

- `{dir}/` — {purpose}
- `{dir}/` — {purpose}

## Conventions

- {Convention 1 — inferred from actual code, not assumed from framework}

## Deployment

- **Target:** {Vercel | Render | GHA | Docker | etc.}
- **Branch:** {default branch}
```

**Rules:**
- Only include sections where data was detected. No empty sections.
- Commands must be verified as present in package.json/Makefile/etc.
- Conventions inferred from actual code, not assumed from framework defaults.
- Keep it under 100 lines. CLAUDE.md is a quick reference, not documentation.

---

## Step 3: Generate .claude/settings.json (if not present)

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

Only add commands that were actually detected.

---

## Step 4: Validate

1. **Verify commands work.** Run each detected command with `--help` or equivalent.
2. **Check for existing CLAUDE.md.** If one exists, show a diff rather than overwriting. Ask before modifying.
3. **Check for @-references.** If the project uses `@AGENTS.md` or similar, respect them.

---

## Step 5: Write and report

1. Write `CLAUDE.md` to project root
2. Write `.claude/settings.json` if it doesn't exist
3. Report:
   > **project-bootstrap complete** — generated CLAUDE.md ({N} lines) + .claude/settings.json for {project-name}. Detected: {language}, {framework}, {deploy-target}. Commands: test={yes/no}, lint={yes/no}, typecheck={yes/no}.

---

## Anti-patterns

- **Don't generate from templates.** Every field must come from actual repo analysis.
- **Don't add commands that don't exist.** If there's no test script, don't add `npm test`.
- **Don't assume framework conventions.** Read the actual code.
- **Don't include secrets or env values.**
- **Don't bloat with every file path.** 5-10 key directories, not a full tree.
- **Don't ignore existing linter configs.** Detect .eslintrc, ruff.toml, etc. and reference them.
- **Don't miss monorepo structure.** If workspaces exist, document each workspace's role.

---

## Changelog

- **2026-06-05 — v1.1: Docker, linter config, monorepo/workspace detection**
  - ADDED: Container detection (Dockerfile, docker-compose)
  - ADDED: Linter/formatter config detection (eslint, prettier, ruff, rubocop, biome, etc.)
  - ADDED: Monorepo/workspace detection (pnpm, npm, lerna, turborepo, nx)
  - ADDED: Anti-patterns for linter configs and monorepo structure
- **2026-05-29 — v1: Initial skill based on config debt analysis**
  - Covers: language detection, command detection, structure analysis, deployment target
  - Motivated by: muse-shopping (65K LOC, 0 config), interior-designer-portfolio (active, 0 config)
