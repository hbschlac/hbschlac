#!/usr/bin/env python3
"""UserPromptSubmit hook: detect a job-posting URL and fire the job-fetch skill.

Reads the hook payload as JSON on stdin, scans the user's prompt for a known ATS
host or an explicit careers/jobs path, and — on a match — emits
`hookSpecificOutput.additionalContext` instructing Claude to run the `job-fetch`
skill via the Composio remote-fetch path and ingest the JD silently.

No network, no writes: pure regex on the prompt text. Stays silent (empty output,
exit 0) on any non-match or any error, so it can never block a normal prompt.
"""
import json
import re
import sys

# Known applicant-tracking-system hosts. Tight list to avoid false positives.
ATS_HOSTS = re.compile(
    r"""https?://[^\s"'>)]*?(
        jobs\.ashbyhq\.com
      | (?:boards|job-boards)\.greenhouse\.io
      | jobs\.lever\.co
      | [a-z0-9-]+\.myworkdayjobs\.com
      | [a-z0-9-]+\.ashbyhq\.com
    )[^\s"'>)]*""",
    re.IGNORECASE | re.VERBOSE,
)

# A generic careers/jobs path on any host (e.g. runlayer.com/careers/...).
CAREERS_PATH = re.compile(
    r"""https?://[^\s"'>)]*?/(?:careers?|jobs?|job-openings?|open-roles?|positions?)(?:/|\?|$)[^\s"'>)]*""",
    re.IGNORECASE,
)

INSTRUCTION = (
    "The user shared what looks like a job-posting URL: {url}\n"
    "This host is almost certainly proxy-blocked (403) in this sandbox, so WebFetch/curl will fail. "
    "Use the `job-fetch` skill: fetch the description OUT of the sandbox via the Composio remote-bash "
    "tool and the ATS public API (see the skill for the URL->API mapping), parse the role, INGEST it "
    "into context, and reply with a single one-line acknowledgment. Do NOT paste the job description "
    "back to the user, and do NOT fall back to a web search."
)


def find_job_url(text: str):
    if not text:
        return None
    m = ATS_HOSTS.search(text)
    if m:
        return m.group(0)
    m = CAREERS_PATH.search(text)
    if m:
        return m.group(0)
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return  # malformed input -> stay silent, never block the prompt

    prompt = payload.get("prompt") or payload.get("user_prompt") or ""
    url = find_job_url(prompt)
    if not url:
        return

    out = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": INSTRUCTION.format(url=url),
        }
    }
    print(json.dumps(out))


if __name__ == "__main__":
    main()
