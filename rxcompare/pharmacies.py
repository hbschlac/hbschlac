"""Which pharmacy chains exist in a ZIP code, from the NPPES NPI Registry (CMS, free, no key).

Used to be honest about gaps: "Walgreens and CVS are in this ZIP, but no source we're allowed
to read has their prices yet."
"""
from __future__ import annotations

import re

from . import http

NPPES = "https://npiregistry.cms.hhs.gov/api/"

# Registered legal names and DBAs vary ("WALGREEN CO", "CVS PHARMACY INC", "SAFEWAY INC" …).
CHAINS = [
    ("CVS", r"\bCVS\b|LONGS DRUG"),
    ("Walgreens", r"WALGREEN|DUANE READE"),
    ("Walmart", r"WAL-?MART"),
    ("Marc's", r"MARC GLASSMAN"),
    ("Kroger", r"KROGER|RALPHS|FRED MEYER|KING SOOPERS|SMITH'?S FOOD|FRY'?S FOOD|HARRIS TEETER|DILLON"),
    ("Albertsons/Safeway", r"SAFEWAY|ALBERTSON|VONS|JEWEL|ACME MARKETS|SHAW'?S|TOM THUMB|RANDALLS|OSCO"),
    ("Costco", r"COSTCO"),
    ("Publix", r"PUBLIX"),
    ("H-E-B", r"\bH-?E-?B\b"),
    ("Meijer", r"MEIJER"),
    ("Giant Eagle", r"GIANT EAGLE"),
    ("Hy-Vee", r"HY-?VEE"),
    ("Ahold Delhaize", r"GIANT FOOD|STOP & SHOP|STOP AND SHOP|FOOD LION|HANNAFORD|MARTIN'?S"),
    ("Sam's Club", r"SAM'?S (CLUB|WEST)"),
    ("Kaiser Permanente", r"KAISER|HPNV"),
]


def chain_of(names: list[str]) -> str:
    text = " | ".join(n.upper() for n in names if n)
    for chain, pattern in CHAINS:
        if re.search(pattern, text):
            return chain
    return "Independent / other"


def chains_in_zip(zip_code: str) -> dict[str, int]:
    """Count of pharmacy NPIs per chain physically located in a 5-digit ZIP.

    `address_purpose=LOCATION` matters: without it NPPES also matches mailing addresses, so a ZIP
    holding a corporate office (Kaiser and Safeway in Oakland) returns stores from all over."""
    data = http.fetch(
        NPPES,
        {"version": "2.1", "postal_code": zip_code[:5], "address_purpose": "LOCATION",
         "taxonomy_description": "Pharmacy", "enumeration_type": "NPI-2", "limit": 200},
    )
    counts: dict[str, int] = {}
    for r in data.get("results") or []:
        names = [r.get("basic", {}).get("organization_name", "")]
        names += [o.get("organization_name", "") for o in r.get("other_names") or []]
        chain = chain_of(names)
        counts[chain] = counts.get(chain, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))
