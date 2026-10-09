# Price sources: what we read, what we don't, and why

Checked 2026-10-09 from a cloud sandbox, one polite request per URL, no attempt to get past bot
protection. **A source is read only if it offers an official API or public data, or its terms
allow automated access.** The registry in `rxcompare/sources/__init__.py` mirrors this table, and
a test fails if they drift.

| Key | Program | Status | How it's read / why not |
|---|---|---|---|
| `costplus_mail` | Cost Plus Drugs, mail order | **Read** | Official keyless pricing API (`api.costplusdrugs.com/pricelist/cpd/search`), [documented publicly](https://mccpdc-llc.github.io/pricing-api-documentation/). Responses link back with `utm_content=pricing-api`. No rate limit or API terms published. |
| `costplus_tcc` | Team Cuban Card (Cost Plus's retail card) | **Read** | Same API, `/pricelist/tcc/search?address=` → the nearest 20 participating pharmacies within 30 mi, with per-pharmacy fees. The only ZIP-aware card source we can read today. |
| `nadac` | NADAC, what pharmacies pay | **Read (benchmark only)** | CMS datastore API on data.medicaid.gov, public. Joined by NDC using Cost Plus's equivalent-NDC list; generic rows only. Never shown as a price. |
| `insiderx` | Inside Rx (Express Scripts; also behind Amazon Prime Rx savings) | Ask | Prices are in the page HTML and robots.txt is open, but the Terms of Use load via a OneTrust script we couldn't read. Unverified terms mean we don't read it. |
| `costco` | Costco Member Prescription Program | Ask | A ZIP-aware JSON endpoint exists, but the terms bar automated access "without our prior written consent" (updated 2026-10-07). |
| `hippo` | Hippo | Ask | Terms bar automated collection "without our prior permission" (updated 2026-09-11), so they invite a request. |
| `optumperks` | Optum Perks (OptumRx network) | Ask | Token-gated API; terms say no scraping and grant a personal, non-commercial license only (effective 2026-08-13). |
| `singlecare` | SingleCare (RxSense; also powers Walgreens Rx Savings Finder) | Ask | Blocked by DataDome bot protection; terms unverified. |
| `americaspharmacy` | America's Pharmacy (MedImpact, per one source) | Ask | Blocked by Cloudflare; terms unverified. |
| `wellrx` | WellRx (ScriptSave) | Ask | Blocked by Cloudflare; terms unverified. |
| `buzzrx` | BuzzRx | Not used | Terms ban use "for any commercial purposes" (revised 2025-07-14), and its pages show fixed default stores, so a ZIP can't be set. |
| `walmart4` | Walmart $4 generic list | Not used | walmart.com bars scraping. The newest copy we found is a third-party PDF effective 2023-04-15; a three-year-old list would mislead patients. |
| `amazon` | Amazon Pharmacy / Prime Rx savings | Not used | Prices load by JavaScript, and the Conditions of Use bar collecting prices. Its Prime savings run on Inside Rx. |
| `rxsaver` | RxSaver | Not used | Owned by GoodRx since 2021; its terms redirect to GoodRx's. |
| `goodrx` | GoodRx | Not used | Site returns 403. The partner API's usage guide has a section titled "Do Not Use Alongside Other Price Sources." GoodRx is compared through `check_quote` instead: the patient brings the number GoodRx showed them. Research data requests go to legal@goodrx.com (named in a 2023 PLOS ONE paper). |

**No PBM publishes its discount-network prices or offers a public lookup.** Caremark's FAQ says
only the pharmacy can quote an exact price. The comparison GoodRx avoids is gated by permission,
and that permission is what the "Ask" rows are for.

## Adding a source when permission arrives

1. Save the written permission (email or contract) and note its date and any limits here.
2. Add `rxcompare/sources/<key>.py` exposing `quotes(req, zip) -> list[Quote]`, recorded-fixture
   tests, and a call in `compare.compare`.
3. Flip the row above and its registry entry to `use`.

## Not sources, but used

- **RxNav (NLM):** drug name → RxNorm products for `search_drug`. Free; NLM asks for 12–24h caching.
- **NPPES NPI Registry (CMS):** which pharmacy chains are physically in a ZIP, so the tool can say
  "Walgreens is here, but we can't read its prices yet."
