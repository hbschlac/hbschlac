---
name: content-quality
description: >
  Prevents AI slop, hallucinated references, and claims that don't match
  what actually shipped. Activates on any task producing user-facing text.
  Enforces voice-matching, URL verification, and claim-vs-shipped checks.
  Includes deduplication guard to prevent rewriting content that already
  exists on other branches.
---

# content-quality

Prevents AI slop, hallucinated references, and claims that don't match what actually shipped. Activates on any task that produces user-facing text: portfolio copy, README content, case study descriptions, landing pages, commit messages describing features.

## Activation

Triggers when the task involves writing or editing:
- Portfolio or case study content
- README descriptions of projects
- Landing page copy
- Any text that makes claims about what a product does
- Blog posts, documentation, or explainer content

Does NOT activate for: code-only changes, config files, internal comments.

**Cross-skill coordination:** When code-builder is handling the code portion of a task, content-quality runs as a post-merge review on any user-facing strings in the diff. Both skills don't need to announce separately — code-builder mentions "content-quality review pending" in its merge report.

## Anti-Slop Rules

These patterns are banned. If Claude catches itself writing any of them, rewrite immediately.

### Banned Phrases

Never write any of these or close variants:
- "Leveraging" / "harnessing" / "utilizing" (use: "using")
- "Cutting-edge" / "state-of-the-art" / "best-in-class"
- "Seamless" / "seamlessly" (say what actually happens)
- "Robust" / "comprehensive" / "holistic"
- "Empower" / "elevate" / "unlock"
- "Streamline" / "optimize" (unless describing a literal performance optimization with numbers)
- "Ecosystem" (unless referring to an actual software ecosystem)
- "Journey" (unless someone is literally traveling)
- "Delve" / "dive deep" / "deep dive"
- "Game-changer" / "paradigm shift"
- "At the end of the day"
- "It's worth noting that"
- "In today's [anything]"
- "As a [role], I [verb]" (the LinkedIn opener pattern)

### Voice Rules

1. **Short sentences.** If a sentence has more than 25 words, split it or cut words.
2. **Concrete over abstract.** Don't say "improved performance" — say "7% CVR improvement" or "cut page load from 3s to 800ms."
3. **Active voice.** "I built X" not "X was built."
4. **No throat-clearing.** Delete any sentence that could be removed without losing information. Opening paragraphs that "set the stage" are almost always throat-clearing.
5. **Match the maker's voice.** The user writes direct, specific, slightly irreverent ("No CS degree.", "book just appears"). Match that energy. Don't smooth it into corporate.

## Hallucination Prevention

### URL Verification

Before including ANY external URL in content:

1. **Never fabricate URLs.** If you don't have a verified URL, say `[TODO: add URL]` instead.
2. **For GitHub repos:** Verify the repo exists by checking the owner/repo pattern matches known repos (the user's repos are under github.com/hbschlac/).
3. **For external sites:** Only include URLs the user has explicitly provided or that appear in existing project files. Never guess at URL structures.
4. **For screenshots/images:** Only reference files that exist in the repo's public/ or assets/ directory. Run `ls` to verify before referencing.

### Claims Verification

Before writing any claim about what a project does:

1. **Check the source of truth.** Read the actual code, package.json, or deployment config — not just the existing README or description (those might be outdated).
2. **Numbers must come from data.** Don't write "264 brands" unless you can point to where that number comes from in the code or data.
3. **Feature claims must match current state.** If the code shows a feature was removed or changed, update the description. Don't describe what was planned — describe what shipped.
4. **"Built solo" / "no CS degree" / other personal claims:** Only include if they appear in the user's existing content. Never embellish personal credentials.

## Content Review Checklist

Run this checklist before finalizing any content change:

- [ ] Zero banned phrases (search the diff)
- [ ] Every URL either verified or marked `[TODO]`
- [ ] Every number has a source (code, data, or user-provided)
- [ ] Every feature claim matches current deployed state
- [ ] No sentences over 25 words
- [ ] No throat-clearing paragraphs
- [ ] Active voice throughout
- [ ] Tone matches the user's existing voice (direct, specific, builder-energy)
- [ ] No emoji unless the user's existing content uses emoji in that context

## Common Failure Modes to Watch For

These are patterns observed in past sessions:

1. **The "impressive rewrite" trap.** When asked to improve copy, don't make it sound more impressive — make it more specific. Specificity IS impressive. "ML system behind ~400M daily product page views" beats "cutting-edge ML platform powering millions of interactions."

2. **The "summary paragraph" trap.** Case studies and project descriptions don't need opening summaries. Lead with the most interesting specific fact.

3. **The "feature list" trap.** Don't enumerate every feature. Pick the 2-3 that are most differentiated and describe those well. "264 brands, 10 retailers, one checkout" is better than a bullet list of 15 features.

4. **The "context-switching" language trap.** When writing JS after working on Python (or vice versa), watch for language idioms leaking: wrong string escaping, wrong iteration patterns, wrong error handling conventions. Always verify the output language matches the target file.

5. **The "rewrite from scratch" trap.** When improving a README or case study, READ the existing version first and iterate on it. Don't start from blank. Five sessions (Apr 22 – May 15) independently rewrote the same README because each started from scratch instead of building on the best prior version. Always `git log --all --oneline -- {file}` to check for better versions on other branches before rewriting.

6. **The "planned feature" trap.** Descriptions of features that were designed but never shipped get committed as if real. Before writing "supports X", grep the codebase for evidence that X actually works. If it's a TODO, say "[planned]" or omit it.

## Deduplication Guard

Before writing or substantially rewriting any content file (README, case study, landing page):

1. Run `git branch -a --contains -- {file}` or `git log --all --oneline -- {file}` to check if the file was recently rewritten on another branch
2. If a recent rewrite exists on another branch, read that version first: `git show {branch}:{file}`
3. Build on the best existing version rather than starting from scratch
4. This prevents the "5 independent README rewrites" failure pattern
