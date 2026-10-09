"""MCP server: every cash price a patient can use for a prescription, cheapest first.

Run:  uv run --directory rx-compare python -m rxcompare.server     (stdio)
"""
from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from . import compare as cmp
from . import normalize
from .models import DrugRequest
from .sources import nadac

INSTRUCTIONS = """\
Shows every cash price a patient can actually use for a prescription, ranked only by what the
patient pays. It takes no money from pharmacies, PBMs or card companies.

Typical flow: search_drug to get the exact strength → compare_prices with the patient's ZIP.
If the patient already has a price from GoodRx, a pharmacy or anyone else, use check_quote.
Always tell the patient which programs could NOT be checked (field `waiting_on_permission`):
those companies forbid automated reads, so a cheaper price may exist there. Never present the
NADAC benchmark as a price anyone can pay — it's what the pharmacy paid.
"""

server = MCPServer(name="rx-compare", instructions=INSTRUCTIONS)


def _req(drug: str, strength: str, qty: float, form: str | None, match: str | None) -> DrugRequest:
    return DrugRequest(name=drug.strip().lower(), strength=strength, qty=qty, form=form, match=match)


@server.tool()
def search_drug(query: str) -> list[dict]:
    """Find the exact products for a drug name (RxNorm). Returns name, strength and form for each
    — pass strength (and form if there are several) to compare_prices."""
    return normalize.search(query)


@server.tool()
def compare_prices(
    drug: str, strength: str, zip_code: str, qty: float = 30, form: str | None = None,
    match: str | None = None,
) -> dict:
    """Every cash price we can legitimately read for this drug near this ZIP, cheapest first.

    drug: generic name, e.g. "atorvastatin". strength: e.g. "40mg", "0.4mg", "875-125mg".
    qty: tablets/capsules (use 1 for one inhaler). form: "tablet" | "capsule" | "inhaler" to
    disambiguate. match: a word the product name must contain, e.g. "XL" or "Extended Release".
    Returns ranked quotes (with participating pharmacies), what pharmacies pay (NADAC), chains in
    the ZIP that have no readable price yet, and programs still waiting on permission."""
    return cmp.compare(_req(drug, strength, qty, form, match), zip_code)


@server.tool()
def check_quote(
    drug: str, strength: str, zip_code: str, quoted_price: float, quoted_by: str = "GoodRx",
    qty: float = 30, form: str | None = None, match: str | None = None,
) -> dict:
    """Is there anything cheaper than the price the patient was quoted (by GoodRx, a pharmacy,
    anyone)? Returns a one-paragraph verdict, the cheaper options, and how the quote compares to
    what the pharmacy paid for the drug."""
    return cmp.check_quote(_req(drug, strength, qty, form, match), zip_code, quoted_price, quoted_by)


@server.tool()
def fair_price(drug: str, strength: str, qty: float = 30, form: str | None = None,
               match: str | None = None) -> dict | None:
    """What pharmacies pay for this drug (NADAC, CMS weekly survey), per unit and for qty.
    A benchmark for judging a price — not a price anyone can buy at."""
    return nadac.benchmark(_req(drug, strength, qty, form, match))


@server.tool()
def list_sources() -> list[dict]:
    """Every price program we know of, whether we read it, and why or why not (terms of use)."""
    return cmp.sources()


def main() -> None:
    server.run("stdio")


if __name__ == "__main__":
    main()
