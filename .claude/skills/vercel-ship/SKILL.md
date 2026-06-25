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

### 2I. Preview deployments

- [ ] **Test the preview URL, not just localhost.** Preview URLs use different domains — CORS, cookies, OAuth redirects may break.
- [ ] **Check the Vercel deployment log, not just the build log.** Runtime errors don't appear in build output.
- [ ] **For subdomain routing: preview URLs don't have subdomains.** Test the rewrite path directly (e.g., `/jamie-bach-2026/`) on preview.

### 2J. Edge vs. Serverless

- [ ] **Edge Runtime cannot use Node.js APIs.** No `fs`, `path`, `child_process`, `crypto` (use `Web Crypto` instead). No native Node modules.
- [ ] **Edge has 128KB code size limit.** Large dependencies (ORMs, sharp, puppeteer) cannot run at the edge.
- [ ] **Middleware always runs at the edge.** Keep middleware lightweight — no DB calls, no heavy computation.
- [ ] **Cron jobs (`vercel.json` cron) use Serverless Functions, not Edge.** Set appropriate `maxDuration`.

### 2K. Supabase integration

- [ ] **Supabase env vars are set in Vercel.** `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` (public), plus `SUPABASE_SERVICE_ROLE_KEY` (server-only, NOT `NEXT_PUBLIC_`).
- [ ] **Auth middleware refreshes the session.** `middleware.ts` must call Supabase `getUser()` on every request to refresh the cookie. Missing this causes silent auth failures after token expiry.
- [ ] **Middleware matcher excludes Supabase callback.** If using OAuth with Supabase, the `/auth/callback` route must not be caught by auth-redirect middleware.
- [ ] **RLS policies are tested on the preview deployment.** Preview uses a different Supabase project (or the same one with preview env vars). Verify that RLS behaves correctly with the preview's JWT issuer.

### 2L. Database Migration Coordination

- [ ] **Run migrations BEFORE deploying new code that depends on them.** New columns, tables, or RLS policies must exist before the app code references them. Deploy sequence: migration → code deploy.
- [ ] **For Supabase: push migrations via CLI or dashboard before Vercel deploy.** `npx supabase db push` or apply via Supabase dashboard. Vercel build does NOT run migrations automatically.
- [ ] **For Prisma: run `prisma migrate deploy` in a CI step before the build step.** Or use `prisma db push` for prototype phase.
- [ ] **Test migration rollback.** Write a "down" migration or verify you can revert with a new forward migration. Never edit a deployed migration file.
- [ ] **Preview deployments need migration access.** If preview branches use a separate database, migrations must be applied there too. Otherwise, preview deploys will crash on missing tables/columns.

### 2M. Vercel KV / Redis

- [ ] **KV env vars are set.** `KV_REST_API_URL` and `KV_REST_API_TOKEN` in Vercel project settings.
- [ ] **KV operations have timeouts.** Vercel KV uses HTTP under the hood. Set reasonable timeouts to prevent hanging serverless functions.
- [ ] **KV keys include environment prefix in dev.** Prevent local development from polluting production KV data. Pattern: `${process.env.NODE_ENV === 'production' ? '' : 'dev:'}kindle:...`

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

### "Runtime Error" (build succeeds, page crashes)

1. Check Vercel Function Logs (not build logs) for the actual stack trace
2. Common causes: missing env var at runtime (set in Vercel dashboard, not `.env`), database connection string uses localhost, `fetch()` to relative URL in server component (needs absolute URL on Vercel)
3. For ISR/SSG pages: check `revalidate` timing — stale data looks like a bug but is caching

### "Cron job not running"

1. Cron requires `vercel.json` `crons` field AND a matching API route
2. Free tier: 1 cron job per day max. Pro: every minute
3. Cron invocations are `GET` requests — your handler must handle `GET`
4. Check Vercel dashboard → Crons tab for execution history

### ISR / SSG stale data ("it shows old content")

1. **Check `revalidate` value.** `export const revalidate = 3600` means data can be up to 1 hour stale. During development, set to `0` or use `export const dynamic = 'force-dynamic'`.
2. **On-demand revalidation.** Use `revalidatePath('/path')` or `revalidateTag('tag')` in API routes after data changes. Without this, ISR pages won't update until the timer expires.
3. **Check the data source, not the page.** If the API returns stale data, the page will be stale regardless of revalidation settings.
4. **Vercel caches aggressively.** Add `Cache-Control: no-store` headers to API routes that must always return fresh data. Don't rely on browser refresh — Vercel's edge cache is separate.
5. **Preview deployments bypass ISR.** If the page looks correct on preview but stale on production, the issue is the production cache, not the code.

