#!/usr/bin/env python3
"""Unit tests for .claude/hooks/cv_guard.py — run: python3 tests/test_cv_guard.py

Each case feeds the hook the JSON Claude Code would, in a throwaway cache dir, and checks the
decision. This proves the guard's LOGIC. It cannot prove the hook FIRES — that is verified next
session by ~/.claude/cv-guard/guard.log (the repo rule: a hook is not real until it has left a
side effect).
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "cv_guard.py"
DOC = "1AbCdEfGhIjKlMnOpQrStUvWxYz0123456789abcdefg"
DOC2 = "1GroceryListDocIdZZZZZZZZZZZZZZZZZZZZZZZZZZZ"
TEXT = ("Hannah Schlacter\nSenior Product Manager building AI-powered products\n"
        "● Built internal GenAI assistant that reduced diagnostic time by 40%\n"
        "● Led BuyBox ranking launches across 50+ teams\n"
        "SKILLS: AI product prototyping | ML ranking systems\n") * 3

failures = []


def run(event, name, tool_input, tool_response=None, env=None):
    payload = {"hook_event_name": event, "tool_name": name, "tool_input": tool_input, "cwd": str(ROOT)}
    if tool_response is not None:
        payload["tool_response"] = tool_response
    p = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True,
                       text=True, env={**os.environ, **(env or {})})
    out = p.stdout.strip()
    return json.loads(out) if out else None


def decision(res):
    return (res or {}).get("hookSpecificOutput", {}).get("permissionDecision")


def context(res):
    return (res or {}).get("hookSpecificOutput", {}).get("additionalContext", "")


def check(label, cond, detail=""):
    print(("  ok   " if cond else "  FAIL ") + label + ("" if cond else f"  — {detail}"))
    if not cond:
        failures.append(label)


def composio(slug, **args):
    return {"tools": [{"tool_slug": slug, "arguments": args}], "sync_response_to_workbench": False}


with tempfile.TemporaryDirectory() as tmp:
    env = {"CV_GUARD_DIR": tmp, "CV_GUARD_TTL_MIN": "30"}
    EXEC = "mcp__Composio_Docs_Drive__COMPOSIO_MULTI_EXECUTE_TOOL"
    print("cv_guard — PreToolUse")
    r = run("PreToolUse", EXEC, composio("GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN", id=DOC, markdown="# x"), env=env)
    check("markdown whole-doc update is denied", decision(r) == "deny")
    r = run("PreToolUse", EXEC, composio("GOOGLEDOCS_UPDATE_DOCUMENT_SECTION_MARKDOWN", document_id=DOC, markdown_text="x"), env=env)
    check("markdown section update is denied", decision(r) == "deny")
    r = run("PreToolUse", "mcp__google_workspace__import_to_google_doc", {"document_id": DOC}, env=env)
    check("import_to_google_doc is denied", decision(r) == "deny")
    r = run("PreToolUse", EXEC, composio("GOOGLEDOCS_REPLACE_ALL_TEXT", document_id=DOC, find_text="Led BuyBox", replace_text="Drove BuyBox"), env=env)
    check("replace without match_case is denied", decision(r) == "deny" and "match_case" in json.dumps(r))
    r = run("PreToolUse", EXEC, composio("GOOGLEDOCS_REPLACE_ALL_TEXT", document_id=DOC, find_text="Led BuyBox", replace_text="", match_case=True), env=env)
    check("empty replace_text is denied (orphan bullet)", decision(r) == "deny" and "orphan" in json.dumps(r))
    r = run("PreToolUse", EXEC, composio("GOOGLEDOCS_REPLACE_ALL_TEXT", document_id=DOC, find_text="Led BuyBox", replace_text="Drove BuyBox", match_case=True), env=env)
    check("replace before any readback is denied (read first)", decision(r) == "deny" and "readback" in json.dumps(r))
    r = run("PreToolUse", "mcp__Google_Drive__download_file_content", {"file_id": "abc"}, env=env)
    check("Drive download_file_content is denied", decision(r) == "deny" and "cvcheck" in json.dumps(r))
    pathlib.Path(tmp, "allow-download").touch()
    r = run("PreToolUse", "mcp__Google_Drive__download_file_content", {"file_id": "abc"}, env=env)
    check("download allowed with the marker", r is None)
    pathlib.Path(tmp, "allow-download").unlink()

    print("cv_guard — PostToolUse caches a readback")
    resp = {"data": {"results": [{"tool_slug": "GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT", "response": {"data": {"text": TEXT}}}]}}
    r = run("PostToolUse", EXEC, composio("GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT", document_id=f"https://docs.google.com/document/d/{DOC}/edit"), tool_response=resp, env=env)
    cache = json.loads(pathlib.Path(tmp, DOC + ".json").read_text())
    check("plaintext readback cached and parsed", cache.get("parsed") is True and "BuyBox" in cache.get("text", ""))
    r = run("PostToolUse", EXEC, composio("GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT", document_id=DOC + "zz"),
            tool_response=[{"type": "text", "text": json.dumps({"results": [{"data": {"text": TEXT}}]})}], env=env)
    check("MCP content-block response is also parsed", json.loads(pathlib.Path(tmp, DOC + "zz.json").read_text()).get("parsed") is True)

    print("cv_guard — Gate 0 before the first CV write")
    r = run("PreToolUse", EXEC, composio("GOOGLEDOCS_REPLACE_ALL_TEXT", document_id=DOC, find_text="Led BuyBox", replace_text="x", match_case=True), env=env)
    check("CV write with no ledger grep recorded is denied (Gate 0)", decision(r) == "deny" and "Gate 0" in json.dumps(r) and "ledger_grep" in json.dumps(r))
    marker = pathlib.Path(tmp, "facts-grepped"); marker.write_text("2026-09-17T00:00:00Z  security\n")
    old = time.time() - 9 * 3600; os.utime(marker, (old, old))
    r = run("PreToolUse", EXEC, composio("GOOGLEDOCS_REPLACE_ALL_TEXT", document_id=DOC, find_text="Led BuyBox", replace_text="x", match_case=True), env=env)
    check("a 9-hour-old ledger grep does not count", decision(r) == "deny" and "9.0 h ago" in json.dumps(r))
    marker.unlink()
    resp2 = {"results": [{"data": {"text": "Grocery list\n" + "eggs, milk, bread, coffee beans, olive oil, lemons, garlic, onions\n" * 6 + "call the plumber UNIQUE2\n"}}]}
    run("PostToolUse", EXEC, composio("GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT", document_id=DOC2), tool_response=resp2, env=env)
    r = run("PreToolUse", EXEC, composio("GOOGLEDOCS_REPLACE_ALL_TEXT", document_id=DOC2, find_text="plumber UNIQUE2", replace_text="electrician", match_case=True), env=env)
    check("a doc that does not read like a CV is not gated", r is None)
    marker.write_text("2026-09-17T16:00:00Z  security compliance\n")

    print("cv_guard — uniqueness against the readback")
    r = run("PreToolUse", EXEC, composio("GOOGLEDOCS_REPLACE_ALL_TEXT", document_id=DOC, find_text="Senior Product Manager building AI-powered products", replace_text="X", match_case=True), env=env)
    check("find_text matching 3× is denied (REPLACE_ALL)", decision(r) == "deny" and "3 times" in json.dumps(r))
    r = run("PreToolUse", EXEC, composio("GOOGLEDOCS_REPLACE_ALL_TEXT", document_id=DOC, find_text="text that is not in the doc", replace_text="X", match_case=True), env=env)
    check("find_text matching 0× is denied (doc changed / inexact)", decision(r) == "deny" and "not in the latest readback" in json.dumps(r))
    uniq = TEXT.replace("Led BuyBox ranking launches across 50+ teams", "Led BuyBox ranking launches across 50+ teams", 1)
    resp1 = {"results": [{"data": {"text": TEXT.split("● Led")[0] + "● Led BuyBox ranking launches across 50+ teams UNIQUE\n" + "SKILLS: tail\n"}}]}
    run("PostToolUse", EXEC, composio("GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT", document_id=DOC), tool_response=resp1, env=env)
    r = run("PreToolUse", EXEC, composio("GOOGLEDOCS_REPLACE_ALL_TEXT", document_id=DOC, find_text="teams UNIQUE", replace_text="teams, once", match_case=True), env=env)
    check("find_text matching exactly once is allowed", r is None)
    r = run("PreToolUse", EXEC, composio("GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT", document_id=DOC, edit_docs=[{"replaceAllText": {"containsText": {"text": "teams UNIQUE", "matchCase": False}, "replaceText": "x"}}]), env=env)
    check("batchUpdate replaceAllText without matchCase is denied", decision(r) == "deny")
    r = run("PreToolUse", EXEC, composio("GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT", document_id=DOC, edit_docs=[{"deleteContentRange": {"range": {"startIndex": 5, "endIndex": 9}}}]), env=env)
    check("structural batchUpdate (deleteContentRange) is allowed", r is None)

    print("cv_guard — replace results update the cache / warn on 0 changes")
    r = run("PostToolUse", EXEC, composio("GOOGLEDOCS_REPLACE_ALL_TEXT", document_id=DOC, find_text="teams UNIQUE", replace_text="teams, once", match_case=True),
            tool_response={"results": [{"data": {"replies": [{"replaceAllText": {"occurrencesChanged": 1}}]}}]}, env=env)
    cache = json.loads(pathlib.Path(tmp, DOC + ".json").read_text())
    check("successful replace applied to the cached copy", "teams, once" in cache["text"] and "teams UNIQUE" not in cache["text"] and r is None)
    r = run("PostToolUse", EXEC, composio("GOOGLEDOCS_REPLACE_ALL_TEXT", document_id=DOC, find_text="gone", replace_text="x", match_case=True),
            tool_response={"results": [{"data": {"replies": [{"replaceAllText": {"occurrencesChanged": 0}}]}}]}, env=env)
    check("0 occurrences changed → warning injected", "0 occurrences" in context(r))

    print("cv_guard — staleness and escape hatches")
    cache["ts"] = time.time() - 45 * 60
    pathlib.Path(tmp, DOC + ".json").write_text(json.dumps(cache))
    r = run("PreToolUse", EXEC, composio("GOOGLEDOCS_REPLACE_ALL_TEXT", document_id=DOC, find_text="teams, once", replace_text="y", match_case=True), env=env)
    check("readback older than TTL is denied (re-read)", decision(r) == "deny" and "min ago" in json.dumps(r))
    pathlib.Path(tmp, "off").touch()
    r = run("PreToolUse", EXEC, composio("GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN", id=DOC, markdown="# x"), env=env)
    check("kill switch disables the guard", r is None)
    pathlib.Path(tmp, "off").unlink()
    r = run("PostToolUse", "mcp__Google_Drive__read_file_content", {"file_id": "x"}, tool_response={"content": "%PDF" + "x" * 60000}, env=env)
    check("a >40k-char Drive read gets the cvcheck warning", "cvcheck" in context(r))
    r = run("PreToolUse", EXEC, {"tools": "garbage"}, env=env)
    check("malformed input never blocks (fails open)", r is None)
    r = run("PreToolUse", "Bash", {"command": "ls"}, env=env)
    check("unrelated tools are untouched", r is None)
    logged = pathlib.Path(tmp, "guard.log").read_text()
    check("every decision leaves a line in guard.log", "DENY" in logged and "CACHE" in logged)

print()
if failures:
    print(f"{len(failures)} FAILED: " + ", ".join(failures))
    sys.exit(1)
print("all cv_guard tests passed")
