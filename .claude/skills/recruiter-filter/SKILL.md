---
name: recruiter-filter
description: >
  Acts as the AI screening layer an Ashby / Greenhouse / Lever / Workday recruiter
  runs applicants through. Give it a CV plus a job posting (link or pasted text) and
  it returns a 0-100 fit score, the knockouts that would drop the application before
  scoring, what the filter and the 6-second human skim actually see, and a ranked
  list of fixes with the points each one recovers. Activates on "score my resume
  against this job", "will this pass the ATS", "rate my CV for this role", "what
  should I fix before I apply", or a CV plus a job link.
---

# recruiter-filter

Screens a CV against a specific job the way the hiring stack actually screens it, then
says what to fix. Diagnosis, not rewriting — rewriting is a handoff (Step 6).

## What is actually being simulated

Get this right or the advice is wrong. **Almost nothing auto-rejects on resume content.**
In a 2026 Enhancv survey of 25 US recruiters, only 8% had configured any content-based
auto-rejection at all (small sample — directionally right, not a hard number).
Ashby's AI review deliberately emits *no numerical score* — it tags fit levels against
recruiter-defined criteria with citations. Greenhouse's AI
surfaces strong candidates to the top and removes no one. Workday/HiredScore grades
A-D, but a human still decides.

So the filter is **three layers, and only the first one is a robot that says no**:

| Layer | Who/what | Kills you by |
|-------|----------|-------------|
| 1. Knockouts | Application-form rules | A wrong answer on work auth, location, years, or a required credential |
| 2. Ranking | ATS AI / recruiter search | Sorting you below the ~20 profiles a human will actually open |
| 3. The skim | A human, ~6 seconds, top third | Not making the JD's core requirement obvious on sight |

The goal is **not** "beat the bot." It is: survive Layer 1, rank in Layer 2, and win
Layer 3. Every fix this skill emits must serve one of those. Detail and sources:
`references/screening-stack.md`.

## Step 0 — Get both inputs. Do not score with one.

