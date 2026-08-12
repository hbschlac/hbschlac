# Session handoff — Kindle app feedback (Hannah + Sam)

**Date:** 2026-08-09 · **Updated:** 2026-08-12
**Harness branch:** `claude/kindle-agent-feedback-4p93uc` (this repo, `hbschlac/hbschlac`)

Spans five feedback rounds, the year-in-review build, the Wish List, Book Clubs,
and the Hobby-plan deploy recovery.

## Where the code lives

All application changes shipped to **`hbschlac/kindle-schlacter-me`** (the Next.js
app that powers `kindle.schlacter.me`) — the correct repo per its own conventions
(one concern per gated PR, squash-merged to `main`, which auto-deploys to Vercel).
The profile repo (`hbschlac/hbschlac`) is not where the app's code belongs, so this
branch carries only this handoff record.

Every PR passed the repo gate before merge: `npx tsc --noEmit && npx vitest run &&
npm run build` (test count grew **176 → 236** across all rounds). PRs
**#69–#114** squash-merged to `main`. (Rounds 1–4 + Book Clubs were by this + a
sibling session; see the deploy-incident note below — production was recovered
after the auto-deploy webhook stalled.)

## Round 1 — initial feedback (all merged to `kindle-schlacter-me:main`)

| # | Feedback | PR |
|---|----------|----|
| 5 | Admin invite: native Share button (opens the iOS share sheet; Copy fallback) | [#69](https://github.com/hbschlac/kindle-schlacter-me/pull/69) |
| 3+4 | Download-to-device delivery mode + Kindle-less signup (account-level mode chosen at signup and in Settings; a "Download to this device" button replaces "Send to Kindle"; new `/api/download`) | [#70](https://github.com/hbschlac/kindle-schlacter-me/pull/70) |
| 2 | Reading history: per-book **notes**, **stars** on Finished, and **back navigation** (URL-driven sub-tabs + a `/book/[key]` back button) | [#71](https://github.com/hbschlac/kindle-schlacter-me/pull/71) |
| 6a | Show each book's **genre** in reading history | [#72](https://github.com/hbschlac/kindle-schlacter-me/pull/72) |
| 6b | **Themes** (curated thematic tags, co-sourced from Google Books categories) on library, detail, book page, and reading history | [#73](https://github.com/hbschlac/kindle-schlacter-me/pull/73) |
| 1 | Personal **reading-stats** panel on History (total, by genre, by source, per-year, avg rating) | [#74](https://github.com/hbschlac/kindle-schlacter-me/pull/74) |

## Round 2 — post-deploy iPhone/iPad feedback (all merged)

| # | Feedback | PR |
|---|----------|----|
| 2,3,4,8,9 | Mobile/rendering polish: note-box overflow on iPhone, "phone/laptop/iPad" copy, `Delivering ✓` badge wrap, Finished-tab stacks on mobile, app-vs-Goodreads split-bar legend, "Finished in the app" relabel | [#75](https://github.com/hbschlac/kindle-schlacter-me/pull/75) |
| 1 | One-tap star ratings on the reads list | [#76](https://github.com/hbschlac/kindle-schlacter-me/pull/76) |
| 5,7a,7b | Reading stats reworked: by-year (no giant all-time total), avg book length, genre drill-down to the library filter | [#77](https://github.com/hbschlac/kindle-schlacter-me/pull/77) |
| 6 | Delete invite links + 5-day expiry | [#78](https://github.com/hbschlac/kindle-schlacter-me/pull/78) |
| 7c | Real "Currently reading" status + started-date tracking → avg time per book | [#79](https://github.com/hbschlac/kindle-schlacter-me/pull/79) |
| 11 | Smarter auto-summary: Open Library + last-resort Goodreads-search fallbacks (so a book Google Books missed still resolves a blurb) | [#80](https://github.com/hbschlac/kindle-schlacter-me/pull/80) |
| 12,4 | iPhone + iPad rendering audit — overflow/clip fixes across history rows, search cards, small-tile controls, toasts | [#81](https://github.com/hbschlac/kindle-schlacter-me/pull/81) |
| 13 | Genre set from the library carries to the reads list and survives finishing | [#82](https://github.com/hbschlac/kindle-schlacter-me/pull/82) |

## Item 10 — year-in-review + History IA + inline genre tagging

The flagship. **Designed first** (a review doc shared with Hannah — the Spotify-
Wrapped-style recap, History restructure, and manual tagging), then built as four
gated phases once she locked the decisions, plus a covers follow-up.

| Phase | What shipped | PR |
|-------|--------------|----|
| 1 | Per-year reading-goal keys + lazy migration (rolls the goal over on Jan 1; past years stay viewable) | [#83](https://github.com/hbschlac/kindle-schlacter-me/pull/83) |
| 2 | History IA: compact "This year in reading" card + `/history/stats` and `/history/reads` sub-pages, each with a "Back to History" link | [#84](https://github.com/hbschlac/kindle-schlacter-me/pull/84) |
| 3 | Inline genre editing (genre only) on library tiles + reads/history rows; Goodreads-only reads get their own genre tag | [#85](https://github.com/hbschlac/kindle-schlacter-me/pull/85) |
| 4 | Year-end "Wrapped": 1080×1920 recap image via `next/og` + Dec-20→Jan-1 banner + Web Share + per-year share picker on `/history/stats` | [#86](https://github.com/hbschlac/kindle-schlacter-me/pull/86) |
| follow-up | Real book covers in the recap — fetched server-side into base64 data URIs with a colored-spine fallback, so a slow/blocked cover can't crash the render | [#87](https://github.com/hbschlac/kindle-schlacter-me/pull/87) |

## Round 3 — post-item-10 feedback (all merged)

| # | Feedback | PR |
|---|----------|----|
| 1 | Add a **"Family & Parenting"** genre (parenting/pregnancy/family books had no home); classifier places it after Biography/History, before Science | [#88](https://github.com/hbschlac/kindle-schlacter-me/pull/88) |
| 3 | **Note editor** in the library book-detail modal (next to the stars) | [#89](https://github.com/hbschlac/kindle-schlacter-me/pull/89) |
| 6 | History **ring click → reads list** (the affordance broke after the IA split) | [#90](https://github.com/hbschlac/kindle-schlacter-me/pull/90) |
| 5,9,10,8 | **Persistent sticky nav** + mobile hamburger + **back-to-top** on long pages (every page/sub-page, iPhone + iPad) | [#91](https://github.com/hbschlac/kindle-schlacter-me/pull/91) |
| 4 | Medium library tiles **2-up on mobile** so the status control isn't clipped ("Not started" → "Not") | [#92](https://github.com/hbschlac/kindle-schlacter-me/pull/92) |
| 2,7 | Admin **metadata backfill** — resolve genres for existing books + Goodreads reads still showing "auto"/Untagged (shared meta store, override-safe) | [#93](https://github.com/hbschlac/kindle-schlacter-me/pull/93) |
| modal | Book-detail modal fixes: note spacing, surfaced genre editor, editable **"started reading" date** | [#94](https://github.com/hbschlac/kindle-schlacter-me/pull/94) |

## Round 4 — bug fixes + the Wish List (this stretch)

Bugs and refinements from live use, then the flagship Wish List.

| Area | What shipped | PR |
|------|--------------|----|
| bug | Admin **"Backfill" button broke ("Network error")** — Google Books 503s made a fixed batch overrun the 60s function limit; now bounded by a **wall-clock budget** (returns partial progress, client loops) | [#95](https://github.com/hbschlac/kindle-schlacter-me/pull/95) |
| admin | **"Counting since" badge** on the active-days stat (the count was accurate but the tracking window is young, so it read as a false positive) | [#96](https://github.com/hbschlac/kindle-schlacter-me/pull/96) |
| feature | **Sort + filter** on the `/history/reads` sub-page (longest/shortest pages, date finished, rating, title; genre + source filters). Page count joined onto reads rows | [#97](https://github.com/hbschlac/kindle-schlacter-me/pull/97) |
| infra | **Hourly cron** runs the genre backfill server-side (no admin clicking) — `/api/cron/backfill-meta`, dedupes by bookKey across all users | [#98](https://github.com/hbschlac/kindle-schlacter-me/pull/98) |
| **Wish List A** | Add a book when a search comes up empty; per-item status (pending/available/found-confirm/failed); one-tap **Get it** / **confirm which book** / **Search manually**; on-open + pooled "Check all" re-checks. Author-gated so it never grabs the wrong book | [#99](https://github.com/hbschlac/kindle-schlacter-me/pull/99) |
| **Wish List B** | **Notifications** (header bell + Library banner) + a **6-hourly detection cron** (`/api/cron/wishlist-check`) so you hear about a book while away | [#100](https://github.com/hbschlac/kindle-schlacter-me/pull/100) |
| **Wish List C** | **Autonomous auto-send**: a confident title+author match on an email account is delivered to the Kindle unattended (non-torrent, quota-respected); anything ambiguous/torrent/device stays one-tap | [#101](https://github.com/hbschlac/kindle-schlacter-me/pull/101) |
| UI | Search page **empty state** (recent-search chips + quick-link cards, all surfaces) + **alphabetical genre dropdown** | [#102](https://github.com/hbschlac/kindle-schlacter-me/pull/102) |

## Status notes

- **Per-year goal keys** migrate the old single goal on first current-year read;
  Jan 1 then shows an empty new-year goal while prior years remain viewable.
- **Wrapped** shares to Instagram Stories via the iOS share sheet (PNG download
  fallback on desktop; there's no direct feed deep-link).
- **Wrapped covers** render as real photos where fetchable (Open Library / Google
  Books / gr-assets), otherwise branded colored spines with the title.
- The **rendering audit** (items 4/12) and the **Wrapped image render** were verified
  at the code/build level and via an ad-hoc `next/og` render test — the sandbox
  can't reach the authed live app or the cover hosts, so live UI confirmation is on
  Hannah's session (e.g. History → All-time stats → "Your Wrapped").
- **Genre** metadata was already fully built (round 1 surfaced it in history);
  **themes** were new in round 1. Inline genre editing (item 10e) is **genre only** —
  themes stay auto-detected per Hannah's decision.
- **Download-to-device** on iPhone saves the `.epub` to Files/Books (iOS Safari
  Downloads), not into the Kindle app — intended for a non-Kindle reader.
- **Wish List** is internally `watchlist` (KV `kindle:watchlist:{email}`), DISTINCT
  from the "Want to Read" list (internally `wishlist`, route `/future`). New routes:
  `/api/watchlist` (CRUD), `/api/watchlist/check`, `/api/notifications`. Auto-send
  lives in `lib/watchlistDeliver.ts` and is called only from the cron.
- **Three crons now run** (`vercel.json`): the existing bounce-poll (07:00) + diag-
  digest (14:00), plus **`/api/cron/backfill-meta` hourly (:22)** and
  **`/api/cron/wishlist-check` every 6h (:42)**. All use `CRON_SECRET` bearer auth.
- **Availability checks call `searchOne()` directly**, not the auth-gated
  `/api/search/source` route — a server-to-server fetch has no session cookie and
  would 401 (this also fixed the latent same bug in the old `/api/wishlist/check`).
- Wish List UI + auto-send were verified at the code/build level; the sandbox can't
  reach the authed live app or drive a real Kindle send, so live confirmation is on
  Hannah's session (add a book → let the cron auto-deliver, or tap "Get it").
- A **targeted learning** from this session's real bugs was added to the
  **`vercel-ship`** skill (serverless wall-clock budgeting + the auth-gated-internal-
  route trap + the vitest `@/`-alias gotcha). Still **no standalone "kindle" skill** —
  the app remains a worked example inside general skills.

`kindle-connector` (the self-hosted torrent bridge) was not touched this session.

## Round 5 — Book Clubs (a sibling session)

Follow the national reading clubs (Oprah / Reese's / Read with Jenna); each new
monthly pick auto-delivers to the library, badged with the club.

| # | What | PR |
|---|------|----|
| 104 | Follow clubs: nav tab + `/book-clubs` page, follows store, per-club backfill | [#104](https://github.com/hbschlac/kindle-schlacter-me/pull/104) |
| 105 | Scrape each club's current pick + show picks on the page | [#105](https://github.com/hbschlac/kindle-schlacter-me/pull/105) |
| 106 | Auto-download a new pick to the library (torrent-inclusive, author-gated) + a monthly cron | [#106](https://github.com/hbschlac/kindle-schlacter-me/pull/106) |
| 107 | Year-end "finished by club" count on the stats page | [#107](https://github.com/hbschlac/kindle-schlacter-me/pull/107) |
| 108 | Wish List auto-deliver from torrent sources too (drop the non-torrent guardrail) | [#108](https://github.com/hbschlac/kindle-schlacter-me/pull/108) |
| 109 | Club-pick badge on each library tile | [#109](https://github.com/hbschlac/kindle-schlacter-me/pull/109) |

Files: `lib/bookclubs/*` (registry, follows store, refresh/scrape, deliver),
`/api/book-clubs/*`, `/api/cron/book-club-scrape`.

## Deploy incident + Hobby plan (Aug 11–12) — IMPORTANT for the next session

- **The project is on the Vercel HOBBY plan** (a stale note said Pro — corrected).
  Hobby: **max 2 cron jobs, daily-only cadence; 60s function cap** (`maxDuration>60`
  is silently capped, not rejected). #111 consolidated 5 crons → **2**: a daily
  dispatcher `/api/cron/daily` (runs diag-digest + poll-bounces + wishlist-check +
  backfill-meta in one 60s function) + the monthly `/api/cron/book-club-scrape`.
  **Do not add a 3rd cron or a sub-daily schedule** — it fails the Hobby deploy.
- **The GitHub→Vercel auto-deploy webhook silently stopped** after a burst of ~13
  rapid merges (#98–#110): `main` advanced but ZERO deployments were created (not
  even failed ones), so prod sat on #97 for hours. **A remote sandbox can't fix or
  force it** — no `VERCEL_TOKEN`, and Vercel API egress is proxy-blocked (403 on
  `api.vercel.com`); `npx vercel` can't run. **Fix (Hannah, dashboard):** project →
  Settings → Git → Disconnect then Connect (re-registers the webhook + redeploys
  latest). The dashboard "Redeploy" button re-runs the OLD commit — it does NOT ship
  latest. Recovered on Aug 12: production now serves the latest (#111+), auto-deploy
  restored, health check clean (no runtime errors). The **Vercel MCP tools work**
  server-side for read-only verification (`get_project` / `list_deployments` /
  `get_runtime_logs`).
- Docs updated so any sandbox inherits this: `kindle-schlacter-me/CONTINUE.md`
  ("Platform + deploy reality" section) + `CHANGELOG.md` (#111/#114).
