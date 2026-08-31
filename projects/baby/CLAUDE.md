# Baby

Baby planning app: registry, names, nursery. Next.js 15 App Router + React 19 + TypeScript +
Tailwind v4, deployed on Vercel. No database, no auth, no runtime dependencies beyond Next/React.

## Layout

```
src/
  app/
    page.tsx          Overview dashboard
    registry/page.tsx Gear list
    names/page.tsx    Name candidates + ratings
    nursery/page.tsx  Setup checklist
    layout.tsx, globals.css, icon.svg
  components/
    Nav.tsx, Rating.tsx, ui.tsx   (ui.tsx holds every shared primitive)
  lib/
    types.ts       Domain model, including the unbuilt phase 2 tracker types
    storage.ts     StorageAdapter interface + localStorage implementation
    useCollection.ts  The one hook every page uses for persisted state
    seed.ts        Starter data
    format.ts      money / titleCase / dollarsToCents
```

## Conventions

- **All four pages are client components.** State is browser-local, so there is nothing to render
  on the server beyond the seed. Don't add `async` server components until there's a database.
- **Persisted state goes through `useCollection(name, seed)`.** Never touch `localStorage`
  directly from a component — that's what `storage.ts` is for.
- **`useCollection` renders the seed first, then swaps in saved data on mount.** This avoids a
  hydration mismatch and an empty flash. It only writes after `loaded` is true; removing that
  guard makes the seed clobber saved data on every page load.
- **Money is stored in cents** (`priceCents`), formatted with `money()`. Never store floats.
- **Enum-ish values are `as const` arrays in `types.ts`**, with the union derived from them, so
  the dropdowns and the type stay in sync automatically.
- **Colors come from the `@theme` block in `globals.css`** — `cream`, `ink`, `muted`, `line`,
  `sage`, `clay` and their `-soft` variants. Don't introduce raw hex in components.
- **Don't override a `bg-*` on `<Card>` via `className`.** Tailwind resolves by stylesheet order,
  so `bg-surface` wins. Use a border accent, or add a `tone` prop to `Card`.

## Before pushing

```bash
npm run typecheck && npm run build
```

Both must pass. The build runs type checking too, but `typecheck` is faster for a quick loop.

## Phase 2: the tracker

Feeds, sleep, diapers, growth. `FeedLog` / `SleepLog` / `DiaperLog` / `GrowthLog` in `types.ts`
are the intended model — they exist so phase 2 doesn't invent a third vocabulary.

Blocking work, in order:

1. **A real database.** localStorage can't sync between two parents' phones, which is the whole
   point of a tracker. Write an HTTP `StorageAdapter` against Route Handlers and a hosted
   Postgres; the phase 1 pages keep working unchanged.
2. **A one-handed logging screen.** Large tap targets, defaults to "now", two taps to log a feed.
   If it's slower than a notes app, it won't get used.
3. **Summary views.** Last feed, time since, daily counts.

Don't build the tracker on localStorage as a shortcut — it produces two divergent copies of the
data and there is no merge story.

## Scope rules

- No specific product recommendations or prices in `seed.ts`. Seed items are generic slots; real
  products and prices are user-entered. This keeps the repo from carrying claims that go stale.
- Keep the runtime dependency list at Next + React. Reach for a library only when something here
  genuinely can't be written in an afternoon.
