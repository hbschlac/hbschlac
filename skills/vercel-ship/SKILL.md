---
name: vercel-ship
description: >
  Pre-deploy validation and debugging patterns for Next.js + Vercel projects.
  Activates on deploy failures, Vercel-specific bugs, serverless config issues,
  OAuth flow debugging, image storage decisions, and middleware routing problems.
  Encodes patterns learned from 100+ Vercel deployments across hannah-portfolio,
  interior-designer-portfolio, muse-shopping, and recs.community. Trigger phrases
  include: "deploy to Vercel", "Vercel build failed", "serverless function error",
  "middleware not working", "OAuth redirect broken", "trust proxy", "image storage",
  "R2 migration", "OG image", "subdomain routing", "cold start", "function size",
  "Vercel Blob", "env vars not working", "500 error on Vercel", "works locally
  but not on Vercel", "edge function", "ISR", "revalidate".
---

# vercel-ship

Pre-deploy validation and Vercel-specific debugging for Next.js projects. Built from patterns across 100+ real deployments and the specific failures documented in build-log.

**Not for:** general Next.js development, CSS/styling, or non-Vercel hosting.

---

## Announce activation

> **vercel-ship activated** — [pre-deploy check | debug {symptom} | config review]. [one-line reason.]

---

## Step 1: Detect project context

```bash
# Required: must be a Next.js project
[ -f "next.config.js" ] || [ -f "next.config.mjs" ] || [ -f "next.config.ts" ] || { echo "Not a Next.js project"; exit 1; }

# Detect Next.js version (API differences are significant)
NEXT_VERSION=$(node -e "console.log(require('next/package.json').version)" 2>/dev/null)

# Detect if using App Router vs Pages Router
[ -d "app" ] && ROUTER="app" || ROUTER="pages"

# Detect if Express/custom server wraps Next
grep -rl "express\|createServer" server.js server.ts src/server.* 2>/dev/null && SERVER="custom" || SERVER="vercel-native"

# Detect backend type
[ -d "src" ] && grep -rl "express" src/ 2>/dev/null && BACKEND="express-api"
[ -d "api" ] && BACKEND="vercel-functions"

# Check for Vercel project config
[ -f "vercel.json" ] && cat vercel.json
[ -f ".vercelignore" ] && cat .vercelignore
```

---

## Step 2: Pre-deploy checklist

Run this BEFORE every deploy. Each item is a real failure that has happened.

### 2A. Environment variables

- [ ] **All `process.env.X` values are trimmed at the read-site.** Copy-pasting from dashboards (GCP, Stripe, Vercel) introduces trailing whitespace/newlines that silently break. Pattern: `const VAR = process.env.X?.trim()`.
- [ ] **No secrets in `NEXT_PUBLIC_` variables.** Anything prefixed `NEXT_PUBLIC_` ships to the browser bundle. Check: `grep -r "NEXT_PUBLIC_" .env* --include="*.env*"` — none should contain API keys, tokens, or passwords.
- [ ] **All env vars referenced in code exist in Vercel project settings.** Run: `grep -roh 'process\.env\.\w\+' --include="*.ts" --include="*.tsx" --include="*.js" --include="*.mjs" | sort -u` and verify each exists in Vercel dashboard or `.env.local`.
- [ ] **Boolean env vars are string-compared.** `process.env.DEBUG === 'true'`, not `process.env.DEBUG` (which is truthy for any non-empty string including `"false"`).

### 2B. Serverless entry points

- [ ] **Express middleware is mounted in the same order in the serverless entry as in dev server.** Vercel serverless entry (e.g., `api/index.ts` or `vercel.json` rewrites) often has different middleware ordering than `server.ts`. Diff them.
- [ ] **Error-handler middleware is mounted LAST.** Express error handlers `(err, req, res, next)` must come after all route definitions — in both the dev server AND the serverless entry.
- [ ] **`trust proxy` is set when behind a reverse proxy.** Vercel, Render, and Cloudflare all proxy requests. Without `app.set('trust proxy', 1)`, `req.ip` returns the proxy IP and `req.protocol` returns `http` even on HTTPS. This breaks: rate limiting, OAuth state validation, secure cookie flags, IP-based logging.
- [ ] **Request body parsing is configured.** Vercel's default body parsing may conflict with Express's. If using custom Express server: `export const config = { api: { bodyParser: false } }` in the API route, and let Express handle parsing.

### 2C. OAuth / Authentication

