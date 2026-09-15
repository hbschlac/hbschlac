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
| `scripts/stories.py` | The ~55 real accomplishments, hand-named. **Every wording maps to one** |
| `scripts/build_page_data.py` | `bullets.json` + experience metadata → `app/data.js` |
| `app/` | The dashboard |
| `RUNBOOK.md` | What Claude does on "apply the pending build" / "publish the queued link" |
| `PORTING.md` | Moving the bench to Vercel if she ever wants to own the hosting |

## The bank: 994 wordings, ~55 stories

Mined 2026-09-14 from **346 CV docs found, 331 fetched (2021+), 256 actual resumes** →
**994 unique bullets** after dedupe and splitting merged lines.

They are unique *strings*. They are **not** unique stories — the mine deduped by normalised
text, so every rewording of the same launch survived as its own row. That is why Walmart first
read as 290 bullets to sort through. `scripts/stories.py` names the real accomplishments and
maps every wording onto one, so the bank is browsed by **story** and the wording is the
interchangeable part.

| Experience | Stories | Wordings |
|---|---|---|
| Walmart | 9 | 290 |
| Uprising | 10 | 281 |
| Siemens | 5 | 132 |
| Accenture | 6 | 81 |
| Berkeley | 3 | 66 |
| Community | 4 | 43 |
| Muse | 4 | 34 |
| AI projects | 4 | 28 |
| Misc | 6 | 20 |
| Illinois | 3 | 16 |
| Coherent Finance | 2 | 3 |

**24 wordings (2.4%) match no story yet** and sit in a per-experience `-other` bucket, visible in
the dashboard's *What's in here* panel. When that number grows, add a story to `stories.py` —
never lower `MIN_SCORE`.

152 wordings are in current rotation (used Aug 2026+). 839 carry a number. 858 are slop-free.
One wording appears in **101 different CVs**.

## Rules it enforces

Format rules come from `career-skills/skills/product-networking/references/resume-subskill.md`;
slop rules from `career-skills/skills/aislop/SKILL.md`; the 100-point scorecard from
`.claude/skills/recruiter-filter/SKILL.md`. The dashboard and `enrich.py` read the same tables so
they cannot drift.

Blocking: **the same story told twice in different words** · repeated opening verb · em dash
inside a bullet · trailing period · `+`/`/` shorthand ·
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
