from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class Quote:
    """One price a cash patient can actually pay. Benchmarks (NADAC) are never Quotes."""

    source: str  # registry key in sources/__init__.py
    program: str  # what the patient uses at the counter or checkout
    price: float  # total out-of-pocket for `qty`, fees and shipping included
    qty: float
    kind: str  # "live" (API quote now) | "published_list" (a dated price list)
    as_of: str  # ISO date the price was read
    fulfillment: str  # "mail" | "pickup"
    product: str  # exact product the source matched, e.g. "Atorvastatin 40mg Tablet"
    pharmacies: list[dict] = field(default_factory=list)  # where it's accepted, nearest first
    membership_needed: str | None = None  # e.g. "Costco membership" — flagged, never hidden
    url: str | None = None
    note: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DrugRequest:
    name: str  # generic name as a patient would type it
    strength: str  # e.g. "40mg", "0.4mg", "875-125mg"
    qty: float = 30
    form: str | None = None  # "tablet", "capsule", "inhaler"… narrows ambiguous matches
    match: str | None = None  # extra word the product name must contain, e.g. "XL"

    def label(self) -> str:
        return f"{self.name} {self.strength} ×{self.qty:g}"
