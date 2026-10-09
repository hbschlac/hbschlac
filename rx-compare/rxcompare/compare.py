"""Fan out to every cleared source, rank by what the patient pays, attach the NADAC benchmark.

Customer-first rules (README.md) enforced here:
  1. Rank strictly by out-of-pocket for the requested quantity, shipping included.
  2. Never hide or demote a cheaper option — there is no revenue to sort by.
  3. Every price carries its kind and as-of date; the benchmark is never ranked as a price.
  4. Membership-gated prices are flagged, not dropped.
  5. Nothing about the request is stored.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from . import pharmacies
from .models import DrugRequest, Quote
from .sources import REGISTRY, costplus, nadac, waiting_on_permission


def rank(quotes: list[Quote]) -> list[Quote]:
    # Price only. Ties go to pickup (no wait for shipping), then by program name for stability.
    return sorted(quotes, key=lambda q: (q.price, q.fulfillment != "pickup", q.program))


def compare(req: DrugRequest, zip_code: str, include_chains: bool = True) -> dict:
    errors: dict[str, str] = {}

    def safe(key, fn, *args):
        try:
            return fn(*args)
        except Exception as e:  # one source failing must never hide the others
            errors[key] = f"{type(e).__name__}: {e}"
            return None

    with ThreadPoolExecutor(max_workers=4) as pool:
        mail = pool.submit(safe, "costplus_mail", costplus.mail_quotes, req)
        card = pool.submit(safe, "costplus_tcc", costplus.card_quotes, req, zip_code)
        chains = pool.submit(safe, "nppes", pharmacies.chains_in_zip, zip_code) if include_chains else None
        quotes = rank((mail.result() or []) + (card.result() or []))
        units = quotes[0].qty if quotes else req.qty
        bench = safe("nadac", nadac.benchmark, req, units)
        nearby = chains.result() if chains else None

    for q in quotes:
        if bench and bench["cost_for_qty"] > 0:
            q.note = (q.note or "") + f" · {q.price / bench['cost_for_qty']:.1f}× what pharmacies pay"

    covered = {p["chain"] for q in quotes for p in q.pharmacies}
    return {
        "request": req.label(),
        "zip": zip_code,
        "quotes": [q.to_dict() for q in quotes],
        "cheapest": quotes[0].to_dict() if quotes else None,
        "benchmark": bench,
        "chains_in_zip": nearby,
        "chains_without_a_price": sorted(c for c in (nearby or {}) if not _covered(c, covered)),
        "waiting_on_permission": waiting_on_permission(),
        "errors": errors,
    }


def _covered(chain: str, covered: set[str]) -> bool:
    # Cost Plus says "Albertsons" for Safeway stores; NPPES-derived names say "Albertsons/Safeway".
    return any(c and (c in chain or chain in c) for c in covered)


def check_quote(req: DrugRequest, zip_code: str, quoted_price: float, quoted_by: str) -> dict:
    """The patient brings a price they were shown (GoodRx, a pharmacy, anyone). We say whether
    anything we can see beats it, by how much, and how it compares to what the pharmacy paid."""
    result = compare(req, zip_code, include_chains=False)
    cheaper = [q for q in result["quotes"] if q["price"] < quoted_price]
    bench = result["benchmark"]
    if cheaper:
        best = cheaper[0]
        verdict = (
            f"Cheaper option found: {best['program']} at ${best['price']:.2f} "
            f"(saves ${quoted_price - best['price']:.2f} vs {quoted_by}'s ${quoted_price:.2f})."
        )
    elif result["quotes"]:
        verdict = (
            f"{quoted_by}'s ${quoted_price:.2f} beats every source we can read "
            f"(next best: {result['quotes'][0]['program']} at ${result['quotes'][0]['price']:.2f})."
        )
    else:
        verdict = "No source we're allowed to read prices this drug, so we can't confirm or beat it."
    if bench and bench["cost_for_qty"] > 0:
        verdict += (
            f" Pharmacies pay about ${bench['cost_for_qty']:.2f} for this (NADAC, "
            f"{bench['effective_date']}); the quote is {quoted_price / bench['cost_for_qty']:.1f}× that."
        )
    return {
        "verdict": verdict,
        "quoted": {"price": quoted_price, "by": quoted_by},
        "cheaper_options": cheaper,
        "benchmark": bench,
        "not_checked": result["waiting_on_permission"],
        "errors": result["errors"],
    }


def sources() -> list[dict]:
    return REGISTRY
