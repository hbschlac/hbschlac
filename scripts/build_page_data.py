"""data/grid.json → app/data.js (window.GRID), trimmed to what the page shows.

    python3 rx-compare/scripts/build_page_data.py
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    grid = json.loads((ROOT / "data/grid.json").read_text())
    rows = []
    for r in grid["rows"]:
        mail = r["mail"]
        bench = r["nadac"]
        row = {
            "drug": r["drug"],
            "strength": r["strength"],
            "form": r["form"],
            "qty": r["qty"],
            "goodrx": r["goodrx_rank"],
            "singlecare": r["singlecare_rank"],
            "note": r["note"],
            "nadac": bench["cost_for_qty"] if bench else None,
            "nadac_date": bench["effective_date"] if bench else None,
            "mail": mail["price"] if mail else None,
            "mail_note": mail["note"].split(" · ")[0] if mail else None,
            "product": (mail or {}).get("product"),
            "zips": {},
        }
        for z, cell in r["by_zip"].items():
            card = cell["card"]
            row["zips"][z] = {
                "card": card["price"] if card else None,
                "card_note": card["note"].split(";")[0] if card else None,
                "n": cell["card_pharmacy_count"],
                "chains": cell["card_chains"],
                "nearest": [
                    {"name": p["name"], "mi": p["distance_mi"]} for p in (card["pharmacies"][:3] if card else [])
                ],
                "best": cell["cheapest_program"],
                "best_price": cell["cheapest_price"],
            }
            if not row["product"] and card:
                row["product"] = card["product"]
        rows.append(row)
    page = {
        "built": grid["built"],
        "zips": grid["zips"],
        "chains_in_zip": grid["chains_in_zip"],
        "waiting": grid["waiting_on_permission"],
        "rows": rows,
    }
    (ROOT / "app/data.js").write_text("window.GRID = " + json.dumps(page, separators=(",", ":")) + ";\n")
    print(f"app/data.js: {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
