"""Author dates of the commits named in Fixes: lines that are older than the local clone (cloned since 1 Jun 2025).
Asks GitHub's GraphQL API, 100 hashes per request, through the gh CLI (needs `gh auth login`).
  python target_dates.py commits.json ../data/target_dates.json
Only the bug-age section uses these; the 90-day comparison needs nothing outside the clone."""
import json, subprocess, sys

rows = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
have = set(h[:12] for h in (r["h"] for r in rows))
START = 1777593600  # 2026-05-01 UTC: the bug-age section covers fixes merged May-October
want = sorted({p[:12] for r in rows if r["ct"] >= START for p in r["fixes"] if len(p) >= 12 and p[:12] not in have})
try:
    got = json.load(open(OUT))
except FileNotFoundError:
    got = {}
todo = [p for p in want if p not in got]
print(len(want), "targets outside the clone;", len(todo), "to fetch", file=sys.stderr)
for i in range(0, len(todo), 100):
    chunk = todo[i:i + 100]
    q = "{ repository(owner:\"torvalds\",name:\"linux\"){ " + " ".join(
        f'c{j}: object(expression:"{p}"){{ ... on Commit {{ oid authoredDate }} }}' for j, p in enumerate(chunk)) + " } }"
    for attempt in range(3):
        r = subprocess.run(["gh", "api", "graphql", "-f", f"query={q}"], capture_output=True, text=True)
        try:
            data = json.loads(r.stdout).get("data", {}).get("repository", {}) or {}
            break
        except (json.JSONDecodeError, AttributeError):
            data = None
    if data is None:
        print("chunk failed, left for a rerun:", i, r.stderr[:200], file=sys.stderr); continue
    for j, p in enumerate(chunk):
        o = data.get(f"c{j}")
        got[p] = [o["oid"], o["authoredDate"]] if o and o.get("oid") else None
    json.dump(got, open(OUT, "w"), indent=0)
    print(i + len(chunk), "/", len(todo), file=sys.stderr)
print(sum(1 for v in got.values() if v), "found,", sum(1 for v in got.values() if not v), "not found", file=sys.stderr)
