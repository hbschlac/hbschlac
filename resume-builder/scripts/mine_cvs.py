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
  Do NOT gzip+base64 it through the conversation (see RUNBOOK). Write the file under /mnt/files/,
  call the workbench's upload_local_file(path) and curl -sSL the backend.composio.dev/api/v3/sl/
  link it returns; check the full-file sha256 against the workbench's. Worked 2026-09-29 and
  2026-09-30 (bullets.tsv and both sidecars, every hash matched first try). If that download is
  ever refused, fall back to printing changed rows in hash-checked batches of 50 (RUNBOOK). Then
  run enrich.py and build_page_data.py.
"""
import hashlib, re, subprocess
from concurrent.futures import ThreadPoolExecutor

SINCE = "2026-09-30T04:53:00Z"   # the last incremental run (2026-09-30); move this forward after each run
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


def fetch_cvs(run_composio_tool, since=SINCE):
    """Every Doc named *CVResume* created after `since` (all of them when since is None)."""
    docs, tok = [], None
    while True:
        args = {"query": "name contains 'CVResume'", "max_results": 100, "order_by": "createdTime asc"}
        if since:
            args["created_after"] = since
        if tok:
            args["page_token"] = tok
        res, err = run_composio_tool(tool_slug="GOOGLEDOCS_SEARCH_DOCUMENTS", arguments=args)
        if err:
            raise RuntimeError(err)
        docs += res["data"]["files"]
        tok = res["data"].get("next_page_token")
        if not tok:
            break
    docs = [d for d in docs if not d["name"].startswith("BACKUP")]

    def get(d):
        r, e = run_composio_tool(tool_slug="GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT",
                                 arguments={"document_id": d["id"]})
        if e:
            raise RuntimeError(f"{d['name']}: {e}")
        return {"id": d["id"], "name": d["name"], "modified": d["modifiedTime"],
                "text": r["data"]["plain_text"]}

    with ThreadPoolExecutor(12) as ex:
        return list(ex.map(get, docs))


def bullets_of(text):
    """Yield each (experienceId, normalised bullet text) in one CV, once per CV."""
    cur, in_cv = None, set()
    for ln in text.split("\n"):
        s = ln.strip()
        if not s:
            continue
        if s.startswith("●"):
            k = (cur, norm(s.lstrip("●").strip()))
            if k[1] and cur is not None and k not in in_cv:
                in_cv.add(k)
                yield k
        elif "|" in s or "\t" in s:
            first = re.split(r"\s*\|\s*", s)[0]
            if not first.lower().startswith(NOT_HEADERS):
                cur = exp_of(first)


def dedupe(cvs):
    """Oldest first; two docs with the same name AND identical text count once."""
    seen, uniq = set(), []
    for c in sorted(cvs, key=lambda c: c["modified"]):
        key = (c["name"], hashlib.sha1(c["text"].encode()).hexdigest())
        if key not in seen:
            seen.add(key); uniq.append(c)
    return uniq


def merge(orig_txt, cvs):
    rows = [l.split("\t") for l in orig_txt.split("\n") if l.strip()]
    idx = {}
    for i, r in enumerate(rows):
        idx.setdefault((r[0], norm(r[4])), i)
    uniq = dedupe(cvs)
    new = {}
    for c in uniq:
        src = c["name"].split("_CVResume")[0].replace("-", " ")[:34]
        day = c["modified"][:10]
        for k in bullets_of(c["text"]):
            row = rows[idx[k]] if k in idx else new.get(k)
            if row is None:
                new[k] = [k[0], "1", day, src, k[1]]
            else:
                row[1] = str(int(row[1]) + 1)
                if day >= row[2]:
                    row[2], row[3] = day, src
    return rows, list(new.values())


# --- workbench cell ---------------------------------------------------------------------
# orig_txt = subprocess.run(["curl", "-sSL", "-A", "Mozilla/5.0", RAW], capture_output=True, text=True).stdout
# rows, newrows = merge(orig_txt, fetch_cvs(run_composio_tool))
# full = "\n".join("\t".join(r) for r in rows + newrows) + "\n"
# print(len(newrows), hashlib.sha256(full.encode()).hexdigest())


# --- who used each bullet: data/cv_index.tsv + data/bullet_uses.tsv (Hannah, 2026-09-30) -----
# bullets.tsv keeps one source and one date per bullet, and enrich.py rejects any row that is not
# exactly 5 columns, so the history lives beside it:
#   cv_index.tsv    cid <TAB> date <TAB> company <TAB> role <TAB> doc name     (one row per CV)
#   bullet_uses.tsv bid <TAB> cid,cid,...   (oldest use first)   bid = bullet_id(exp, text)
# bench_map.py (career-skills) reads both to show company / role / category / date per pick and
# to rank recent bullets above old ones. The category (PM, FDE, CoS, Ops) is derived there from
# company + role, so the rule lives in one place.

def bullet_id(exp, text):
    return hashlib.sha1(f"{exp}\t{norm(text)}".encode()).hexdigest()[:10]


def parse_name(name):
    """Company and role from her doc titles, in every form they have taken:
    'Uber-SrPM-AppliedAI-v2_CVResume-Hannah Schlacter' -> ('Uber', 'SrPM AppliedAI')
    'Kaizen_ChiefOfStaff_CVResume-Hannah Schlacter'   -> ('Kaizen', 'ChiefOfStaff')
    'CVResume-Hannah Schlacter_Walmart Ads'           -> ('Walmart Ads', '')   (Feb 2026 form)
    'Spark Driver Platform-CVResume-Hannah Schlacter' -> ('Spark Driver Platform', '')"""
    n = re.sub(r"^(Copy of |BACKUP )+", "", name).strip()
    m = re.match(r"CVResume-Hannah Schlacter_(.+)$", n)
    if m:
        return m.group(1).strip(), ""
    base = re.split(r"[-_]CVResume", n)[0]
    base = re.sub(r"[-_ ]v\d+$", "", base)
    company, _, role = re.sub(r"_", "-", base, count=1).partition("-")
    return company.strip(), role.replace("-", " ").replace("_", " ").strip()


B36 = "0123456789abcdefghijklmnopqrstuvwxyz"


def cid_of(n):
    return B36[n // 1296 % 36] + B36[n // 36 % 36] + B36[n % 36]


def index_uses(cvs, cv_index="", uses=""):
    """Add these CVs to the index and their bullets to the uses. Pass the committed sidecars'
    text to extend them (incremental run); pass nothing to rebuild from the CVs given (full
    re-mine). A CV already in the index (same doc name and date) is skipped."""
    idx = [l.split("\t") for l in cv_index.split("\n") if l.strip()]
    known = {(r[4], r[1]) for r in idx}
    used = {}
    for l in uses.split("\n"):
        if l.strip():
            b, _, cs = l.partition("\t")
            used[b] = cs.split(",")
    for c in dedupe(cvs):
        day = c["modified"][:10]
        if (c["name"], day) in known:
            continue
        known.add((c["name"], day))
        cid = cid_of(len(idx))
        idx.append([cid, day, *parse_name(c["name"]), c["name"]])
        for exp, text in bullets_of(c["text"]):
            used.setdefault(bullet_id(exp, text), []).append(cid)
    return ("\n".join("\t".join(r) for r in idx) + "\n",
            "".join(f"{b}\t{','.join(cs)}\n" for b, cs in sorted(used.items())))


# --- workbench cell: full re-mine of every CV's uses (one time, 2026-09-30) -------------------
# cvs = fetch_cvs(run_composio_tool, since=None)
# cv_index, uses = index_uses(cvs)
# write both under /mnt/files/bullet-bench/, print their sha256 and row counts, then hand them to
# the session with upload_local_file (a download link, not the conversation).
# Incremental runs: after merge(), also run index_uses(new_cvs, cv_index=<committed cv_index.tsv>,
# uses=<committed bullet_uses.tsv>) on the same CVs and ship all three files together, so the
# sidecars never fall behind bullets.tsv.
