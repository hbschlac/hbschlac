---
name: content-quality
description: >
  Prevents AI slop, hallucinated references, and claims that don't match
  what shipped. Activates on any task producing user-facing text: portfolio
  copy, README content, case studies, landing pages.
---

# content-quality

## Activation

Triggers when writing or editing: portfolio/case study content, README descriptions,
landing page copy, any text making claims about what a product does.

Does NOT activate for: code-only changes, config files, internal comments.

Also invoked by code-builder Step 6 when a code diff includes user-facing text.

---

## Banned Phrases

Never write these or close variants:

- "Leveraging" / "harnessing" / "utilizing" → use "using"
- "Cutting-edge" / "state-of-the-art" / "best-in-class" → remove or be specific
- "Seamless" / "seamlessly" → say what actually happens
- "Robust" / "comprehensive" / "holistic" → remove or be specific
- "Empower" / "elevate" / "unlock" → remove
- "Streamline" / "optimize" → only if describing literal perf optimization with numbers
- "Ecosystem" → only for actual software ecosystems
- "Journey" → only if someone is literally traveling
- "Delve" / "dive deep" / "deep dive" → remove
- "Game-changer" / "paradigm shift" → remove
- "At the end of the day" / "It's worth noting that" / "In today's [anything]" → remove
- "As a [role], I [verb]" → the LinkedIn opener pattern, remove
- "Passionate about" / "excited to" → remove or state the specific interest
- "End-to-end" → only for literal pipeline descriptions with defined endpoints
- "Innovative" / "groundbreaking" / "revolutionary" → remove
- "Spearheaded" / "orchestrated" / "championed" → use "led" / "built" / "ran"
- "Synergy" / "cross-functional" → say who was actually involved
- "Stakeholder alignment" → say what was actually agreed on
- "Drive [noun]" (as in "drive impact") → say what actually happened
- "Passionate problem-solver" / "detail-oriented" → remove, show don't tell
- "World-class" / "enterprise-grade" → remove unless literally describing enterprise software
- "Democratize" / "democratizing" → say who gets access to what

---

## Voice Rules

1. **Short sentences.** Over 25 words → split or cut.
2. **Concrete over abstract.** Not "improved performance" — say "7% CVR improvement" or "cut page load from 3s to 800ms."
3. **Active voice.** "I built X" not "X was built."
4. **No throat-clearing.** Delete sentences that could be removed without losing information.
5. **Match the maker's voice.** Hannah writes direct, specific, slightly irreverent ("No CS degree.", "book just appears"). Match that energy. Don't smooth it into corporate.
6. **No hedging.** Don't write "I helped build" or "I contributed to" when "I built" is accurate.
7. **No filler transitions.** Don't write "Additionally," "Furthermore," "Moreover." Just state the next point.
8. **Numbers before adjectives.** "264 brands" is more convincing than "hundreds of brands." If you have the number, use it.

---

## Hallucination Prevention

### URLs

- Never fabricate URLs. Use `[TODO: add URL]` if unverified.
- For GitHub repos: verify owner/repo pattern matches known repos.
- For external sites: only include URLs the user provided or that appear in project files.
- For images: only reference files that exist. Run `ls` to verify.

### Claims

- Check the source of truth. Read actual code/config, not just existing README.
- Numbers must come from data. Don't write "264 brands" without a source.
- Feature claims must match current deployed state, not what was planned.
- Personal claims ("built solo", "no CS degree"): only include if in existing content.
- Stack/technology claims: verify by reading actual dependency files.

---

## Review Checklist

Before finalizing content:

- [ ] Zero banned phrases (search the diff)
- [ ] Every URL verified or marked `[TODO]`
- [ ] Every number has a source
- [ ] Every feature claim matches deployed state
- [ ] No sentences over 25 words
- [ ] No throat-clearing paragraphs
- [ ] Active voice throughout
- [ ] Tone matches existing voice
- [ ] No emoji unless existing content uses them in that context

---

## Common Failure Modes

1. **The "impressive rewrite" trap.** Don't make copy sound more impressive — make it more specific. "ML system behind ~400M daily product page views" beats "cutting-edge ML platform powering millions of interactions."

2. **The "summary paragraph" trap.** Case studies don't need opening summaries. Lead with the most interesting specific fact.

3. **The "feature list" trap.** Don't enumerate every feature. Pick the 2-3 most differentiated.

4. **The "inflated scope" trap.** Don't describe a side project with the same gravity as a production system. Match tone to actual scale.

5. **The "resume voice" trap.** Portfolio content is not a resume. Don't write "Spearheaded cross-functional initiative to drive stakeholder alignment." Write "Led 3 engineers to ship the feature in 2 weeks."

6. **The "Claude voice" trap.** If the output reads like a ChatGPT/Claude response rather than something Hannah would write, rewrite it. Test: would Hannah post this on her LinkedIn? If it sounds like an AI wrote it, it's wrong.

---

## Changelog

- **2026-05-29 — v4: Added "Claude voice" failure mode, expanded banned phrases**
  - Added: "passionate problem-solver", "world-class", "enterprise-grade", "democratize"
  - Added: "numbers before adjectives" voice rule
  - Added: "Claude voice" failure mode (#6)
  - Carried forward all v3 improvements
- **2026-05-27 — v3: expanded banned phrases and failure modes**
- **2026-05-24 — v2: consolidated from 25 session branches**
- **2026-05-16 — v1: initial version**