- [ ] **Redirect URIs include BOTH localhost AND production domain.** In GCP/Meta/Apple OAuth console, add: `http://localhost:3000/auth/callback` AND `https://yourdomain.com/auth/callback`. Missing one causes redirect_uri_mismatch.
- [ ] **OAuth env vars use the production domain, not localhost.** Common mistake: `GOOGLE_REDIRECT_URI=http://localhost:3000/...` in Vercel env vars.
- [ ] **OAuth-only accounts are handled.** Users who sign up via OAuth don't have a password. Login flow must not crash on `bcrypt.compare(password, null)`.
- [ ] **Session/JWT secrets are set in production.** `JWT_SECRET` or `SESSION_SECRET` must exist in Vercel env vars — falling back to a hardcoded default in production is a security vulnerability.
- [ ] **CSRF state parameter is validated.** OAuth `state` parameter must be checked on callback to prevent CSRF attacks.

### 2D. Middleware and routing

- [ ] **Middleware matcher is specific.** `export const config = { matcher: [...] }` should NOT match API routes, `_next/static`, `_next/image`, or `favicon.ico` unless intentional. Overly broad matchers cause infinite redirect loops or block static assets.
- [ ] **Subdomain routing uses middleware rewrites, not DNS.** For `sub.domain.com` routing to `/sub-path`, use Next.js middleware to rewrite based on `req.headers.host`. Vercel DNS alone isn't enough — the app must interpret the subdomain.
- [ ] **Middleware doesn't return Response for API routes.** API routes that go through middleware must use `NextResponse.next()`, not `NextResponse.redirect()` — redirecting API calls breaks fetch clients.

### 2E. Images and static assets

- [ ] **Image domains are configured in `next.config.js`.** External image URLs (R2, Blob, S3, Unsplash) must be in `images.remotePatterns` or `images.domains`.
- [ ] **Image URLs use HTTPS.** Mixed content (HTTP images on HTTPS page) will be blocked by browsers.
- [ ] **Vercel Blob URLs include the correct account prefix.** Blob URLs are account-scoped; using a URL from a different account/project silently 404s.
- [ ] **R2/S3 CORS is configured for the production domain.** Missing CORS headers cause image loads to fail in the browser but work in Postman/curl.

### 2F. Build

- [ ] **TypeScript compiles clean.** `npx tsc --noEmit` — Vercel will fail the build on type errors.
- [ ] **No `import` of server-only code from client components.** Check for `fs`, `path`, `crypto` imports in `"use client"` files — these crash at build time.
- [ ] **`output: 'standalone'` is set if using custom server.** Without this, the build output doesn't include node_modules and the serverless function fails at runtime.

---

## Step 3: Debug common failures

### "500 Internal Server Error" on Vercel (works locally)

1. Check Vercel Function Logs (Runtime Logs tab) for the actual error
2. Most common causes:
   - Missing env var (check `process.env.X` values)
   - Trust proxy not set (OAuth/session failures)
   - Middleware ordering different from dev server
   - Database connection string uses localhost
   - Body parsing conflict (Vercel vs Express)

### "Redirect loop" or "ERR_TOO_MANY_REDIRECTS"

1. Check middleware matcher — is it catching `_next/*` or the redirect target itself?
2. Check for HTTP->HTTPS redirect conflicting with Vercel's automatic HTTPS
3. Auth middleware redirecting to login page that also requires auth

### "Function Size Exceeded" (50MB limit)

1. Check for accidentally bundled `node_modules`: `du -sh .next/server/chunks/*.js | sort -rh | head -20`
2. Use `output: 'standalone'` to tree-shake server bundle
3. Move heavy deps to edge functions or external services

### "Cold start too slow" (>10s)

1. Reduce function bundle size (see above)
2. Move initialization out of request handler (DB connections, SDK init)
3. Consider edge runtime for latency-sensitive routes: `export const runtime = 'edge'`
4. For Playwright/puppeteer: offload to GitHub Actions instead of serverless (learned from libby-hold-monitor: bumped from 30s->4min timeout before pivoting to GHA entirely)

### "Image not loading" / broken images after migration

1. Verify image URL returns 200: `curl -I {url}`
2. Check `next.config.js` `images.remotePatterns` includes the new domain
3. Check CORS headers: `curl -H "Origin: https://yourdomain.com" -I {url}` — look for `Access-Control-Allow-Origin`
4. For R2 migration: verify the object key matches the expected path (Vercel Blob uses flat keys, R2 uses path-style)
5. Check for 1x1 placeholder images — migration scripts that download before upload is complete produce empty files

### OAuth flow failures

Diagnosis order:
1. Check redirect URI matches EXACTLY (including trailing slash, www vs non-www)
2. Check env vars are trimmed (no trailing whitespace)
3. Check trust proxy is set
4. Check the OAuth provider's error response (not just your app's 500)
5. Check if the user has an OAuth-only account trying password login (or vice versa)
6. For Google: `www.domain.com` and `domain.com` are different redirect URIs — register both

---

## Step 4: Image storage decision tree