### When to escalate to debug-escalation

vercel-ship handles deploy and config issues. If the problem is deeper, hand off:
- **Build failure fix attempted 2+ times** → debug-escalation Step 2 (the root cause isn't a type error — it's architectural)
- **500 error traced to upstream API, not Vercel config** → debug-escalation Step 0 (production incident response with resilience patterns)
- **Runtime error not in any debugging table above** → debug-escalation Step 1 (stop and investigate before more config changes)

### OAuth flow failures

Diagnosis order:
1. Redirect URI matches EXACTLY (trailing slash, www vs non-www)
2. Env vars are trimmed
3. Trust proxy is set
4. Check the OAuth provider's error response
5. Check if OAuth-only account trying password login
6. For Google: `www.domain.com` and `domain.com` are different URIs

### Webhook failures (events not arriving)

1. Verify the webhook endpoint URL matches the production domain exactly
2. Check that the webhook secret env var is set and trimmed in Vercel
3. Verify the endpoint handles the correct HTTP method (usually POST)
4. Check Vercel Function Logs — webhook requests may be hitting the function but failing silently
5. For Resend webhooks: verify the exact event types are enabled (e.g., `email.delivered`, `email.bounced`)
6. Return 200 quickly — webhook providers retry on timeout. Do heavy processing async.
7. Implement idempotency — webhooks can be delivered more than once

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

## Step 7: Domain migration checklist

When renaming a domain, subdomain, or repo (e.g., community.recs → recs.community):

1. **Rename the GitHub repo first.** Old URL auto-redirects. Update `git remote set-url origin` locally.
2. **Update Vercel project settings.** Change the domain in Vercel Dashboard → Project → Domains. Add the new domain, verify DNS, then remove the old one.
3. **DNS propagation.** After changing DNS records, allow up to 48h. Verify with `dig +short {domain}` or `nslookup {domain}`. During propagation, keep both old and new domains active.
4. **Update all hardcoded URLs.** Search the codebase: `grep -rn 'old-domain' --include='*.ts' --include='*.tsx' --include='*.json' --include='*.md'`. Common locations: `package.json` name, `next.config.*` domains, `middleware.ts` host checks, OAuth redirect URIs, README links, CLAUDE.md references.
5. **Update OAuth providers.** Add the new domain's redirect URIs BEFORE removing the old ones. Test login on the new domain.
6. **Update webhook endpoints.** Any external service (Resend, Stripe, etc.) sending webhooks to the old domain needs the URL updated.
7. **SEO: canonical URLs and redirects.** Add redirects from old domain → new domain in `vercel.json` or middleware. Update `<link rel="canonical">` and `og:url` in metadata.
8. **Update external references.** GitHub repo description, linked sites, portfolio references, README badges.

---

## Step 8: MCP tools for deployment verification

When running in a Claude Code web session with Vercel MCP tools available, use them for deployment verification instead of (or in addition to) manual checks.

**Important:** Load tool schemas via `ToolSearch` before calling. Use `ToolSearch` with query `+Vercel deploy` or `select:mcp__Vercel__list_deployments` to get the schemas.

### Concrete MCP workflows

**Check if a deploy succeeded:**
1. `mcp__Vercel__list_projects` → find the project
2. `mcp__Vercel__list_deployments` (with project name) → check most recent deploy state
3. If state is "ERROR": `mcp__Vercel__get_deployment_build_logs` → read the actual error

