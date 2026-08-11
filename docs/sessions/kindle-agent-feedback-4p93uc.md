# Session handoff — Kindle app feedback (Hannah + Sam)

**Date:** 2026-08-09 · **Updated:** 2026-08-11
**Harness branch:** `claude/kindle-agent-feedback-4p93uc` (this repo, `hbschlac/hbschlac`)

Spans two feedback rounds plus the flagship year-in-review build.

## Where the code lives

All application changes shipped to **`hbschlac/kindle-schlacter-me`** (the Next.js
app that powers `kindle.schlacter.me`) — the correct repo per its own conventions
(one concern per gated PR, squash-merged to `main`, which auto-deploys to Vercel).
The profile repo (`hbschlac/hbschlac`) is not where the app's code belongs, so this
branch carries only this handoff record.

Every PR passed the repo gate before merge: `npx tsc --noEmit && npx vitest run &&
npm run build` (test count grew **176 → 203** across both rounds). Production deploy
after the final PR (#87) is READY.

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
- There is **no standalone "kindle" skill** in this repo — the app appears only as
  worked examples inside general skills, so no skill needed changes.

`kindle-connector` (the self-hosted torrent bridge) was not touched this session.
