"""NADAC — National Average Drug Acquisition Cost (CMS, weekly). What pharmacies pay wholesalers.

Used only as a benchmark: "this pharmacy paid about $X; you're being charged $Y." It is never
ranked as a price, because no patient can buy at NADAC.
"""
from __future__ import annotations

import datetime as dt
import re
import statistics

from .. import http
from ..models import DrugRequest
from . import costplus

API = "https://data.medicaid.gov/api/1"
FIELDS = ["ndc", "ndc_description", "nadac_per_unit", "effective_date", "pricing_unit",
          "classification_for_rate_setting"]


def dataset_id(year: int | None = None) -> str | None:
    """CMS publishes one NADAC dataset per year; find this year's by title, not a hardcoded id."""
    year = year or dt.date.today().year
    for d in http.fetch(f"{API}/metastore/schemas/dataset/items", {"show-reference-ids": "false"}):
        title = d.get("title", "")
        if title.startswith("NADAC (National Average Drug Acquisition Cost)") and title.endswith(str(year)):
            return d["identifier"]
    return None


def _query(ds: str, conditions: list[dict]) -> list[dict]:
    body = {
        "conditions": conditions,
        "properties": FIELDS,
        "sorts": [{"property": "effective_date", "order": "desc"}],
        "limit": 500,
    }
    return http.fetch(f"{API}/datastore/query/{ds}/0", body=body).get("results", [])


# NADAC truncates long names; these are the spellings it actually uses.
ALIASES = {"amphetamine-dextroamphetamine": "DEXTROAMP-AMPHETAMIN"}
FORMS = {"tablet": "TAB", "capsule": "CAP"}  # "TAB" matches both "TAB" and "TABLET"


def _description_patterns(req: DrugRequest) -> list[str]:
    # NADAC descriptions read like "ATORVASTATIN 40 MG TABLET" / "PHENTERMINE 37.5 MG CAPSULE".
    num, unit = re.match(r"([\d.\-]+)\s*([a-z]+)", req.strength.lower()).groups()
    names = [ALIASES.get(req.name, req.name.upper())]
    if "-" in req.name:  # combinations can be listed in either order
        names.append("-".join(reversed(req.name.upper().split("-"))))
    form = FORMS.get((req.form or "").lower(), "")
    return [f"{n}%{num} {unit.upper()}%{form}%" for n in names]


def summarize(rows: list[dict], brand: bool = False) -> dict | None:
    """Latest price per NDC, generics only (the equivalent-NDC list includes the brand, which
    costs ~500× more), then the median across manufacturers."""
    want = "B" if brand else "G"
    latest: dict[str, dict] = {}
    for r in rows:
        if (r.get("classification_for_rate_setting") or "G") != want:
            continue
        cur = latest.get(r["ndc"])
        if cur is None or r["effective_date"] > cur["effective_date"]:
            latest[r["ndc"]] = r
    if not latest:
        return None
    per_unit = statistics.median(float(r["nadac_per_unit"]) for r in latest.values())
    newest = max(r["effective_date"] for r in latest.values())
    sample = next(iter(latest.values()))
    # Most common description, so a branded generic ("RELGAABI 300 MG") doesn't label the row.
    descriptions = [r.get("ndc_description") for r in latest.values()]
    return {
        "per_unit": round(per_unit, 5),
        "pricing_unit": sample.get("pricing_unit"),
        "effective_date": newest,
        "ndc_count": len(latest),
        "description": statistics.mode(descriptions),
    }


def benchmark(req: DrugRequest, units: float | None = None) -> dict | None:
    """`units` overrides req.qty when a source priced a whole pack (inhaler grams, etc.)."""
    ds = dataset_id() or dataset_id(dt.date.today().year - 1)
    if not ds:
        return None
    ndc_list = costplus.ndcs(req)
    rows = _query(ds, [{"property": "ndc", "value": ndc_list, "operator": "in"}]) if ndc_list else []
    for pattern in _description_patterns(req) if not rows else []:
        # Cost Plus doesn't carry it (e.g. controlled substances): match on the description
        rows = _query(ds, [{"property": "ndc_description", "value": pattern, "operator": "like"}])
        if rows:
            break
    s = summarize(rows)
    if not s:
        return None
    s["units"] = units or req.qty
    s["cost_for_qty"] = round(s["per_unit"] * s["units"], 2)
    s["matched_by"] = "ndc" if ndc_list else "description"
    return s
