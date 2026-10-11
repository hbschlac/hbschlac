# rx-compare

Every cash price a patient can use for a prescription near a ZIP, ranked only by what they pay,
next to what the pharmacy paid (NADAC). An MCP server (`rxcompare/server.py`, registered in
`.mcp.json`) plus a research grid. Private for now; Hannah plans to make it public at launch.

**Grid:** https://claude.ai/artifact/52W5sBzsyG4xWZoUMgNTnd (private artifact). Read `README.md` first.

## Rules that matter

- **`SOURCES.md` decides what may be read.** Only the Cost Plus public API (mail order + its ZIP-aware
  Team Cuban Card network) and CMS NADAC are cleared. Every other card blocks bots or forbids automated
  access. Never scrape GoodRx, RxSaver (GoodRx-owned) or any "Ask" row. A written yes = new
  `rxcompare/sources/<key>.py` + flip the row in `SOURCES.md` and `rxcompare/sources/__init__.py`
  (a test keeps the two in sync).
- GoodRx is compared via `check_quote` (the patient brings the GoodRx number), never via its API: its
  terms bar showing its prices next to other sources.
- Rank by patient price only; never show NADAC as a price anyone can pay; store nothing about users.

## Permission requests

Seven plain-text drafts sit in Hannah's Gmail (Costco, Hippo, SingleCare, Optum Perks, Inside Rx,
WellRx/ScriptSave, GoodRx research), rewritten 2026-10-11 to lead with who she is and why. They
contain no links: the Gmail connector wraps any link in a google.com/url redirect that reads as
spam. America's Pharmacy publishes no email; it needs its web contact form.

## Commands

- Tests (offline, stdlib): `python3 -m unittest discover tests`
- End-to-end MCP check: `uv run python scripts/mcp_smoke.py`
- Rebuild grid: `uv run python scripts/build_grid.py` → `python3 scripts/build_page_data.py` →
  republish `app/index.html` (+ `app/data.js` as `data.js`) to the artifact URL above.
