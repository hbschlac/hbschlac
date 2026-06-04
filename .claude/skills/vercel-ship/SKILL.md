---
name: vercel-ship
description: >
  Pre-deploy validation and debugging patterns for Next.js + Vercel projects.
  Activates on deploy failures, Vercel-specific bugs, serverless config issues,
  OAuth flow debugging, image storage decisions, and middleware routing problems.
  Built from 100+ real deployments across schlacter-me, interior-designer-portfolio,
  muse-shopping, kindle-schlacter-me, and fashionista-hannah. Covers the #1 real
  failure mode: TypeScript type errors from interface changes not propagated to callers.
---

# vercel-ship

Pre-deploy validation and Vercel-specific debugging for Next.js projects. Built from patterns across 100+ real deployments and 13 documented build failures.

**Not for:** general Next.js development, CSS/styling, or non-Vercel hosting.

---

## Announce activation

> **vercel-ship activated** — [pre-deploy check | debug {symptom} | config review]. [one-line reason.]

---

## Step 1: Detect project context

```bash
[ -f "next.config.js" ] || [ -f "next.config.mjs" ] || [ -f "next.config.ts" ] || { echo "Not a Next.js project"; exit 1; }
NEXT_VERSION=$(node -e "console.log(require('next/package.json').version)" 2>/dev/null)
[ -d "app" ] && ROUTER="app" || ROUTER="pages"
grep -rl "express\|createServer" server.js server.ts src/server.* 2>/dev/null && SERVER="custom" || SERVER="vercel-native"
[ -d "api" ] && BACKEND="vercel-functions"
[ -f "vercel.json" ] && cat vercel.json
```

---

## Step 2: Pre-deploy checklist

Run this BEFORE every deploy. Every item is a real failure that has happened.

### 2A. TypeScript type propagation (THE #1 FAILURE MODE)

100% of real Vercel build failures across all projects are TypeScript type errors. The root cause is always the same: an interface/type changes but not all consuming files are updated in the same commit.

- [ ] **Run `tsc --noEmit` BEFORE pushing.** This is the single highest-value check. If it passes locally, Vercel will not fail on types.
- [ ] **When changing any type/interface, find ALL callers.** `grep -rn "TypeName" --include="*.ts" --include="*.tsx"` — update every file in the same commit.
- [ ] **When adding required fields to a type, search for all object literals of that type.** Missing properties won't error at the definition site — they'll error at every usage site.
- [ ] **When renaming props, update the component AND every parent that passes the prop.** Real example: `BrandLogo` props renamed but `brands/[slug]/page.tsx` still used old names → 2 failed deploys.
- [ ] **When adding a new value to a union type, update all switch/if-else chains.** Real example: `"current-home"` added to activePage but NavBar's type union not updated → 3 failed deploys.

### 2B. File completeness

- [ ] **All imported files exist in git.** Run: `git status` and check that no imported file is untracked. Real example: `ShareDropdown.tsx` existed locally but wasn't committed → Vercel build failed on missing module.
- [ ] **No local-only files referenced in imports.** `git diff --name-only HEAD` should not include files that other committed files import from.

### 2C. Environment variables

- [ ] **All `process.env.X` values are trimmed at the read-site.** Copy-pasting from dashboards introduces trailing whitespace/newlines. Pattern: `const VAR = process.env.X?.trim()`.
- [ ] **No secrets in `NEXT_PUBLIC_` variables.** Anything prefixed `NEXT_PUBLIC_` ships to the browser bundle.
- [ ] **All env vars referenced in code exist in Vercel project settings.** Run: `grep -roh 'process\.env\.\w\+' --include="*.ts" --include="*.tsx" --include="*.js" --include="*.mjs" | sort -u`
- [ ] **Boolean env vars are string-compared.** `process.env.DEBUG === 'true'`, not `process.env.DEBUG`.

### 2D. Serverless entry points

- [ ] **Express middleware is mounted in the same order in the serverless entry as in dev server.** Diff them.
- [ ] **Error-handler middleware is mounted LAST.** `(err, req, res, next)` must come after all route definitions in both dev server AND serverless entry.
- [ ] **`trust proxy` is set when behind a reverse proxy.** Without `app.set('trust proxy', 1)`, `req.ip` returns the proxy IP. Breaks: rate limiting, OAuth state validation, secure cookie flags.
- [ ] **Request body parsing is configured.** Vercel's default body parsing may conflict with Express's. Use `export const config = { api: { bodyParser: false } }` if needed.

### 2E. OAuth / Authentication

- [ ] **Redirect URIs include BOTH localhost AND production domain.** In OAuth console, add both. Missing one causes redirect_uri_mismatch.
- [ ] **OAuth env vars use the production domain, not localhost.**
- [ ] **OAuth-only accounts are handled.** Users who sign up via OAuth don't have a password. Login flow must not crash on `bcrypt.compare(password, null)`.
- [ ] **Session/JWT secrets are set in production.** Falling back to a hardcoded default is a security vulnerability.
- [ ] **CSRF state parameter is validated on callback.**
- [ ] **Register both www and non-www redirect URIs.** Google treats them as different URIs.

### 2F. Middleware and routing

- [ ] **Middleware matcher is specific.** Should NOT match `_next/static`, `_next/image`, `favicon.ico`, or API routes unless intentional.
- [ ] **Subdomain routing uses middleware rewrites, not just DNS.**
- [ ] **Middleware doesn't return Response for API routes.** Use `NextResponse.next()`, not `NextResponse.redirect()` for API calls.

### 2G. Images and static assets

