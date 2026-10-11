"""Registry of every price source we know about — used, gated, or out — and why.

This mirrors SOURCES.md (a test keeps them in sync). Only `status == "use"` sources are called.
A permission that comes back = one new module in this package + one row flipped here.
"""

CHECKED = "2026-10-09"

REGISTRY = [
    {
        "key": "costplus_mail",
        "program": "Cost Plus Drugs (mail order)",
        "operator": "Mark Cuban Cost Plus Drug Company",
        "status": "use",
        "access": "Public pricing API, no key (api.costplusdrugs.com/pricelist/cpd/search)",
        "terms": "Official public API, documented at mccpdc-llc.github.io/pricing-api-documentation; "
        "no API terms or rate limits published",
        "zip_aware": False,
    },
    {
        "key": "costplus_tcc",
        "program": "Team Cuban Card (Cost Plus retail network)",
        "operator": "Mark Cuban Cost Plus Drug Company",
        "status": "use",
        "access": "Same public API, /pricelist/tcc/search with an address → nearest 20 pharmacies",
        "terms": "Same as above",
        "zip_aware": True,
    },
    {
        "key": "nadac",
        "program": "NADAC — what pharmacies pay (benchmark, never a price)",
        "operator": "CMS / Medicaid",
        "status": "use",
        "access": "data.medicaid.gov datastore API, no key",
        "terms": "Public federal data",
        "zip_aware": False,
    },
    {
        "key": "insiderx",
        "program": "Inside Rx (Express Scripts; also powers Amazon Prime Rx savings)",
        "operator": "Evernorth / Cigna",
        "status": "ask",
        "access": "Chain-level prices in page HTML; no API",
        "terms": "Terms load via a OneTrust script we could not read — unverified, so not used",
        "zip_aware": False,
    },
    {
        "key": "costco",
        "program": "Costco Member Prescription Program",
        "operator": "Costco Health Solutions",
        "status": "ask",
        "access": "Undocumented ZIP-aware JSON endpoint",
        "terms": "No automated access 'without our prior written consent' (updated 2026-10-07)",
        "zip_aware": True,
    },
    {
        "key": "hippo",
        "program": "Hippo",
        "operator": "Hippo Network LLC",
        "status": "ask",
        "access": "Prices in page HTML",
        "terms": "No automated collection 'without our prior permission' (updated 2026-09-11)",
        "zip_aware": False,
    },
    {
        "key": "optumperks",
        "program": "Optum Perks (OptumRx network)",
        "operator": "RVO Health",
        "status": "ask",
        "access": "Token-gated API behind the site",
        "terms": "Explicit no-scrape; personal, non-commercial license (effective 2026-08-13)",
        "zip_aware": False,
    },
    {
        "key": "singlecare",
        "program": "SingleCare (RxSense; also powers Walgreens Rx Savings Finder)",
        "operator": "RxSense",
        "status": "ask",
        "access": "Blocked (DataDome)",
        "terms": "Unverified",
        "zip_aware": None,
    },
    {
        "key": "americaspharmacy",
        "program": "America's Pharmacy (MedImpact, per one source)",
        "operator": "America's Pharmacy",
        "status": "ask",
        "access": "Blocked (Cloudflare)",
        "terms": "Unverified",
        "zip_aware": None,
    },
    {
        "key": "wellrx",
        "program": "WellRx",
        "operator": "ScriptSave / Medical Security Card Co.",
        "status": "ask",
        "access": "Blocked (Cloudflare)",
        "terms": "Unverified",
        "zip_aware": None,
    },
    {
        "key": "buzzrx",
        "program": "BuzzRx",
        "operator": "Buzz Health",
        "status": "out",
        "access": "Store prices in HTML, but stores are fixed defaults — ZIP can't be set",
        "terms": "Bans use 'for any commercial purposes' (revised 2025-07-14)",
        "zip_aware": False,
    },
    {
        "key": "walmart4",
        "program": "Walmart $4 generic list",
        "operator": "Walmart",
        "status": "out",
        "access": "Site blocked; newest copy found is a third-party PDF effective 2023-04-15",
        "terms": "Explicit no-scrape. A 3-year-old list would mislead patients, so not shown",
        "zip_aware": False,
    },
    {
        "key": "amazon",
        "program": "Amazon Pharmacy / Prime Rx savings",
        "operator": "Amazon (prices from Inside Rx)",
        "status": "out",
        "access": "Prices load by JavaScript; no endpoint found",
        "terms": "Conditions of Use bar collecting prices",
        "zip_aware": False,
    },
    {
        "key": "rxsaver",
        "program": "RxSaver",
        "operator": "GoodRx (acquired 2021)",
        "status": "out",
        "access": "Prices in HTML",
        "terms": "Terms redirect to GoodRx's — same restriction as GoodRx",
        "zip_aware": False,
    },
    {
        "key": "goodrx",
        "program": "GoodRx",
        "operator": "GoodRx Holdings",
        "status": "out",
        "access": "Site returns 403; partner API by application",
        "terms": "API usage guide: 'Do Not Use Alongside Other Price Sources'. Compared instead via "
        "check_quote, where the patient brings the GoodRx number",
        "zip_aware": None,
    },
]


def by_status(status: str) -> list[dict]:
    return [s for s in REGISTRY if s["status"] == status]


def waiting_on_permission() -> list[str]:
    return [s["program"] for s in by_status("ask")]
