# Fetches the two public inputs the analysis reads, so the count can be rerun from scratch:
#   data/claude-changelog.md  - CHANGELOG.md of anthropics/claude-code (main branch)
#   data/cc_times.json        - npm publish time of every @anthropic-ai/claude-code version
# The changelog changes daily; the article's numbers are from the copy read on 20 November 2026.
# The advisory TSVs (data/gadv__*.tsv, adv_patched.tsv, adv_repo_only.tsv) were read from the GitHub advisory
# database and the repository's security page on the same day (see METHOD.md).
#   python code/fetch.py            (OUT=<folder> python code/fetch.py writes elsewhere)
import json
import os
import urllib.request

D = os.environ.get("OUT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")  # OUT=<dir> to test without overwriting
URLS = {
    "claude-changelog.md": "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md",
    "npm": "https://registry.npmjs.org/@anthropic-ai/claude-code",
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "workings-fetch"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


open(os.path.join(D, "claude-changelog.md"), "wb").write(get(URLS["claude-changelog.md"]))
meta = json.loads(get(URLS["npm"]))
times = {v: t for v, t in meta["time"].items() if v not in ("created", "modified")}
json.dump(times, open(os.path.join(D, "cc_times.json"), "w"), indent=0)
print(len(times), "npm versions; changelog saved")
