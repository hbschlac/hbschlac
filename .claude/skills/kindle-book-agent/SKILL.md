---
name: kindle-book-agent
description: >
  Dev and ops for Hannah's Kindle book-delivery system: the kindle-schlacter-me
  web app (Next.js 16 + Upstash Redis + Resend) and the kindle-connector torrent
  bridge (Flask + Jackett + qBittorrent + Calibre, self-hosted). Covers the
  multi-source search waterfall, the Send-to-Kindle email pipeline, the `kindle:`
  KV schema, the two-bridge failover, deploy/verify, and the E999 debugging lore.
  Activates on work in either repo, or on "a book didn't arrive on my Kindle" triage.
---

# kindle-book-agent

Two repos, one product: type a book title, get the EPUB on your Kindle, no steps.
This skill is the map so a session does not have to re-read six docs and two
codebases to make a safe change.

## Activation

- Explicit: `/kindle-book-agent`, "work on kindle-schlacter-me", "the kindle
  bridge / connector", "a book didn't show up on the Kindle", "why did the send fail".
- Implicit: editing `kindle-schlacter-me` or `kindle-connector`, or touching
  `lib/sources/*`, the send pipeline, any `kindle:` KV key, or `bridge/app.py`.
- Do NOT use for: schlacter.me portfolio work (use `portfolio-dev`). For the
  actual Vercel deploy mechanics of the web app, defer to `vercel-ship`.

**Attach the repos first.** Neither is cloned into a fresh web session. Run
`add_repo hbschlac/kindle-schlacter-me` and `add_repo hbschlac/kindle-connector`,
clone each one at a time, then `register_repo_root`. You can only push to
`hbschlac/hbschlac` from a web session, so land changes to these repos as a PR via
the GitHub MCP tools (or on the laptop).

## The system in one picture

```
                 kindle.schlacter.me  (Vercel: Next.js + Upstash KV + Resend)
                          │
        search ──────────┤ 4 fast sources IN PARALLEL, dedupe by title::author
   Standard Ebooks ──────┤   standardebooks · gutenberg · openlibrary · libgen
        + torrent lane ──┘   torrent results come from the bridge (~30s, folded in late)
                          │
        send  ────────────┤ fetch EPUB → jszip fixes metadata+cover → Resend email
                          │   subject = title, body = "Convert", to the user's @kindle.com
                          ▼
                    Amazon Send-to-Kindle  ──►  Kindle library

   Torrent / heavy downloads offload to the bridge (past Vercel's function timeout):
                          │
   kindle-connector  ◄────┘  POST /search · POST /prepare-file · GET /file/<id>
   (Flask, self-hosted)      Jackett → qBittorrent → Calibre clean → Gmail SMTP → @kindle.com
```

The web app is the front door and does the legal free sources itself. The bridge
is the torrent lane and the heavy-download proxy. They share one goal (a clean
EPUB Amazon will accept) and both end at a `@kindle.com` address.

## Two repos, two roles

| Repo | Stack | Host | Role | Deploy skill |
|---|---|---|---|---|
| `kindle-schlacter-me` | Next.js 16 App Router, React 19, Tailwind 4, `@upstash/redis`, Resend, jszip | Vercel (`hannah-schlacters-projects/kindle-schlacter-me`) | Web app: auth, search, library, send | `vercel-ship` |
| `kindle-connector` | Python 3.11 Flask, Jackett, qBittorrent, Calibre | Self-hosted, two bridges (see below) | Torrent search → download → clean → email | `code-builder` |

---

## kindle-schlacter-me (the web app)

**Scripts:** `dev` = `next dev`, `build` = `next build --webpack`, `test` =
`vitest run`, `lint` = `next lint`. There is a Vitest suite next to most `lib`
files (`*.test.ts`). Run it before pushing. There is a SessionStart hook that
runs `npm install` only when `CLAUDE_CODE_REMOTE=true`.

**Auth:** magic-link only. `/api/auth/request` mints a 15-min token
(`kindle:magic:*`), the emailed link hits `/verify`, and a 30-day session cookie
(`kindle:session:*`) is set. `bcryptjs` is in the tree from an abandoned password
path, so do not build on it. Magic-link is the shipped route. Invite-only:
`/api/bootstrap` (once) seeds the admin, admins mint invites at `/admin`.

**Search waterfall** (`lib/sources/index.ts`):
- Fast sources run in parallel and paint immediately: `standardebooks`,
  `gutenberg`, `openlibrary`, `libgen`. The torrent lane is separate and slower
  (~30s through the bridge), folded in when it returns. The UI drives this
  per-source via `/api/search/source`.
- Dedupe key is `` `${title}::${author}` `` lowercased, first hit wins, then sort
  by `SOURCE_PRIORITY`.
