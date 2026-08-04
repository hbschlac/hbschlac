---
name: mbb-slides
description: >
  Builds management-consulting-grade slide decks (McKinsey / Bain / BCG house
  style): action titles, pyramid + MECE storyline, real labeled charts, one
  message per slide, sourced claims. Activates on "make a deck / slides /
  presentation," strategy recommendations, board/exec readouts, or case-study
  decks. Routes to the pptx skill to render editable PowerPoint.
---

# mbb-slides

The MBB discipline layer for decks. It does the thinking — storyline, message,
evidence, layout — then hands a spec to a **renderer**. It does not reinvent
file plumbing.

## Activation

Triggers on: "build a deck," "make slides," "put together a presentation,"
"exec/board readout," "strategy recommendation deck," "case-study deck,"
"turn this into slides," or any request for a persuasive/analytical
presentation to a decision-maker.

Does NOT activate for: internal design docs, a single chart with no deck
around it (route to `dataviz`), or reveal.js/marketing landing decks where
consulting rigor is the wrong register.

### Renderer routing (decide at intake, don't guess)

| User wants | Renderer | How |
|---|---|---|
| Editable PowerPoint (default for execs) | **`pptx` skill** | Build the storyline + slide specs here, then invoke the `pptx` skill to render native, editable slides. Charts as native pptx chart objects, not images. |
| Fast in-chat preview / share link | **Artifact** (HTML) | Render the deck as a single self-contained HTML artifact, one `<section>` per slide, per `artifact-design`. |
| They named `.pptx` / "editable" / "our template" | **`pptx` skill** | Same as default; pass their `.potx` template through. |

Default to the **`pptx` skill** unless they ask for a preview. Execs edit decks;
a screenshot they can't touch is the #1 complaint about AI slides.

---

## Five hard rules (a violation is a failed slide)

1. **Action titles.** Every title is a complete sentence stating the *so-what*,
   not a label. "Revenue grew 34%, but all of it came from one region" — never
   "Revenue Overview." Titles alone, read top to bottom, must tell the whole
   story. ≤2 lines.
2. **Pyramid + MECE.** Conclusion first (governing thought), then 2–4 mutually
   exclusive, collectively exhaustive supporting branches. Every slide earns its
   place under a branch. See `references/storylining.md`.
3. **One message per slide.** A slide proves exactly one claim — the one in its
   title. If it proves two, it's two slides.
