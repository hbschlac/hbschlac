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

**5 — Apply one swap per call.**
```
GOOGLEDOCS_REPLACE_ALL_TEXT
  document_id:<new id>  find_text:<exact>  replace_text:<new>  match_case:true
```
**`match_case` defaults to `false`** — always pass `true` explicitly.

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

**8 — Page fit.** Count non-blank lines; 52–56 ≈ one page. Say plainly that this is a proxy —
no API confirms page count — and ask her to eyeball it before sending.

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