- Empty-result recall: if a query yields nothing and parses as "Title by Author",
  it retries with just the title (so "Death by Black Hole" still works on the
  first pass and never gets mis-split).
- **Anna's Archive was removed** as a source: its free download needs a per-session
  JS challenge no server can solve. LibGen covers the same catalog with a working
  two-hop `ads.php → get.php` chain and carries in-copyright titles the
  public-domain sources lack.

**Send pipeline** (`/api/send`, `lib/email.ts`):
- Fetch the EPUB, fix OPF metadata + cover with `jszip`, then Resend it to the
  user's Kindle address. From `kindle@schlacter.me` (domain verified on Resend),
  **subject = the book title, body text = `"Convert"`**, attachment `slug.epub`.
- Hard cap 22 MB before send (Resend's real base64 ceiling is ~30 MB). Over that,
  surface "try a different source", do not let it 408.
- Sends are server-tracked as jobs (`kindle:sendjobs:*`) and deduped by
  book + targets so a refresh or PWA cold-start cannot double-send or double-charge
  the daily quota (`kindle:quota:send:*`, default 20/day).

**Bridge offload** (`lib/sources/torrent.ts`): the torrent lane and LibGen direct
downloads are pushed to the connector to get past Vercel's function timeout.
`pickBridge()` health-checks `KINDLE_BRIDGE_URL`, then `KINDLE_BRIDGE_URL_FALLBACK`,
caches the healthy one, and calls `POST /search`, `POST /prepare-file`, polls
`GET /jobs/<id>`, and streams the EPUB from `GET /file/<id>?token=...`.

**Delivery signal** (Amazon gives no on-device confirmation, so this is inferred):
- Resend webhook `/api/webhooks/resend` (`RESEND_WEBHOOK_SECRET`) records
  `delivered` / `bounced` per Kindle **address** in `kindle:devicestate:{addr}`,
  monotonic so out-of-order webhooks cannot flip the banner backwards.
- `/api/cron/poll-bounces` (`CRON_SECRET`) is the backstop. A successful real send
  stamps the device and supersedes a stale bounce.

**Env vars:** `KV_REST_API_URL`, `KV_REST_API_TOKEN`, `RESEND_API_KEY`, `APP_URL`,
`ADMIN_BOOTSTRAP_EMAIL`, `SUPPORT_EMAIL` (opt), `CRON_SECRET`,
`RESEND_WEBHOOK_SECRET`, `GOOGLE_BOOKS_API_KEY` (book summaries/ratings),
`KINDLE_EMBED_SUMMARY` (opt flag), and the bridge trio `KINDLE_BRIDGE_URL`,
`KINDLE_BRIDGE_URL_FALLBACK`, `KINDLE_BRIDGE_TOKEN`.

### KV schema (all keys prefixed `kindle:`)

Everything lives in one Upstash DB. Never write outside the `kindle:` namespace.

| Key | Type | What |
|---|---|---|
| `kindle:user:{email}` | JSON | The User record (name, `kindleEmails[]`, invitedBy, flags) |
| `kindle:users` | set | All user emails |
| `kindle:admins` | set | Admin emails |
| `kindle:kindleemail:{addr}` | string | Reverse index: Kindle address → owning account (enforces one-owner) |
| `kindle:devicestate:{addr}` | JSON | Per-address delivered/bounce/success, monotonic |
| `kindle:magic:{token}` | JSON (900s) | Magic-link token |
| `kindle:session:{token}` | JSON (30d) | Session |
| `kindle:invite:{token}` / `kindle:invites` | JSON / set | Invites (7-day TTL) |
| `kindle:history:{email}` | list (≤200) | Send history |
| `kindle:books:{email}` | hash | The user's library, field = `bookKey(title,author)` |
| `kindle:bookmeta:{bookKey}` | JSON | Summary + rating, **shared across users**, 7-day negative cache |
| `kindle:sendjobs:{email}` | hash | Server-tracked send jobs (dedupe/anti-double-send) |
| `kindle:searches:{email}` | list (≤200) | Search history |
| `kindle:searchcache:{kind}:{q}` | JSON (300s) | Per-source search cache |
| `kindle:wishlist:{email}` | hash | Future reads |
| `kindle:goodreads:{email}` / `kindle:readinggoal:{email}` | JSON | Imported Goodreads reads + yearly goal |
| `kindle:quota:send:{email}:{date}` | int (25h) | Daily send cap |
| `kindle:lastseen:` / `kindle:activedays:` / `kindle:seenguard:{email}` | mixed | Admin activity analytics (throttled ~1/hr) |

---

## kindle-connector (the torrent bridge)

`bridge/app.py` is the whole service (Flask, single file). Owned by Hannah,
collaborator Sam Giddins. Personal, not-for-profit use.

**Two bridges, automatic failover:**
- **Primary:** Sam's k8s cluster, `https://kindle-connector-bridge.schlacter.me`.
- **Fallback:** Hannah's Oracle Always Free VM, `https://oracle-books.taile2c385.ts.net`
  (Tailscale host `oracle-books`, `E2.1.Micro`, 1 GB RAM + swap).
- The web app hits the primary and fails over to the fallback (see `pickBridge`).

**Pipeline** (`process_job`): `jackett_search` (queries each configured indexer in
parallel, ranks by ebook-format → under the email size limit → MyAnonamouse
preference → seeders → size, caps to top 5) → `qbit_add` (adds a magnet, or fetches
the `.torrent` and computes the btih infohash so a private-tracker link or a qBit
409 de-dupe still resolves) → poll up to 60 min with dead-torrent detection (~90s
of zero progress and zero seeders fails fast) → `find_best_ebook` →
`normalize_epub` (belt) → `calibre_clean_epub` (the E999 fix) → `email_to_kindle`
(Gmail SMTP). `POST /jobs/<id>/retry` tries the next untried torrent.

| Endpoint | Purpose |
|---|---|
| `GET /health` | Liveness (no auth) |
| `POST /request` | `{title, author}` → full search-to-Kindle pipeline |
| `POST /search` | `{q}` → Jackett search only (what the web app calls) |
| `POST /prepare-file` | `{title, author, magnet?, link?}` → download+clean, no email, then fetch via `/file/<id>` |
| `POST /proxy-download` | `{url}` → stream a direct URL (e.g. a LibGen `get.php` link) to disk |
| `GET /file/<id>?token=` | Stream the prepared file once `done` (202 while running) |
| `GET /jobs/<id>` · `GET /jobs` · `POST /jobs/<id>/retry` | Job status / last 50 / retry |
| `GET /admin/diag` · `GET /admin/logs` · `POST /admin/restart` | Phone triage (see below) |

All routes except `/health` auth on `X-Bridge-Token: $BRIDGE_TOKEN` (or `?token=`).
`BRIDGE_TOKEN` equals `KINDLE_BRIDGE_TOKEN` in the web app's Vercel env, and is in
Hannah's 1Password. It is NOT in either repo.

**Fixing it from your phone (no SSH, no kubectl, no deploy):**

```bash
BR=https://kindle-connector-bridge.schlacter.me   # fallback: https://oracle-books.taile2c385.ts.net
TOKEN=...                                          # BRIDGE_TOKEN

curl "$BR/admin/diag?token=$TOKEN" | jq            # whole-system health: qbit / jackett / calibre / disk / jobs
curl "$BR/admin/logs?token=$TOKEN&grep=E999"       # read the real error (case-insensitive)
curl "$BR/jobs?token=$TOKEN" | jq '.[0:5]'         # recent jobs + failure messages
curl -X POST "$BR/admin/restart?token=$TOKEN"      # clear a stale qBit session / wedged thread (no rebuild)
```

Runtime-fixable from the phone: a wrong or E999 book takes `POST /jobs/<id>/retry`,
a wedged bridge takes `/admin/restart`, and a down indexer is named by
`/admin/diag` (fix it in the Jackett UI). A **code** change to `app.py` needs a
redeploy (it is `COPY`d into the image). A phone can push that code, but a box has
to roll the image.

**Config lives in `.env` on the host** (never committed): `JACKETT_API_KEY`,
`JACKETT_INDEXERS` (leave `all`: the bridge auto-discovers and fans out in
parallel), `QBIT_USER`/`QBIT_PASS`, `SMTP_USER`/`SMTP_PASS` (Gmail App Password),
`KINDLE_EMAIL`, `BRIDGE_TOKEN`, `KINDLE_MAX_EMAIL_BYTES` (25 MB), `PROXY_MAX_BYTES`
(200 MB), `MAM_*`. SMTP host/port are set in `docker-compose.yml` (`smtp.gmail.com:587`).

**Do NOT change without a reason** (each is load-bearing):
- The Calibre `ebook-convert` step: it is the E999 fix.
- `normalize_epub`: cheap belt-and-suspenders before Calibre.
- `qbit_login()` accepting HTTP 204: new qBittorrent returns 204, old returned `Ok.`.
- The single-stage Docker build for Calibre: its installer needs runtime libs at install time.

---

## The E999 lesson (load-bearing lore)

Amazon Send-to-Kindle rejects many torrent-sourced EPUBs with an opaque
"E999 Internal Error" and zero diagnostics. The fix is **Calibre `ebook-convert`
from EPUB to a clean EPUB**. It reparses OPF metadata, strips non-spec elements,
and re-zips properly, which Amazon's strict parser accepts. A file that opens
fine in every reader and passes `unzip`/`file` can still E999.

- **Accepted by Send-to-Kindle (2026):** EPUB, PDF, DOC/DOCX, HTML/HTM, RTF, TXT,
  JPEG/GIF/PNG/BMP.
- **Rejected:** AZW3 (converting to it gives E001 "Unsupported File Format", since
  Amazon dropped it as an upload format) and MOBI (deprecated 2022). Do not "convert to
  AZW3/MOBI to fix it".
- **Diagnostic order for a new E999:** send a known-good Gutenberg EPUB (proves the
  mail path), then a `.txt` (proves the address is allow-listed), then Calibre-clean
  your file. If the first two land and yours does not, cleaning it is the whole answer.
- **Send-to-Kindle setup requirements:** the bridge's SMTP path needs a Gmail
  **App Password** (2FA on). The sending address must be on Amazon's *Approved
  Personal Document E-mail List* (`amazon.com/hz/mycd/myx` → Personal Document
  Settings), or Amazon silently drops the attachment. Gmail's 25 MB per-message cap
  is the binding limit, not Amazon's 50 MB. (The web app's Resend path from `kindle@schlacter.me`
  is a separate sender and separate 22 MB cap.)

