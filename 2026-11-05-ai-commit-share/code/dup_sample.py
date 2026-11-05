"""How many times does the commit index hold the same commit? Sample commits from 3 Nov (sorted by committer date,
pages spread over the day) for the whole index and for the Claude trailer, then count copies of each SHA with hash:.
Output: data/dup_sample.json"""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gh import search
random.seed(20261105)
out = {}
for label, term in [("all", ""), ("claude", '"Co-Authored-By: Claude" ')]:
    shas = []
    for h in random.sample(range(24), 10):
        q = f"{term}committer-date:2026-11-03T{h:02d}:00:00..2026-11-03T{h:02d}:59:59"
        r = search(q, per_page=100, page=random.randint(1, 10))
        items = r["items"]
        random.shuffle(items)
        shas += [(i["sha"], i["repository"]["full_name"], i["repository"].get("fork")) for i in items[:10]]
    rows = []
    for sha, repo, fork in shas:
        r = search(f"hash:{sha}", per_page=100)
        rows.append({"sha": sha, "repo": repo, "fork": fork, "copies": r["total_count"], "incomplete": r["incomplete_results"]})
        print(label, sha[:8], r["total_count"], flush=True)
    out[label] = rows
json.dump(out, open(os.path.join(os.path.dirname(__file__), "..", "data", "dup_sample.json"), "w"), indent=1)
for k, v in out.items():
    c = [x["copies"] for x in v]
    print(k, "n", len(c), "mean copies", sum(c) / len(c), "harmonic-weighted distinct share", sum(1 / max(x, 1) for x in c) / len(c))
