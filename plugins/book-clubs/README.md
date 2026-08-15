# Book Clubs (MCP plugin)

A Claude Code plugin that gives Claude the **kindle.schlacter.me book-club lookup**:
name a club (or just describe it) → get the club and its recent monthly picks.

It's the same catalog and Book Notification parser the web app uses (`lib/bookclubs/*`
in [`hbschlac/kindle-schlacter-me`](https://github.com/hbschlac/kindle-schlacter-me)) —
one parser, two front doors. The split is deliberate:

- **Deterministic + keyless** lives in the tools: the 32-club catalog, name / celebrity /
  typo-tolerant matching, Book Notification pick fetching, and generic scraping of an
  arbitrary club page.
- **The open-ended intelligence lives in Claude** (the MCP host), at no extra API cost:
  interpreting a fuzzy request, and — for a club the catalog doesn't carry —
  web-searching for its page, then calling `fetch_club_picks` with the URL.

No LLM call and no API key anywhere in the server.

## Enable it

In the repo (or user settings) where you want it, add the marketplace and turn the
plugin on:

```json
{
  "enabledPlugins": { "book-clubs@hbschlac": true }
}
```

The server is a single bundled Node file (`dist/server.mjs`) — no `npm install`, just
Node. Claude Code launches it over stdio when the plugin is enabled.

## Tools

| Tool | What it does |
|------|--------------|
| `find_book_club` | Find the club a query means (name, short name, or the person behind it — "Dua Lipa" → Service95; misspellings tolerated) and return its 3–6 recent picks. A low-confidence or empty match is flagged in `note` so Claude falls back to web search + `fetch_club_picks`. |
| `list_book_clubs` | The whole curated catalog (id, name, who's behind it, blurb). |
| `get_club_picks` | Recent picks for a known catalog club id. |
| `fetch_club_picks` | Generic-scrape an **off-catalog** club's own page (its Book Notification page or official site) for its picks — the fallback after a web search. |

## The intended flow

1. You ask for a club — a name, a nickname, or a description.
2. Claude calls `find_book_club`. A catalog hit comes back with the club + recent picks.
3. If there's no match (or a low-confidence one), Claude **web-searches** for the club,
   finds its Book Notification page or homepage, and calls `fetch_club_picks` with that
   URL — so clubs beyond the 32 still resolve, keylessly.

Ask things like *"find the Dakota Johnson book club and its last few picks"* or *"what's
the Reese Witherspoon club reading lately?"*

## Notes

- **Network:** `find_book_club` / `get_club_picks` read booknotification.com;
  `fetch_club_picks` reads the URL you pass. Both send a modern-Chrome UA (to clear Book
  Notification's browser wall) and time out rather than hang. If your environment blocks
  booknotification.com by egress policy, the catalog and matching still work offline —
  only live pick-fetching needs the host.
- **What's shipped:** `dist/server.mjs` is a self-contained bundle (server + tools +
  the shared `lib/bookclubs` parser + the MCP SDK) with no external runtime deps.

## Rebuilding the bundle

The bundle is generated from the source in `hbschlac/kindle-schlacter-me`. From a checkout
of that repo:

```bash
npx esbuild mcp/book-clubs/server.ts \
  --bundle --platform=node --format=esm --target=node18 \
  --outfile=/path/to/plugins/book-clubs/dist/server.mjs
```

The tools and the parser they reuse are tested there (`mcp/book-clubs/*.test.ts` and the
`lib/bookclubs/` fixture tests).
