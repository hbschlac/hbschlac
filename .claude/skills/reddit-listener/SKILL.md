---
name: reddit-listener
description: >
  Pull Reddit posts and comments from a web/cloud session past the 403 egress block that
  now hits reddit.com/*.json and PullPush. Uses the Arctic Shift archive API. Covers subreddit
  monitoring, thread ingestion, one-shot pulls, and scheduled listeners. Use when a task needs
  Reddit data ("what are people saying in r/X", "monitor r/Y", "pull this thread") from a sandboxed session.
---

# reddit-listener

Getting Reddit data into a Claude Code **web/cloud** session is not what it was. This skill
records the method that actually works from a sandboxed IP as of Aug 2026, so you don't
rediscover the 403 wall every time.

**Not for:** posting to Reddit, authenticated user actions, or laptop sessions with real OAuth
credentials (there, PRAW is still fine — see the last section).

**Relationship to research-pipeline:** research-pipeline owns the classify → analyze → present
pipeline once you have data. This skill owns *getting the data* past the egress block. Its
Reddit row ("PRAW or pushshift API") is the laptop path and is **stale for web sessions** — use
this skill's endpoint instead, then hand off to research-pipeline at Step 3.

---

## Announce activation

> **reddit-listener activated** — [one-shot pull | subreddit monitor | thread ingest]. [subreddit/URL.]

---

## Step 0: What breaks (so you don't waste calls confirming it)

Verified from a web sandbox, Aug 2026:

| Endpoint | Result from sandbox | Don't |
|---|---|---|
| `reddit.com/r/X/*.json`, `old.reddit.com/...json` | **403** — Reddit blocks unauthenticated cloud IPs, returns an HTML block page | Retry with more headers; it won't help |
| `api.pullpush.io` (Pushshift successor) | Rate-limited / blocks agent traffic | Rely on it for anything |
| `oauth.reddit.com` (official API) | Needs client_id/secret we don't have in-sandbox | Assume creds exist |
| **`arctic-shift.photon-reddit.com`** | **200** — full post/comment JSON | — |

**Do not** open with `WebFetch` on a `reddit.com` URL and conclude Reddit is unreachable. Go
straight to Arctic Shift.

---

## Step 1: The working endpoint — Arctic Shift

Free Reddit archive/mirror. No auth. Be gentle (it's a volunteer project): a short timeout and
a descriptive User-Agent, and don't hammer it in a tight loop.

**Base:** `https://arctic-shift.photon-reddit.com/api/`

### Posts in a subreddit (verified)

```
GET /posts/search?subreddit=<name>&limit=100&sort=desc
```

- `subreddit` — name without `r/`. Case-insensitive in practice, but use the canonical case
  (`Comcast_Xfinity`, `ATT`, `GoogleFi`) to be safe.
- `limit` — up to 100 per call.
- `sort=desc` — newest first (this is your "listener" ordering).
- Returns `{"data": [ {full reddit post objects} ]}` — same field names as the real Reddit API
  (`id`, `created_utc`, `score`, `num_comments`, `title`, `selftext`, `author`, `permalink`, …).

### Comments (search by subreddit or by post)

```
GET /comments/search?subreddit=<name>&limit=100&sort=desc
GET /comments/search?link_id=<post_id>&limit=100        # comments on one post
```

> `link_id` / thread-comment fan-out is **not yet verified** in this environment — confirm the
> shape on first use and update this line. Posts/search IS verified.

### Time-windowing a listener

Use `after` / `before` (epoch seconds or ISO) to pull only what's new since last run:

```
GET /posts/search?subreddit=<name>&after=<last_seen_utc>&sort=asc&limit=100
```

Persist the max `created_utc` you've seen; next run pass it as `after`. That's incremental
collection — don't re-pull the whole subreddit each cycle.

---

## Step 2: How to run it in-sandbox

`WebFetch` mangles JSON APIs. Prefer a shell `curl` when a bash/remote-exec tool is available;
in this repo's web sessions that's the Composio remote-bash tool (real egress). Pattern that
works — pull, project to the fields you need with `jq`, append to an ndjson cache:

```bash
API="https://arctic-shift.photon-reddit.com/api/posts/search"
: > telecom.ndjson
for sr in verizon tmobile ATT Comcast_Xfinity GoogleFi; do
  curl -sS -m 12 -H "User-Agent: reddit-listener/1.0 (research)" \
    "$API?subreddit=$sr&limit=100&sort=desc" \
  | jq -c --arg sr "$sr" \
      '.data[]? | {id, subreddit:$sr, created_utc, score, num_comments,
                   title, self:((.selftext//"")[0:600])}' >> telecom.ndjson
  echo "$sr -> $(wc -l < telecom.ndjson)"
done
```

Notes:
- `.data[]?` — the `?` tolerates an empty/absent `data` (dead or renamed subreddit) instead of
  erroring the whole loop.
- Truncate `selftext` (`[0:600]`) so the cache stays small; keep full text only if you'll quote it.
- **Cache raw before processing** (research-pipeline Step 2B rule): you can re-classify, you
  can't re-pull a deleted post.
- If no shell tool is live, `WebFetch` the Arctic Shift URL directly — it returns JSON as text
  you can read, just clumsier than `jq`.

---

## Step 3: Hand off

Once cached, you have a normal dataset. Switch to **research-pipeline** for taxonomy →
classification → analysis → presentation, and **content-quality** before writing any user-facing
summary. Don't rebuild that here.

For a lightweight "what's the vibe" answer (no dashboard), skip straight to: sort by `score`,
read the top ~20 titles + snippets, cluster by theme manually, report findings-first.

---

## Scheduled listener (cron routine)

To turn a one-shot pull into an ongoing monitor, register a routine that:

1. Reads the stored `last_seen_utc` for each subreddit.
2. Pulls `/posts/search?...&after=<last_seen>&sort=asc`.
3. If new posts crossed a threshold (volume spike, or a keyword like "outage" / "down" /
   "breach" in titles), summarizes and PushNotifies; otherwise updates `last_seen` silently.

Keep it to a **health-check/monitor** shape — see session-safety's routine templates. Do NOT
wire it to the "review skills" prompt (blocking circuit breaker). Log what you dropped if you
cap subreddits or posts per run — silent truncation reads as full coverage.

---

## Laptop / authenticated path (when creds exist)

If the session genuinely has Reddit OAuth (`client_id` + `secret`), PRAW against
`oauth.reddit.com` is still the richest source (live threads, `replace_more()` for full comment
trees, 60 req/min). Arctic Shift is the *sandbox* answer because those creds aren't present in
web sessions — don't reach for it on a laptop that can authenticate.

---

## Anti-patterns

- **Don't conclude "Reddit is blocked, can't help."** The `.json` 403 is expected; Arctic Shift
  is the way through. Only report a hard block after Arctic Shift itself fails.
- **Don't hammer Arctic Shift.** It's a free volunteer mirror. Descriptive UA, timeouts, no
  tight retry loops.
- **Don't re-pull the whole subreddit each cycle.** Persist `last_seen_utc`, use `after`.
- **Don't publish usernames.** Anonymize `author` in any shared output (research-pipeline rule).
- **Don't trust one dead subreddit to kill the run.** `.data[]?` and per-subreddit error
  handling so one 404 doesn't drop the rest.
