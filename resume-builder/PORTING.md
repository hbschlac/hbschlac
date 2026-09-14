# Porting Bullet Bench to Vercel

The bench runs as a private Claude Artifact. The bullet bank lives in **this git repo**, not in
the artifact, so moving hosts costs nothing in data — that was the point of keeping it here.

## What would need building

| Artifact capability | Vercel replacement | Real cost |
|---|---|---|
| private by default | auth (Vercel password protection, or NextAuth) | Without it, anyone with the URL reads the whole employment archive |
| `sample` (Claude, on her account) | Anthropic API key in env vars | A real secret to store, rotate, and pay for separately from her Claude sub |
| `db` (per-artifact store) | Postgres / Upstash | Schema, migrations, backups |
| `downloads` | a normal `<a download>` | Trivial |

## What ports unchanged

- `data/bullets.json` — the whole bank, already plain JSON
- `scripts/enrich.py` — all the rules
- The linter and slop tables in `app/index.html` — pure functions over a bullet record
- `RUNBOOK.md` — the Composio calls are account-level and host-independent

## Shape

Next.js App Router on the existing `schlacter-me` Vercel project, at `/bench`:

```
app/bench/page.tsx          the workbench (port app/index.html)
app/api/jd/route.ts         JD parse -> Anthropic API (server-side key)
app/api/check/route.ts      Final check -> Anthropic API
lib/bullets.ts              import data/bullets.json
lib/lint.ts                 format + slop rules (port from index.html)
```

Deploy loop: web sessions can't push to `hannah-portfolio` directly — branch → PR → merge, which
is slower than republishing an artifact.

## Honest recommendation

Don't, unless the artifact becomes a real constraint. The artifact is **more private by default**
than a Vercel app would be before auth is built, and it has **no secret to leak**. The one thing
Vercel buys is the `schlacter.me` domain — and the *published resume links* already live there
via the redirect, which is the part outsiders actually see. Keeping the data in git already
gives her the ownership; the hosting is the cheap half to move later.
