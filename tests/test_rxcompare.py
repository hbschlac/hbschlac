"""Offline tests: recorded Cost Plus responses (2026-10-09), synthetic NADAC rows, no network.

    cd rx-compare && python3 -m unittest discover tests      (stdlib only)
"""
from __future__ import annotations

import json
import pathlib
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rxcompare import compare, http  # noqa: E402
from rxcompare.models import DrugRequest, Quote  # noqa: E402
from rxcompare.sources import REGISTRY, costplus, nadac  # noqa: E402

FIX = ROOT / "tests/fixtures"
CPD = json.loads((FIX / "costplus_cpd_atorvastatin.json").read_text())
TCC = json.loads((FIX / "costplus_tcc_atorvastatin_94612.json").read_text())
ATORVA = DrugRequest("atorvastatin", "40mg", 30)


def fake_fetch(url, params=None, body=None):
    if url.endswith("/pricelist/cpd/search"):
        return CPD
    if url.endswith("/pricelist/tcc/search"):
        return TCC
    if url.endswith("/metastore/schemas/dataset/items"):
        return [{"identifier": "ds2026", "title": "NADAC (National Average Drug Acquisition Cost) 2026"}]
    if "/datastore/query/" in url:
        return {"results": NADAC_ROWS}
    if "npiregistry" in url:
        return {"results": [
            {"basic": {"organization_name": "WALGREEN CO"}, "other_names": []},
            {"basic": {"organization_name": "SAFEWAY INC"}, "other_names": []},
            {"basic": {"organization_name": "SELAM PHARMACY LLC"}, "other_names": []},
        ]}
    raise AssertionError(f"unexpected request in an offline test: {url}")


NADAC_ROWS = [
    # two generic manufacturers, latest week and an older week; plus the brand (Lipitor) row
    {"ndc": "63304082905", "nadac_per_unit": "0.03743", "effective_date": "2026-09-30",
     "classification_for_rate_setting": "G", "pricing_unit": "EA", "ndc_description": "ATORVASTATIN 40 MG TABLET"},
    {"ndc": "63304082905", "nadac_per_unit": "0.05000", "effective_date": "2026-01-07",
     "classification_for_rate_setting": "G", "pricing_unit": "EA", "ndc_description": "ATORVASTATIN 40 MG TABLET"},
    {"ndc": "55111012305", "nadac_per_unit": "0.03900", "effective_date": "2026-09-23",
     "classification_for_rate_setting": "G", "pricing_unit": "EA", "ndc_description": "ATORVASTATIN 40 MG TABLET"},
    {"ndc": "00071015623", "nadac_per_unit": "19.11383", "effective_date": "2026-09-30",
     "classification_for_rate_setting": "B", "pricing_unit": "EA", "ndc_description": "LIPITOR 40 MG TABLET"},
]


