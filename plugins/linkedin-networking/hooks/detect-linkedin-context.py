#!/usr/bin/env python3
"""UserPromptSubmit hook: detect LinkedIn / networking intent and fire the skill.

Reads the hook payload as JSON on stdin, scans the user's prompt for a LinkedIn
(or Sales Navigator) URL or a networking-intent phrase, and — on a match — emits
`hookSpecificOutput.additionalContext` steering Claude into the
`linkedin-networking` skill AND reminding it this is a compliant, no-scrape,
no-send workflow.

No network, no writes: pure regex on the prompt text. Stays silent (empty output,
exit 0) on any non-match or any error, so it can never block a normal prompt.
"""
import json
import re
import sys

# A linkedin.com URL of any shape (profile, company, school, sales navigator).
LINKEDIN_URL = re.compile(
    r"""https?://[^\s"'>)]*?linkedin\.com[^\s"'>)]*""",
    re.IGNORECASE,
)

# Networking intent expressed in plain language (no URL needed). Kept specific to
# discovery/outreach so it doesn't fire on unrelated mentions of "LinkedIn".
INTENT = re.compile(
    r"""(
        \balumni\b
      | \bhaas\b
      | who\s+(?:should\s+i|to)\s+(?:connect|reach\s*out|message|contact)
      | people\s+to\s+(?:connect|reach\s*out|message|contact)
      | (?:find|source)\s+(?:me\s+)?(?:relevant\s+)?(?:people|contacts|connections)
      | (?:companies|people)\s+to\s+(?:look\s+into|research|reach\s*out\s+to)
      | (?:networking|outreach|prospect(?:ing)?)\b.*\blinkedin\b
      | \blinkedin\b.*(?:networking|outreach|prospect(?:ing)?|connect\s+with)
    )""",
    re.IGNORECASE | re.VERBOSE,
)

INSTRUCTION = (
    "The user's prompt is about LinkedIn networking / finding people or companies to reach "
    "out to{url_note}. Use the `linkedin-networking` skill.\n"
    "This is a STRICTLY COMPLIANT, discovery-and-drafting workflow. Hard rules:\n"
    "- NEVER fetch, scrape, read, or automate LinkedIn (profiles, search, Alumni tool, "
    "Sales Navigator). LinkedIn hosts are also proxy-blocked in the web sandbox — that block "
    "is expected and must not be routed around.\n"
    "- NEVER send or automate messages or connection requests.\n"
    "- DO: source companies from off-LinkedIn data, build Sales Navigator search URLs for the "
    "user to click manually, draft outreach (delegating voice to the product-networking skill), "
    "and track contacts in a private Google Sheet. Follow the skill's 5 steps."
)


def find_signal(text: str):
    """Return (matched_url_or_None, bool_intent) or None if no networking signal."""
    if not text:
        return None
    url_match = LINKEDIN_URL.search(text)
    intent_match = INTENT.search(text)
    if url_match or intent_match:
        return (url_match.group(0) if url_match else None, bool(intent_match))
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return  # malformed input -> stay silent, never block the prompt

    prompt = payload.get("prompt") or payload.get("user_prompt") or ""
    signal = find_signal(prompt)
    if not signal:
        return

    url, _intent = signal
    url_note = f" (shared URL: {url})" if url else ""
    out = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": INSTRUCTION.format(url_note=url_note),
        }
    }
    print(json.dumps(out))


if __name__ == "__main__":
    main()
