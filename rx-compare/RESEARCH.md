# What a cash patient can actually pay for a prescription

Research behind rx-compare, October 2026. Every figure has a source. Numbers that came through a
secondary summary, or that we couldn't verify, are marked as such.

## Findings

1. **For a common generic, the drug is the cheap part.** Across the 25 drugs we could price, pharmacies
   paid a median of $1.22 for the drug (NADAC). The cheapest price a patient could get was a median
   of $11.16. Fees and shipping were 93% of the typical Cost Plus mail-order price. Price is mostly
   a fee schedule.
2. **Discount cards aren't a search of every PBM's rates.** GoodRx is a marketplace of its own PBM
   partners. It's paid a share of the fee each PBM charges the pharmacy per fill. A cheaper price
   on a network GoodRx doesn't work with never appears on GoodRx.
3. **Comparing cards is gated by permission, not by technology.** Of 15 cash-price programs we
   checked, one (Cost Plus) offers an open pricing API. The rest block automated reads or forbid
   them in their terms. That includes GoodRx, whose API terms bar showing its prices next to
   anyone else's.
4. **No peer-reviewed study compares discount cards at the same pharmacy.** We found small,
   contradictory affiliate-site comparisons and one 2022 study across three services. A
   card × pharmacy × drug grid doesn't exist publicly.
5. **Pharmacy choice beats card choice.** In a July 2026 sample of 350 checks, a grocery or warehouse
   pharmacy was cheapest 99% of the time (Rx.com, a commercial source; directional).

## 1. Who sets the price

