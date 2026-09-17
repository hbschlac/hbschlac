#!/usr/bin/env python3
"""Shared guard: which registration path is driving this hook invocation.

Why two registration paths exist
--------------------------------
These hooks were originally registered only as a plugin (`hooks/hooks.json`,
enabled via `enabledPlugins` in the project's `.claude/settings.json`). That
works on a laptop, where `claude plugin install` has run. It does NOT work in a
Claude Code web session: the container syncs account-level plugins only and never
acts on a project's `enabledPlugins`, so `claude plugin marketplace list` reports
"No marketplaces configured", the plugin is never installed, and every hook it
declares silently never fires.

Measured on 2026-09-17 in a web session: `installed_plugins.json` was empty, the
session-capture staging dir had never been created, and the session transcript
showed exactly one hook running all session -- the user-scope launcher hook. The
capture branch on the private repo still held nothing but the 2026-09-15 test
artifacts, and job-fetch had never auto-fired on a job URL.

So the hooks are ALSO registered directly in `.claude/settings.json`, which
Claude Code reads natively with no install step. Those invocations set
CLAUDE_HOOKS_VIA_SETTINGS=1 so this module can tell the two apart and keep a
laptop -- where both paths are live -- from running every hook twice.

This file is duplicated verbatim into each plugin that needs it. Plugins install
into separate roots and cannot import each other, so a shared copy is not
possible; keep them byte-identical (`cmp` them) when editing.
"""
import json
import os
import pathlib

INSTALLED = pathlib.Path(
    os.path.expanduser("~/.claude/plugins/installed_plugins.json")
)


def defer_to_plugin(plugin):
    """True when settings.json fired us but the installed plugin will fire too.

    `plugin` is the plugin's name as it appears in `installed_plugins.json`,
    without the `@marketplace` suffix -- e.g. "session-capture".

    Biased to run rather than skip: an unreadable or surprising install state
    returns False. A duplicated run is recoverable; a hook that never fires is
    exactly the failure this guard was added to fix.
    """
    if not os.environ.get("CLAUDE_HOOKS_VIA_SETTINGS"):
        return False  # plugin invocation -- always the authoritative one
    try:
        installed = json.loads(INSTALLED.read_text()).get("plugins", {})
    except Exception:
        return False
    return any(str(name).startswith(plugin + "@") for name in installed)
