#!/usr/bin/env python3
"""session_meter.py — what this session actually cost, from its own transcript.

    python3 scripts/session_meter.py                 # newest transcript for this cwd
    python3 scripts/session_meter.py PATH.jsonl      # a specific transcript
    python3 scripts/session_meter.py --json          # machine-readable
    python3 scripts/session_meter.py --append        # one JSON line to ~/.claude/cv-guard/meter.log

Reads the per-message `usage` that Claude Code writes to ~/.claude/projects/<cwd>/<session>.jsonl,
dedupes by requestId (one API call is written once per content block), and counts the tool
calls that drove the 2026-09-15 CV session's cost: doc edits, read-backs, PDF pulls, rubric
runs. Baseline for that session: 127 edits · 27 PDF pulls · 9 rubric runs · 46 messages ·
context exhausted once. Run it at the end of a CV session and compare.

Stdlib only. Never prints the transcript, only the totals.
"""
import glob
import json
import os
import pathlib
import sys
import time
from collections import Counter


def find_transcript(explicit=None):
    if explicit:
        return pathlib.Path(explicit)
    cwd = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    slug = cwd.replace("/", "-")
    paths = glob.glob(os.path.expanduser(f"~/.claude/projects/{slug}/*.jsonl"))
    if not paths:
        paths = glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl"))
    if not paths:
        return None
    return pathlib.Path(max(paths, key=os.path.getmtime))


def classify(name, inp):
    """Map a tool_use to the CV-session categories the baseline was counted in."""
    cats = []
    n = name or ""
    if n.endswith("COMPOSIO_MULTI_EXECUTE_TOOL"):
        for item in (inp.get("tools") or []) if isinstance(inp, dict) else []:
            slug = str(item.get("tool_slug", "")) if isinstance(item, dict) else ""
            if slug == "GOOGLEDOCS_REPLACE_ALL_TEXT":
                cats.append("doc_edits")
            elif slug == "GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT":
                cats.append("doc_edits")
            elif slug in ("GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT", "GOOGLEDOCS_GET_DOCUMENT_BY_ID"):
                cats.append("readbacks")
            elif "MARKDOWN" in slug:
                cats.append("markdown_imports")
    elif n.endswith("find_and_replace_doc") or n.endswith("batch_update_doc"):
        cats.append("doc_edits")
    elif n.endswith("get_doc_content"):
        cats.append("readbacks")
    elif n.endswith("import_to_google_doc"):
        cats.append("markdown_imports")
    elif n.endswith("download_file_content"):
        cats.append("pdf_pulls")
    elif n == "Skill" and isinstance(inp, dict) and "recruiter-filter" in str(inp.get("skill", "")):
        cats.append("rubric_runs")
    return cats


def meter(path):
    usage = {"input_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 0}
    seen = set()
    tools = Counter()
    cats = Counter()
    api_calls = 0
    user_msgs = 0
    peak_context = 0
    compactions = 0
    model = ""
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                o = json.loads(line)
            except Exception:
                continue
            t = o.get("type")
            if o.get("isCompactSummary") or t == "summary":
                compactions += 1
            if t == "user":
                m = o.get("message") or {}
                c = m.get("content")
                # a real human turn is a string, or a list without tool_result blocks
                if isinstance(c, str) or (isinstance(c, list) and not any(
                        isinstance(b, dict) and b.get("type") == "tool_result" for b in c)):
                    user_msgs += 1
            if t != "assistant":
                continue
            m = o.get("message") or {}
            model = model or str(m.get("model") or "")
            for b in m.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    tools[b.get("name", "?")] += 1
                    for cat in classify(b.get("name"), b.get("input") or {}):
                        cats[cat] += 1
            rid = o.get("requestId") or m.get("id")
            if rid in seen:
                continue
            seen.add(rid)
            u = m.get("usage") or {}
            if not u:
                continue
            api_calls += 1
            for k in usage:
                usage[k] += int(u.get(k) or 0)
            ctx = int(u.get("input_tokens") or 0) + int(u.get("cache_creation_input_tokens") or 0) \
                + int(u.get("cache_read_input_tokens") or 0)
            peak_context = max(peak_context, ctx)
    total_in = usage["input_tokens"] + usage["cache_creation_input_tokens"] + usage["cache_read_input_tokens"]
    return {
        "transcript": str(path),
        "api_calls": api_calls,
        "user_messages": user_msgs,
        "peak_context_tokens": peak_context,
        "compactions": compactions,
        "model": model,
        "window_tokens": 200_000 if "haiku" in model.lower() else 1_000_000,
        "input_tokens_uncached": usage["input_tokens"],
        "cache_write_tokens": usage["cache_creation_input_tokens"],
        "cache_read_tokens": usage["cache_read_input_tokens"],
        "output_tokens": usage["output_tokens"],
        "total_input_processed": total_in,
        "cv": {k: cats.get(k, 0) for k in ("doc_edits", "readbacks", "pdf_pulls", "rubric_runs", "markdown_imports")},
        "top_tools": tools.most_common(10),
    }


BASELINE = {"doc_edits": 127, "readbacks": 15, "pdf_pulls": 27, "rubric_runs": 9, "markdown_imports": 0}


def render(r):
    k = lambda n: f"{n/1000:,.0f}k" if n >= 1000 else str(n)
    lines = [
        f"session meter — {os.path.basename(r['transcript'])}",
        f"  API calls {r['api_calls']:>5}   your messages {r['user_messages']:>4}   compactions {r['compactions']}",
        f"  peak context {k(r['peak_context_tokens']):>7}   of a {k(r['window_tokens'])} window ({r['model'] or 'model unknown'})",
        f"  input processed {k(r['total_input_processed']):>7}  = uncached {k(r['input_tokens_uncached'])} + cache-write {k(r['cache_write_tokens'])} + cache-read {k(r['cache_read_tokens'])}",
        f"  output {k(r['output_tokens'])}",
        "  CV ops        this session   2026-09-15 baseline",
    ]
    for key, label in (("doc_edits", "doc edits"), ("readbacks", "read-backs"), ("pdf_pulls", "PDF pulls"),
                       ("rubric_runs", "rubric runs"), ("markdown_imports", "markdown imports")):
        lines.append(f"    {label:<16}{r['cv'][key]:>6}   {BASELINE[key]:>10}")
    if r["top_tools"]:
        lines.append("  top tools: " + ", ".join(f"{n} ×{c}" for n, c in r["top_tools"][:6]))
    return "\n".join(lines)


def main(argv):
    as_json = "--json" in argv
    append = "--append" in argv
    explicit = next((a for a in argv if a.endswith(".jsonl")), None)
    path = find_transcript(explicit)
    if not path or not path.exists():
        if not append:
            print("session_meter: no transcript found", file=sys.stderr)
        return 0 if append else 1
    r = meter(path)
    if append:
        try:
            out = pathlib.Path(os.path.expanduser("~/.claude/cv-guard")); out.mkdir(parents=True, exist_ok=True)
            r["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            with (out / "meter.log").open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + "\n")
        except Exception:
            pass
        return 0
    print(json.dumps(r, indent=2) if as_json else render(r))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
