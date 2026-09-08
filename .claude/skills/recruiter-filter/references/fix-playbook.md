# Fix playbook

Loaded at Step 5, when converting a score into edits. Patterns are written against
Hannah's real material (Walmart BuyBox, Uprising VC, Accenture, Kindle × Schlacter,
recs.community, Muse, Haas MBA) so the before/afters are usable, not generic.

## The truth rule, restated

Three legal moves: **surface**, **reframe**, **quantify**. If a fix is none of those, it
is a gap — report it. The test: *could she defend this line under five minutes of
questioning from someone who does the job?* If not, cut it. A CV that scores 90 and
falls apart on the screening call is worse than one that scores 70 and holds.

**Quantify never means invent.** If the number isn't on the page and isn't in her
material, ask her. An estimated metric on a resume is a fabricated metric.

## Pattern 1 — Top-third takeover (highest yield, almost always available)

The 6-second skim reads headline + current title + first two bullets. If the JD's core
requirement isn't in that block, nothing else you fix matters as much.

The move is not to add — it is to **reorder**. Promote the bullet that covers the JD's
top must-have into position one of the current role, and demote the one covering its
lowest-priority ask. Same content, different order, big rank delta.

For a platform/infra req:
> before (bullet 3): "Owner of the BuyBox, the ML system behind ~400M daily product page views."
> after (bullet 1):  "Own the BuyBox — the ML ranking system serving ~400M daily product
>                     page views and ~30% of marketplace volume."

For a 0→1 / founding / agent req, the lead project belongs above the Walmart bullets or
in the headline rather than filed on page 2 — see *Which project to lead with* below.

## Pattern 2 — Vocabulary reframe (cheap, safe, moves Dimensions 1 and 4 together)

Companies name the same work differently. Use the req's noun, keep her work.

| Her word | Req's word (use the req's) |
|----------|---------------------------|
| BuyBox | ranking / relevance / marketplace pricing / ML-driven selection |
| Experiments | A/B testing, experimentation platform, causal measurement |
| Internal GenAI assistant | internal AI tooling, LLM application, RAG assistant, AI enablement |
| KPI platform | analytics platform, portfolio reporting, data infrastructure |
| Chief of Staff | strategy & operations, business operations, founder's office |
| Vibe-coded / side project | built and shipped, 0→1, prototype to production |

Two rules. **Mirror, don't stack** — one term per concept, the req's term, not a slash
pile. And **only where the work matches**: calling the KPI platform "data infrastructure"
is fair; calling it "data engineering" is not.

## Pattern 3 — Title bridging (Dimension 1, 20 points)

Recruiter boolean search runs on titles. When her title isn't a title they'd search:

- Add a **parenthetical scope line**, never a false title:
  `Senior Product Manager, Search & Ranking (BuyBox)` — accurate, and now matches a
  search for "ranking."
- For a pivot req, a **target-title headline** above the experience block does the work
  legitimately: `Product Manager — ML/Platform · marketplace ranking at ~400M daily views`.
- Never restyle the employer-of-record title. Scope qualifiers are fair; a promotion
  you didn't get is not.

## Pattern 4 — Evidence upgrade (Dimension 3, 20 points)

Duty verbs score low; outcomes with scope score high. And match the JD's *own* metric —
if the req is measured on conversion, lead with conversion.

> before: "Ran experiments to improve the BuyBox and drive conversion."
> after:  "Shipped the Secondary BuyBox (~45M daily impressions); drove 7% CVR
>          improvement YoY across ~30% of marketplace volume."

Prefer, in order: outcome + scope + timeframe > outcome > scope alone > activity.
An unquantifiable bullet can still carry **scope** — org size, volume, surface area,
dollars raised. `$400M+ raised across 30 portfolio startups` is scope without an
attribution claim.

## Pattern 5 — Recency rescue (Dimension 5, 10 points)

A must-have last touched at Uprising in 2021 scores badly. Two honest routes:

1. **Find it in current work.** Often the skill is live and unlabeled — the internal
   GenAI assistant is current AI-product work whether or not it's in the job description.
2. **Use the projects.** Kindle × Schlacter and recs.community are *current* and dated.
   A shipped side project is legitimate recency evidence and it is the fastest truthful
   fix for a stale skill — provided it is one she'd still defend today.

If neither works, it's a gap. Say so.

## Pattern 6 — Parse and skim safety (Dimension 6, 10 points)

Actual failure modes, in order of how often they bite:

- Contact details inside a header/footer or a graphic → often dropped by the parser.
- Multi-column layouts → columns interleave; bullets get attached to the wrong employer.
- Skills rendered as icons, ratings, or bar charts → no text, no match, no citation.
- Inconsistent date formats (`2024–present` vs `Jan 2024 - Now`) → broken tenure math,
  which then breaks a "5+ years" screen.
- Image-only PDF → parses to nothing. Text-layer PDFs are fine; the myth is that PDFs
  as a format fail.
- Non-standard section headers ("My Journey") → the parser can't map the section.
  Use Experience / Education / Skills / Projects.

Skim-safety is the other half: if page one is a wall, the human bails before the parser
ever mattered.

## Which project to lead with

Do not lead with the biggest-sounding project. Lead with the one that survives the
follow-up question. Rank by, in order: **is it running now**, **can she defend how it
works in detail**, **does it evidence this req's load-bearing requirement**, and only
then how impressive the description sounds.

**Default lead: Kindle × Schlacter.** It is current, it actually runs, and it is a
genuine autonomous agent — request a title, it arrives on the device, unattended, with
cross-source fallback across three download providers. That reliability detail is the
strongest part and the part most people leave off: handling provider failure without a
human is the difference between a script and an agent. For applied-AI, agent, automation,
platform, or infra reqs, this is the lead.

**Muse is not the default, despite being the bigger story.** It shipped, but it never got
users — so "264 brands, 10 retailers" is surface area, not traction, and the first
screener question ("how many people used it?") collapses the bullet. Use Muse only where
its *specific* content is the match — commerce, checkout, catalog integration, payments —
and describe it as built scope, never as adoption. Never imply usage it did not have; the
skill's truth rule applies to her own portfolio first.

**recs.community** is the fit for community/social/consumer reqs. **The Claude Skills
work** is the fit for developer-experience, docs, and AI-enablement reqs.

If she wants a number on any of these, **ask her** — usage figures for these projects are
not in her written material, and an estimated metric is a fabricated one.

## Application questions (Layer 1 — where the actual rejects live)

Check these before polishing prose. On Ashby and Greenhouse the custom questions are the
real auto-reject surface.

- **Gating questions** (work auth, sponsorship, onsite days, years, licensure) — answer
  accurately. A false answer here is the one unrecoverable move; it surfaces at offer.
- **Free-text boxes** ("why this company," "tell us about a project") are increasingly
  LLM-read. Treat each as a scored short answer: name the company's actual product, one
  specific piece of evidence, under 150 words. Route drafts through `aislop`.
- **Salary expectations** — a number outside the band is a silent knockout. If the
  posting shows a range, stay inside it.

## When the honest answer is "don't apply cold"

Under 55 after the top fixes, or a hard-gate fail: say it plainly. The highest-EV move
is a referral or a targeted project, not another resume pass. Route to `job-search`
(better-fitting reqs at the same company), `product-networking` (outreach to a human who
can bypass the stack entirely), or `project` (build something for that team). One warm
intro outranks every point on this rubric.
