# Bullet Bench

Every resume bullet Hannah has ever written, in one place, selectable against a specific JD.

**Dashboard:** https://claude.ai/artifact/RWLv53mteWtb4dmZ1qJSnf (private)

## The problem it solves

Applying to ~30 roles at a time, every bullet has to be measurable *and* aligned to that JD.
The bottleneck was never writing — it was **selection**. The same Uprising story has a strategy
framing and a product framing; Walmart has a marketplace framing and an AI/ML-platform framing.
Those variants existed, but scattered across 256 CV Google Docs, so each application meant
re-deriving choices already made.

## What's here

| Path | What it is |
|---|---|
| `data/bullets.tsv` | Raw mined bank — 990 rows, one per unique bullet |
| `data/bullets.json` | Enriched: verb, metrics, skills, archetypes, slop flags, recency |
| `scripts/mine_cvs.py` | Drive archive → `bullets.tsv` (runs in the Composio workbench) |
| `scripts/enrich.py` | `bullets.tsv` → `bullets.json`. **The rules live here**, not in the payload |
| `scripts/build_page_data.py` | `bullets.json` + experience metadata → `app/data.js` |
| `scripts/linefit.py` | Exported PDF → true line count per bullet + page count. **Measures, doesn't estimate** |
| *(evidence ledger)* | **Read before writing any bullet.** Lives in the private skills repo — see below |
| `app/` | The dashboard |
| `RUNBOOK.md` | What Claude does on "apply the pending build" / "publish the queued link" |
| `PORTING.md` | Moving the bench to Vercel if she ever wants to own the hosting |

## Selection was only half the problem

The bank solves **selection** — 994 bullets she has already written, browsable and badged.
It does not solve **evidence**: the things she knows that were never on a CV in the first place.

The 2026-09-15 Anthropic build took **3h08m of working time and 127 doc edits** for nine bullets,
because roughly **14 of her 46 messages were facts Claude did not have** — her Uprising security
framework, the xfn pillar she owned, the dashboard engineering leadership ran on. Each arrived
after a bullet was already written and scored, so each triggered a full rewrite cycle. One bullet
reached **15 versions**. None of those facts were saved anywhere.

The **evidence ledger** is that missing half. Read it before writing; append to it whenever she
states something new. `RUNBOOK.md` Step 0 makes this blocking.

It lives in `hbschlac/career-skills` → `skills/product-networking/references/evidence.md` (**private repo — run `add_repo` first**; if `product-networking-skills` 404s, retry as `career-skills`) — **not in this repo, which is public.** The ledger records
what she deliberately kept off her CV and why, which is exactly the material that should not be
searchable on her GitHub profile.

## The bank

Mined 2026-09-14 from **346 CV docs found, 331 fetched (2021+), 256 actual resumes** →
**994 unique bullets** after dedupe and splitting merged lines.

| Experience | Variants |
|---|---|
| Walmart | 290 |
| Uprising | 281 |
| Siemens | 132 |
| Accenture | 81 |
| Berkeley | 66 |
| Community | 43 |
| Muse | 34 |
| AI projects | 28 |
| Illinois | 16 |
| Coherent Finance | 3 |

152 are in current rotation (used Aug 2026+). 839 carry a number. 858 are slop-free.
One bullet appears in **101 different CVs**.

## Rules it enforces

Format rules come from `career-skills/skills/product-networking/references/resume-subskill.md`;
slop rules from `career-skills/skills/aislop/SKILL.md`; the 100-point scorecard from
`.claude/skills/recruiter-filter/SKILL.md`. The dashboard and `enrich.py` read the same tables so
they cannot drift.

Blocking: repeated opening verb · em dash inside a bullet · trailing period · `+`/`/` shorthand ·
bullet over 2 lines · tagline wrapping · present tense on Walmart (the role ended 2026) ·
any contact that isn't `hbschlac@gmail.com`.

Warnings: no number · GMV leading instead of the $400M+ charter · the encodable aislop categories.

## Known, and deliberate

- **The score is uncalibrated.** It models the screen; it is not the screen. Disclosed every run.
- **Page fit is estimated.** 52–56 non-blank lines ≈ one page. No API confirms this — she checks
  visually before sending.
- **A bullet in `Decagon-PM_CVResume` is spliced mid-word** in the source document itself
  (`"Deployed analyt…Streamlined resource allocation…ics dashboard"`). Flagged in
  `bullets.json → anomalies`, deliberately not silently repaired — it's her doc.
- **Nothing is invented.** The tool surfaces, reorders and reframes real work only.
