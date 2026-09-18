# session-capture

> **STATUS: ENABLED 2026-09-15**, after the test plan at the bottom passed end to end.
> `flush.py` is verified — a real push to `hbschlac/career-skills` left that clone's HEAD,
> checked-out branch, `status --porcelain` and `.git/index` byte-identical.
>
> **2026-09-17: fired on the laptop only.** Web sessions never ran a single hook — see
> *How these hooks are registered* below. Fixed by registering the hooks in
> `.claude/settings.json` as well. To stop them you must now remove **both**
> `session-capture@hbschlac` from `enabledPlugins` **and** the `hooks` block from
> `.claude/settings.json`.

Durable session memory. Solves the two ways a session's knowledge disappears.

## The two disappearances

**Compaction.** The 2026-09-15 Anthropic CV session compacted at 19:37. Roughly 14 of
Hannah's 46 messages were career facts Claude did not have — the Uprising security
framework, the xfn pillar, the dashboard engineering leadership ran on. After
compaction the model's view of the first three hours was a *summary*, not her words.
Any end-of-session "extract the learnings" pass had nothing real left to read.

**The container.** Claude Code web sessions run in ephemeral containers. Anything on
local disk is reclaimed when the session ends. So capturing to disk survives
compaction but still evaporates.

`resume-learn` already does the hard part — classify feedback, route it to one
canonical file, edit in place. In that five-hour session with ~15 rounds of
corrections it was invoked **zero times**, because it depends on remembering a
trigger phrase at the end of a long session. A memory that has to be remembered is
not a memory.

## What each hook does

| Event | Script | Job |
|---|---|---|
| `SessionStart` | `remind.py` | Inject the evidence-ledger pointer + flag unflushed logs. Retrieval stops depending on recall. |
| `SessionStart` | `freshness.py` | Warn when the ACCOUNT's uploaded skills are behind the repo — the one distribution path nothing else guards. |
| `UserPromptSubmit` | `capture.py` | Append the message to a local JSONL. No intelligence, ~0 tokens, never in context — so compaction can't touch it. |
| `Stop` | `flush.py` | Push if ≥5 new lines or ≥10 min since last push. Bounds loss to a few turns without a push per turn. |
| `PreCompact` | `flush.py` | Forced push. Context is about to be lost. |
| `SessionEnd` | `flush.py` | Forced push. Last chance before the container goes. |

## How these hooks are registered

Twice, on purpose.

| Path | Declared in | Works where |
|---|---|---|
| Plugin | `hooks/hooks.json` + `enabledPlugins` | Laptop, after `claude plugin install` |
| Settings | `hooks` block in `.claude/settings.json` | Everywhere, no install step |

The plugin path alone was the original design, and it silently did nothing on web for
two days. A Claude Code web container syncs *account-level* plugins only — it never acts
on a project's `enabledPlugins`. Measured in a web session on 2026-09-17:
`claude plugin marketplace list` reported **"No marketplaces configured"** even though
`.claude/settings.json` declared the marketplace correctly; `installed_plugins.json` was
`{"plugins": {}}`; `~/.claude/session-capture/` had never been created; and the session
transcript showed exactly one hook running all session — the user-scope launcher hook.
Meanwhile the capture branch still held nothing but the 2026-09-15 test artifacts.

Nothing was misconfigured. The config was correct and nothing ever read it.

The settings path needs no install, so it works in a fresh container. Both paths run the
same scripts; the settings invocations set `CLAUDE_HOOKS_VIA_SETTINGS=1`, and
`_registration.defer_to_plugin()` uses that to stand down when the plugin is also
installed — so a laptop with both live still captures each message exactly once. That
guard is deliberately biased to run: an unreadable install state returns `False`, because
a duplicated line is recoverable and a missed message is the whole failure being fixed.

**This does not fix persistence on its own.** A web session still has to attach the
private repo (`add_repo`, owner `hbschlac`, repo `career-skills`, access **push** — read
access clones fine but cannot flush). `remind.py` says so at `SessionStart`; before this
fix, that reminder never fired either.

## The third pipeline, and why `freshness.py` exists

Skills reach a session three ways, and only two were ever guarded:

1. `~/.claude/skills/` — laptop canonical
2. `hbschlac/career-skills` — repo mirror &nbsp;&nbsp;← `sync.sh` guards 1 ↔ 2, both directions
3. **account-level uploaded zips** — what web and phone sessions actually load

Nothing watched 3. It refreshes only when someone runs `build-web-zips.py` and then
manually re-uploads each zip. On 2026-09-17 the uploaded `resume` skill was two weeks
behind — no ledger, no Step 0 gate, no her-noun rule, and a Composio ban that had been
narrowed on evidence. The detection mechanism was a session remarking that the skill
seemed "stale and old". Within two days of re-uploading, it had drifted again.

`freshness.py` compares the loaded account copy against the repo at `SessionStart`. Two
things make it trustworthy rather than noisy:

- **It applies the build's own `rewrite()` before hashing.** The bundle deliberately
  rewrites `~/.claude/skills/...` paths so it works on a phone, so a raw byte comparison
  flags every file containing one. Importing `rewrite` from the repo's `build-web-zips.py`
  keeps a single source of truth instead of a copy that drifts.
