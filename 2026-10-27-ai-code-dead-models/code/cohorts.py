# Older cohorts: repositories created in a window and last pushed within 30 days of creation (code frozen near
# creation). Default model = most frequent ID in call-site files; age at creation by vendor.
import sys, json, collections, statistics as st, datetime as dt
from registry import classify
day = lambda s: dt.date.fromisoformat(s[:10])
rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
seen, out = set(), []
for r in sorted((r for r in rows if r.get("status") == "ok"), key=lambda r: r["created"]):
    calls = [f for f in r["files"] if f["call"] and len(f["ids"]) <= 8]
    cnt = collections.Counter()
    for f in calls: cnt.update(f.get("n") or {i: 1 for i in f["ids"]})
    if not cnt: continue
    fp = tuple(sorted(f["h"] for f in calls))
    if fp in seen: continue
    seen.add(fp); out.append((r["created"][:10], cnt.most_common(1)[0][0]))
print(sys.argv[1], "repos calling a model:", len(out))
for v in ("openai", "anthropic", "google"):
    xs = [(c, m) for c, m in out if classify(m)["vendor"] == v]
    ages = [(day(c) - day(classify(m)["released"])).days / 30.44 for c, m in xs if classify(m)["released"] and classify(m)["released"] <= c]
    dead = sum(classify(m, c)["status"] == "retired" for c, m in xs)
    if xs: print(f"  {v:9s} n={len(xs):4d} median age at creation {st.median(ages):4.1f} mo  dead on creation day {100*dead/len(xs):4.1f}%  top {collections.Counter(m for _, m in xs).most_common(3)}")