## Dead ends: do not re-derive

| Thing | Why it fails |
|---|---|
| Anna's Archive downloads | Per-session JS challenge, unscriptable. Removed as a source. |
| oceanofpdf.com | Cloudflare bot detection, 403 on any non-browser request. |
| bdebooks.com | Account-walled, exposes no direct file URLs. |
| AZW3 / MOBI to Kindle | Not accepted as Send-to-Kindle uploads (see above). |
| Guessing MIME / filename / body to fix E999 | Not the cause. Instrument first, change one variable. |
| Oracle Resource Manager (Terraform) Stack | Drops SSH key + public IP. Use the Compute UI form. |
| Oracle A1.Flex (ARM) free VM | Capacity-locked in US regions. Use `E2.1.Micro` x86. |

## Deploy and verify

- **Web app:** push to `main` → Vercel auto-deploys. Gate on `tsc --noEmit`,
  `next build --webpack`, and `vitest run`. Deploy mechanics and the type-drift
  failure mode live in `vercel-ship`.
- **Bridge (Oracle fallback):** the compose dir is `/home/ubuntu/books` (scp-managed,
  not a git clone). Iterate with
  `scp bridge/app.py ubuntu@oracle-books:/home/ubuntu/books/bridge/app.py` then
  `ssh ... 'cd /home/ubuntu/books && sudo docker compose up -d --build bridge'`.
