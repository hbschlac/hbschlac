# Baby

Registry, names, and nursery planning in one place. Next.js App Router, deployed on Vercel.

Phase 1 (what's here now) is the planning half: decide what to buy, argue about names in a
structured way, and work through nursery setup. Phase 2 is the tracker — feeds, sleep, diapers,
growth — which needs a real database first.

Requirements and schedule: [`docs/PRD.md`](docs/PRD.md).

## Running it

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
npm run typecheck
```

## What's in it

| Route | What it does |
|-------|--------------|
| `/` | Overview — open must-haves, registry estimate, shortlisted names, nursery tasks left |
| `/registry` | Gear list grouped by category. Status, priority, price, link, filters |
| `/names` | Candidate names with independent per-voter 1–5 ratings; sorts by combined score |
| `/nursery` | Setup checklist by area with todo → doing → done |

The registry seed is deliberately generic ("Infant car seat", not a specific model) — it's a set of
slots to research into, with no prices that go stale. Everything is editable.

## Storage

Data lives in `localStorage` under the `baby:v1:` prefix. That means:

- It works offline and needs no backend or account.
- It does **not** sync between devices or browsers.

All reads and writes go through `StorageAdapter` in `src/lib/storage.ts`. Swapping in a database
means writing a second adapter and changing the `adapter` export — no page or component changes.

## Phase 2: tracker

The tracker types (`FeedLog`, `SleepLog`, `DiaperLog`, `GrowthLog`) are already defined in
`src/lib/types.ts` so the storage layer and any future API share one vocabulary. Not built yet;
it needs a hosted database and a logging screen that's fast to use one-handed at 3am.

## Stack

Next.js 15 (App Router) · React 19 · TypeScript · Tailwind CSS v4. No other runtime dependencies.