class Offline(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(http, "fetch", side_effect=fake_fetch)
        patcher.start()
        self.addCleanup(patcher.stop)


class TestMatching(unittest.TestCase):
    def test_strength_normalization(self):
        self.assertEqual(costplus.norm_strength("300 MG"), "300mg")
        self.assertEqual(costplus.norm_strength("875mg-125mg"), "875-125mg")
        self.assertEqual(costplus.norm_strength("0.4mg"), "0.4mg")
        self.assertEqual(costplus.norm_strength("250 MG/5ML"), "250mg/5ml")

    def test_combination_products_are_dropped(self):
        names = [e["medication_name"] for e in costplus.match(CPD, ATORVA)]
        self.assertEqual(names, ["Atorvastatin"])

    def test_combination_request_keeps_combinations(self):
        entries = [{"medication_name": "Amoxicillin-Pot Clavulanate", "strength": "875mg-125mg", "form": "Tablet"}]
        req = DrugRequest("amoxicillin-clavulanate", "875-125mg", 20, "tablet")
        self.assertEqual(len(costplus.match(entries, req)), 1)

    def test_extended_release_only_when_asked(self):
        entries = [
            {"medication_name": "Metformin", "strength": "500mg", "form": "Tablet"},
            {"medication_name": "Metformin HCl ER (Mod)", "strength": "500mg", "form": "Tablet Extended Release"},
        ]
        plain = costplus.match(entries, DrugRequest("metformin", "500mg", 60, "tablet"))
        self.assertEqual([e["medication_name"] for e in plain], ["Metformin"])
        er = costplus.match(entries, DrugRequest("metformin", "500mg", 60, "tablet", match="ER"))
        self.assertEqual([e["medication_name"] for e in er], ["Metformin HCl ER (Mod)"])


class TestPriceMath(Offline):
    def test_mail_price_matches_cost_plus_published_total(self):
        # Cost Plus's own sample_pack_price_w_shipping_dispensing for 30 count is 10.92
        (q,) = costplus.mail_quotes(ATORVA, today="2026-10-09")
        self.assertEqual(q.price, 10.92)
        self.assertEqual(q.fulfillment, "mail")

    def test_mail_price_scales_with_quantity(self):
        (q,) = costplus.mail_quotes(DrugRequest("atorvastatin", "40mg", 90))
        self.assertEqual(q.price, round(round(0.02242 * 90, 2) + 5 + 5.25, 2))

    def test_missing_shipping_field_is_derived_not_zero(self):
        # Recorded 2026-10-09: tamsulosin's entry had no cash_shipping_cost but its totals did.
        ch = {"cash_dispensing_fee": 5, "price_per_unit": 0.03358,
              "sample_pack_price_total_to_patient_without_shipping": "6.01",
              "sample_pack_price_w_shipping_dispensing": "11.26"}
        self.assertEqual(costplus._shipping(ch), 5.25)

    def test_card_price_matches_cost_plus_published_total(self):
        (q,) = costplus.card_quotes(ATORVA, "94612", today="2026-10-09")
        self.assertEqual(q.price, 13.72)  # Cost Plus's sample_pack_price_w_dispensing
        self.assertEqual(len(q.pharmacies), 3)
        self.assertEqual(q.pharmacies, sorted(q.pharmacies, key=lambda p: (p["price"], p["distance_mi"])))


class TestNadac(Offline):
    def test_brand_excluded_latest_week_median(self):
        s = nadac.summarize(NADAC_ROWS)
        self.assertEqual(s["ndc_count"], 2)
        self.assertAlmostEqual(s["per_unit"], (0.03743 + 0.03900) / 2, places=5)
        self.assertEqual(s["effective_date"], "2026-09-30")

    def test_benchmark_cost_for_quantity(self):
        b = nadac.benchmark(ATORVA)
        self.assertEqual(b["cost_for_qty"], round(b["per_unit"] * 30, 2))
        self.assertEqual(b["matched_by"], "ndc")


def q(program, price, fulfillment="mail"):
    return Quote(source=program, program=program, price=price, qty=30, kind="live",
                 as_of="2026-10-09", fulfillment=fulfillment, product="x")


class TestRanking(Offline):
    def test_cheapest_first_ties_prefer_pickup(self):
        ranked = compare.rank([q("B", 12.0), q("A", 9.0), q("C", 12.0, "pickup")])
        self.assertEqual([r.program for r in ranked], ["A", "C", "B"])

    def test_compare_ranks_and_keeps_benchmark_out_of_quotes(self):
        r = compare.compare(ATORVA, "94612")
        prices = [x["price"] for x in r["quotes"]]
        self.assertEqual(prices, sorted(prices))
        self.assertEqual(r["cheapest"]["price"], 10.92)
        self.assertNotIn("nadac", {x["source"] for x in r["quotes"]})
        self.assertIn("Walgreens", r["chains_without_a_price"])  # in the ZIP, no readable price
        self.assertNotIn("Albertsons/Safeway", r["chains_without_a_price"])  # covered by the card

    def test_one_failing_source_does_not_hide_the_others(self):
        with mock.patch.object(costplus, "card_quotes", side_effect=TimeoutError("slow")):
            r = compare.compare(ATORVA, "94612")
        self.assertIn("costplus_tcc", r["errors"])
        self.assertEqual([x["source"] for x in r["quotes"]], ["costplus_mail"])


class TestCheckQuote(Offline):
    def test_cheaper_found(self):
        r = compare.check_quote(ATORVA, "94612", 30.0, "GoodRx")
        self.assertTrue(r["verdict"].startswith("Cheaper option found: Cost Plus Drugs (mail order) at $10.92"))
        self.assertIn("saves $19.08", r["verdict"])
        self.assertIn("Costco Member Prescription Program", r["not_checked"])  # gaps are always named

    def test_quote_already_lowest(self):
        r = compare.check_quote(ATORVA, "94612", 4.00, "Walmart")
        self.assertEqual(r["cheaper_options"], [])
        self.assertIn("beats every source we can read", r["verdict"])


class TestRegistry(unittest.TestCase):
    def test_every_source_is_documented_in_sources_md(self):
        doc = (ROOT / "SOURCES.md").read_text()
        for s in REGISTRY:
            self.assertIn(f"`{s['key']}`", doc, f"{s['key']} missing from SOURCES.md")

    def test_only_cleared_sources_are_called(self):
        used = {s["key"] for s in REGISTRY if s["status"] == "use"}
        self.assertEqual(used, {"costplus_mail", "costplus_tcc", "nadac"})


if __name__ == "__main__":
    unittest.main()
