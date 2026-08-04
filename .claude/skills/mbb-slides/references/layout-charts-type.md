# Layout, charts, and typography

Flat, dense, aligned. To this audience, decoration reads as *less* credible.

## The grid

- **Canvas:** 16:9. For the `pptx` renderer, standard widescreen; for HTML
  artifacts, a 1280×720 `<section>` per slide.
- **Margins:** generous and consistent (~64px top / 48px sides / 40px bottom on
  a 1280 canvas). Never crowd the edge.
- **Whitespace:** ≥20% of the slide is empty. Density comes from *information*,
  not from filling every pixel.
- **Alignment:** everything sits on a column grid. Ragged left edges are the
  fastest tell of an amateur deck. Align labels, align numbers (right-align
  numerals), align exhibit tops.
- **No:** cards, drop shadows, gradients, rounded containers, 3-D effects,
  clip-art, stock photos, or icon soup. Icons only as small row/pillar markers
  (thin stroke, ~1.5px), never decorative.

## Slide anatomy (top to bottom)

1. **Action title** — brand color, ≤2 lines, with a thin (2px) rule beneath it.
2. **Body** — the single exhibit (chart / table / framework) proving the title.
3. **Takeaway callouts** — 1–2 short annotations pointing at the "so what" on
   the exhibit itself.
4. **Source line** — bottom, small (but ≥15px), e.g. "Source: company filings,
   2025; team analysis." Every data slide has one.
5. **Optional page furniture** — section tracker, page number.

## The workhorse charts

Ninety percent of consulting exhibits are one of these. Prefer them; they read
instantly.

- **Bar + callout** — ranked horizontal bars, the one bar that matters in the
  highlight color, a callout annotating it. Best default for comparison.
- **Stacked-over-time** — stacked columns across a time axis to show mix shift.
  Label the total on top; annotate the segment that's changing.
- **Waterfall** — bridges a start value to an end value through +/− steps.
  The go-to for "what drove the change." Label each step's delta.
- **Line** — trend over time. Two or three series max; label series at the end
  of the line, not in a detached legend.
- **2×2 matrix** — two axes, four quadrants named, items plotted. For
  positioning/prioritization. Name the quadrants with words, not just axes.
- **Column comparison** — side-by-side options against consistent criteria rows.

### Chart rules

- **Real chart objects.** Native pptx charts via the renderer; Chart.js in an
  HTML artifact. Never CSS-width bars, never hand-drawn SVG rectangles, never a
  screenshot of a chart.
- **Axes labeled with units.** "$M," "%", "days." A y-axis the reader has to
  guess at is a failed exhibit.
- **One highlight.** Grey out the context; color only the data point the title
  is about. The eye should land where the argument is.
- **Data labels over gridlines.** Label the bars/points directly; drop heavy
  gridlines. Less ink, faster read.
- **No dual axes** unless unavoidable, and never a second y-axis just to fit
  two series — it distorts.
- **Color decisions route to `dataviz`.** Don't hand-pick categorical palettes
  here.

## Frameworks (when there's no chart)

Some slides argue with structure, not data:

- **Issue tree / driver tree** — MECE decomposition, left-to-right. Each split
  is exhaustive at its level.
- **Stage / process row** — 3–5 stages left to right with one line each. For
  sequence or methodology.
- **Harvey-ball scorecard** — options × criteria grid, filled circles
  (0/¼/½/¾/full) for at-a-glance comparison. The consulting classic for
  qualitative scoring.
- **Pyramid / layered** — for hierarchies or maturity models.

Keep frameworks as clean as charts: aligned, labeled, one message.

## Typography

- **One type scale, integer sizes.** Pick from a fixed scale (e.g. 15 / 18 / 22
  / 28 / 36). No 13.5px, no arbitrary sizes.
- **Floor: 15px / 11pt.** Nothing smaller anywhere — including axis labels, data
  labels, and source lines. If content doesn't fit at 15px, there's too much on
  the slide; cut it, don't shrink it.
- **Hierarchy through size and weight, not color.** Title > exhibit heading >
  body > source, by size. Color is reserved for the highlight job.
- **Right-align numbers** in tables so digits line up by place value.
- **Sentence case** for titles (not Title Case, not ALL CAPS) — it reads as a
  sentence, which is the point of an action title.

## Executive summary slide

Decks with 4+ content slides get one, right after the title slide:

- The **governing thought** as the headline (the deck's one-sentence answer).
- The **2–4 branches** as supporting lines, each with its key number.
- No chart. This slide is the whole argument in 30 seconds — the one slide a
  busy exec will actually read.
