# Bullet Bench — runbook

What Claude does when Hannah says one of the trigger phrases. Works from **any** session,
including phone, because every step is a Composio MCP call on her account — nothing here
depends on her Mac.

> **Why Composio and not the google-workspace MCP.** `resume-subskill.md` bans Composio
> `GOOGLEDOCS_*` for CV editing. That ban exists because *whole-doc / markdown imports* rewrite
> the document and destroy native formatting — "the #1 cause of wrong-format resumes."
> `GOOGLEDOCS_REPLACE_ALL_TEXT` is not that. It is the same `replaceAllText` batchUpdate call the
> sanctioned `find_and_replace_doc` makes and that `docs_writer.py:124` already uses; it never
> touches document structure.
>
> **Proven 2026-09-14**, not assumed: copied `General Role_CVResume`, applied 3 swaps hitting a
> bulleted list item, the header tagline and an *italic* descriptor, then diffed the result against
> the untouched original across all 35 paragraphs — `documentStyle` identical, `namedStyles`
> identical, paragraph count 35→35, **0 paragraphStyle / 0 bullet / 0 runStyle diffs**, italic
> scope `[6,7,9,12,17,18,21,26,30]` unchanged. The italic descriptor was itself one of the edits
> and kept its italics.
>
> The narrowed rule: **no whole-doc or markdown import, whatever the provider.** Still banned —
> `import_to_google_doc`, `create_file` from HTML/markdown, and `GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT`
> used as a full rewrite.

---

## Step 0 — Before you write a single bullet (BLOCKING)

The 2026-09-15 Anthropic CV took **3h08m of working time and 127 doc edits** for nine bullets.
Roughly **14 of Hannah's 46 messages were facts Claude did not have**, each arriving *after* a
bullet had been written, scored, exported and reviewed. One Walmart bullet went through
**15 distinct versions**. That is a sequencing failure, not a writing failure.

**1 — Read the evidence ledger.** It holds every fact Hannah has stated, tagged by the JD
dimension it answers, with provenance and hedges. It lives in the **private** skills repo, not
here — this repo is public, and the ledger records what she deliberately kept *off* her CV:

> `hbschlac/career-skills` → `skills/product-networking/references/evidence.md` (**private repo — run `add_repo` first**; if `product-networking-skills` 404s, retry as `career-skills`)

**2 — Parse the JD into its requirement list**, then grep the ledger by tag for each one. What you
find is evidence you already have. **Never ask a question the ledger already answers**, and never
declare a gap unfixable before grepping it — "the IT/Security gap is unfixable without fabricating"
was wrong and cost five points.

**3 — Batch every remaining gap into ONE message.** Not one question per turn. The session that
motivated this file asked them serially across four hours.

**4 — Append her answers to the ledger in the same turn**, before writing the bullet. Not at the
end of the session: sessions run out of context, and that one did, at 19:37.

**5 — Keep her nouns.** When she supplies a fact in her own words, the bullet keeps her noun. She
said *dashboard*; Claude wrote *"planning tool"*; twenty minutes later she reported the content as
missing from the page. It was there, under a synonym. **If the author can't spot it, a reader won't.**

---

## "Apply the pending resume build"

**1 — Read the queued build.**
```
Artifact action:"read_db"  url:<bench url>  db_op:"get"
  collection:"builds"  doc_id:"pending"
```
Gives `baseDoc`, `baseName`, `tagline`, `skills`, `bullets[]`, `company`, `blocking`.
If `blocking > 0`, say so before touching anything and let her decide.

**2 — Copy the base.** Never edit a CV she has called final; always work on a fresh copy.
```
GOOGLEDOCS_COPY_DOCUMENT  document_id:<baseDoc>  title:"<Company>_CVResume-Hannah Schlacter"
```

**3 — Read the copy back.** This is where exact `find_text` values come from. Never guess them.
```
GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT  document_id:<new id>
```

**4 — Check uniqueness before every swap.** `REPLACE_ALL_TEXT` replaces *all* occurrences. Count
each `find_text` in the plaintext first; if it appears more than once, lengthen it until it is
unique. (Verified: `" | "` occurs 21× in a real CV — a short string silently changes 21 places.)

**5 — Draft in plaintext first, then apply the whole round in one batch.**

Do **not** iterate against the live Doc. Every wording change against the Doc costs an edit, a PDF
export and a review round-trip; 127 such edits is what three hours looks like. Instead write the
full proposed set to a scratch `.txt`, settle the wording there where a rewrite is free, and only
then push the round.

`COMPOSIO_MULTI_EXECUTE_TOOL` takes an **array** — send the round as one call:
```
COMPOSIO_MULTI_EXECUTE_TOOL  tools:[
  {tool_slug:"GOOGLEDOCS_REPLACE_ALL_TEXT", arguments:{document_id:<id>, find_text:<exact>,
                                                        replace_text:<new>, match_case:true}},
  ... one entry per swap in this round ...
]
```
**`match_case` defaults to `false`** — always pass `true` explicitly, on every entry.

**6 — Structural edits, if a bullet must be removed entirely.**
Blanking a bullet with `replace_text:""` leaves an orphan `●`. Delete the *paragraph*:
```
GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT  document_id:<id>
  edit_docs:[{"deleteContentRange":{"range":{"startIndex":N,"endIndex":M}}}]
```
Get indices from `GOOGLEDOCS_GET_DOCUMENT_BY_ID`. The range must **not** include the segment's
trailing newline — if the segment ends at N, use `endIndex: N-1`.

