---
name: linkedin-networking
description: >
  Compliant helper for finding people and companies to reach out to — especially
  companies to research and Haas / MBA alumni to contact. Sources companies from
  off-LinkedIn data, builds Sales Navigator + Alumni-tool searches for the user to
  run manually, drafts outreach (via the product-networking skill), and tracks
  contacts in a private Google Sheet. NEVER scrapes, reads, or automates LinkedIn,
  and NEVER sends messages or connection requests. Activates on a linkedin.com URL
  or networking intent ("which Haas alumni should I contact at X", "who should I
  reach out to", "companies to look into").
---

# linkedin-networking

Find the right companies and the right alumni to contact, draft the outreach, track it —
without ever touching LinkedIn programmatically. You do the two things LinkedIn requires a
human for (viewing results, hitting send); this skill does everything around them.

**Not for:** scraping, automated reading/export of profiles or search results, third-party
LinkedIn data resellers (Evaboot / PhantomBuster / Apollo / Proxycurl-style), or
sending/automating any message or connection request. If asked for any of those, refuse and
route back to the manual Sales Navigator step below.

## Why this shape (read once)

LinkedIn's User Agreement §8.2 bans bots/scrapers/automation from **reading or copying**
profile data — not just messaging. There is no official people/alumni-search API for
individuals, and the sanctioned "smart search" surface is **Sales Navigator, used manually**.
So the compliant tool never reads LinkedIn: its value is sourcing, search-building, drafting,
and tracking. Everything below stays on the right side of that line.

## The 5-step loop

### Step 1 — Intake the target

Get a concrete target from the user, e.g. *"Senior PM roles, Series B–D fintech, SF Bay Area."*
If vague, ask 1–2 sharpening questions (function, seniority, stage/size, geography, themes she
cares about). Don't proceed on a fuzzy target — the whole shortlist quality depends on it.

### Step 2 — Source companies (off-LinkedIn only)

Research matching companies from sources that are **not LinkedIn**, via `WebSearch` /
`WebFetch`: Crunchbase, company career/leadership pages, funding news, and job boards. Return a
**ranked shortlist** (~8–15) with, per company: name, one-line what-they-do, stage/size, why
it fits the target, and 1–2 open-role or signal links. Prefer verifiable specifics over
adjectives.

> Egress note: on Claude Code web the sandbox proxy is a strict allowlist — some non-LinkedIn
> hosts may 403. If a needed research host is blocked, use the Composio remote-exec MCP fallback
> exactly as the `job-fetch` skill does (`mcp__Composio_Docs_Drive__COMPOSIO_REMOTE_BASH_TOOL`,
> load via ToolSearch). Do **not** use it to reach LinkedIn — LinkedIn is out of scope by design.

### Step 3 — Build the alumni angle (search recipes, not fetches)

For each shortlisted company, help the user find **Haas / MBA (and broader Berkeley) alumni**
who work there. You never fetch these — you hand her searches to run manually.

**A. Sales Navigator (her primary surface).** Give the exact filters to set in a Sales Nav
*people* search — this is reliable; deep-link URLs are brittle, so lead with the recipe:
- **Current company** = `<company>`
- **School** = `UC Berkeley, Haas School of Business` (add `University of California, Berkeley`
  to widen beyond the MBA program)
- **Geography / Function / Seniority** = inherit from the Step 1 target
- Optional keyword: `MBA` in the keyword box to bias toward MBA alumni
As a convenience you may also provide a starter link she can refine:
`https://www.linkedin.com/sales/search/people` (she applies the filters above). **Do not fetch it.**

**B. Free LinkedIn Alumni tool (no Sales Nav needed).** The school "people" page lets her filter
alumni by *Where they work* and *What they do* — fully manual, fully compliant. Point her to the
Berkeley/Haas school page's **People** tab, e.g.:
- Haas: `https://www.linkedin.com/school/uc-berkeley-haas-school-of-business/people/`
- Berkeley (all): `https://www.linkedin.com/school/university-of-california-berkeley/people/`
(Confirm the exact school slug on her account; these are the canonical ones.) **Do not fetch these.**

**C. Official alumni directory (off LinkedIn).** The **UC Berkeley / @cal / Haas alumni
directory** exists specifically for alumni-to-alumni contact — a compliant complement to
LinkedIn. Suggest it for warm, in-network intros, and (if useful) note the Haas alumni
association / class channels.

Output for this step: per company, the filter recipe + the two manual links + a note on which
2–3 people-profiles to prioritize *once she's looking at them* (e.g. "same function, 1–2 levels
up, recent joiner = good warm ask").

### Step 4 — Draft outreach (voice delegated)

When the user picks a person, draft a **connection note** (≤300 chars) and a **first message**,
personalized to that person + company + her angle. Delegate voice/content to the external
**product-networking** skill rather than duplicating it:
- `add_repo hbschlac/product-networking-skills` first. **Redirect gotcha:** if that returns "not
  accessible," retry `add_repo hbschlac/career-skills` (old name, still resolves the grant).
- Entry: `skills/product-networking/SKILL.md`. Pass it the person/company/angle context.
Output the drafts for her to **copy and send manually**. Never send anything.

### Step 5 — Track (private Google Sheet, never the repo)

Log each contact so follow-ups don't slip. Write to a **private Google Sheet** via the connected
Google Drive MCP (find tools via ToolSearch: `google drive sheet`). Columns: `Name`, `Company`,
`Role`, `School/angle`, `Source` (Sales Nav / Alumni tool / directory), `Status`
(researched / requested / connected / messaged / replied), `Last touch`, `Next follow-up`,
`Notes`. Reuse an existing tracker sheet if she has one; else create one in her Drive.

**Never** write contact names or personal data into this (public) repo — no committed CSVs,
no notes files. Tracking lives in her private Drive only.

## Compliance guardrails (hard no's)

- No code or tool call that logs into, fetches, scrapes, or reads LinkedIn — profiles, search
  results, the Alumni tool, or Sales Navigator. You build searches; she runs them.
- No third-party LinkedIn exporters / data APIs (Evaboot, PhantomBuster, Apollo, Proxycurl, etc.).
- No sending or automating messages or connection requests, and no bulk actions.
- No committing personal contact data to this repo.
If a request needs any of the above, say so plainly and offer the manual-equivalent step instead.

## Install it everywhere (desktop + web)

Ships as a **plugin** (`linkedin-networking`) from the `hbschlac/hbschlac` marketplace, so the
skill and its auto-trigger hook travel together.

- **Desktop (global, persists):** `/plugin marketplace add hbschlac/hbschlac` then
  `/plugin install linkedin-networking`.
- **Web (per repo):** enable it in the repo's committed `.claude/settings.json`:

  ```json
  {
    "extraKnownMarketplaces": {
      "hbschlac": { "source": { "source": "github", "repo": "hbschlac/hbschlac" } }
    },
    "enabledPlugins": { "linkedin-networking@hbschlac": true }
  }
  ```

  (`hbschlac/hbschlac` itself enables it from its local clone — no fetch needed.)