4. **Every number sourced and real.** Each exhibit carries a source line. Never
   fabricate a figure, a percentage, or a stamp. Unknown → `[source: TBD]`, and
   flag it to the user. Vendor/self-reported numbers get hedged ("company-
   reported ~X"), the Sierra habit — see the case-study template below.
5. **Real charts, labeled.** Native chart objects with titled axes and units.
   No CSS bars, no hand-drawn SVG, no chart with a mystery y-axis. Type floor
   **15px / 11pt** everywhere, including inside charts. See
   `references/layout-charts-type.md`.

---

## Workflow

Do not open the renderer until Step 3. Storyline before slides, always.

### Step 0 — Intake (one batch of questions, then proceed)
Confirm in a single message: **audience** (who decides?), **the decision**
being asked for, **deck type** (recommendation / readout / case-study /
narrative), **length**, **brand** (colors/logo/template, or house default),
and **renderer** (see routing table). Ask only for what's missing; assume
sensible defaults and state them.

### Step 1 — Storyline (the real work)
Write, in text, before any slide:
- **Governing question** — the one question the deck answers.
- **Governing thought** — the one-sentence answer (this becomes the exec-summary line).
- **2–4 MECE branches** — the supporting arguments.
- **Action-title list** — one title per planned slide, in order.
- **Headline-flow test:** read the titles alone, top to bottom. Do they argue
  the case with no body content? If not, fix the storyline — not the slides.

Get storyline sign-off from the user before rendering when the deck is >4
content slides. Cheap to change here, expensive to change after rendering.

### Step 2 — Slide plans
For each slide, one line before building: **message** (= the title's claim),
**evidence** (the exhibit + its source), **layout pattern** (see references),
**chart type** (or "no chart — framework/table").

### Step 3 — Render
Invoke the chosen renderer with the specs. Decks with 4+ content slides get a
**title slide + a one-slide executive summary** (the governing thought plus the
2–4 branches) prepended automatically.

### Step 4 — Humanizer pass (route to content-quality)
Run the copy through the `content-quality` skill: kill banned phrases, enforce
numbers-over-adjectives, active voice, no throat-clearing. Consulting decks are
a prime slop vector ("leverage synergies to drive holistic value"). This pass
is not optional.

### Step 5 — Self-check (the critic)
Run the checklist below per slide. Anything unchecked → fix before delivery.
For high-stakes decks, do a dedicated critic pass: read the deck *as the
skeptical executive* and answer "what's the weakest claim, and where's the
missing 'so what?'"

---

## Built-in layouts

Standard patterns (full specs in `references/layout-charts-type.md`): **lead
exhibit** (one big chart + action title + 1–2 takeaway callouts), **2×2
matrix**, **driver tree / issue tree**, **waterfall**, **column comparison**,
**stage/process row**, **Harvey-ball scorecard**.

### The proof / case-study slide (Sierra pattern)

For any slide showcasing a shipped project, customer, or result, use the
outcome-led skeleton lifted from how Sierra writes up client work — one rigid
pattern, repeated, led by the outcome:

> **Problem** (why it was needed) → **Solution** (what was built, in one line)
> → **Metric + quote** (one verifiable number, hedged if vendor-reported) →
> **Detail** (2–4 concrete examples of what it does).

The action title states the *outcome*, never the activity: "Cut cancellations
50% by catching intent before checkout" — not "The Retention Agent." A catalog
of many projects becomes one dense table: **Name · Context · What it does ·
Result**. This is also the `case-study` skill's core template — use that skill
to draft the write-up, then drop it into this layout.

---

## Palette & type (defaults)

- **Colors:** one primary brand color (action title + 2px rule + key series),
  one secondary, one highlight for the single thing the eye should land on,
  greyscale for everything contextual. Every color has a job. Adopt a supplied
  brand kit; fallback is a deep neutral (charcoal/maroon), never rainbow.
- **Layout:** white background, aligned columns, ≥20% whitespace, generous
  margins. No cards, shadows, gradients, rounded boxes, or clip-art.
- **Type:** integer sizes from one scale, nothing below 15px/11pt anywhere.
- For any chart color or categorical-palette decision, route to **`dataviz`** —
  don't hand-pick chart colors here.

---

## Self-check checklist (per slide)

- [ ] Title is a complete-sentence so-what, ≤2 lines
- [ ] Titles read alone tell the full story (headline-flow test passes)
- [ ] Exactly one message on the slide
- [ ] Chart is real, axes labeled with units, ≥15px type
- [ ] Every number has a source line; vendor figures hedged
- [ ] Zero fabricated data or sources
- [ ] Maps to a MECE branch (no orphan slide)
- [ ] Ran content-quality: zero banned phrases
- [ ] ≥20% whitespace; flat styling; palette roles honored

---

## Cross-skill routing

- **`content-quality`** — Step 4 humanizer pass. Mandatory.
- **`dataviz`** — all chart-color and categorical-palette decisions.
- **`pptx`** — the default renderer for editable decks.
- **`case-study`** — drafting any project/customer write-up that lands on a
  proof slide.
- **`theme-factory`** — when the user wants a distinct visual theme over the
  consulting default.

## Failure modes

1. **Rendering before storylining.** The most expensive mistake. If titles
   don't argue the case, no amount of chart polish saves the deck.
2. **Label titles.** "Market Overview" is a table of contents entry, not a
   slide title. State the conclusion.
3. **Two messages, one slide.** Split it.
4. **Decoration over density.** Shadows and gradients read as *less* credible to
   this audience, not more. Flat and dense is the signal.
5. **Invented precision.** A fabricated "37%" destroys the deck's authority the
   moment someone asks for the source. `[source: TBD]` and ask.
