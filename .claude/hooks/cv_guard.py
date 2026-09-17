#!/usr/bin/env python3
"""cv_guard.py — enforce the CV-editing wall rules outside the model's memory.

Registered in `.claude/settings.json` as a PreToolUse and a PostToolUse hook. The
rules it enforces already existed in the resume skill on 2026-09-15 and were ignored
in the very session that wrote them, because a rule in a file is only as good as the
model's memory of it — and memory is the first thing a long session loses. A hook
runs whether or not anyone remembers.

What it refuses (PreToolUse, `permissionDecision: deny`, the reason names the rule):
  * any whole-doc / markdown import into an existing doc
    (Composio GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN / _SECTION_MARKDOWN, laptop
    import_to_google_doc) — the #1 cause of wrong-format resumes
  * a find→replace without `match_case: true` (Composio defaults it to false)
  * an empty replace_text (leaves an orphan bullet marker)
  * a find→replace on a doc that has not been read this session, whose last plaintext
    readback is older than CV_GUARD_TTL_MIN minutes (Hannah may have edited it), or
    whose find_text matches 0 or 2+ times in that readback — REPLACE_ALL replaces
    every occurrence, and a 0-match "fixed" by inserting is how her edits get reverted
  * a Drive download_file_content (a PDF pulled into the chat; 27 of these exhausted
    the 2026-09-15 session) — use resume-builder/scripts/cvcheck.sh instead

What it records (PostToolUse):
  * the plaintext of every doc readback, keyed by doc id, so the checks above have
    something to check against; each successful replace is applied to that copy
  * a warning back to the model when a replace changed 0 occurrences, or when a
    Drive read dumped >40k characters into the conversation

Escape hatches (documented in every refusal): `touch ~/.claude/cv-guard/off` disables
the guard; `touch ~/.claude/cv-guard/allow-download` permits one session's downloads.
Every decision is appended to `~/.claude/cv-guard/guard.log` — that file is the proof
the hook fired (a hook cannot be verified in the session that adds it).

Fails open on anything unexpected: an exception exits 0 with no output, so a bug here
can never block Hannah's work. The deterministic checks (input-only) run first.
"""
import json
import os
import pathlib
import re
import sys
import time

GUARD_DIR = pathlib.Path(os.environ.get("CV_GUARD_DIR") or os.path.expanduser("~/.claude/cv-guard"))
TTL_MIN = int(os.environ.get("CV_GUARD_TTL_MIN", "30"))
BIG_READ_CHARS = 40_000

BANNED_COMPOSIO = {
    "GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN",
    "GOOGLEDOCS_UPDATE_DOCUMENT_SECTION_MARKDOWN",
}
WALL = (
    "The wall (career-skills skills/resume/SKILL.md): copy a base doc and edit it with "
    "find→replace only; match_case:true on every replace; find_text must match exactly "
    "once in the LATEST plaintext readback; never a whole-doc or markdown import; never "
    "a PDF into the chat. Escape hatch: `touch ~/.claude/cv-guard/off` and tell Hannah "
    "the guard misfired."
)


# ----------------------------------------------------------------------------- io
def log(msg):
    try:
        GUARD_DIR.mkdir(parents=True, exist_ok=True)
        with (GUARD_DIR / "guard.log").open("a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + msg + "\n")
    except Exception:
        pass


def deny(reason):
    log("DENY " + reason.split("\n")[0][:160])
    json.dump({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason + "\n\n" + WALL,
    }}, sys.stdout)
    sys.exit(0)


def allow(note=None):
    if note:
        log("ALLOW " + note)
    sys.exit(0)


def post_context(msg):
    log("NOTE " + msg.split("\n")[0][:160])
    json.dump({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": msg,
    }}, sys.stdout)
    sys.exit(0)


# ------------------------------------------------------------------------ cache
def doc_id(value):
    s = str(value or "").strip()
    m = re.search(r"/d/([A-Za-z0-9_-]+)", s)
    return m.group(1) if m else s


def cache_path(doc):
    return GUARD_DIR / (re.sub(r"[^A-Za-z0-9_-]", "_", doc)[:120] + ".json")


def load_cache(doc):
    try:
        return json.loads(cache_path(doc).read_text(encoding="utf-8"))
    except Exception:
        return None


def save_cache(doc, text, parsed, ts=None):
    GUARD_DIR.mkdir(parents=True, exist_ok=True)
    cache_path(doc).write_text(json.dumps({
        "doc": doc, "ts": ts if ts is not None else time.time(),
        "parsed": bool(parsed), "text": text or "",
    }), encoding="utf-8")


