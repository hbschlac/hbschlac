# Baby — Product Requirements

**Status:** Draft
**Owner:** Hannah
**Users:** Two (Hannah + partner)
**Due date (D):** Tuesday, December 8, 2026
**Last updated:** 2026-08-31

> **Anchor date:** milestones are pinned to **D** = Dec 8, 2026 — 14 weeks out as of this
> revision. If D moves, §11 moves with it.

---

## 1. What this is

A private app for two people to plan for a baby and then track one. Not a product for
other parents. No accounts to sell, no growth loop, no market.

It has two halves with opposite lifespans:

| Half | Lives | Dies |
|------|-------|------|
| **Planning** — registry, names, nursery | Now until D | Goes read-only at birth |
| **Tracking** — feeds, sleep, diapers, growth | D onward | Fades around month 12 |

Planning is built and shipped. Tracking is not built, and it's the half that matters.

## 2. Why build this instead of using an existing app

Huckleberry, Baby Tracker, and half a dozen others already do this, most of them well.
There is no gap in the market and this document should not pretend there is one.

The actual reasons to build it:

- You own the data. No subscription, no ads, no company deciding to sunset it.
- It does your workflow exactly, with nothing else on screen.
- You want to build it.

Those are sufficient reasons for a personal project. They are *not* sufficient to
tolerate a worse experience. **The bar: on day one, this must be at least as fast and as
reliable as the app you'd otherwise download.** If it isn't, you will stop using it after
one bad night and never come back.

Stated up front so it isn't a failure later: **if this fails the 3am test in the first
week, switch to an off-the-shelf app.** A half-logged dataset is worse than a complete one
somewhere else. Building this is not a commitment to using it.

## 3. Users and context

Two adults, two phones, one baby. Both are exhausted. Assume every interaction happens:

- one-handed, because the other arm is holding a baby
- in the dark, without glasses
- half-asleep, with no working memory of what the last screen said
- possibly with no usable wifi, in a room at the far end of the house

That context is the whole design brief. Every requirement below follows from it.

**Both parents must log.** If the app is even slightly awkward, one person becomes the
scribe, resents it, and the data goes stale the first time they're out of the house. Equal
ease of use is a design goal, not a nicety.

## 4. Goals

1. Answer "when did she last eat, and how much" in under two seconds, without tapping.
2. Log a completed feed in under ten seconds, three taps, without reading.
3. Both phones show the same truth, within seconds, without either person doing anything.
4. Never lose a log. Not on bad wifi, not on a force-quit, not on a dead battery.
5. Get the planning half done before D so it stops taking attention.

## 5. Non-goals

Explicitly not building. Each of these is a real temptation and each is a "no":

| Not building | Why |
|---|---|
| Growth percentile curves | That's medical interpretation. The pediatrician does it. |
| Any "is this normal" guidance | Same. Out of scope, permanently. |
| Photos, milestones, memory book | The camera roll already does this better. |
| Push notifications and reminders | A newborn is its own reminder. A buggy 3am push is a disaster. |
| Sharing, invites, multi-household | There are two users. There will always be two users. |
| Sleep training programs, schedules, routines | Opinionated content. Not our job. |
| Charts and analytics | Tempting to build, rarely opened. Revisit at month 3 if the data is actually complete. |
| Native iOS/Android app | An installed PWA clears the bar. A second toolchain does not. |

## 6. Constraints

- **14 weeks, and the back half is worth less than the front half.** Calendar time is
  not the binding constraint — energy is. The third trimester starts in early October.
  Schedule the hard technical work before it, not after.
- **Two devices, always in sync.** This is what off-the-shelf apps give you for free and
  it is the entire reason phase 2 needs a backend.
- **Offline must work.** Not degrade gracefully — work. See §8.4.
- **One developer, working in gaps.** Prefer boring, proven, small.

---

## 7. Phase 1 — Planning (shipped)

Four routes, live and working: overview, registry, names, nursery. State persists in
`localStorage` through the `StorageAdapter` seam in `src/lib/storage.ts`.

### 7.1 What's left before D

| # | Requirement | Priority |
|---|---|---|
| P1.1 | Registry, names, and nursery data sync between both phones | Must — see §8.3, same backend |
| P1.2 | Real prices entered on must-have registry items, so the estimate means something | Must — by mid-October |
| P1.3 | Nursery checklist worked down to zero | Should — the point of the list |
| P1.4 | Names narrowed to a shortlist of ≤5 | Should — this has a hard deadline too |

**The registry has an earlier deadline than everything else in this document.** It has to
be finished before invitations go out, and gifts need shipping time — which in practice means
usable by **mid-October**, not by D. It is the one piece of the planning half that can't slip.

No new planning features. The planning half is done being built.

### 7.2 Sunset