- **Bridge (k8s primary):** `./deploy.sh` on a host with docker + kubectl.
- **Verify in production, do not trust a container start.** Confirm `/health` returns
  `{"ok": true}` AND run one real `POST /request` for a known-good book
  ("Pride and Prejudice" / Jane Austen) through to `status: done` on the Kindle, and
  check no new E999 mail in `hbschlac@gmail.com`.

## Working conventions (Hannah's, apply to both repos)

- **Scope discipline.** Before anything with more than 2 moving parts (a webhook,
  a cron, a new service, a headless browser), state the boring version in one
  sentence, the ambitious version in two bullets, and wait for a pick. Default boring.
- **Change one variable per attempt** when debugging opaque external services
  (Send-to-Kindle, MAM). The E999 saga cost extra time by batching fixes.
- **Voice:** terse, builder-not-marketer, explain in plain words (Hannah is a PM,
  not an engineer). No em-dashes in prose, no reintroduced semicolons, no AI slop
  ("crush", "unlock", "leverage", "dive deep"), no "it's not X, it's Y".
- **Sandbox:** a web session can only push to `hbschlac/hbschlac`. Ship changes to
  these repos as a PR through the GitHub MCP tools, or hand exact commands to the laptop.

## Known gaps / good next pickups

- `kindle-schlacter-me` has **no CLAUDE.md** (only a `CONTINUE.md` handoff). Run
  `project-bootstrap` to generate one so future sessions get the conventions.
- **LibGen relevance** is weak on bare titles ("the nightingale" misses the Kristin
  Hannah bestseller). The fix is Open Library query enrichment + re-rank, fully
  specced in `kindle-schlacter-me/CONTINUE.md` (Tasks 1 and 2).
- `lib/sources/index.ts` `resolveDownload` carries a **stale comment** ("libgen is
  metadata/cover-only") that contradicts `libgen` being in `DOWNLOADABLE_SOURCES`.
  Reconcile it so the intent is unambiguous.
- Bridge backlog: multi-user (it is one `KINDLE_EMAIL` today), IMAP-based auto-retry
  on async E999 bounces, and CI auto-deploy (the last manual step).
- The bridge docs still call `app.py` "~350 LOC", though it is far larger now. Refresh if you touch them.
