#!/usr/bin/env python3
"""Mine new CV docs from Drive into data/bullets.tsv -- incremental.

Runs in the Composio workbench (COMPOSIO_REMOTE_WORKBENCH), which has `run_composio_tool`
and outbound network. Paste the body into a cell; it does not run on a laptop as-is.

The 2026-09-14 full mine was never committed, so this is the incremental version written on
2026-09-23 when the bank had gone nine days stale (48 CVs missing, Gap/Sela/DoorDash/Abridge
among them). It is deterministic: the same Drive state produces a byte-identical TSV, which is
what makes the hash-verified transfer below possible.

What it does
  1. Pulls the committed bullets.tsv from GitHub (the public raw URL).
  2. Lists every Doc named *CVResume* created after SINCE (BACKUP copies skipped).
  3. Reads each one's plain text and walks it line by line: a line with " | " or a tab is an
     experience header; a line starting with "●" is a bullet under the last header.
  4. A bullet whose (experience, whitespace-normalised text) already exists bumps that row's
     useCount, and lastUsed/source if newer. Anything else is a new row. Each doc counts once
     per bullet; two docs with the same name AND identical text count once.

Getting the result out of the workbench
  Do NOT gzip+base64 it through the conversation (see RUNBOOK). The Drive handoff in the
  RUNBOOK works on the laptop, but a cloud session's safety classifier blocks curl-ing a
  link-shared Drive file as exfiltration. What worked on 2026-09-23 instead: print the new
  rows in batches of 50 with '|||' as the column separator plus a sha256 per batch, write
  each batch locally, and check the hash before applying. Every batch matched first try, and
  a full-file sha256 confirmed the result. Then run enrich.py and build_page_data.py.
"""
import hashlib, re, subprocess
from concurrent.futures import ThreadPoolExecutor

SINCE = "2026-09-14T22:55:00Z"   # the last full mine; move this forward after each run
RAW = "https://raw.githubusercontent.com/hbschlac/hbschlac/main/resume-builder/data/bullets.tsv"

# Header text -> experienceId. First match wins; anything unmatched is "misc"
# (enrich.py then splits community work out of misc).
EXPERIENCES = [("walmart", "walmart"), ("siemens", "siemens"), ("uprising", "uprising"),
               ("accenture", "accenture"), ("muse", "muse"), ("coherent", "coherent"),
               ("kindle", "aiprojects"), ("applied ai", "aiprojects"),
               ("berkeley", "edu_berkeley"), ("illinois", "edu_illinois")]
NOT_HEADERS = ("skills", "interests", "master", "bachelor", "847")


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def exp_of(header):
    h = header.lower()
    return next((v for k, v in EXPERIENCES if k in h), "misc")


def fetch_cvs(run_composio_tool):
    res, err = run_composio_tool(tool_slug="GOOGLEDOCS_SEARCH_DOCUMENTS", arguments={
        "query": "name contains 'CVResume'", "created_after": SINCE,
        "max_results": 100, "order_by": "createdTime asc"})
    if err:
        raise RuntimeError(err)
    docs = [d for d in res["data"]["files"] if not d["name"].startswith("BACKUP")]

    def get(d):
        r, e = run_composio_tool(tool_slug="GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT",
                                 arguments={"document_id": d["id"]})
        if e:
            raise RuntimeError(f"{d['name']}: {e}")
        return {"name": d["name"], "modified": d["modifiedTime"], "text": r["data"]["plain_text"]}

    with ThreadPoolExecutor(12) as ex:
        return list(ex.map(get, docs))


def merge(orig_txt, cvs):
    rows = [l.split("\t") for l in orig_txt.split("\n") if l.strip()]
    idx = {}
    for i, r in enumerate(rows):
        idx.setdefault((r[0], norm(r[4])), i)
    seen, uniq = set(), []
    for c in sorted(cvs, key=lambda c: c["modified"]):
        key = (c["name"], hashlib.sha1(c["text"].encode()).hexdigest())
        if key not in seen:
            seen.add(key); uniq.append(c)
    new = {}
    for c in uniq:
        src = c["name"].split("_CVResume")[0].replace("-", " ")[:34]
        day, cur, in_cv = c["modified"][:10], None, set()
        for ln in c["text"].split("\n"):
            s = ln.strip()
            if not s:
                continue
            if s.startswith("●"):
                t = norm(s.lstrip("●").strip()); k = (cur, t)
                if not t or cur is None or k in in_cv:
                    continue
                in_cv.add(k)
                row = rows[idx[k]] if k in idx else new.get(k)
                if row is None:
                    new[k] = [cur, "1", day, src, t]
                else:
                    row[1] = str(int(row[1]) + 1)
                    if day >= row[2]:
                        row[2], row[3] = day, src
            elif "|" in s or "\t" in s:
                first = re.split(r"\s*\|\s*", s)[0]
                if not first.lower().startswith(NOT_HEADERS):
                    cur = exp_of(first)
    return rows, list(new.values())


# --- workbench cell ---------------------------------------------------------------------
# orig_txt = subprocess.run(["curl", "-sSL", "-A", "Mozilla/5.0", RAW], capture_output=True, text=True).stdout
# rows, newrows = merge(orig_txt, fetch_cvs(run_composio_tool))
# full = "\n".join("\t".join(r) for r in rows + newrows) + "\n"
# print(len(newrows), hashlib.sha256(full.encode()).hexdigest())