**7 — Verify.** Read the doc back and report every replacement that changed **0** occurrences
(find text was wrong) or **more than 1** (was not unique). Do not report success without this.

**8 — Page fit — measure it, don't estimate it and don't outsource it to her.**

Export to a **file path** and run [`scripts/linefit.py`](scripts/linefit.py):
```
curl -sSL "https://docs.google.com/document/d/<DOC_ID>/export?format=pdf" -o /tmp/cv.pdf
python3 scripts/linefit.py /tmp/cv.pdf --over 2     # exit 1 if any bullet wraps past 2 lines
```
It decodes the exported PDF's glyph positions and reports the true line count per paragraph plus
the page count. Exit code 1 means over one page or an over-long bullet, so it gates a send.

- **Never export the PDF into the conversation.** The 2026-09-15 session ran 27 exports through the
  Drive MCP tool and *all 27 blew the token limit* — that is what exhausted the context window.
- **Character count is a bad proxy.** The cap was guessed at ~224 for most of that session; measured
  against the shipped CV, a **236-char bullet still fits two lines**. Proportional fonts don't care
  about character counts.
- Hannah reported "siemens bullet is 3 lines in doc" because nothing else was checking. This checks.

**9 — Tracker.** Update the row in [Job Search Tracker 2026](https://docs.google.com/spreadsheets/d/18Eyec7GlbuYUELhPMxIN9zRgcOjnlTd31y4O6kY929w/edit):
status → `CV drafted` (col C), doc link (col F), angle summary (col H).

---

## "Publish the queued resume link"

**1 — Read the queued slug.**
```
Artifact action:"read_db"  url:<bench url>  db_op:"list"  collection:"slugs"
```

**2 — Refuse to repoint `/resume`.** That link is already out in outreach as the general CV.
A company-tailored CV always gets its own slug.

**3 — Make the Doc readable.**
```
GOOGLEDRIVE_CREATE_PERMISSION  file_id:<doc id>  type:"anyone"  role:"reader"
```
Then verify with `GOOGLEDRIVE_LIST_PERMISSIONS` — want `{"role":"reader","type":"anyone"}`.
Without this, every click lands on a request-access screen.

**4 — PR the redirect** on `hbschlac/hannah-portfolio`, into `next.config.ts` → `async redirects()`:
```ts
{ source: "/resume-<company>-<role>",
  destination: "https://docs.google.com/document/d/<DOC_ID>/preview",
  permanent: false }
```
- **`/preview`, not `/edit`** — read-only, no Docs editor chrome, and it keeps the real resume
  layout. The legacy `schlacter.me/[slug]` renderer flattens the doc into web text; don't use it.
- **`permanent: false` (307), never 308.** A 308 is cached hard by every browser that already
  followed it, so repointing the slug later silently fails for exactly the people who clicked.
- Config redirects run before routing, so `/resume-*` wins over `app/[slug]`.
- Web sessions can't push to `hannah-portfolio` — branch → PR → merge with the GitHub MCP tools.

**5 — Confirm the deploy.** Merging main triggers production on the **`schlacter-me`** Vercel
project (`prj_qdU1qdFu2IiBxGwFJ2524sONk34C`, team `team_Buhju9iWfQMntrbqt8HTEMBu`). Want
`state: READY` with `schlacter.me` in `.alias`. The orphaned Vercel project named
`hannah-portfolio` is **not** the live site.

**6 — Hand the last check to her.** The sandbox egress proxy blocks `schlacter.me`, so Claude can
confirm the deploy but cannot fetch the URL. Ask her to open it in a private window.

---

## "Fetch this JD" (a job posting URL)

The published page's own network is blocked and `sample` cannot browse, so **the page can never
fetch a URL itself**. Every URL path runs through a session:

1. `job-fetch` resolves the URL to the ATS public API (Ashby / Greenhouse / Lever / Gem) and
   fetches it via `COMPOSIO_REMOTE_BASH_TOOL`, which runs outside the sandbox egress block.
   Send a real User-Agent — `api.ashbyhq.com` 403s a bare Python UA but returns 200 to curl.
2. Extract themes, must-haves and load-bearing vocabulary.
3. Write it into the bench so the page picks it up:
```
Artifact action:"write_db"  url:<bench url>  db_op:"set"
  collection:"jd"  doc_id:"current"
  data:{company, role, text, requirements:[{label, keywords[], mustHave}], themes[], knockouts[]}
```

This works from her phone because the *session* does the fetching, not the device.

---

## Re-mining the archive

`scripts/mine_cvs.py` documents the pipeline; it runs in the Composio workbench
(`COMPOSIO_REMOTE_WORKBENCH`), which has `run_composio_tool` and outbound network. Then:

```
python3 scripts/enrich.py            # bullets.tsv -> bullets.json
python3 scripts/build_page_data.py   # bullets.json -> app/data.js
```

**Transferring the bank out of the workbench:** do **not** gzip+base64 it through the
conversation — a single mistyped character silently corrupts the whole archive (this happened;
correct length, valid charset, wrong hash). Instead write it to Drive and pull it down directly:

```
GOOGLEDRIVE_CREATE_FILE_FROM_TEXT  file_name:"ZZTEMP-transfer.tsv"  mime_type:"text/plain"
GOOGLEDRIVE_CREATE_PERMISSION      file_id:<id>  type:"anyone"  role:"reader"
curl -sSL "https://drive.google.com/uc?export=download&id=<id>" -o data/bullets.tsv
```
`docs.google.com` and `drive.google.com` are reachable from the sandbox (verified). **Trash the
temp file immediately after** — it is briefly link-readable, and it is her career data.
