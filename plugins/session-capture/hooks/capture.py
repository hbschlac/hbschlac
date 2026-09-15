#!/usr/bin/env python3
"""UserPromptSubmit hook: append every user message to a local capture log.

Why this exists
---------------
The 2026-09-15 Anthropic CV session compacted at 19:37. Roughly 14 of Hannah's 46
messages were facts about her career that Claude did not have, and after compaction
the model's view of the first three hours was a summary, not her words. An
end-of-session "extract the learnings" pass therefore had nothing real to read, and
`resume-learn` — which exists and is well designed — was never invoked at all.

This hook captures her raw words the moment she types them, to a file that never
enters the context window. It is immune to compaction because it was never in
context, and it needs no intelligence: classification happens later, offline.

Contract
--------
Reads the hook payload as JSON on stdin. Appends one JSONL record per prompt.
Emits NOTHING and always exits 0 — a capture failure must never block a prompt or
leak noise into the conversation.
"""
import datetime
import json
import os
import pathlib
import re
import sys

STAGING = pathlib.Path(os.path.expanduser("~/.claude/session-capture"))

# Redact obvious secrets before anything is written to disk. Cheap insurance:
# she pastes a lot of material and this log is committed to a git repo.
REDACTIONS = [
    # sk-ant- must be tested before the generic sk- rule, or it is mislabelled.
    (re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{16,}"), "[redacted:anthropic-key]"),
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}"), "[redacted:openai-key]"),
    (re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}"), "[redacted:github-token]"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"), "[redacted:github-pat]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[redacted:aws-key]"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"), "[redacted:slack-token]"),
    (re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{20,}"), "[redacted:bearer]"),
    (re.compile(r"(?i)\b(pass(?:word|wd)|secret|api[_-]?key|token)\s*[:=]\s*\S+"),
     r"\1: [redacted]"),
]


def scrub(text):
    for pattern, replacement in REDACTIONS:
        text = pattern.sub(replacement, text)
    return text


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    prompt = payload.get("prompt") or ""
    if not prompt.strip():
        return 0

    session = str(payload.get("session_id") or "unknown")[:48]
    # Keep the filename filesystem-safe and one-file-per-session, so two concurrent
    # sessions can never write the same path and never conflict on push.
    session = re.sub(r"[^A-Za-z0-9_\-]", "", session) or "unknown"
    day = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    record = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "session_id": session,
        "cwd": payload.get("cwd") or "",
        "prompt": scrub(prompt),
    }

    try:
        STAGING.mkdir(parents=True, exist_ok=True)
        path = STAGING / f"{day}-{session}.jsonl"
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # Disk full, permissions, anything — stay silent. Never block her prompt.
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
