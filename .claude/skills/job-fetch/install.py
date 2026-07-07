#!/usr/bin/env python3
"""Install the job-fetch skill + auto-trigger hook at USER scope (~/.claude).

Run once on a desktop machine to make the skill and its UserPromptSubmit hook
fire in every session, in any repo:

    python3 .claude/skills/job-fetch/install.py

It copies the skill dir to ~/.claude/skills/job-fetch/, copies the detector to
~/.claude/hooks/detect-job-url.py, and idempotently merges the hook into
~/.claude/settings.json. Safe to re-run. Does nothing destructive to existing
settings — it only adds the hook if it isn't already present.

(Web sessions load ~/.claude ephemerally, so this is primarily for desktop; on
web, keep the files committed in the repos you use.)
"""
import json
import shutil
from pathlib import Path

REPO_CLAUDE = Path(__file__).resolve().parents[2]  # .../.claude
SKILL_SRC = REPO_CLAUDE / "skills" / "job-fetch"
HOOK_SRC = REPO_CLAUDE / "hooks" / "detect-job-url.py"

USER_CLAUDE = Path.home() / ".claude"
SKILL_DST = USER_CLAUDE / "skills" / "job-fetch"
HOOK_DST = USER_CLAUDE / "hooks" / "detect-job-url.py"
SETTINGS = USER_CLAUDE / "settings.json"

HOOK_CMD = 'python3 "$HOME/.claude/hooks/detect-job-url.py"'


def copy_skill():
    SKILL_DST.parent.mkdir(parents=True, exist_ok=True)
    if SKILL_DST.exists():
        shutil.rmtree(SKILL_DST)
    shutil.copytree(SKILL_SRC, SKILL_DST)
    print(f"  skill  -> {SKILL_DST}")


def copy_hook():
    HOOK_DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HOOK_SRC, HOOK_DST)
    print(f"  hook   -> {HOOK_DST}")


def merge_settings():
    settings = {}
    if SETTINGS.exists():
        try:
            settings = json.loads(SETTINGS.read_text() or "{}")
        except json.JSONDecodeError:
            print(f"  ! {SETTINGS} is not valid JSON — not touching it. Add the hook manually.")
            return
    hooks = settings.setdefault("hooks", {})
    ups = hooks.setdefault("UserPromptSubmit", [])
    # Already installed? (match on our detector filename)
    for group in ups:
        for h in group.get("hooks", []):
            if "detect-job-url.py" in h.get("command", ""):
                print(f"  hook already registered in {SETTINGS}")
                return
    ups.append({"hooks": [{"type": "command", "command": HOOK_CMD}]})
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS.write_text(json.dumps(settings, indent=2) + "\n")
    print(f"  hook registered in {SETTINGS}")


def main():
    print("Installing job-fetch at user scope (~/.claude):")
    copy_skill()
    copy_hook()
    merge_settings()
    print("Done. New sessions on this machine will auto-fire job-fetch on job URLs.")


if __name__ == "__main__":
    main()
