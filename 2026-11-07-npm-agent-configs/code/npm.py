"""Small helper for the npm registry: retries, a polite pace, JSON or bytes."""
import json, time, urllib.request, urllib.parse
def get(url, raw=False, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "workings-research", "Accept-Encoding": "identity"})
            with urllib.request.urlopen(req, timeout=60) as r: b = r.read()
            return b if raw else json.loads(b)
        except Exception:
            if i == tries - 1: raise
            time.sleep(2 * (i + 1))
def packument(name): return get("https://registry.npmjs.org/" + urllib.parse.quote(name, safe="@"))
