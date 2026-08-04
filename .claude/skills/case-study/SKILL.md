---
name: case-study
description: >
  Writes any shipped project, customer story, or past-work item in an
  outcome-led skeleton (Problem → Solution → Metric → Detail), modeled on how
  Sierra writes up client work. Activates on "write up this project," case
  studies, portfolio entries, customer stories, résumé project bullets, or a
  "past projects" section. Leads with the result, one verifiable number each.
---

# case-study

One rigid pattern, repeated, led by the outcome. Borrowed from how Sierra
catalogs client work: every project written to the same skeleton, headline is
the *result*, one verifiable metric each — never the activity, never a wall of
prose.

## Activation

Triggers on: "write up this project," "case study," "portfolio entry," "customer
story," "past projects section," "project bullets for my résumé," "describe what
I built for X." Also invoked by **`mbb-slides`** when a proof/showcase slide
needs its copy, and pairs with **`portfolio-dev`** for schlacter.me entries.

Always run the output through **`content-quality`** — this skill produces
user-facing claims, the highest slop-risk surface.

## The skeleton (every project, same order)

> **1. Problem** — why it was needed, in the reader's terms. The pain, not the
> backstory.
> **2. Solution** — what was built, in one line. Concrete, not category.
> **3. Metric + proof** — one verifiable number that shows it worked, plus a
> quote or source if there is one.
> **4. Detail** — 2–4 concrete examples of what it actually does / how it works.

That's it. Do not add a summary paragraph on top (see failure modes). The first
thing the reader sees is the outcome.

## The rules that make it land

1. **Lead with the outcome, not the activity.** "Cut library-to-Kindle delivery
   to zero touches" — not "Built a book-delivery automation." The title/first
   line states the result.
2. **One verifiable number.** Every write-up carries exactly one hard metric,
   and it must be real and checkable (live site, repo, dashboard, deployment).
   No metric > a fabricated one. If there's genuinely no number, lead with the
   most concrete *capability* instead and say so — don't invent a percentage.
3. **Hedge borrowed numbers.** Vendor-reported, self-reported, or estimated
   figures get marked as such: "company-reported ~70% resolution," "estimated,"
   "as of last check." Stating a stale or single-source figure with false
   precision is the fastest way to lose credibility. (The Sierra habit: say
   "last I saw ~X," not a bare number.)
4. **Two sources named for any system.** For technical projects, name both what
   grounds it (data/knowledge) and what it acts on (the API/tool/integration).
   Specificity is the proof you actually built it.
5. **Resolved, not deflected.** Report the outcome that matters, not the vanity
   metric next to it. "70% resolved *and* 4.6 CSAT" beats "50% deflection." Name
   the honest measure even when a softer one looks bigger.
6. **Same skeleton across a set.** A portfolio or "past projects" list is the
   pattern applied N times — identical shape every entry. Consistency reads as
   rigor and lets a reader scan.

## Formats

### Single project (portfolio / case-study block)

```
{Outcome as a headline — result + verb, one line.}

Problem. {Why it was needed, in the user's terms — 1–2 sentences.}
Solution. {What was built — one concrete line.}
Result. {One verifiable number, hedged if borrowed} — {quote/source if any}.
How it works. {2–4 concrete examples: what it does, what it's built on.}

{Link — live site / repo. Verify it resolves; never fabricate a URL.}
```

### Catalog (many projects — the dense table)

When showcasing several, collapse to one scannable table — the Sierra client-
catalog move:

| Project | Context | What it does | Result |
|---|---|---|---|
| {name} | {who/where} | {one-line capability} | {one metric, hedged if borrowed} |

Lead the table with a one-line pattern statement ("Six shipped products, one
spine: …") so the reader sees the theme before the rows.

### Résumé / bullet form

One line, outcome-first, number-carrying, active verb:

- "Cut page load 3s→800ms by moving render server-side" — not "Responsible for
  performance improvements."
- Verb + what + number. No "helped," no "contributed to," no adjectives standing
  in for a metric.

## Failure modes

1. **The summary-paragraph trap.** No opening "This project was an exciting
   opportunity to…" Lead with the outcome. Delete any sentence that could be cut
   without losing a fact.
2. **Activity dressed as outcome.** "Built a comprehensive platform" says
   nothing happened. What changed for the user? State that.
3. **The fabricated metric.** A made-up "37%" collapses the moment someone asks
   for the source. Real number, or the concrete capability, or `[metric: TBD]`
   and ask.
4. **Inflated scope.** A weekend side project written with the gravity of a
   production system reads as dishonest. Match tone to actual scale.
5. **Vanity over honest metric.** Don't reach for the softer, bigger-looking
   number. The credible one is the outcome the reader actually cares about.
6. **Inconsistent skeletons.** In a set, one entry Problem-first and the next
   Solution-first breaks the scan. Same order every time.

## Cross-skill routing

- **`content-quality`** — mandatory final pass (banned phrases, numbers over
  adjectives, verify every URL/claim). Always.
- **`mbb-slides`** — when the write-up lands on a proof/showcase slide; this
  skeleton *is* that layout's copy.
- **`portfolio-dev`** — schlacter.me project entries and the projects data model.