When you pay cash with a discount card, the pharmacy runs the card's codes (BIN/PCN/Group) like an
insurance claim. The PBM behind the card returns a price from the rate the pharmacy agreed to for
*discount-card* claims. That rate schedule is separate from the PBM's insured-member rates, and
usually weaker. The PBM also charges the pharmacy a per-claim admin fee. Pharmacies report fees
averaging $5.86 per claim, ranging $4–$36 (Frier Levitt, citing an InteliSys average). The PBM shares
part of that fee with the card marketer.
GoodRx's FY2025 10-K says it's paid "a percentage of the fees that PBMs charge to pharmacies" or a
fixed per-fill amount ([SEC](https://www.sec.gov/Archives/edgar/data/1809519/000180951926000031/gdrx-20251231.htm)).

A third party can't get a truly live, adjudicated price; only the pharmacy can, at the counter.
Every aggregator, GoodRx included, shows quotes from PBM rate files.

## 2. The universe

**Walk-in pharmacy chains, 2025 prescription revenue** ([Drug Channels, Mar 2026](https://www.drugchannels.net/2026/03/the-top-15-us-pharmacies-of-2025-market.html);
figures below the top three via a [Becker's](https://www.beckershospitalreview.com/pharmacy/top-15-pharmacies-by-2025-prescription-revenue/) summary):

| Chain | 2025 Rx revenue |
|---|---|
| CVS Health | $119.0B |
| Walgreens (private under Sycamore since Aug 2025) | $90.8B |
| Walmart | $36.8B |
| Kroger | $17.1B |
| Publix | $11.7B |
| Albertsons (incl. Safeway) | $11.3B |
| Costco | $4.7B |
| Ahold Delhaize | $4.1B |

These totals include each company's mail and specialty business. Rite Aid closed its last stores in
October 2025. The rest of the top 15 is mail and specialty pharmacy owned by PBMs and insurers
(Express Scripts, Optum Rx, CenterWell, CarelonRx).

**PBMs, share of 2025 claims** ([Drug Channels, Mar 2026](https://www.drugchannels.net/2026/03/the-top-pharmacy-benefit-managers-of.html)):
Express Scripts 31%, CVS Caremark 26%, Optum Rx 23%, Humana 7%, MedImpact 5%, Prime 3%, all
others 5%.

**Cash programs and who's behind them:**

| Program | Who processes the claim |
|---|---|
| GoodRx | "Dozens of PBMs," unnamed in its 10-K. In 2020, Navitus, MedImpact and Express Scripts were 42% of its revenue ([Drug Channels, Jun 2021](https://www.drugchannels.net/2021/06/how-goodrxs-rapid-growth-creates.html)) |
| SingleCare | RxSense, contracting with pharmacies directly. Walgreens' Rx Savings Finder also runs on RxSense (per MobiHealthNews) |
| Optum Perks | OptumRx ([Optum Perks](https://perks.optum.com/blog/optum-perks-vs-goodrx)) |
| Inside Rx | Express Scripts / Evernorth ([Evernorth](https://www.evernorth.com/media/21861)) |
| Amazon Prime Rx savings | Inside Rx, so also Express Scripts ([Amazon, Jan 2023](https://press.aboutamazon.com/2023/1/amazon-pharmacy-introduces-rxpass-unlimited-prescription-medications-for-only-5-a-month-delivered-free-to-your-door-available-exclusively-for-prime-members)) |
| America's Pharmacy | MedImpact (one secondary source) |
| RxSaver | Owned by GoodRx since 2021 |
| Costco Member Prescription Program | Costco Health Solutions; accepted at ~19,000 outside pharmacies ([Costco FAQ](https://www.costco.com/pharmacy/member-prescription-program-frequently-asked-questions.html)) |
| Cost Plus Drugs / Team Cuban Card | Cost Plus's own pricing; the card works at participating retail pharmacies |
| WellRx, BuzzRx, Hippo, NeedyMeds | Processor not verified |

Discontinued: Walgreens Prescription Savings Club (Aug 2024) and Kroger's GoodRx-run program (Jul 2024).

**Pharmacies don't have to accept every card.** Acceptance runs through each PBM's discount-network
contract. CVS Caremark moved to per-card opt-in for pharmacies in July 2025 ([Frier Levitt](https://www.frierlevitt.com/articles/pharmacy-alert-cvs-caremark-moves-towards-opt-in-model-for-caremark-cost-saver-program-following-class-action-lawsuit/)).
A Mississippi court temporarily blocked forced card acceptance in April 2025 ([Bloomberg Government](https://news.bgov.com/health-law-and-business/mississippi-court-blocks-goodrx-cvs-discount-plan-at-pharmacies)).
Kinney Drugs stopped accepting GoodRx in December 2023 ([Chain Drug Review](https://chaindrugreview.com/kinney-drugs-no-longer-accepting-goodrx-prescription-savings-cards)).
Independent pharmacies are suing GoodRx, Caremark, Express Scripts, MedImpact and Navitus in a
consolidated federal case (MDL 3148, D.R.I.). It alleges GoodRx's integrated savings program let
PBMs fix what they pay pharmacies. These are allegations; there's no ruling on the merits ([NCPA, May 2026](https://ncpa.org/newsroom/qam/2026/05/07/plaintiffs-file-response-goodrx-and-pbms-motion-dismiss)).

**GoodRx in 2026.** It launched GoodRx Companion at $14.99/month on May 28, 2026 ([HLTH](https://hlth.com/insights/news/goodrx-launches-goodrx-companion-subscription-to-expand-affordable-healthcare-access)).
Its prescription revenue was $544M in 2025, down 6%, and its three largest PBM customers were 22%
of revenue (10-K). One documented case found an old GoodRx card getting $8.68 at a Stop & Shop
where GoodRx's site showed about double ([Mouse Print, Mar 2026](https://www.mouseprint.org/2026/03/09/goodrx-prices-can-vary-using-their-cards-vs-their-website/)).

## 3. The two top-20 lists

**GoodRx's top 20**, in GoodRx's order ([goodrx.com/hcp/drug-info](https://www.goodrx.com/hcp/drug-info), undated;
reprinted by [Becker's](https://www.beckershospitalreview.com/pharmacy/20-most-prescribed-medications-goodrx-2) 2025-10-09).
GoodRx doesn't say whether it counts GoodRx fills, searches or all U.S. prescriptions:

1. atorvastatin
2. amlodipine
3. levothyroxine
4. lisinopril
5. losartan
6. rosuvastatin
7. metoprolol ER
8. metformin
9. gabapentin
10. pantoprazole
11. escitalopram
12. omeprazole
13. hydrochlorothiazide
14. albuterol
15. bupropion
16. trazodone
17. sertraline
18. tamsulosin
19. montelukast
20. fluoxetine

**SingleCare's top 20**, ranked by 2025 fills on its own card, with opioids excluded by SingleCare
([singlecare.com](https://www.singlecare.com/blog/most-prescribed-drugs/), updated 2026-01-13):

1. tadalafil
2. phentermine
3. sildenafil
4. amlodipine
5. atorvastatin
6. lisinopril
7. amphetamine-dextroamphetamine
8. levothyroxine
9. escitalopram
10. fluoxetine
11. losartan
12. sertraline
13. gabapentin
14. amoxicillin
15. benzonatate
16. pantoprazole
17. omeprazole
18. rosuvastatin
19. amoxicillin-clavulanate
20. metoprolol succinate ER

The lists share 13 drugs. SingleCare's reflects what people actually pay cash for on a card:
erectile dysfunction, weight loss, ADHD and short antibiotic courses. GoodRx's reads like national
prescribing. An older GoodRx list led with sildenafil, Adderall, phentermine and
hydrocodone/acetaminophen, which looks more like card-fill data.

## 4. What the grid found (2026-10-09)

All 27 drugs, three ZIPs, every source we're allowed to read. Data: `data/grid.json`, `data/grid.csv`.

| | GoodRx's 20 | SingleCare's 20 |
|---|---|---|
| Drugs with a readable price | 20 | 18 |
| Median cheapest price (Oakland) | $10.93 | $11.17 |
| Median pharmacy cost (NADAC) | $1.08 | $1.20 |

- **Cost Plus mail order was cheapest for 24 of 25 priced drugs.** Its prices ran $10.45 to $17.56,
  shipping included. Gabapentin was the exception: Cost Plus doesn't ship it, so the card was the
  only price.
- **The Team Cuban Card price is the same in every ZIP.** Only availability changes: 20
  participating pharmacies within 30 miles in Oakland (mostly Safeway) and in Westerville, OH
  (Kroger, Giant Eagle, Meijer), and 2 independents in Kosciusko, MS. Its $12 pharmacy fee plus
  $1 admin fee put it a median $2.80 above mail order.
- **Markup over what the pharmacy paid** ran from 1.1× (albuterol inhaler) to 33.7× (amlodipine). The
  median was 9.7×.
- **Two drugs have no readable price:** phentermine and amphetamine-dextroamphetamine, both controlled
  substances that Cost Plus doesn't sell. Pharmacies pay $2.18 and $8.70 for 30 tablets.
- **Chains we couldn't price:** Walgreens in Oakland. CVS, Marc's and Walmart in Westerville. CVS
  and Walmart in Kosciusko. Their prices come through the card programs that are waiting on
  permission.

**What the grid can't say yet:** whether GoodRx, SingleCare or Optum Perks beat these prices at a
particular chain. Their published samples suggest they sometimes do for cheap generics at grocery
chains. SingleCare's own page showed atorvastatin at $6.99 at Kroger on 2026-10-09, with no ZIP set.
That's the comparison the permission requests are for.

## 5. Other evidence on price spread

- Rx.com, July 2026, one card, 350 checks: median generic fill was $9.69 at Meijer, $11.08 at
  Kroger, $15.00 at Walmart, $23.98 at Costco, $38.20 at Walgreens and $38.60 at CVS. CVS ran 1.3×
  to 8.3× the cheapest chain per drug ([Rx.com](https://rx.com/research/generic-drug-price-lottery)).
  Rx.com sells its own card, and its tables don't fully agree with each other.
- J Gen Intern Med 2024: the cheapest source for common generics was Costco 31% of the time, Amazon
  27%, Walmart 20% and Cost Plus about 10%. Cost Plus did better on expensive generics ([AJMC summary](https://www.ajmc.com/view/1-in-5-most-costly-generics-not-available-through-national-direct-to-consumer-pharmacies)).
- Circ Cardiovasc Qual Outcomes 2023: a three-drug heart failure regimen cost $10.58 to $30.86 a
  month depending on the service (GoodRx, NeedyMeds or Blink), in six Tennessee ZIPs ([PubMed](https://pubmed.ncbi.nlm.nih.gov/37847754/)).

## 6. What would change these answers

- **Permission from any card program.** Seven requests are drafted (see `SOURCES.md`). Costco's
  answer matters most: its endpoint is ZIP-aware and covers ~19,000 pharmacies.
- **Insurance price transparency.** A federal rule published 2026-10-06 requires health plans to
  publish pharmacy-level negotiated drug rates. Enforcement is reportedly around December 2027,
  which we haven't verified. That covers insured patients, not discount cards.
- **Partner feeds.** White-label discount programs sell real network quotes per claim. Judi Health
  charges $0.99 per adjudicated claim. Taking that route means earning from fills, which is the
  conflict this project exists to avoid. It needs a decision on disclosure and fee handling first.