- **It refuses to judge from a clone that is behind `origin/main`.** While this was being
  written, an eight-commits-behind clone made it report the account as stale when the
  account was current and the *clone* was stale. Acting on that would have rebuilt the zips
  from old content and overwritten newer uploaded skills — the same shape as the sync that
  deleted the ledger's hard-limits section. A comparison against a behind clone isn't a
  weak signal, it's an inverted one, so it says so and stops.

## Design decisions worth knowing

**Capture is dumb on purpose.** It classifies nothing. Promotion into skills happens
later, offline, where it can be gated. Capture is cheap and automatic; promotion is
expensive and gated. That asymmetry is what keeps this from becoming the 45-sessions
of skill-review bloat that produced the circuit breaker.

**The log is not a learnings file.** It is raw input to a distillation. `resume-learn`'s
"one source of truth per rule, never append to a learnings log, edit in place"
principle stays intact — this feeds that skill, it does not replace or bypass it.

**It fails closed on destination.** The raw log is everything she types. `ALLOWED_REMOTES`
lists private repos only; `hbschlac/hbschlac` is named in `REFUSED_REMOTES` because it
is public. If no allowed private clone is attached, nothing is pushed and a forced
event prints a visible warning naming the path.

**It never touches the working tree.** The push uses git plumbing — `hash-object`,
`read-tree`, `update-index`, `write-tree`, `commit-tree` — against a temporary
`GIT_INDEX_FILE`. No checkout, no branch switch, no index mutation. It cannot disturb
whatever the session is actually doing.

**Concurrent sessions cannot collide.** One file per session id, so content conflicts
are impossible. Only the branch tip moves, and the push re-reads `FETCH_HEAD` first.

**Secrets are scrubbed before the write**, not before the push — nothing unredacted
ever reaches disk.

## The one real limitation

The private repo has to be attached for persistence to work, and a fresh remote
session does not clone it automatically. `remind.py` asks for it at `SessionStart`,
which raises the hit rate but does not guarantee it. When it is missing, the forced
flush prints the log path rather than failing silently — data loss is loud, not quiet.

## Test plan — run this before enabling

Authored without Bash, so `flush.py` shipped unverified. **Run 2026-09-15 against
`hbschlac/career-skills`: 1–4 all pass.** Re-run it after any change to these hooks.

```bash
# 1. capture: redaction, empty prompt, malformed input — all must exit 0
echo '{"session_id":"t1","cwd":"/home/user/hbschlac","prompt":"key sk-ant-AAAAAAAAAAAAAAAAAAAA"}' \
  | python3 hooks/capture.py; echo "exit=$?"
cat ~/.claude/session-capture/*.jsonl      # expect [redacted:...], no raw key

# 2. fail-closed: with ONLY the public repo attached, a forced flush must refuse
echo '{"hook_event_name":"SessionEnd"}' | python3 hooks/flush.py
#    expect the "NOT persisted" warning, and NO push

# 3. real push: attach hbschlac/career-skills with access push, then
git -C /home/user/career-skills rev-parse HEAD > /tmp/before.sha
git -C /home/user/career-skills status --porcelain > /tmp/before.status
echo '{"hook_event_name":"SessionEnd"}' | python3 hooks/flush.py
#    MUST hold: HEAD and status identical to before (plumbing touched nothing)
diff <(git -C /home/user/career-skills rev-parse HEAD) /tmp/before.sha
diff <(git -C /home/user/career-skills status --porcelain) /tmp/before.status
#    and the branch must exist remotely with the log in it
git -C /home/user/career-skills fetch origin session-capture
git -C /home/user/career-skills ls-tree -r FETCH_HEAD --name-only

# 4. idempotence: run flush again immediately — expect "no change", no empty commit
```

Enable only after 1–4 pass (done 2026-09-15 in `.claude/settings.json`):

```json
"enabledPlugins": { "job-fetch@hbschlac": true, "session-capture@hbschlac": true }
```

To disable in a hurry, remove that key — the hooks stop firing immediately.

### What the 2026-09-15 run established

Beyond the four steps, three claims made above were exercised rather than assumed:

- **The plumbing really is inert.** Before/after comparison of the receiving clone showed an
  identical HEAD, checked-out branch, `status --porcelain`, and an unmodified `.git/index` —
  the temporary `GIT_INDEX_FILE` absorbed every write. `hash-object -w` accepts the log's
  absolute path from outside the work tree, which is what makes that possible.
- **Concurrency holds.** A second session's file was committed to the branch, then this
  session flushed new content of its own: the foreign file survived and the new commit was
  parented on it. Re-reading `FETCH_HEAD` is what preserves it — a push that skipped the
  fetch would clobber the other session.
- **A hostile `session_id` cannot escape the staging directory.** `../../etc/passwd`
  sanitizes to `etcpasswd`.

Two behaviors worth knowing when reading these logs later: the first push onto a
non-existent branch is an **orphan commit** (no parent), and `Stop` genuinely throttles —
one new line inside the 10-minute window pushes nothing, by design.

**One caveat found during cleanup:** this sandbox's git relay refuses ref *deletions*
(`push --delete` disconnects). The branch can be cleared forward with an empty-tree commit,
but it cannot be removed from inside a web session.

## What this does not do yet

Distillation. Capture gets her words off the box; turning them into skill edits is a
separate asynchronous pass that should read the `session-capture` branch and open a PR
using `resume-learn`'s routing table. That is the natural job for one of the scheduled
routines currently misconfigured to "review skills" (CLAUDE.md open issue #7) — they
hit the circuit breaker every run because they have no real input. This gives them one.
