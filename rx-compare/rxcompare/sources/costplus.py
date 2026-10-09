"""Cost Plus Drugs public pricing API: mail order (CPD) and Team Cuban Card retail network (TCC).

Docs: https://mccpdc-llc.github.io/pricing-api-documentation/ — keyless, read-only.
Price formulas are the documented ones:
  CPD: units × price_per_unit + cash_dispensing_fee + cash_shipping_cost
  TCC: units × price_per_unit + pharmacy_dispensing_fee (per pharmacy) + admin_fee
"""
from __future__ import annotations

import datetime as dt
import re

from .. import http
from ..models import DrugRequest, Quote

BASE = "https://api.costplusdrugs.com"


EXTENDED = re.compile(r"extended release|\((?:er|xl|xr|sr|mod)\)|\b(?:er|xl|xr|sr)\b", re.I)


def norm_strength(s: str) -> str:
    """'300 MG' → '300mg', '875mg-125mg' → '875-125mg', '0.4mg' stays. The two Cost Plus channels
    write strengths differently, so both sides go through this before comparing."""
    s = re.sub(r"\s+", "", (s or "").lower())
    if "/" in s:  # liquids and inhalers ('250mg/5ml'): keep the ratio as written
        return s
    nums, units = re.findall(r"\d+(?:\.\d+)?", s), re.findall(r"[a-z]+", s)
    return "-".join(nums) + (units[-1] if units else "")


