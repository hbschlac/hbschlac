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

Also activates for: GitHub repo descriptions, PR titles/descriptions, commit messages in
public repos, project taglines, **GitHub profile README** (`hbschlac/hbschlac/README.md`).

Also invoked by code-builder Step 6 when a code diff includes user-facing text.

### Profile README rules

The profile README is the highest-traffic content piece. Extra rules:
- **Keep it current.** Every shipped project should be represented. Check: does the projects table match what's actually deployed?
- **Projects table is the portfolio's front door.** Each row: name (linked), one-line description, stack. No filler. No unshipped projects.
- **Tone: builder, not marketer.** "No CS degree." is the voice. "Passionate about leveraging technology" is not.
- **Work section: numbers over narrative.** "7% CVR improvement" beats "drove significant improvements."
- **Update triggers:** new project shipped, role change, significant feature launch. Not every commit.

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
- "It's important to note" / "It's worth mentioning" → just say it
- "Let me [verb]" / "I'd be happy to" → just do it (Claude-voice tell)
- "Great question" / "That's a great point" → remove (flattery filler)
- "In order to" → "to"
- "A wide range of" / "a variety of" → be specific or use a number
- "Solution" (as a product descriptor) → say what it actually does

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

## Commit and PR Content

Commits and PRs are the most frequent content every session produces. Apply voice rules here too.

### Commit messages

- **Lead with what changed, not what you did.** "Add retry logic for webhook delivery" not "Updated the webhook handler to include retry logic."
- **No AI filler.** "This commit updates..." / "The following changes..." — just state the change.
- **Be specific.** "Fix TypeScript error in NavBar props" not "Fix build error."
- **Keep the first line under 72 chars.** Details go in the body.

### PR titles and descriptions

- **Title: imperative mood, under 70 chars.** "Add cross-source download fallback" not "Added comprehensive fallback system for downloads."
- **Body: what and why, not how.** The diff shows how. The body explains what problem this solves and why this approach.
- **No banned phrases in PR descriptions.** "Robust error handling" → "Retry with 3 fallback sources." Same rules as portfolio copy.
- **Include numbers.** "30s→3s search latency" is more useful than "improved performance."
- **Out-of-scope list.** State what's intentionally NOT included. Prevents reviewers from asking about missing features.

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

## Ship Announcements

When a project ships or hits a milestone, you need announcement content. These are not portfolio copy — they're shorter, more casual, and have a call to action.

### LinkedIn/social post template

```
{What I built — one line, concrete.}

{The interesting technical or product detail — what makes it not boring.}

{The number or result — users, improvement, scale.}

{Link or CTA.}
```

Example: "Built a system that delivers library books to your Kindle automatically. You reserve a book at the library, it just appears on your Kindle. No steps. Zero-touch cloud automation with fallback across 3 download sources. kindle.schlacter.me"

**Rules:**
- No "excited to announce" / "thrilled to share" — banned phrases apply here too
- Lead with what it does, not that you built it
- One technical detail that makes it interesting to builders
- One number that proves it works
- Under 200 words for LinkedIn, under 280 chars for Twitter/X
- Don't self-deprecate ("just a side project") and don't oversell ("revolutionary")

### Release notes / changelog

For feature updates to shipped products:

```
## {Version or date}

- **{Feature name}:** {What it does, in one line.} {Why it matters.}
- **Fix:** {What was broken.} {What it does now.}
```

No "various improvements" or "bug fixes and performance improvements." If you can't name it, it's not worth announcing.

---

## Error and Status Copy

User-facing error messages and status indicators are content too. The same banned-phrase and voice rules apply, plus:

### Error messages

