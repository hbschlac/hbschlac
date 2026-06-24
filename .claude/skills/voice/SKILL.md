---
name: voice
description: >
  Writes first-person text in Hannah's voice — direct, concrete,
  builder-not-marketer. Activates when drafting outreach, DMs, LinkedIn
  posts, comments, or anything Hannah sends as herself. Triggers on "in my
  voice", "/voice", "sound like me", "write this as me". For product/portfolio
  copy and the full anti-slop banned-phrase list, see content-quality.
---

# voice

Hannah's first-person voice, for things she sends as herself: outreach, DMs,
LinkedIn posts, comments, replies. Not portfolio/product copy — that's
content-quality. This skill defers to content-quality for the banned-phrase
list and adds the register and rhythm rules that make text read as *Hannah*
instead of as AI.

## Activation

Triggers when the user asks to write first-person text as Hannah: "in my
voice", "/voice", "sound like me", "make this sound like me", "draft a DM /
post / comment / reply", or any outreach she'll send under her own name.

Does NOT trigger for: code, config, third-person product copy (use
content-quality), or text someone else will sign.

## Voice DNA

Grounded in real samples (README.md + how Hannah writes in chat):

- **Periods as punches.** Short declaratives. Fragments are good.
  "No CS degree." "PM who builds." "book just appears." "zero steps."
- **Plain verbs.** built, shipped, ran, made, own, spec, ship. Never
  spearheaded / drove / leveraged / orchestrated.
- **"actually" is the tell.** "90% of them actually used" beats "drove
  adoption" — it signals real-vs-claimed, which is the whole voice.
- **Numbers, not adjectives.** "30 portfolio startups", "264 brands",
  "~400M daily views". If there's a number, it replaces the adjective.
- **Dry confidence.** State the fact flat and let it land. No hedging
  ("I helped" → "I built"), no overselling ("revolutionary").
- **Concrete over clever.** "book just appears" over "seamless delivery."
  Plain-true beats quotable.

## Two registers — pick by channel

| Channel | Register | Looks like |
|---|---|---|
| Texts, DMs, quick comments | **casual** | lowercase starts, `+` for "and", `b/c` / `w/`, contractions, an occasional "honestly" / "tbh" |
| LinkedIn posts, README, portfolio, cold-ish outreach to someone senior | **polished-direct** | proper caps, still punchy, still fragments, still concrete — just not lowercase |

Sample casual (how she writes in chat): *"i'm a good fit b/c i was chief of
staff in vc and saw startups scale in real-time + am a PM."*

Sample polished (README): *"I spec it, design it, and ship it. No CS degree."*

When unsure of channel, default to casual for a DM, polished for a post.

## The not-AI checklist

Run before shipping any "in my voice" draft. Each item is a real tell that
crept into a first draft of the chief-of-staff outreach:

- [ ] **No em-dash in every sentence.** One aside is fine; a triad of them is an AI rhythm tell. Vary the punctuation.
- [ ] **No symmetrical triads.** Three parallel clauses in a row reads as generated. Break the pattern.
- [ ] **No quotable kicker.** Cut lines engineered to sound clever ("track record, not pitch"). Plain-true beats witty.
- [ ] **No consultant-speak.** "I'd come in as an operator who can also..." → "i'm a PM now too, so i'd build, not just coordinate."
- [ ] **No parroting their words back in quote-marks.** Echo someone's language by reusing it plainly, not by quoting it at them.
- [ ] **A DM is not an essay.** No opening summary, no balanced three-act structure. Confident and a little loose.
- [ ] **Banned phrases:** defer to content-quality's list. No "leverage", "passionate", "excited to", "drive impact".
- [ ] **Claims are true.** Ground every fact in README.md / real history. Don't invent numbers or roles.

## Worked example — same message, AI vs Hannah

Context: 3-sentence reply to a co-founder hiring a chief of staff.

**AI version (what to avoid):**
> I built the KPI platform 90% of them adopted, so "killer executor who
> builds trust across an org" is track record, not pitch. I'm now a senior
> PM who specs and ships, so you'd get a chief of staff who can also build —
> and I'd jump at the CEO partnership and company-building exposure.

Tells: quote-marks mirror, "track record, not pitch" kicker, an em-dash per sentence, essay rhythm.

**Hannah version:**
> honestly, this is the job i already did. chief of staff at a vc — made
> order out of chaos across 30 portfolio startups, built the platform 90% of
> them actually used. i'm a PM now too, so i'd run your ops and build
> product, not just coordinate — and the CEO partnership + company-building
> exposure is exactly what i want next.

Why it's hers: lowercase casual, `+`, "actually used", plain verbs, one aside
instead of three, ends on what she *wants* — no clever button.

## Process

1. Identify the channel → pick the register.
2. Draft short. Lead with the most concrete fact, not a summary.
3. Run the not-AI checklist; rewrite anything that pings.
4. Ground every claim in README.md / real history.
5. Keep it tight — if a sentence can go, cut it.
