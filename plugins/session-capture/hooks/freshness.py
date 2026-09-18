#!/usr/bin/env python3
"""SessionStart hook: warn when the ACCOUNT's uploaded skills have gone stale.

The gap this closes
-------------------
Skills reach a session by three paths, and only two of them have a guard:

  1. ~/.claude/skills/            laptop canonical
  2. hbschlac/career-skills       repo mirror      <- sync.sh guards 1 <-> 2
  3. account-level uploaded zips  what web and phone sessions actually load

Nothing watched 3. It is refreshed by running build-web-zips.py and then
manually re-uploading each zip at claude.ai -> Settings -> Capabilities -> Skills.
Miss that step and every web and phone session silently runs old instructions.

On 2026-09-17 the uploaded `resume` skill was two weeks behind: no evidence ledger,
no Step 0 intake gate, no her-noun rule, and a blanket Composio ban that had been
narrowed on evidence. A session loaded it, called it "stale and old", and that
remark was the entire detection mechanism. Within two days of re-uploading, two
files had drifted again.

How it decides
--------------
The uploaded copy is NOT a byte copy of the repo: build-web-zips.py rewrites
`~/.claude/skills/...` paths so the bundle is self-contained on a phone. Comparing
raw bytes therefore reports drift on every file containing such a path. So this
imports `rewrite` from the repo's own build-web-zips.py and applies it before
hashing — one source of truth, and a difference that survives it is real.

Contract
--------
Emits hookSpecificOutput.additionalContext on stdout as JSON, or nothing. Always
exits 0, and stays silent on anything unexpected. A freshness warning is never
worth breaking a session over.
"""
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

CANDIDATE_CLONES = [
    os.path.expanduser("~/career-skills"),
    os.path.expanduser("~/product-networking-skills"),
    os.path.expanduser("~/code/career-skills"),
    os.path.expanduser("~/src/career-skills"),
    "/home/user/career-skills",
    "/home/user/product-networking-skills",
]
SYNCED = pathlib.Path(os.path.expanduser("~/.claude/skills/synced"))


def find_repo():
    for repo in CANDIDATE_CLONES:
        p = pathlib.Path(repo)
        if (p / "build-web-zips.py").is_file() and (p / "skills").is_dir():
            return p
    return None


def load_build(repo):
    """Import the repo's own build script so rewrite/BUNDLE/SHARED never drift."""
    spec = importlib.util.spec_from_file_location(
        "_bwz", str(repo / "build-web-zips.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def commits_behind(repo):
    """How far this clone trails origin/main, or None if it cannot be determined.

    This guard is the whole reason the check is trustworthy. While developing it,
    an eight-commits-behind clone made the comparison report the account as stale
    when the account was in fact CURRENT and the clone was the stale side. Acting
    on that would have rebuilt the zips from old content and overwritten newer
    uploaded skills — the same shape as the sync that deleted the ledger's
    hard-limits section on 2026-09-16. A comparison against a clone that is behind
    is not a weak signal, it is an inverted one.
    """
    try:
        subprocess.run(["git", "-C", str(repo), "fetch", "--quiet", "origin", "main"],
                       capture_output=True, timeout=20)
    except Exception:
        pass  # offline is fine; the count below still uses the last known origin/main
    try:
        res = subprocess.run(
            ["git", "-C", str(repo), "rev-list", "--count", "HEAD..origin/main"],
            capture_output=True, text=True, timeout=15)
        if res.returncode != 0:
            return None
        return int(res.stdout.strip())
    except Exception:
        return None


def digest(text):
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


def canonical_shared(repo, bwz, name):
    """Where a bundled shared file comes from, expressed as a repo path.

    SHARED points into ~/.claude/skills (the laptop). A web session has the repo
    instead, so map the tail of that path onto skills/ in the clone.
    """
    src = pathlib.Path(str(bwz.SHARED[name]))
    parts = src.parts
    if "skills" not in parts:
        return None
    tail = parts[parts.index("skills") + 1:]
    return repo.joinpath("skills", *tail)


def stale_files(repo, bwz, account_root):
    """Return [(skill, file)] whose uploaded copy differs from the repo's."""
    out = []
    for skill, shared in bwz.BUNDLE.items():
        adir = account_root / skill
        if not adir.is_dir():
            # Not uploaded at all. Real, and worth reporting once.
            out.append((skill, "(skill not on the account)"))
            continue
        rskill = repo / "skills" / skill / "SKILL.md"
        askill = adir / "SKILL.md"
        if rskill.is_file() and askill.is_file():
            if digest(askill.read_text(encoding="utf-8", errors="replace")) != \
               digest(bwz.rewrite(rskill.read_text(encoding="utf-8", errors="replace"))):
                out.append((skill, "SKILL.md"))
        for name in shared:
            rp = canonical_shared(repo, bwz, name)
            ap = adir / "references" / name
            if rp is None or not rp.is_file():
                continue
            if not ap.is_file():
                out.append((skill, f"references/{name} (missing from the upload)"))
                continue
            if digest(ap.read_text(encoding="utf-8", errors="replace")) != \
               digest(bwz.rewrite(rp.read_text(encoding="utf-8", errors="replace"))):
                out.append((skill, f"references/{name}"))
    return out


def warn_clone_behind(behind, repo):
    """Say we cannot tell, rather than guessing in the dangerous direction."""
    n = "an unknown number of" if behind is None else str(behind)
    try:
        json.dump({"hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": (
                "Upload-freshness check SKIPPED: the %s clone is %s commit(s) behind "
                "origin/main, so comparing the account's skills against it would be "
                "misleading — and misleading in the direction that destroys work, "
                "because a rebuild from a stale clone overwrites newer uploaded "
                "skills. Run `git -C %s pull --rebase origin main` and restart to "
                "get the check back." % (repo.name, n, repo)
            ),
        }}, sys.stdout)
    except Exception:
        pass
    return 0


def main():
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    try:
        repo = find_repo()
        if repo is None:
            return 0
        roots = sorted(p for p in SYNCED.glob("*") if p.is_dir())
        if not roots:
            return 0
        behind = commits_behind(repo)
        if behind is None or behind > 0:
            return warn_clone_behind(behind, repo)
        bwz = load_build(repo)
        stale = stale_files(repo, bwz, roots[-1])
    except Exception:
        return 0

    if not stale:
        return 0

    lines = [
        "STALE UPLOADED SKILLS — the account copies this session loaded are behind "
        "the repo. Web and phone sessions run the UPLOADED zips, not this repo, so "
        "instructions you can see in the files here may not be the ones in force.",
        "",
        "Behind:",
    ]
    for skill, f in stale[:12]:
        lines.append(f"  {skill}: {f}")
    if len(stale) > 12:
        lines.append(f"  ... and {len(stale) - 12} more")
    lines += [
        "",
        "Fix (laptop only — a web session cannot upload):",
        "  cd ~/career-skills && ./sync.sh && ./sync.sh --pull && ./sync.sh",
        "  python3 ~/career-skills/build-web-zips.py",
        "  then re-upload each zip at claude.ai -> Settings -> Capabilities -> Skills",
        "",
        "Until then, prefer the repo copies under skills/ over the loaded skill text, "
        "and tell Hannah the upload is stale rather than working around it silently.",
    ]

    try:
        json.dump({"hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lines),
        }}, sys.stdout)
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