At birth, planning goes read-only rather than being deleted:

- Registry and nursery: archived, reachable from a footer link, off the main nav.
- Names: collapses to the chosen name. Keep the list; it's a nice artifact.
- Nav becomes tracker-first the moment the first feed is logged.

**Requirement P1.5:** archiving is a single manual action, not a date trigger. Babies
don't arrive on schedule.

---

## 8. Phase 2 — Tracker (the actual work)

### 8.1 The 3am test

This is the primary acceptance criterion. Everything else is subordinate to it.

> From a locked phone, using one hand, in the dark, log a completed 20-minute left-side
> feed in **under 10 seconds** and **at most 3 taps**, without reading any text on screen.

If a proposed feature makes this slower, it doesn't ship. Test it for real, in the dark,
before D — not on a desk in daylight.

### 8.2 Logging

| # | Requirement | Priority |
|---|---|---|
| T1 | Log a feed: breast (side, duration) or bottle (volume) | Must |
| T2 | **Live nursing timer** — start it, lock the phone, come back. Timer survives app close, phone lock, and browser eviction because it's stored server-side, not in a JS interval. | Must |
| T3 | The *other* phone shows a feed in progress and its elapsed time | Must |
| T4 | Log a diaper: wet / dirty / both | Must |
| T5 | Log sleep: start and end, or a completed duration after the fact | Must |
| T6 | Every log records **who** entered it | Must — "did you already feed her?" is the most-asked question in a house with a newborn |
| T7 | Every log defaults to *now*, and the time is editable in one tap | Must — half of all logging is retroactive |
| T8 | Edit or delete any log | Must — everything gets mis-tapped at 3am |
| T9 | Log growth: weight, length, head circumference, with a date | Should — a few times a year, entered from a pediatrician visit. Low frequency, low priority, no curves. |
| T10 | Duplicate guard: if a feed was logged in the last 10 minutes, say so before accepting another | Should — two half-asleep people double-log constantly |

### 8.3 Sync

| # | Requirement | Priority |
|---|---|---|
| T11 | A log entered on one phone appears on the other within ~5 seconds when both are online | Must |
| T12 | Logs are append-only events with client-generated UUIDs | Must — makes retry safe and idempotent |
| T13 | Conflicts resolve last-write-wins per record. No CRDTs, no merge UI. | Must — two people editing the same log is vanishingly rare and not worth the complexity |
| T14 | Auth is a shared household passcode exchanged for a long-lived cookie. Each device is named once, at setup, to attribute logs. | Must — no OAuth, no email, no password reset. Two users. |

### 8.4 Offline

The single most important technical requirement, and the one most likely to be
under-built.

| # | Requirement | Priority |
|---|---|---|
| T15 | The log button **never** waits on the network. Write locally, confirm instantly, sync in the background. | Must |
| T16 | Queued writes survive a force-quit and flush on reconnect | Must |
| T17 | Reads serve last-known state offline. The app opens and is useful with no connection. | Must |
| T18 | Sync state is visible but quiet — a small indicator, never a blocking modal or an error dialog | Must |

A spinner at 3am is a failure. An error dialog at 3am is how the app gets deleted.

### 8.5 Home screen

Answers the standing questions with zero taps, in type large enough to read without
glasses:

- Time since last feed, plus which side
- Time since last diaper, and what kind
- Whether a feed is in progress right now, and for how long
- Who logged the last entry

Below that: the log buttons. Nothing else. No charts, no tips, no summary cards.

**T19 (Must):** installable to the home screen and launches full-screen. If it opens in a
browser tab with an address bar, it reads as a website and won't get used.

### 8.6 Nice-to-have, explicitly after D

| # | Requirement |
|---|---|
| T20 | Daily rollup: feed count, total volume, diaper count, longest sleep |
| T21 | CSV export, for pediatrician appointments |
| T22 | Pumped-milk inventory (what's in the fridge, what's in the freezer, what expires) |

None of these block launch. T22 is the one most likely to actually earn its place.

---

## 9. Technical requirements

### 9.1 The stack decision

Phase 1 is Next.js 15 App Router, React 19, TypeScript, Tailwind v4, no runtime
dependencies beyond Next and React. Phase 2 keeps that and adds exactly two things:
a hosted Postgres and a write queue.

**Decision: hosted Postgres (Neon or Supabase) behind Next.js Route Handlers.**

Rejected alternatives:

- **Firebase/Firestore** — gives sync and offline for free, which is genuinely tempting.
  Rejected because it pulls in a large SDK, a second mental model, and vendor lock-in for
  a dataset that is a few thousand rows.
- **Staying on localStorage** — no. Two phones diverge immediately and there is no merge
  story. This is the one shortcut that must not be taken.
