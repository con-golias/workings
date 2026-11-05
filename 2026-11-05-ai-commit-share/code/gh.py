"""Paced GitHub commit-search helper (one call per ~3 s, backoff on secondary rate limit)."""
import json, subprocess, time

_last = [0.0]


def search(q, per_page=1, page=1):
    for attempt in range(8):
        wait = 3.2 - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        r = subprocess.run(["gh", "api", "-X", "GET", "search/commits", "-f", f"q={q}", "-f", f"per_page={per_page}",
                            "-f", f"page={page}"], capture_output=True, text=True, encoding="utf-8")
        if r.returncode == 0:
            return json.loads(r.stdout)
        if "rate limit" in (r.stdout + r.stderr).lower():
            time.sleep(30 * (attempt + 1))
            continue
        raise RuntimeError(r.stdout[:300] + r.stderr[:300])
    raise RuntimeError("rate limited")
