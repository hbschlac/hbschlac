"""One place every outbound request goes through: honest User-Agent, timeout, one retry, TTL cache.

Tests swap `fetch` for a fixture router, so no unit test touches the network.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "rx-compare/0.1 (+https://github.com/hbschlac/hbschlac/tree/main/rx-compare)"
TIMEOUT = 60
TTL_SECONDS = 6 * 3600  # prices move weekly at most; NLM asks RxNav callers to cache 12-24h

_cache: dict[str, tuple[float, object]] = {}


def _key(url: str, params: dict | None, body: dict | None) -> str:
    return json.dumps([url, params or {}, body or {}], sort_keys=True)


def _request(url: str, params: dict | None, body: dict | None):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params, doseq=True)}"
    data = json.dumps(body).encode() if body is not None else None
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.load(resp)


def fetch(url: str, params: dict | None = None, body: dict | None = None):
    """GET (or POST when `body` is given) JSON. Retries once on 5xx/timeouts — Cost Plus returns
    an occasional 504 that clears on the next try."""
    key = _key(url, params, body)
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < TTL_SECONDS:
        return hit[1]
    for attempt in (1, 2):
        try:
            result = _request(url, params, body)
            break
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == 2:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2)
    _cache[key] = (time.time(), result)
    return result
