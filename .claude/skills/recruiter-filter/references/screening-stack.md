# What the screening stack actually does

Loaded when the per-vendor behavior matters — a specific ATS in the URL, a claim about
auto-rejection, or a question about why an application went silent.

## The headline finding

**Content-based auto-rejection is rare.** In a 2026 Enhancv survey of 25 US recruiters,
only 8% had configured any content-based auto-rejection; 92% said their ATS does not
auto-reject on formatting, content, or design. What the systems actually do is **rank**,
and ranking decides which ~20 profiles a human opens. Optimize for rank and for the
human skim, not for an imaginary reject bot.

## Per-vendor

### Ashby
- AI-Assisted Application Review evaluates applicants against **criteria the recruiter
  defines**, not a generic resume score.
- **Emits no numerical ranking.** It tags fit levels and provides **citations** linking
  to the specific evidence in the profile.
- Consequence for the candidate: a requirement with no *citable line* is uncovered even
  if the experience is real. Evidence must be a sentence a tool can point at.
- Also ships AI screening and AI rediscovery (old applications resurfaced for new reqs —
  so a strong CV keeps paying out after the first rejection).
- Recruiters are told to double-check the criteria filter before trusting it. A human
  reads the shortlist.

### Greenhouse
- Parses the resume into structured fields, stores the candidate, and lets recruiters
  **search and rate**. Recruiter boolean search over titles and skills is a bigger real
  filter here than any AI feature.
- **Knockout questions** on the application form are the genuine auto-reject surface:
  yes/no items for work authorization, certifications, location, sometimes years.
- The 2026 AI screening module scores and ranks to surface strong candidates at the top.
  It **removes no one** — a recruiter makes every advance/reject call.

### Workday (HiredScore)
- HiredScore grades candidates **A / B / C / D**, where A is the closest match, against
  the req's stated requirements.
- Ranks on job relevance plus historical success signals, to prioritize review order.
- Workday's own Responsible AI position is that the grade prioritizes; the human decides.
- Workday applications also carry the longest, most gate-heavy forms — most Workday
  losses are Layer 1 (form answers), not Layer 2.

### Lever
- Posting API exposes clean role text; matching and search behave like Greenhouse.
  Same advice: titles, knockouts, evidence.

### Layered on top (any ATS)
Eightfold, SeekOut, Paradox, HireVue, and standalone scorers like Skima are often bolted
on for verified scoring with reasoning. They raise the weight of explicit, evidenced,
recent skill statements. None of them changes the three-layer model.

## Myths to refuse

**"75% of resumes are rejected by ATS before a human sees them."** Traced to a 2012
marketing claim by Preptel, a resume-software vendor that shut down in 2013 without ever
publishing a study, sample size, or methodology. Repeating it points the fix effort at
the wrong layer.

**White text / hidden keywords.** Modern parsers read the underlying text regardless of
color, so the terms do get counted — and they are equally visible to any recruiter who
selects the text, pastes it into email, or prints it. Enterprise teams treat hidden-text
stuffing as a trust flag and reject on sight. Never suggest it.

**Keyword stuffing generally.** Parsing is context-based, not raw keyword counts.
Recruiters see keyword walls instantly, and many systems display the original document
right beside the parsed profile. Stuffed terms with no supporting evidence collapse at
the first screening call.

**"PDFs don't parse."** Text-layer PDFs parse fine. Scanned/image PDFs and text living
inside graphics or headers do not. That is a parse-safety issue, not a format issue.

## Regulatory tells (US/EU, current as of 2026)

Worth knowing because disclosure language in a posting tells you a scoring tool is live:

- **NYC Local Law 144** — automated employment decision tools used for NYC roles require
  an annual bias audit and candidate notice. A posting carrying an AEDT notice is telling
  you a scoring tool is in the loop.
- **Colorado SB 24-205** — duties around high-risk AI systems including employment.
- **EU AI Act** — employment screening is classified high-risk, with transparency duties.

None of this creates a right to a better score. It does mean an explicit AEDT notice is a
signal to weight Dimensions 2 and 4 harder for that application.

## Sources

- [Ashby's AI Recruiting Features: A Complete Guide for 2026](https://www.heymilo.ai/blog/automate-ai-candidate-screening-and-engagement-in-ashby)
- [Ashby Review 2026 — Skima](https://skima.ai/blog/product-deep-dives/ashby-reviews)
- [AI Screened integration — Greenhouse Support](https://support.greenhouse.io/hc/en-us/articles/29122364864539-AI-Screened-integration)
- [Greenhouse Job Application: fields, knockout questions (2026)](https://notchresume.com/resources/greenhouse-job-application.html)
- [HiredScore AI for Recruiting — Workday](https://www.workday.com/en-us/products/talent-management/ai-recruiting.html)
- [Workday & HiredScore on Compliance and Bias Mitigation](https://www.workday.com/en-us/legal/responsible-ai-and-bias-mitigation.html)
- [10 ATS Resume Myths, Debunked (2026)](https://atsverification.com/blog/ats-resume-myths-debunked/)
- [The "75% ATS Rejection" Stat Is Fake — Real 2026 Resume Data](https://mytoolshub.co.in/blog/ats-resume-rejection-myth)
- [White Text & Hidden Keywords: the myth that gets you blacklisted (2026)](https://airesume.guru/blog/hidden-keywords-white-text-on-resumes-the-myth-that-gets-you-blacklisted)
- [How Applicant Tracking Systems Actually Work in 2026 — Huntr](https://huntr.co/blog/how-applicant-tracking-systems-work)

Vendor features move. If a claim here drives a consequential call, re-verify it.
