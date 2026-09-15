# session-capture

> **STATUS: NOT ENABLED. `flush.py` is UNVERIFIED.** Registered in the marketplace but
> deliberately absent from `enabledPlugins`. Run the test plan at the bottom before
> turning it on — these hooks fire on every prompt and every turn.

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
| `UserPromptSubmit` | `capture.py` | Append the message to a local JSONL. No intelligence, ~0 tokens, never in context — so compaction can't touch it. |
| `Stop` | `flush.py` | Push if ≥5 new lines or ≥10 min since last push. Bounds loss to a few turns without a push per turn. |
| `PreCompact` | `flush.py` | Forced push. Context is about to be lost. |
| `SessionEnd` | `flush.py` | Forced push. Last chance before the container goes. |

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

Bash was unavailable when this was authored, so `capture.py` is tested and `flush.py`
is not. Run outside auto mode:

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

Enable only after 1–4 pass:

```json
"enabledPlugins": { "job-fetch@hbschlac": true, "session-capture@hbschlac": true }
```

To disable in a hurry, remove that key — the hooks stop firing immediately.

## What this does not do yet

Distillation. Capture gets her words off the box; turning them into skill edits is a
separate asynchronous pass that should read the `session-capture` branch and open a PR
using `resume-learn`'s routing table. That is the natural job for one of the scheduled
routines currently misconfigured to "review skills" (CLAUDE.md open issue #7) — they
hit the circuit breaker every run because they have no real input. This gives them one.
