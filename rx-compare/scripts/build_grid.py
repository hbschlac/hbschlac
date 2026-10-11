"""27 drugs × 3 ZIPs → data/grid.json + data/grid.csv, using only cleared sources.

    uv run --directory rx-compare python scripts/build_grid.py

Polite by construction: sequential requests, 0.5 s apart, every response cached for the run.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rxcompare import pharmacies  # noqa: E402
from rxcompare.models import DrugRequest  # noqa: E402
from rxcompare.sources import costplus, nadac, waiting_on_permission  # noqa: E402

PAUSE = 0.5


def _try(fn, *args):
    try:
        out = fn(*args)
        time.sleep(PAUSE)
        return out, None
    except Exception as e:  # record the failure in the grid instead of dying mid-run
        return None, f"{type(e).__name__}: {e}"


def main() -> int:
    drugs = json.loads((ROOT / "data/drugs.json").read_text())["drugs"]
    zips = json.loads((ROOT / "data/zips.json").read_text())["zips"]
    today = dt.date.today().isoformat()

    chains = {}
    for z in zips:
        chains[z["zip"]], err = _try(pharmacies.chains_in_zip, z["zip"])
        print(f"chains {z['zip']}: {chains[z['zip']]} {err or ''}", file=sys.stderr)

    rows = []
    for d in drugs:
        req = DrugRequest(d["name"], d["strength"], d["qty"], d.get("form"), d.get("match"))
        mail, mail_err = _try(costplus.mail_quotes, req)
        mail = (mail or [None])[0]
        units = mail.qty if mail else req.qty
        bench, bench_err = _try(nadac.benchmark, req, units)
        row = {
            "drug": d.get("display") or d["name"],
            "strength": d["strength"],
            "form": d.get("form"),
            "qty": d["qty"],
            "goodrx_rank": d.get("goodrx_rank"),
            "singlecare_rank": d.get("singlecare_rank"),
            "note": d.get("note"),
            "nadac": bench,
            "mail": mail.to_dict() if mail else None,
            "by_zip": {},
            "errors": {k: v for k, v in (("mail", mail_err), ("nadac", bench_err)) if v},
        }
        for z in zips:
            card, card_err = _try(costplus.card_quotes, req, z["zip"])
            card = (card or [None])[0]
            options = [q for q in (mail, card) if q]
            cheapest = min(options, key=lambda q: q.price) if options else None
            row["by_zip"][z["zip"]] = {
                "card": card.to_dict() if card else None,
                "card_pharmacy_count": len(card.pharmacies) if card else 0,
                "card_chains": sorted({p["chain"] for p in card.pharmacies}) if card else [],
                "cheapest_program": cheapest.program if cheapest else None,
                "cheapest_price": cheapest.price if cheapest else None,
                "error": card_err,
            }
        rows.append(row)
        z0 = row["by_zip"][zips[0]["zip"]]
        print(f"{row['drug']:32} mail={mail.price if mail else '—'} card@{zips[0]['zip']}="
              f"{z0['card']['price'] if z0['card'] else '—'} nadac={bench['cost_for_qty'] if bench else '—'}",
              file=sys.stderr)

    grid = {
        "built": today,
        "zips": zips,
        "chains_in_zip": chains,
        "waiting_on_permission": waiting_on_permission(),
        "rows": rows,
    }
    (ROOT / "data/grid.json").write_text(json.dumps(grid, indent=1) + "\n")

    with open(ROOT / "data/grid.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["drug", "strength", "qty", "goodrx_rank", "singlecare_rank", "nadac_cost",
                    "costplus_mail"] + [f"team_cuban_card_{z['zip']}" for z in zips])
        for r in rows:
            w.writerow([r["drug"], r["strength"], r["qty"], r["goodrx_rank"], r["singlecare_rank"],
                        r["nadac"]["cost_for_qty"] if r["nadac"] else "",
                        r["mail"]["price"] if r["mail"] else ""]
                       + [(r["by_zip"][z["zip"]]["card"] or {}).get("price", "") for z in zips])
    print(f"wrote {len(rows)} rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
