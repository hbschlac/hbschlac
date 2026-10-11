"""Drug name → RxNorm concepts via NLM RxNav (free, no key, 20 req/s; NLM asks for 12-24h caching)."""
from __future__ import annotations

import re

from . import http

RXNAV = "https://rxnav.nlm.nih.gov/REST"


def search(query: str, limit: int = 15) -> list[dict]:
    """Clinical drugs (SCD) matching `query`, e.g. 'atorvastatin' → 'atorvastatin 40 MG Oral Tablet'.
    Falls back to RxNav's spelling-tolerant approximate match when the exact name finds nothing."""
    data = http.fetch(f"{RXNAV}/drugs.json", {"name": query})
    groups = (data.get("drugGroup") or {}).get("conceptGroup") or []
    out = [
        {"rxcui": c["rxcui"], "name": c["name"], **_parse(c["name"])}
        for g in groups
        if g.get("tty") == "SCD"
        for c in g.get("conceptProperties") or []
    ]
    if not out:
        approx = http.fetch(f"{RXNAV}/approximateTerm.json", {"term": query, "maxEntries": 5})
        names = {c.get("name") for c in (approx.get("approximateGroup") or {}).get("candidate") or []}
        names.discard(None)
        if names:
            return search(sorted(names, key=len)[0], limit)
    out.sort(key=lambda d: (" / " in d["name"], d["name"]))  # single-ingredient products first
    return out[:limit]


def _parse(scd_name: str) -> dict:
    """'atorvastatin 40 MG Oral Tablet' → strength '40mg', form 'tablet'. Strengths are written the
    way the Cost Plus API writes them so a search result can be passed straight to compare_prices."""
    m = re.search(r"([\d.]+(?:\s*MG)?(?:\s*/\s*[\d.]+)?\s*(MG|MCG|ML|UNT|%)(?:/ML|/ACTUAT)?)", scd_name)
    strength = re.sub(r"\s+", "", m.group(1)).lower() if m else ""
    form = scd_name.rsplit(" ", 1)[-1].lower() if " " in scd_name else ""
    return {"strength": strength, "form": form}