- **A local-first sync engine (Replicache, ElectricSQL, etc.)** — correct tool, wrong
  timeline. Learning one in the weeks before a birth is how this doesn't ship.

### 9.2 Implementation requirements

| # | Requirement |
|---|---|
| A1 | Write a second `StorageAdapter` (HTTP) in `src/lib/storage.ts`. Phase 1 pages change zero lines. |
| A2 | The tracker types already in `src/lib/types.ts` are the schema. Don't invent a third vocabulary. |
| A3 | Server owns time. Clients send their own timestamps; the server records receipt time too. Two phones with drifting clocks will otherwise produce a nonsense timeline. |
| A4 | All log writes are idempotent on client UUID, so retries can't duplicate. |
| A5 | Daily automated backup of the database. Losing the first three months of data is unrecoverable in a way that matters. |

## 10. Success metrics

For a two-person tool, the only honest metrics are behavioral:

| Metric | Target | What it tells you |
|---|---|---|
| Share of feeds actually logged, first 2 weeks | > 90% | The only metric that matters. Below this, the tool failed. |
| Median time to log a feed | < 10 seconds | The 3am test, measured |
| Logs entered by the less-frequent parent | > 30% | Whether one person became the scribe |
| Data-loss incidents | 0 | Non-negotiable |
| Still in use at week 6 | Yes | Whether it beat the alternative |

## 11. Schedule

**D = Tuesday, December 8, 2026.**

The first draft of this document assumed a few weeks total and crammed the backend into the
last month. With 14 weeks, that's the wrong shape. The backend moves to **September**, while
the energy for it exists, and the gate at D-14 becomes a safety net instead of a coin flip.

Assumes evenings and pieces of weekends, not focused weeks.

| By | What | Gate |
|---|---|---|
| **Oct 13** (D-56) | Postgres provisioned, schema deployed, HTTP adapter written, planning half syncing between both phones | Proves the whole architecture on low-stakes data |
| **Oct 13** | Registry finalized — real items, real prices | Driven by shower timing and shipping lead times, not by D |
| **Nov 3** (D-35) | Feed, diaper, and sleep logging working online. Home screen answering the standing questions. Live nursing timer, visible on both phones. | |
| **Nov 10** (D-28) | Offline queue and sync. Installed to both home screens. | Feature complete |
| **Nov 24** (D-14) | Two weeks of real use on live data. The 3am test run for real: in the dark, one-handed, both phones, wifi off. | **Go/no-go — see §12** |
| **Dec 1** (D-7) | Fix-only. Planning half archived. Nursery list at zero. | Freeze |
| **Dec 1 – Dec 8** | Nothing. Rest. | |
| **Dec 8** | Use it | |
| **After** | Growth logging, rollups, CSV export, pumped-milk inventory | |

**Nov 10 is the real deadline**, not Nov 24. The two weeks between them are for using the
thing on live data and fixing what breaks — which is where the actual bugs surface. Building
into that window is how you arrive at D with something untested.

Babies come early. Treat every date above as two weeks softer than it looks.

## 12. Risks

**1. September slips and the backend lands in November.** Highest-probability failure, and
the reason §11 front-loads it. It is the least fun part, it is on the critical path, and
every week it slips lands it in a worse week than the one before.

> *Mitigation — hard go/no-go at Nov 24.* If sync isn't working on both phones by then,
> stop. Ship the tracker single-device on `localStorage`, one designated phone, and treat
> the other parent's logs as verbal handoff. Better: download Huckleberry. Do not spend
> the last two weeks before D debugging a sync bug.

**2. It's unreliable once, and that's the end.** One lost night of data, one white screen
at 3am, and the app is dead — trust doesn't come back. This is why offline-first and
"never block on network" are Must and not Should.

**3. Scope creep from the fun half.** Charts, growth curves, a design pass. All more
appealing than a write queue. The cut list in §5 exists to be re-read when this happens.

**4. The tool doesn't survive contact with an actual newborn.** Possible even if
everything ships. §2 already gives permission to walk away.

## 13. Open questions

1. ~~What is D?~~ **Answered: Dec 8, 2026.** §11 is pinned to it.
2. **Whose phone is the primary?** Matters for the single-device fallback in §12.
3. **Neon or Supabase?** Neon is less to learn if all you need is Postgres. Supabase gives
   auth and realtime you'd otherwise hand-roll — but §8.3 says the auth is a passcode, so
   most of Supabase goes unused. Leaning Neon.
4. **Does sleep tracking survive first contact?** It's the least reliably logged thing in
   every tracker, because sleep ends while you're asleep. Possibly should be a
   nice-to-have rather than a Must.
5. **Is the pumped-milk inventory (T22) actually the highest-value post-launch feature?**
   Suspect yes, and that it's underrated by every app in this category.