def _tokens(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", s.lower())


def match(entries: list[dict], req: DrugRequest) -> list[dict]:
    """Keep entries that are this drug at this strength and form. Cost Plus's `term` search is a
    substring match, so 'atorvastatin' also returns Amlodipine-Atorvastatin (dropped unless the
    request is itself a combination), and 'metformin' returns the ER tablet (dropped unless the
    request's `match` asks for extended release)."""
    want = _tokens(req.name)
    is_combo = "-" in req.name or "/" in req.name
    wants_extended = bool(req.match and EXTENDED.search(req.match))
    out = []
    for e in entries:
        name = e.get("medication_name") or ""
        described = f"{name} {e.get('form') or ''}"
        if not all(t in _tokens(name) for t in want):
            continue
        if not is_combo and re.search(r"-|/|&", name):
            continue
        if norm_strength(e.get("strength")) != norm_strength(req.strength):
            continue
        if req.form and req.form.lower() not in (e.get("form") or "").lower():
            continue
        if req.match and req.match.lower() not in described.lower():
            continue
        if EXTENDED.search(described) and not wants_extended:
            continue
        out.append(e)
    return out


def _units(entry: dict, req: DrugRequest) -> float:
    # Inhalers, creams etc. are priced per gram or per package; a "qty" of 1 there means one pack.
    if (entry.get("unit") or "ea") != "ea" and req.qty <= 1:
        return float(entry.get("sample_pack_size") or entry.get("pack_size") or 1)
    return float(req.qty)


def _search(channel: str, req: DrugRequest, address: str | None = None) -> list[dict]:
    # First word only: Cost Plus spells combinations "Amoxicillin-Pot Clavulanate" and
    # "Amoxicillin & Pot Clavulanate", so the full name wouldn't substring-match; `match` filters.
    params = {"term": _tokens(req.name)[0]}
    if address:
        params["address"] = address
    return http.fetch(f"{BASE}/pricelist/{channel}/search", params) or []


def _product(e: dict) -> str:
    return f"{e.get('medication_name')} {e.get('strength')} {e.get('form') or ''}".strip()


def _cheapest(quotes: list[Quote]) -> list[Quote]:
    """Several catalog entries can match (three albuterol HFA inhalers); the patient only needs
    the cheapest one per program."""
    return [min(quotes, key=lambda q: q.price)] if quotes else []


def _shipping(ch: dict) -> float:
    """Standard shipping. Some entries omit `cash_shipping_cost` (tamsulosin, 2026-10-09) while
    their delivered total still includes it, so derive it from Cost Plus's own two totals rather
    than quoting $0 shipping and under-pricing the order."""
    if ch.get("cash_shipping_cost") is not None:
        return float(ch["cash_shipping_cost"])
    with_ship = ch.get("sample_pack_price_w_shipping_dispensing")
    without = ch.get("sample_pack_price_total_to_patient_without_shipping")
    if with_ship is not None and without is not None:
        return round(float(with_ship) - float(without), 2)
    return 0.0


def mail_quotes(req: DrugRequest, today: str | None = None) -> list[Quote]:
    today = today or dt.date.today().isoformat()
    quotes = []
    for e in match(_search("cpd", req), req):
        ch = e.get("cpd_channel") or {}
        if ch.get("price_per_unit") is None:
            continue
        units = _units(e, req)
        drug_cost = round(float(ch["price_per_unit"]) * units, 2)
        fee = float(ch.get("cash_dispensing_fee") or 0)
        ship = _shipping(ch)
        quotes.append(
            Quote(
                source="costplus_mail",
                program="Cost Plus Drugs (mail order)",
                price=round(drug_cost + fee + ship, 2),
                qty=units,
                kind="live",
                as_of=today,
                fulfillment="mail",
                product=_product(e),
                url=e.get("url"),
                note=f"${drug_cost:.2f} drug + ${fee:.2f} pharmacy fee + ${ship:.2f} standard shipping"
                + ("" if ch.get("in_stock", True) else " — OUT OF STOCK"),
            )
        )
    return _cheapest(quotes)


def card_quotes(req: DrugRequest, zip_code: str, today: str | None = None) -> list[Quote]:
    """Team Cuban Card price at participating pharmacies near `zip_code` (nearest 20, ≤30 mi)."""
    today = today or dt.date.today().isoformat()
    quotes = []
    for e in match(_search("tcc", req, address=zip_code), req):
        ch = e.get("tcc_channel") or {}
        if ch.get("price_per_unit") is None:
            continue
        units = _units(e, req)
        drug_cost = round(float(ch["price_per_unit"]) * units, 2)
        admin = float(ch.get("admin_fee") or 0)
        default_fee = float(ch.get("pharmacy_dispensing_fee") or 0)
        pharmacies = []
        for p in ch.get("pharmacies") or []:
            fee = float(p.get("pharmacy_dispensing_fee", default_fee))
            pharmacies.append(
                {
                    "name": p.get("name"),
                    "chain": p.get("chain"),
                    "address": p.get("address"),
                    "distance_mi": float(p.get("distance") or 0),
                    "npi": p.get("npi"),
                    "price": round(drug_cost + fee + admin, 2),
                }
            )
        pharmacies.sort(key=lambda p: (p["price"], p["distance_mi"]))
        if not pharmacies:
            continue  # no participating pharmacy within 30 miles: not a usable option here
        quotes.append(
            Quote(
                source="costplus_tcc",
                program="Team Cuban Card",
                price=pharmacies[0]["price"],
                qty=units,
                kind="live",
                as_of=today,
                fulfillment="pickup",
                product=_product(e),
                pharmacies=pharmacies,
                url="https://costplusdrugs.com/teamcubancard/",
                note=f"${drug_cost:.2f} drug + ${default_fee:.2f} pharmacy fee + ${admin:.2f} admin fee;"
                f" accepted at {len(pharmacies)} pharmacies within 30 mi",
            )
        )
    return _cheapest(quotes)


def ndcs(req: DrugRequest) -> list[str]:
    """Generic-equivalent NDCs Cost Plus lists for this product — the join key into NADAC."""
    out: list[str] = []
    for channel in ("cpd", "tcc"):
        for e in match(_search(channel, req), req):
            out += [n.replace("-", "") for n in e.get("equivalent_ndcs") or []]
        if out:
            break
    return sorted(set(out))