# ------------------------------------------------------------ response digging
def normalize(obj):
    """Tool responses arrive as a dict, a JSON string, or MCP content blocks."""
    if isinstance(obj, str):
        try:
            return json.loads(obj)
        except Exception:
            return obj
    if isinstance(obj, list) and obj and all(isinstance(b, dict) for b in obj) \
            and any("text" in b for b in obj):
        texts = [b.get("text", "") for b in obj if isinstance(b.get("text"), str)]
        joined = "\n".join(texts)
        try:
            return json.loads(joined)
        except Exception:
            parsed = []
            for t in texts:
                try:
                    parsed.append(json.loads(t))
                except Exception:
                    parsed.append(t)
            return parsed if len(parsed) > 1 else (parsed[0] if parsed else joined)
    return obj


def find_key(obj, keys):
    """First value found under any of `keys`, depth-first."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in keys:
                return v
        for v in obj.values():
            r = find_key(v, keys)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_key(v, keys)
            if r is not None:
                return r
    return None


def strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from strings(v)


def longest_string(obj, min_len):
    best = ""
    for s in strings(obj):
        if len(s) > len(best):
            best = s
    return best if len(best) >= min_len else None


def looks_truncated(text):
    tail = text[-40:].lower()
    return ("truncated" in tail) or tail.endswith("…") or tail.endswith("...") \
        or "sync_response_to_workbench" in text[-400:]


def results_list(resp):
    r = find_key(resp, ("results", "responses", "outputs"))
    return r if isinstance(r, list) else None


# ----------------------------------------------------------------- the checks
def check_replace(doc, find_text, replace_text, match_case, label):
    if match_case is not True:
        deny(f"{label}: match_case must be true (it defaults to false and would match the wrong "
             "case). Re-send with match_case: true.")
    if not find_text:
        deny(f"{label}: find_text is empty.")
    if replace_text == "":
        deny(f"{label}: replace_text is empty — that leaves an orphan bullet marker (●). To remove "
             "a bullet, delete the paragraph with GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT "
             "deleteContentRange (step4-apply.md, API pitfalls).")
    if not doc:
        return
    c = load_cache(doc)
    if c is None:
        deny(f"{label}: no plaintext readback of doc {doc} in this session. Read it first "
             "(GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT with sync_response_to_workbench:false, or "
             "get_doc_content), then retry. The doc is the truth; the conversation is not.")
    if not c.get("parsed"):
        return  # a readback happened but could not be indexed — the deterministic rules still held
    age_min = (time.time() - float(c.get("ts", 0))) / 60
    if age_min > TTL_MIN:
        deny(f"{label}: the last readback of doc {doc} was {int(age_min)} min ago and Hannah may "
             "have edited it since. Re-read the doc, then retry.")
    n = c.get("text", "").count(find_text)
    if n == 0:
        deny(f"{label}: find_text is not in the latest readback of doc {doc}. Either the doc "
             "changed since that readback or the text is inexact. Re-read and copy the plaintext "
             "exactly. Never insert or rewrite the paragraph to compensate — that is how her "
             "edits get reverted. (If you just re-read and this still fails, the readback may be "
             "truncated: re-read with sync_response_to_workbench:false.)")
    if n > 1:
        deny(f"{label}: find_text matches {n} times in doc {doc}; REPLACE_ALL replaces every one. "
             "Use a longer find_text that is unique.")


def pre(name, tool_input):
    if (GUARD_DIR / "off").exists():
        allow()
    if name.endswith("import_to_google_doc"):
        deny("import_to_google_doc rewrites the whole document and destroys native formatting "
             "(fonts, spacing, margins, bullet styles). Copy a base doc and use find_and_replace_doc.")
    if name.endswith("download_file_content"):
        if (GUARD_DIR / "allow-download").exists():
            allow("download permitted by marker")
        deny("Drive download_file_content pulls the whole file (a PDF is 10–25k tokens) into the "
             "conversation. For a CV, run `bash resume-builder/scripts/cvcheck.sh <DOC_ID>` in "
             "hbschlac/hbschlac — it exports the PDF to a file and prints only the line-fit "
             "summary. If you genuinely need the file in the chat: `touch "
             "~/.claude/cv-guard/allow-download` and retry.")
    if name.endswith("COMPOSIO_MULTI_EXECUTE_TOOL"):
        for item in (tool_input.get("tools") or []):
            if not isinstance(item, dict):
                continue
            slug = str(item.get("tool_slug", ""))
            args = item.get("arguments") or {}
            if slug in BANNED_COMPOSIO:
                deny(f"{slug} replaces document content from markdown and destroys native formatting. "
                     "Edit with GOOGLEDOCS_REPLACE_ALL_TEXT (one find→replace per change) on a copy "
                     "of a base doc.")
            if slug == "GOOGLEDOCS_REPLACE_ALL_TEXT":
                check_replace(doc_id(args.get("document_id") or args.get("id")),
                              args.get("find_text"), args.get("replace_text"),
                              args.get("match_case"), slug)
            if slug == "GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT":
                doc = doc_id(args.get("document_id") or args.get("id"))
                for req in (args.get("edit_docs") or []):
                    rat = req.get("replaceAllText") if isinstance(req, dict) else None
                    if rat:
                        ct = rat.get("containsText") or {}
                        check_replace(doc, ct.get("text"), rat.get("replaceText"),
                                      ct.get("matchCase"), slug + " replaceAllText")
        allow()
    if name.endswith("find_and_replace_doc"):
        check_replace(doc_id(tool_input.get("document_id")), tool_input.get("find_text"),
                      tool_input.get("replace_text"), tool_input.get("match_case"),
                      "find_and_replace_doc")
        allow()
    allow()


def post(name, tool_input, tool_response):
    if (GUARD_DIR / "off").exists():
        allow()
    resp = normalize(tool_response)
    if name.endswith("COMPOSIO_MULTI_EXECUTE_TOOL"):
        items = [i for i in (tool_input.get("tools") or []) if isinstance(i, dict)]
        results = results_list(resp)
        notes = []
        for idx, item in enumerate(items):
            slug = str(item.get("tool_slug", ""))
            args = item.get("arguments") or {}
            payload = results[idx] if results and idx < len(results) and len(results) == len(items) else resp
            if slug == "GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT":
                doc = doc_id(args.get("document_id") or args.get("id"))
                text = longest_string(payload, 200)
                parsed = bool(text) and not looks_truncated(text)
                save_cache(doc, text, parsed)
                log(f"CACHE {doc} parsed={parsed} chars={len(text or '')}")
            elif slug == "GOOGLEDOCS_REPLACE_ALL_TEXT":
                doc = doc_id(args.get("document_id") or args.get("id"))
                n = find_key(payload, ("occurrencesChanged", "occurrences_changed"))
                if n == 0:
                    notes.append(f"GOOGLEDOCS_REPLACE_ALL_TEXT on doc {doc} changed 0 occurrences: "
                                 "the doc no longer contains that find_text — it changed since your "
                                 "readback, or the text is inexact. Re-read the doc before any other "
                                 "edit. Do not insert or rewrite the paragraph to compensate.")
                else:
                    c = load_cache(doc)
                    if c and c.get("parsed") and args.get("find_text"):
                        c["text"] = c["text"].replace(str(args["find_text"]), str(args.get("replace_text", "")))
                        save_cache(doc, c["text"], True, ts=c.get("ts"))
        if notes:
            post_context("\n".join(notes))
        allow()
    if name.endswith("get_doc_content"):
        doc = doc_id(tool_input.get("document_id"))
        text = longest_string(resp, 200)
        save_cache(doc, text, bool(text) and not looks_truncated(text))
        allow(f"cache {doc}")
    if name.endswith("find_and_replace_doc"):
        doc = doc_id(tool_input.get("document_id"))
        c = load_cache(doc)
        if c and c.get("parsed") and tool_input.get("find_text"):
            c["text"] = c["text"].replace(str(tool_input["find_text"]), str(tool_input.get("replace_text", "")))
            save_cache(doc, c["text"], True, ts=c.get("ts"))
        allow()
    if name.endswith("read_file_content") or name.endswith("download_file_content"):
        size = len(json.dumps(tool_response, default=str)) if not isinstance(tool_response, str) else len(tool_response)
        if size > BIG_READ_CHARS:
            post_context(f"That Drive read put ~{size // 1000}k characters (~{size // 4000}k tokens) into "
                         "the conversation. If it was a PDF or an exported CV, do not repeat it: "
                         "`bash resume-builder/scripts/cvcheck.sh <DOC_ID>` writes the PDF to a file "
                         "and returns only the line-fit summary.")
        allow()
    allow()


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    try:
        event = payload.get("hook_event_name", "")
        name = str(payload.get("tool_name", ""))
        tool_input = payload.get("tool_input") or {}
        if not isinstance(tool_input, dict):
            tool_input = {}
        if event == "PreToolUse":
            pre(name, tool_input)
        elif event == "PostToolUse":
            post(name, tool_input, payload.get("tool_response"))
    except SystemExit:
        raise
    except Exception as exc:  # never block on a bug in the guard itself
        log(f"ERROR {type(exc).__name__}: {exc}")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