**Debug a runtime 500 error:**
1. `mcp__Vercel__get_runtime_logs` → find the stack trace (build logs won't show runtime errors)
2. If the error is a missing env var: `mcp__Vercel__get_project` → check which env vars are set
3. Fix in code → push → `mcp__Vercel__list_deployments` to watch the new deploy land

**Verify production after deploy:**
1. `WebFetch` the production URL → check for 200 response and correct content
2. `mcp__Vercel__get_runtime_logs` → check for errors in the first 5 minutes
3. If the site uses subdomains: `WebFetch` each subdomain separately

**Scheduled health monitoring (for routines):**
1. `mcp__Vercel__list_projects` → enumerate all projects
2. For each: `mcp__Vercel__list_deployments` → check latest deploy state + age
3. `WebFetch` each production URL → verify the site responds
4. Only notify if something is down or a deploy failed

**When to use MCP tools vs. manual checks:**
- **Pre-deploy (Step 2):** Still run `tsc --noEmit` locally. MCP tools don't replace local validation.
- **Post-deploy debugging:** Use `get_deployment_build_logs` first — faster than scrolling the Vercel dashboard.
- **Runtime errors:** Use `get_runtime_logs` to see server-side errors that don't appear in build logs.
- **Verifying config:** Use `get_project` to confirm env vars are set without needing dashboard access.
- **Health checks:** Use `list_deployments` + `WebFetch` in scheduled routines to catch outages before users report them.

---

## Step 9: Non-Vercel Deployment Patterns (Docker / k8s)

Not all projects deploy to Vercel. For projects using Docker and/or Kubernetes (e.g., kindle-connector):

### Docker pre-deploy checklist

- [ ] **Dockerfile builds locally.** `docker build -t {name} .` must succeed before pushing.
- [ ] **Multi-stage builds reduce image size.** Build stage (with dev deps) → production stage (runtime only).
- [ ] **`.dockerignore` excludes node_modules, .git, .env, tests.** Large contexts slow builds.
- [ ] **No hardcoded localhost in app code.** Use env vars for service URLs: `process.env.API_URL || 'http://localhost:3000'`.
- [ ] **Health check endpoint exists.** k8s liveness/readiness probes need a `/health` or `/healthz` route.
- [ ] **Graceful shutdown.** Handle `SIGTERM` — finish in-flight requests, close DB connections, then exit 0.
- [ ] **Env vars injected at runtime, not baked into image.** Secrets must come from k8s Secrets or ConfigMaps, not Dockerfile `ENV`.

### k8s deployment checklist

- [ ] **Resource limits are set.** CPU and memory limits prevent one pod from starving the node.
- [ ] **Replicas > 1 for production.** Single-replica deployments have downtime during updates.
- [ ] **Rolling update strategy.** `maxUnavailable: 0, maxSurge: 1` ensures zero-downtime deploys.
- [ ] **Secrets are k8s Secrets, not env vars in the manifest.** `kubectl create secret` or sealed-secrets.
- [ ] **Service ports match container ports.** Mismatch = silent connection refused.
- [ ] **Ingress/DNS is configured for the production domain.** Verify with `curl -sI https://{domain}`.

### Docker/k8s debugging

| Symptom | Check first |
|---|---|
| Container starts then exits | `docker logs {container}` — usually missing env var or crash on import |
| Pod in CrashLoopBackOff | `kubectl logs {pod}` + `kubectl describe pod {pod}` — check readiness probe, resource limits |
| Service unreachable | `kubectl get svc` — verify port mapping, then `kubectl port-forward` to test directly |
| Image not found | Verify image tag, registry auth, pull policy (`Always` vs `IfNotPresent`) |
| "Connection refused" to another service | DNS: use `{service-name}.{namespace}.svc.cluster.local`, not localhost |

Evidence: kindle-connector deploys Python + Flask to k8s. Known issue #9 in CLAUDE.md (non-Vercel deployment barely covered) is now addressed.

---

## Step 10: Post-Deploy Observability

Deploying successfully is not the end. These checks prevent "it's been broken for 3 days and nobody noticed."

### 2M. Post-deploy verification (add to Step 2 checklist)

- [ ] **Hit the production URL after deploy.** Not just the build log — load the actual page. Check for runtime errors in browser console.
- [ ] **Verify API endpoints return expected data.** `curl -s https://your-app.vercel.app/api/health | jq .` — should return 200 with valid JSON.
- [ ] **Check Vercel Function Logs for the first 5 minutes.** Runtime errors often appear only on first real traffic.
- [ ] **For webhook-dependent features:** trigger a test event and verify it arrives. Webhook endpoints can pass build but fail at runtime.

### Monitoring setup for Vercel projects

| What | How | Why |
|---|---|---|
| **Deploy failure alerts** | Vercel dashboard → Settings → Notifications | Know immediately when a push breaks the build |
| **Runtime error monitoring** | `mcp__Vercel__get_runtime_logs` in web sessions, or integrate Sentry/LogRocket | Build success ≠ runtime success |
| **External dependency health** | GHA cron that pings external APIs every 6h (see debug-escalation) | Catch upstream outages before users report them |
| **Uptime monitoring** | Free tier: UptimeRobot or similar. Ping production URL every 5min | Know when the site is down, not when someone tweets about it |

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
