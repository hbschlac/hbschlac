#!/usr/bin/env python3
"""Stop / PreCompact / SessionEnd hook: push the capture log to the PRIVATE repo.

The evaporation problem
-----------------------
Claude Code web sessions run in ephemeral containers. A capture log written to
local disk survives compaction — the main threat to in-context memory — but not
the container, which is reclaimed when the session ends. So capture alone buys
nothing durable. The log has to leave the box.

How it leaves
-------------
It is committed to the PRIVATE skills repo on a dedicated `session-capture`
branch, using git plumbing (hash-object / read-tree / write-tree / commit-tree)
against a temporary GIT_INDEX_FILE. That never touches the session's index,
working tree, or checked-out branch, so it cannot disturb whatever the session is
actually doing.

Each session writes one uniquely-named file, so two concurrent sessions can never
conflict on content — only on the branch tip, which is retried.

Safety
------
* Fails CLOSED on destination. The raw log contains everything Hannah types. If
  the remote is not a recognised private repo it is NOT pushed, ever. In
  particular `hbschlac/hbschlac` is public and is explicitly refused.
* Always exits 0. A capture failure must never block her session.
* Every git call is timed out.
"""
import json
import os
import pathlib
import subprocess
import sys
import time

STAGING = pathlib.Path(os.path.expanduser("~/.claude/session-capture"))
STATE = STAGING / ".flush-state.json"
BRANCH = "session-capture"
DEST_DIR = "session-capture"

# Clones that may receive the log. Must be private.
# Where the private clone might be. The remote sandbox checks repos out under
# /home/user; a laptop puts them under $HOME. Hardcoding only the sandbox paths
# made find_repo() return None on every laptop session, so capture wrote to disk,
# never pushed, and printed "NOT persisted" at each session end — the plugin
# looked enabled and did nothing.
CANDIDATE_CLONES = [
    os.path.expanduser("~/career-skills"),
    os.path.expanduser("~/product-networking-skills"),
    os.path.expanduser("~/code/career-skills"),
    os.path.expanduser("~/src/career-skills"),
    "/home/user/career-skills",
    "/home/user/product-networking-skills",
]
ALLOWED_REMOTES = ("hbschlac/career-skills", "hbschlac/product-networking-skills")
# Explicitly refused: public. Named so a future edit can't widen this by accident.
REFUSED_REMOTES = ("hbschlac/hbschlac",)

FORCED_EVENTS = {"PreCompact", "SessionEnd"}
MIN_LINES = 5        # flush on Stop after this many new lines
MIN_SECONDS = 600    # ...or this long since the last flush


def git(repo, *args, timeout=60):
    return subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True, text=True, timeout=timeout,
    )


def find_repo():
    """First candidate clone whose origin is an allowed PRIVATE repo."""
    for repo in CANDIDATE_CLONES:
        if not pathlib.Path(repo, ".git").exists():
            continue
        try:
            res = git(repo, "remote", "get-url", "origin", timeout=15)
        except Exception:
            continue
        if res.returncode != 0:
            continue
        url = (res.stdout or "").strip()
        if any(bad in url for bad in REFUSED_REMOTES):
            continue
        if any(ok in url for ok in ALLOWED_REMOTES):
            return repo, url
    return None, None


def load_state():
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {}


def save_state(state):
    try:
        STAGING.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps(state))
    except Exception:
        pass


def count_lines(path):
    try:
        with path.open(encoding="utf-8") as fh:
            return sum(1 for _ in fh)
    except Exception:
        return 0


def should_flush(event, logs, state):
    if event in FORCED_EVENTS:
        return True
    if time.time() - state.get("last_flush", 0) >= MIN_SECONDS:
        return True
    flushed = state.get("flushed", {})
    pending = sum(max(0, count_lines(log) - flushed.get(log.name, 0)) for log in logs)
    return pending >= MIN_LINES


def push(repo, logs):
    """Commit the logs onto BRANCH via plumbing. Returns (ok, detail)."""
    env = dict(os.environ)
    index = STAGING / ".git-index-tmp"
    try:
        index.unlink()
    except Exception:
        pass
    env["GIT_INDEX_FILE"] = str(index)
    env.setdefault("GIT_AUTHOR_NAME", "claude-session-capture")
    env.setdefault("GIT_AUTHOR_EMAIL", "noreply@anthropic.com")
    env.setdefault("GIT_COMMITTER_NAME", "claude-session-capture")
    env.setdefault("GIT_COMMITTER_EMAIL", "noreply@anthropic.com")

    def g(*args, timeout=90):
        return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                              text=True, timeout=timeout, env=env)

    # Start from the remote tip so a concurrent session's commits are preserved.
    parent = None
    if g("fetch", "--depth", "1", "origin", BRANCH).returncode == 0:
        rev = g("rev-parse", "FETCH_HEAD")
        if rev.returncode == 0:
            parent = rev.stdout.strip()

    if parent:
        if g("read-tree", parent).returncode != 0:
            return False, "read-tree failed"
    else:
        g("read-tree", "--empty")

    staged = 0
    for log in logs:
        blob = g("hash-object", "-w", "--", str(log))
        if blob.returncode != 0:
            continue
        sha = blob.stdout.strip()
        if g("update-index", "--add", "--cacheinfo",
             f"100644,{sha},{DEST_DIR}/{log.name}").returncode == 0:
            staged += 1
    if not staged:
        return False, "nothing staged"

    tree = g("write-tree")
    if tree.returncode != 0:
        return False, "write-tree failed"
    tree_sha = tree.stdout.strip()

    # Nothing changed since the last push — don't make an empty commit.
    if parent:
        parent_tree = g("rev-parse", parent + "^{tree}")
        if parent_tree.returncode == 0 and parent_tree.stdout.strip() == tree_sha:
            return True, "no change"

    args = ["commit-tree", tree_sha, "-m", "session capture: %d log(s)" % staged]
    if parent:
        args += ["-p", parent]
    commit = g(*args)
    if commit.returncode != 0:
        return False, "commit-tree failed"
    commit_sha = commit.stdout.strip()

    pushed = g("push", "origin", "%s:refs/heads/%s" % (commit_sha, BRANCH), timeout=180)
    if pushed.returncode != 0:
        detail = (pushed.stderr or "push failed").strip().splitlines()
        return False, (detail[-1] if detail else "push failed")[:200]
    return True, commit_sha[:12]


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    event = payload.get("hook_event_name") or "Stop"

    try:
        logs = sorted(p for p in STAGING.glob("*.jsonl") if p.stat().st_size > 0)
    except Exception:
        return 0
    if not logs:
        return 0

    state = load_state()
    if not should_flush(event, logs, state):
        return 0

    repo, url = find_repo()
    if not repo:
        if event in FORCED_EVENTS:
            print(
                "[session-capture] Capture log NOT persisted — the private skills repo "
                "is not attached to this session. %d log(s) in %s will be lost when this "
                "container is reclaimed. To save them: attach hbschlac/career-skills "
                "(add_repo, access push), then re-run this hook or copy the files out."
                % (len(logs), STAGING)
            )
        return 0

    try:
        ok, detail = push(repo, logs)
    except Exception as exc:
        ok, detail = False, str(exc)[:200]

    if ok:
        flushed = state.setdefault("flushed", {})
        for log in logs:
            flushed[log.name] = count_lines(log)
        state["last_flush"] = time.time()
        save_state(state)
    elif event in FORCED_EVENTS:
        print("[session-capture] Push to %s failed (%s). Log(s) still in %s — they will "
              "not survive this container." % (url, detail, STAGING))
    return 0


if __name__ == "__main__":
    sys.exit(main())