- [ ] **Image domains are configured in `next.config.js` `images.remotePatterns`.**
- [ ] **Image URLs use HTTPS.**
- [ ] **R2/S3 CORS is configured for the production domain.**

### 2H. Build

- [ ] **`tsc --noEmit` passes.** (Repeat — this is the #1 failure.)
- [ ] **No `import` of server-only code from client components.** Check for `fs`, `path`, `crypto` imports in `"use client"` files.
- [ ] **`output: 'standalone'` is set if using custom server.**

---

## Step 3: Debug common failures

### "500 Internal Server Error" on Vercel (works locally)

1. Check Vercel Function Logs (Runtime Logs tab) for the actual error
2. Most common causes:
   - Missing env var
   - Trust proxy not set (OAuth/session failures)
   - Middleware ordering different from dev server
   - Database connection string uses localhost
   - Body parsing conflict (Vercel vs Express)

### "Build failed" on Vercel

1. **Read the actual error message.** 100% of real build failures have been TypeScript type errors.
2. Pattern: find the file:line in the error → check if a type/interface was recently changed → find all callers that need updating.
3. Fix ALL callers in one commit, not one at a time (which causes chained failures).

### "Redirect loop" / "ERR_TOO_MANY_REDIRECTS"

1. Middleware matcher catching `_next/*` or the redirect target itself?
2. HTTP→HTTPS redirect conflicting with Vercel's automatic HTTPS?
3. Auth middleware redirecting to login page that also requires auth?

### "Function Size Exceeded" (50MB limit)

1. `du -sh .next/server/chunks/*.js | sort -rh | head -20`
2. Use `output: 'standalone'` to tree-shake
3. Move heavy deps to external services

### "Cold start too slow" (>10s)

1. Reduce function bundle size
2. Move initialization out of request handler
3. Consider edge runtime: `export const runtime = 'edge'`
4. For Playwright/puppeteer: offload to GitHub Actions (learned from libby-hold-monitor: 30s→4min timeout before pivoting to GHA)

### OAuth flow failures

Diagnosis order:
1. Redirect URI matches EXACTLY (trailing slash, www vs non-www)
2. Env vars are trimmed
3. Trust proxy is set
4. Check the OAuth provider's error response
5. Check if OAuth-only account trying password login
6. For Google: `www.domain.com` and `domain.com` are different URIs

---

## Step 4: Image storage decision tree

| Storage | Use when | Avoid when | Cost model |
|---|---|---|---|
| **Cloudflare R2** | High traffic, need egress-free reads, S3-compatible | Need Vercel-native integration | Free egress, pay per storage + operations |
| **Vercel Blob** | Simple uploads, <100MB, low-medium traffic | High traffic, need migration flexibility | Pay per GB stored + bandwidth |
| **S3** | AWS ecosystem, full S3 API, Lambda triggers | Egress costs are a concern | Pay per everything |

**Migration checklist (from Vercel Blob → R2 emergency):**
1. Create admin endpoint to list all current URLs
2. Download from source, upload to target — verify each file is not a 1x1 placeholder (check file size)
3. Update all database URL references
4. Update `next.config.js` image domains
5. Keep old storage active 30 days as fallback

---

## Step 5: Subdomain routing pattern

Proven pattern from jamie's bach (jamiesbach.schlacter.me):

```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const host = request.headers.get('host') || '';
  const subdomain = host.split('.')[0];

  if (subdomain === 'jamiesbach') {
    const url = request.nextUrl.clone();
    url.pathname = `/jamie-bach-2026${url.pathname === '/' ? '' : url.pathname}`;
    return NextResponse.rewrite(url);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

Requirements:
- Vercel domain settings: add subdomain as alias
- DNS: CNAME to `cname.vercel-dns.com`
- Matcher must exclude API routes and static assets

---

## Step 6: OG image / social preview pattern

```typescript
// app/api/og/route.tsx
import { ImageResponse } from 'next/og';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const title = searchParams.get('title') || 'Default Title';
  return new ImageResponse(
    <div style={{ /* card styles */ }}><h1>{title}</h1></div>,
    { width: 1200, height: 630 }
  );
}
```

Gotchas:
- OG images must be absolute URLs in production
- Twitter uses `twitter:image`, OpenGraph uses `og:image` — set both
- iMessage caches aggressively — cache-busting param during dev

---

## Deployment Failure Database

Real failures from 10 Vercel projects, 13 failed deployments. All TypeScript type errors.

| Project | Error | Root Cause | Deploys to fix |
|---|---|---|---|
| schlacter-me | literal type `1` vs `0` comparison | Type narrowing too strict | 1 |
| interior-designer-portfolio | `"current-home"` not in activePage union | New union value not added to NavBar props | 3 |
| interior-designer-portfolio | Cannot find module `./ShareDropdown` | File not committed to git | 1 |
| fashionista-hannah | Missing `semanticSummary` + `stylingContext` | New required fields not added to all constructors | 1 |
| frontend (muse) | `stores` not on `CheckoutReadiness` | API response shape changed, frontend types stale | 3 |
| frontend (muse) | `data` not on `AuthResponse` | Auth response restructured, callers not updated | 3 |
| muse-shopping | `logoUrl` not on `BrandLogoProps` | Props interface renamed, callers not updated | 2 |

---

## Changelog

- **2026-05-29 — v1: Initial skill based on 100+ deployments, 13 failures, 10 projects**
  - TypeScript type propagation as #1 pre-deploy check (data-driven from 100% failure rate)
  - Deployment failure database with real examples
  - File completeness check (uncommitted imports)
  - Subdomain routing pattern from jamie's bach
  - Image storage decision tree from Blob→R2 migration
  - OAuth debugging from muse-shopping incidents