- **Say what happened, not what went wrong internally.** "This book couldn't be delivered" not "EPUB validation failed: mimetype entry not STORED."
- **Say what to do next.** Every error should have an action: retry, try another version, contact support. "Download failed" with no next step is a dead end.
- **Be honest about what you know.** "Sent to Amazon — it may take a few minutes to appear" is better than "Delivered!" when you don't actually know if Amazon accepted it. (kindle-schlacter-me PR#16)
- **Don't hide failures.** A download that fails silently is worse than one that shows an error. Make failures visible and persistent — they shouldn't disappear on page reload. (kindle-schlacter-me PR#13)

### Status indicators

- **Match the status to reality.** If the server completed but the client doesn't know, the status should resolve on the next check — not stay stuck on "Sending..." indefinitely. (kindle-schlacter-me PR#18)
- **Use progressive disclosure.** "Sending to Kindle" → "Sent — check your Kindle in a few minutes" → "Delivered." Don't jump from "working" to done without the intermediate.
- **Failure status should be sticky.** Success can auto-dismiss. Failure should stay visible until the user acknowledges it or retries.

### Copy patterns for common states

| State | Good | Bad |
|---|---|---|
| In progress | "Sending to Kindle..." | "Processing your request..." |
| Completed | "Sent — should appear on your Kindle shortly" | "Success!" |
| Failed (retryable) | "Download failed — [Try again] [Try another version]" | "Error occurred" |
| Failed (terminal) | "This file can't be delivered to Kindle (format not supported)" | "An error has occurred. Please try again later." |
| Partially completed | "Book sent, but cover image couldn't be loaded" | "Completed with warnings" |

---

## Common Failure Modes

1. **The "impressive rewrite" trap.** Don't make copy sound more impressive — make it more specific. "ML system behind ~400M daily product page views" beats "cutting-edge ML platform powering millions of interactions."

2. **The "summary paragraph" trap.** Case studies don't need opening summaries. Lead with the most interesting specific fact.

3. **The "feature list" trap.** Don't enumerate every feature. Pick the 2-3 most differentiated.

4. **The "inflated scope" trap.** Don't describe a side project with the same gravity as a production system. Match tone to actual scale.

5. **The "resume voice" trap.** Portfolio content is not a resume. Don't write "Spearheaded cross-functional initiative to drive stakeholder alignment." Write "Led 3 engineers to ship the feature in 2 weeks."

6. **The "Claude voice" trap.** If the output reads like a ChatGPT/Claude response rather than something Hannah would write, rewrite it. Test: would Hannah post this on her LinkedIn? If it sounds like an AI wrote it, it's wrong.

7. **The "repo description" trap.** GitHub repo descriptions are the first thing anyone reads. Rules: under 120 chars, lead with what it does (not what it is), include a concrete differentiator. Bad: "A comprehensive personalized shopping platform." Good: "Personalized shopping · 264 brands · 10 retailers · one checkout · built solo."

8. **The "research summary" trap.** Research content (case studies, data analyses, community research) should lead with the finding, not the methodology. Bad: "We conducted an analysis of 1,183 data points." Good: "1,183 Twitch users say discovery is broken. Here's what they want instead."

---

## Changelog

- **2026-06-13 — v9: Error and status copy**
  - ADDED: Error and status copy section — user-facing error messages, status indicators, and honest copy patterns
  - ADDED: Copy patterns table for common states (in progress, completed, failed retryable, failed terminal, partially completed)
  - ADDED: Rules for error messages (say what happened not internal details, always include next action, be honest about uncertainty, make failures visible)
  - Evidence: kindle-schlacter-me PRs #13 (durable failures), #16 (honest "emailed to Amazon" copy), #18 (stuck "Sending" status). content-quality covered marketing/portfolio copy but not the error UX copy that every app produces.
- **2026-06-12 — v8: Ship announcements and launch content**
  - ADDED: Ship announcement section — LinkedIn/social post template, release notes template
  - ADDED: Rules for launch content (no "excited to announce," lead with what it does, include one number)
  - Evidence: content-quality covered portfolio copy but not the "I just shipped, tell people" workflow; no template for announcing features or projects
- **2026-06-11 — v7: Profile README rules**
  - ADDED: GitHub profile README to explicit activation scope
  - ADDED: Profile README rules (keep current, projects table, builder tone, update triggers)
  - Evidence: profile README hasn't been updated to reflect kindle-schlacter-me or recs.community; 2 shipped projects missing from the projects table
- **2026-06-10 — v6: Commit and PR content quality**
  - ADDED: Commit message quality rules (lead with change, no AI filler, be specific, 72-char limit)
  - ADDED: PR title/description rules (imperative mood, what not how, include numbers, out-of-scope lists)
  - Evidence: every session produces commits/PRs but had no quality guidance for this content type
- **2026-06-05 — v5: GitHub repo descriptions, research content, expanded Claude-voice bans**
  - ADDED: 7 more banned phrases targeting Claude-specific output patterns
  - ADDED: Activation for GitHub repo descriptions, PR titles, commit messages
  - ADDED: "repo description" failure mode (#7) with length/structure rules
  - ADDED: "research summary" failure mode (#8) — lead with finding, not methodology
- **2026-05-29 — v4: Added "Claude voice" failure mode, expanded banned phrases**
  - Added: "passionate problem-solver", "world-class", "enterprise-grade", "democratize"
  - Added: "numbers before adjectives" voice rule
  - Added: "Claude voice" failure mode (#6)
  - Carried forward all v3 improvements
- **2026-05-27 — v3: expanded banned phrases and failure modes**
- **2026-05-24 — v2: consolidated from 25 session branches**
- **2026-05-16 — v1: initial version**