**Job posting.** If given a URL, the `job-fetch` skill handles it (ATS public APIs, with
a Composio remote-exec fallback for the web sandbox's 403 egress block). Note the ATS
from the host — it changes the Layer-1 advice. If given pasted text, use it as-is.

**CV.** Pasted or uploaded text wins. If none is supplied, pull the base resume:
`add_repo hbschlac/product-networking-skills` → read `references/resume.md`. Redirect
gotcha: if that returns "not accessible," retry `add_repo hbschlac/career-skills`.

Missing either one → ask for it. Never score against a remembered or assumed CV.

## Step 1 — Rebuild the recruiter's criteria list

This is the step people skip. A recruiter configures screening criteria from the JD;
reconstruct that list before judging anything. Extract into a table:

- **Title(s)** the req is filed under, and the seniority band.
- **Must-haves** — everything in Requirements / Qualifications stated without a hedge,
  plus anything repeated in the summary. Years, domain, scale, tools, credentials.
- **Nice-to-haves** — "preferred," "bonus," "a plus."
- **Outcomes** — what the role is measured on ("own the roadmap for X," "grow Y").
  These matter more than the skills list; they are what evidence gets matched against.
- **Hard gates** — location/onsite days, work authorization, clearance, degree, comp band.
- **Vocabulary** — the exact nouns this company uses for the work. Copy them verbatim.

## Step 2 — Knockout gate (pass/fail, before scoring)

Check each hard gate. Any fail is reported **first and on its own** — a 92 that fails
work authorization is a 0, and saying "great match!" above it is malpractice.

Also screen the **application questions**, not just the resume: on Ashby and Greenhouse
the custom questions are where knockouts are actually wired, and free-text boxes ("why
this company") are increasingly LLM-read. If the posting's questions are visible, flag
the ones that gate.

Distinguish **hard** gates (authorization, clearance, licensure, physical location for
onsite roles) from **soft** ones (a "5+ years" against her 4.5, a degree preference).
Soft gates cost points in Step 3; they do not end the run.

## Step 3 — Score, 100 points

| # | Dimension | Pts | How to award |
|---|-----------|-----|--------------|
| 1 | Title & seniority match | 20 | Full if a CV title matches a title a recruiter would search for this req. Partial for adjacent-but-searchable ("Product Owner" vs "Product Manager"). Low if the mapping needs a human to infer it. |
| 2 | Must-have coverage | 25 | Score each Step-1 must-have: **full** = present with evidence, **half** = claimed but unevidenced, **zero** = absent. Sum, normalize to 25. |
| 3 | Evidence & impact | 20 | Quantified outcomes that match the JD's *own* success metrics. Scope numbers (users, revenue, volume, team, budget) beat activity verbs. Unquantified duty lists score low however senior. |
| 4 | Vocabulary alignment | 15 | The JD's exact nouns, present in context on the CV. Both the search index and the embedding match run on these. Stuffing scores zero — see Anti-patterns. |
| 5 | Recency & trajectory | 10 | Matches in the current/most recent role are worth far more than the same matches six years ago. Rising scope, no unexplained gaps. |
| 6 | Parse & skim safety | 10 | Machine-readable *and* human-skimmable: single column, real text, standard section headers, consistent dates, contact details in the body not the header image. |

**Bands**

- **85-100 — Top of stack.** Apply as-is. Spend the time on outreach instead.
- **70-84 — Makes the pile.** Two or three fixes moves it to the top.
- **55-69 — Buried mid-stack.** Real work needed; the fixes below are the job.
- **Under 55 — Will not surface.** Either a structural rewrite, or the honest read is
  that this is the wrong req. Say which. A cold application at this level is a lottery
  ticket; a referral is worth more than any edit.

Show the per-dimension breakdown, not just the total — the total says how she's doing,
the breakdown says where the work is.

## Step 4 — The two things a screener actually sees

Report these verbatim before the fixes. They are more persuasive than the score.

**What the AI review cites.** For each must-have, the exact CV line the tool would cite
as evidence — or "no evidence found." Ashby-style review is citation-based; a must-have
with no citable line is functionally uncovered even if she's done the work.

**What the 6-second skim retains.** Read only the top third of page one — headline,
current title, first two bullets. State what a recruiter walks away knowing, then say
which of the JD's must-haves that covers. If the role's core requirement is not visible
in that block, that is almost always the single highest-value fix on the page.

## Step 5 — The fix list, ranked by points recovered

The deliverable. Every fix carries: the dimension, the **exact before → after line**,
the points it recovers, and which of the three legal moves it is. Close with the
projected score: *"62 → 84 if you do the top three."*

**Three legal moves. Everything else is a gap, not a fix.**

1. **Surface** — she has it; it's buried, late, or unlabeled. Move it up, name it in the
   JD's words. Highest yield, zero risk, most commonly available.
2. **Reframe** — same work, the JD's vocabulary. "Owned the BuyBox" → "owned the ML
   ranking system behind ~400M daily product page views." The work is identical; the
   words are the ones the req was written in.
3. **Quantify** — she knows the number and it isn't on the page. **Ask her for it.**
   Never estimate a number onto a resume.

If a requirement can't be met by one of those three, it is a **gap**. Report it as a
gap and say whether it is survivable (most are — reqs are wishlists) or effectively
disqualifying. Do not paper over it. Fabricating experience fails the first screening
call and is the one failure mode that costs more than not applying.

Cap the list at the top 5-7. A fix list longer than the resume gets ignored.

## Step 6 — Handoffs (only when asked)

- **Apply the edits** → `product-networking` skill (separate repo; `add_repo` per Step 0).
  Pass it the fix list; it owns resume format, rules, and publishing.
- **Check any rewritten line** → `aislop` skill, then `content-quality`. Resume bullets
  are exactly where AI phrasing reads as filler.
- **Log the application** → `job-tracker` skill.
- **Under 55, or a role worth extra** → `project` skill (build something for the team)
  and `job-search` (find better-fitting reqs at the same company).

## Anti-patterns — do not emit these as advice

- **Keyword stuffing or white-text keywords.** Parsers read hidden text regardless of
  color, recruiters see the wall instantly, and enterprise teams treat it as a trust
  flag and reject on sight. Terms without supporting evidence collapse at the first call.
- **"The ATS auto-rejected you."** It almost certainly did not. Repeating the debunked
  "75% of resumes are auto-rejected" line (traced to a 2012 vendor claim, never
  substantiated) sends the fix effort to the wrong layer.
- **Template panic.** Plain single-column formatting matters, but a clean CV that
  doesn't evidence the must-haves loses to a plain one that does. Dimension 6 is 10
  points for a reason.
- **Rewriting the whole CV per application.** Tailor the headline, the top-third, and
  the current-role bullets. The rest is stable.
- **Scoring generously.** An inflated score costs her a week of silence. If it's a 58,
  it's a 58.

## Output shape

```
VERDICT   74/100 — Makes the pile. Three fixes puts it top of stack.
KNOCKOUTS Pass (onsite SF ✓ · work auth ✓ · 5+ yrs ✓)

SCORE     Title & seniority    16/20
          Must-have coverage   17/25   ← weakest
          Evidence & impact    18/20
          Vocabulary           10/15
          Recency              8/10
          Parse & skim         5/10

SEES      Top-third skim: "Senior PM at Walmart, ML/BuyBox, 400M daily views."
          Covers 2 of 5 must-haves. Missing: platform/API ownership, 0→1.

FIX 1  (+6, must-haves · surface)  Muse is on page 2 as a side project; it is
       the only 0→1 platform evidence you have. Move it into the top third.
       before: "Muse — personal project, shopping platform"
       after:  "Muse (muse.shopping) — built and shipped a 0→1 agentic
                commerce platform solo: 264 brands, 10 retailers, one checkout."
FIX 2  (+4, vocabulary · reframe)  ...
FIX 3  (+3, parse · surface)  ...

PROJECTED  74 → 87
GAPS       No B2B SaaS experience (survivable — 1 of 9 "preferred" bullets).
```

Adapt the shape to the case; keep the order: verdict → knockouts → score → what it
sees → ranked fixes → projected → gaps.