When to use what:

| Storage | Use when | Avoid when | Cost model |
|---|---|---|---|
| **Vercel Blob** | Simple uploads, <100MB, low-medium traffic | High traffic (CDN costs), need migration flexibility | Pay per GB stored + bandwidth |
| **Cloudflare R2** | High traffic, need egress-free reads, S3-compatible | Need Vercel-native integration | Free egress, pay per storage + operations |
| **S3** | AWS ecosystem, need full S3 API, Lambda triggers | Egress costs are a concern | Pay per everything |
| **Uploadthing** | Quick setup, file type validation built-in | Need custom upload logic, large files | Free tier + paid |

**Migration checklist (learned from Vercel Blob -> R2 emergency):**
1. Create admin endpoint to list all current URLs: `GET /api/admin/debug-urls`
2. Create migration endpoint that downloads from source and uploads to target: `POST /api/admin/migrate`
3. Verify each migrated file is not a 1x1 placeholder (check file size > threshold)
4. Update all database references (URLs change between providers)
5. Update `next.config.js` image domains
6. Test with real images before cutting over
7. Keep old storage active for 30 days as fallback
8. Create repair endpoint for files that failed: `POST /api/admin/repair-from-source`

---

## Step 5: Subdomain routing pattern

Proven pattern from jamie's bach (jamiesbach.schlacter.me):

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const host = request.headers.get('host') || '';
  const subdomain = host.split('.')[0];

  // Map subdomains to internal paths
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
- Vercel domain settings: add `subdomain.domain.com` as alias
- DNS: CNAME `subdomain.domain.com` -> `cname.vercel-dns.com`
- Matcher must exclude API routes and static assets

---

## Step 6: OG image / social preview pattern

For custom social preview cards (iMessage, Slack, Twitter):

```typescript
// app/api/og/route.tsx (App Router)
import { ImageResponse } from 'next/og';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const title = searchParams.get('title') || 'Default Title';

  return new ImageResponse(
    <div style={{ /* OG card styles */ }}>
      <h1>{title}</h1>
    </div>,
    { width: 1200, height: 630 }
  );
}
```

In the page's metadata:
```typescript
export const metadata = {
  openGraph: {
    images: [{ url: '/api/og?title=My+Page', width: 1200, height: 630 }],
  },
};
```

Gotchas:
- OG images must be absolute URLs in production (include `https://domain.com`)
- Twitter uses `twitter:image`, OpenGraph uses `og:image` — set both
- Test with: https://developers.facebook.com/tools/debug/ and Twitter Card Validator
- iMessage caches aggressively — add a cache-busting query param during development

---

## Current learnings

Last synced: 2026-05-28 (initial population from build-log + cross-repo commit analysis)

### A. Environment & Config

- **Trim all env vars at read-site.** 4 separate fixes across schlacter.me; also hit in muse OAuth. Pattern: `process.env.X?.trim()`. (5 citations)
- **Vercel serverless entry middleware order must match dev server.** Silent 500s when error handler is before routes. (1 citation: muse `d01750d`)
- **Set trust proxy behind any reverse proxy.** Broke OAuth in muse, session validation in calmar. (2 citations: muse `0c92c13`, `3a83f67`)

### B. Image Storage

- **Verify migrated images are not 1x1 placeholders.** Download-before-upload-complete produces empty files. Needed dedicated repair endpoint. (1 citation: interior-designer-portfolio R2 migration)
- **Keep old storage active 30 days after migration.** Vercel Blob CDN suspension caused emergency; R2 fallback saved the project. (1 citation: interior-designer-portfolio)

### C. OAuth

- **Register both www and non-www redirect URIs.** Google treats them as different URIs. (1 citation: muse `68d29d4`)
- **Handle OAuth-only accounts in password login flow.** `bcrypt.compare(input, null)` crashes. (1 citation: muse `3a83f67`)
- **Trim OAuth provider env vars.** GCP console copy-paste includes trailing whitespace. (1 citation: muse `3f11f7e`)

### D. Infrastructure

- **Offload Playwright to GHA instead of serverless.** Cold starts on Vercel/Render exceed 30s; GHA runners handle 4min+ operations. (1 citation: libby-hold-monitor architecture pivot)
- **Compress auth state for GitHub Secrets.** gzip+b64 to fit GitHub's 48KB secret limit. (1 citation: libby-hold-monitor)

### E. Routing

- **Subdomain routing needs middleware rewrite, not just DNS.** Vercel DNS CNAME alone doesn't route — app must interpret host header. (1 citation: hannah-portfolio Jamie's bach)
- **Middleware matcher must exclude _next/static, _next/image, and API routes.** Overly broad matchers cause redirect loops on static assets. (1 citation: hannah-portfolio)
