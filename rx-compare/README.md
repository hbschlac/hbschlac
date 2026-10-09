# rx-compare

Every cash price a patient can actually use for a prescription, cheapest first. An MCP server, so
Claude (or any MCP client) can answer "what's the cheapest way to fill this near me?"

**Price grid:** https://claude.ai/artifact/52W5sBzsyG4xWZoUMgNTnd (private) — 27 drugs × 3 ZIPs, built 2026-10-09.

## The problem it solves

GoodRx shows you prices from the PBMs it has deals with. It's paid a cut of the fee those PBMs
charge the pharmacy on every fill ([GoodRx FY2025 10-K](https://www.sec.gov/Archives/edgar/data/1809519/000180951926000031/gdrx-20251231.htm)).
So the $30 it shows you at Walgreens can sit next to a $20 option it doesn't show. Since May 2026
its best prices sit behind a $14.99/month subscription (GoodRx Companion).

rx-compare takes no money from pharmacies, PBMs or card companies. It ranks by one thing: what you pay.

## What it does today

| Tool | What it answers |
|---|---|
| `search_drug` | "Which atorvastatin?" → exact strengths and forms (RxNorm) |
| `compare_prices` | Every price we can legitimately read near a ZIP, cheapest first, with the pharmacies that take it |
| `check_quote` | "GoodRx quoted me $30" → is anything cheaper, by how much, and how $30 compares to what the pharmacy paid |
| `fair_price` | What pharmacies pay wholesalers for the drug (NADAC, CMS weekly). A yardstick, not a price |
| `list_sources` | Every program we know of, whether we read it, and why or why not |

Atorvastatin 40mg ×30, Oakland 94612, run 2026-10-09:

```
Cost Plus Drugs (mail order)   $10.92   $0.67 drug + $5.00 fee + $5.25 shipping
Team Cuban Card (pickup)       $13.72   at 20 pharmacies within 30 mi (Safeway + 3 independents)
Pharmacies pay (NADAC)          $1.12   benchmark, not for sale
check_quote($30, "GoodRx") →   "Cheaper option found … saves $19.08 … the quote is 26.8× that."
```

## Sources: the honest part

Only three sources are both automated and clearly allowed today: the Cost Plus Drugs public API
(mail order, plus its Team Cuban Card retail network by ZIP), and CMS's NADAC data. Every other
discount card blocks automated reads or forbids them in its terms. That includes Optum Perks,
Inside Rx, SingleCare, Hippo, Costco, BuzzRx and GoodRx. Requests for written permission are out.
Each one granted adds a source. [`SOURCES.md`](SOURCES.md) has the clause and date for every
program.

Every answer lists the programs it couldn't check, so a patient knows a cheaper price may exist there.

## Customer-first rules (enforced in `rxcompare/compare.py`)

1. Rank strictly by what the patient pays for the quantity asked, shipping included.
2. Never hide or demote a cheaper option.
3. Label every price: live quote or published list, and its date. The benchmark is never ranked.
4. Flag prices that need a membership; don't drop them.
5. Store nothing about who searched for what. No accounts, no query logs.
6. Read only sources whose terms allow it. Honest User-Agent, robots.txt respected.

## Run it

```bash
cd rx-compare
uv sync                                   # installs the MCP SDK (mcp 2.x)
uv run python -m rxcompare.server         # stdio MCP server
uv run python scripts/mcp_smoke.py        # spawns the server, lists tools, calls two
python3 -m unittest discover tests        # offline tests, stdlib only
uv run python scripts/build_grid.py       # 27 drugs × 3 ZIPs → data/grid.json + grid.csv
python3 scripts/build_page_data.py        # grid.json → app/data.js
```

The repo-root `.mcp.json` registers the server for Claude Code sessions in this repo.

## What's here

| Path | What it is |
|---|---|
| `rxcompare/sources/` | One module per cleared source; `__init__.py` is the registry of all 15 programs |
| `rxcompare/compare.py` | Fan-out, ranking, `check_quote` |
| `rxcompare/normalize.py` | Drug name → RxNorm products (NLM RxNav) |
| `rxcompare/pharmacies.py` | Which chains are physically in a ZIP (CMS NPPES), to name the gaps |
| `rxcompare/server.py` | The MCP server |
| `data/drugs.json` | The 27 drugs: GoodRx's top 20 and SingleCare's top 20, with each list's rank |
| `data/grid.json`, `grid.csv` | The priced grid |
| `app/` | The grid page (published as a private artifact) |
| `RESEARCH.md` | Who sets drug prices, the card universe, both top-20 lists, what the grid found |
| `SOURCES.md` | What we read, what we don't, and the terms behind each call |

## Not in v1

- A public consumer app. v1 is the MCP server and a private grid page.
- Eligibility screening ("do you qualify for something better than cash?", like Walgreens' Find
  Rx Coverage Advisor).
- Insurance prices. A federal rule published 2026-10-06 requires plans to publish pharmacy-level
  negotiated rates, which makes them a later source for insured patients.
- Our own discount card. Issuing one would mean taking per-fill fees, which is the conflict this
  project exists to avoid.
