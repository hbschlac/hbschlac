---
name: recruiter-filter
description: >
  Acts as the AI screening layer an Ashby / Greenhouse / Lever / Workday recruiter
  runs applicants through. Give it a CV plus a job posting (link or pasted text) and
  it returns a 0-100 fit score, the knockouts that would drop the application before
  scoring, what the filter and the 6-second human skim actually see, and a ranked
  list of fixes with the points each one recovers. Also runs a read-only Gmail scan to
  find what actually happened to submitted applications and feed outcomes back into the
  rubric. Activates on "score my resume against this job", "will this pass the ATS",
  "rate my CV for this role", "what should I fix before I apply", a CV plus a job link,
  or "did I get rejected", "check my applications for outcomes", "is the score working".
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

Then mark which must-haves are **load-bearing**. A req's requirement list is part real
bar, part copied-from-the-last-req padding. Load-bearing = it appears in the title, or in
the role summary, or in the first three responsibility bullets — ideally two of those.
Everything else is wishlist. Score all of them, but weight fixes toward the load-bearing
ones; a perfect score against padding wins nothing.

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

**Check whether the req is alive.** A high score on a dead posting is worse than useless.
Tells: posted date older than ~4 weeks, the same req reposted repeatedly, a listing that
has been open far longer than its peers on the same board, or a company in a public
freeze or recent layoff. The ATS APIs in `job-fetch` return posting dates — use them.
Report req health next to the score. If it looks stale, say the highest-EV move is a
human, not an edit.

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

**Stop optimizing before it costs voice.** Dimension 4 is the one that rewards drifting
toward the JD's language, and 15 points is not worth a resume that reads machine-tailored.
Mirror the req's nouns for the load-bearing requirements only, leave the rest in her
words, and route every rewritten line through `aislop`. Applying this skill across twenty
applications must not produce twenty near-identical resumes.

## Step 6 — Handoffs (only when asked)

- **Apply the edits** → `product-networking` skill (separate repo; `add_repo` per Step 0).
  Pass it the fix list; it owns resume format, rules, and publishing.
- **Check any rewritten line** → `aislop` skill, then `content-quality`. Resume bullets
  are exactly where AI phrasing reads as filler.
- **Log the application** → `job-tracker` skill. Record the score alongside it so Step 7
  can pair it with the outcome later. That pairing is the only route this rubric has to
  ever becoming calibrated.
- **Under 55, or a role worth extra** → `project` skill (build something for the team)
  and `job-search` (find better-fitting reqs at the same company).

## Step 7 — Outcome scan (separate mode; run it on its own)

Scoring is a guess until an outcome lands. This mode reads Gmail (**read-only**) for what
actually happened to submitted applications and turns each one into evidence about the
rubric. Mechanics, verified query shapes, and classification tells:
`references/outcome-scan.md`. Read it before running — the obvious design is wrong in
four specific ways.

1. **Scope the search.** Company names do not appear in ATS sender addresses — almost
   everything arrives from `no-reply@ashbyhq.com` whatever the employer — so match on
   subject and body. Never run bare keyword searches like `subject:application`: her
   mailbox holds financial and medical mail a broad query will surface.
2. **Classify inbound messages only.** She forwards rejections onward, so her own `SENT`
   mail sits in the same thread. And a candidate-experience survey ("Thanks for
   interviewing with X!") is not a rejection — the easiest mistake available here.
3. **Pair confirmation with decision** for days-to-decision, then read the layer:
   - **Under ~72h, no human contact** → knockout or fast skim. If this skill scored the
     application well, **the rubric was wrong** — say so, and re-examine the knockout gate.
   - **1-4 weeks, no interview** → she made the pile and lost on rank. The fix list was
     aimed correctly; Dimensions 2, 3 and 4 are the work.
   - **After an interview** → not a resume problem. Do not open the CV. Route to
     `interview`.
   - **30+ days silent** → ghosted, or the req was never live. Feed back into Step 2.
4. **Write the outcome back** to `job-tracker` as an appended `[rf]` line in `notes` — the
   tracker has no field for scores or outcomes. On web the tracker secret is unreachable
   (laptop path), so print the lines for her to paste instead.

Never commit any of this to the repo. `hbschlac/hbschlac` is public.

## What this does not see — state it, don't bury it

The score is the most quotable thing in the output and the least trustworthy. Say so in
the run; a confident number that hides its own limits is the main way this skill could
do harm.

- **It is uncalibrated.** No outcome data sits behind the rubric *yet*. A 74 is not a
  74% chance of anything — it is ordinal, and re-reading the same bullets can move it
  several points. Lead with the **band**; use the number to rank fixes against each
  other, never as a forecast. Step 7 is the route out, and it needs roughly 15-20 scored
  applications with landed outcomes before it means anything. Until then the honest
  output is "not enough data yet," not a trend.
- **Ranking is relative; this score is absolute.** No view of applicant volume or who
  else applied. The same 74 is a reject in a 400-deep pool and an interview in a 12-deep
  one. If she can see an applicant count, factor it into the band read.
- **The layout is invisible.** This reads text, which is what a working parser does — so
  the multi-column interleave, contact details locked in a header, and skills rendered as
  an image are exactly the failures it cannot observe. Score Dimension 6 as inference and
  say so, or ask her to describe the file.
- **The projection is self-graded.** "74 → 87" is this skill's estimate of its own edits.
  Re-scoring after applying them proves nothing.
- **It only sees the resume.** LinkedIn, GitHub, the portfolio, the cover letter, and
  whether a human inside will vouch for her are all outside the frame, and any one of
  them can outweigh every point on this rubric.

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
VERDICT   Makes the pile (74/100, uncalibrated). Three fixes puts it top.
KNOCKOUTS Pass (onsite SF ✓ · work auth ✓ · 5+ yrs ✓)
REQ       Posted 9 days ago, not reposted — live.

SCORE     Title & seniority    16/20
          Must-have coverage   17/25   ← weakest
          Evidence & impact    18/20
          Vocabulary           10/15
          Recency              8/10
          Parse & skim         5/10

SEES      Top-third skim: "Senior PM at Walmart, ML/BuyBox, 400M daily views."
          Covers 2 of 5 must-haves. Missing: platform/API ownership, 0→1.

FIX 1  (+6, must-haves · surface)  Kindle x Schlacter sits on page 2 as a side
       project; it is your strongest current evidence of a shipped autonomous
       agent. Move it into the top third.
       before: "Kindle x Schlacter — side project, ebook automation"
       after:  "Kindle x Schlacter (kindle.schlacter.me) — built and shipped an
                autonomous delivery agent for ebooks and audiobooks: request a
                title, it arrives on the device. Runs unattended, with
                cross-source fallback across three providers."
FIX 2  (+4, vocabulary · reframe)  ...
FIX 3  (+3, parse · surface)  ...

PROJECTED  74 → 87
GAPS       No B2B SaaS experience (survivable — 1 of 9 "preferred" bullets).
```

Adapt the shape to the case; keep the order: verdict → knockouts → req health → score
→ what it sees → ranked fixes → projected → gaps. Close any run that leans on the number
with the one-line caveat: the rubric is uncalibrated and ranks fixes, it does not predict
callbacks.
