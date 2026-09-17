#!/usr/bin/env python3
"""SessionStart hook: make the evidence ledger load, instead of hoping it gets read.

The retrieval half
------------------
`resume-learn` is a well-designed skill that turns session feedback into permanent
skill edits. In the 2026-09-15 Anthropic CV session — five hours, ~15 rounds of
corrections — it was invoked zero times, because it depends on Hannah remembering
a trigger phrase at the end of a long session.

A memory that has to be remembered is not a memory. This hook injects the pointer
automatically so retrieval does not depend on anyone's recall.

It also surfaces any capture log that has not been persisted, so an ephemeral
container does not quietly take her words with it.

Contract
--------
Emits `hookSpecificOutput.additionalContext` on stdout as JSON. Stays silent and
exits 0 on anything unexpected — a reminder is never worth breaking a session over.
"""
import json
import os
import pathlib
import sys

try:
    from _registration import defer_to_plugin
except Exception:  # a missing guard must never break the hook's contract
    def defer_to_plugin():
        return False

STAGING = pathlib.Path(os.path.expanduser("~/.claude/session-capture"))
STATE = STAGING / ".flush-state.json"

# Only fire where career/resume work actually happens. Elsewhere this is noise.
CAREER_MARKERS = ("hbschlac", "career-skills", "product-networking")

LEDGER = (
    "Career/resume context detected. Two standing rules for this session:\n"
    "\n"
    "1. READ THE EVIDENCE LEDGER BEFORE WRITING ANY RESUME BULLET. It lives in the "
    "private repo `hbschlac/career-skills` at "
    "`skills/product-networking/references/evidence.md`. A remote session does not "
    "clone it automatically — run `add_repo` (owner hbschlac, repo career-skills, "
    "access push) first. It holds every fact Hannah has stated, tagged by JD "
    "dimension, with provenance and hedges. Grep it per JD requirement before asking "
    "her anything, batch any genuine gaps into ONE message, and append her answers to "
    "it in the same turn. Never declare a gap unfixable before grepping it.\n"
    "\n"
    "2. Attaching that repo with push access also lets this session's capture log "
    "persist. Without it, everything she types is lost when the container is "
    "reclaimed."
)


def unflushed():
    """Lines written but not yet confirmed pushed."""
    try:
        logs = [p for p in STAGING.glob("*.jsonl") if p.stat().st_size > 0]
    except Exception:
        return 0
    if not logs:
        return 0
    try:
        flushed = json.loads(STATE.read_text()).get("flushed", {})
    except Exception:
        flushed = {}
    total = 0
    for log in logs:
        try:
            with log.open(encoding="utf-8") as fh:
                total += max(0, sum(1 for _ in fh) - flushed.get(log.name, 0))
        except Exception:
            continue
    return total


def main():
    # Registered twice on a laptop (plugin + settings.json). Run once.
    if defer_to_plugin():
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    cwd = (payload.get("cwd") or "").lower()
    if not any(marker in cwd for marker in CAREER_MARKERS):
        return 0

    parts = [LEDGER]
    pending = unflushed()
    if pending:
        parts.append(
            "\nNOTE: %d captured message(s) from this container have not been "
            "persisted yet. If the private repo is not attached, say so — they will "
            "not survive the session." % pending
        )

    try:
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "\n".join(parts),
            }
        }, sys.stdout)
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
