"""Robustness of the bug-age result: without the busiest taggers; per-author medians; same authors' untagged fixes."""
import sys, json, statistics, collections
sys.argv = ["analysis.py", sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]]
src = open("analysis.py", encoding="utf-8").read().split("# age distribution buckets")[0]
exec(src)
med = lambda a: round(statistics.median(a), 2) if a else None
t = groups["tagged"]; o = groups["other"]
cnt = collections.Counter(r["ae"] for r in t)
top10 = {a for a, _ in cnt.most_common(10)}
res = {"tagged_all": med(ages(t)), "tagged_without_top10": med(ages([r for r in t if r["ae"] not in top10])),
       "other_all": med(ages(o))}
# authors who wrote both tagged and untagged fixes May-Oct: compare their own fixes
fa = collections.defaultdict(lambda: ([], []))
for r in t: fa[r["ae"]][0].append(r)
for r in o: fa[r["ae"]][1].append(r)
both = {a: v for a, v in fa.items() if v[0] and v[1]}
res["same_authors_n"] = len(both)
res["same_authors_tagged"] = med(ages([r for v in both.values() for r in v[0]]))
res["same_authors_untagged"] = med(ages([r for v in both.values() for r in v[1]]))
# median of per-author medians (each author counts once)
pa = [statistics.median(ages(v[0])) for v in fa.values() if v[0] and ages(v[0])]
res["per_author_median_tagged"] = med(pa)
pb = [statistics.median(ages(v[1])) for v in fa.values() if v[1] and ages(v[1])]
res["per_author_median_other"] = med(pb)
res["share_over_10y_without_top10"] = round(100 * sum(x > 10 for x in ages([r for r in t if r["ae"] not in top10])) / len(ages([r for r in t if r["ae"] not in top10])), 1)
print(json.dumps(res, indent=1))
json.dump(res, open(sys.argv[3] + "/bug_age_robust.json", "w"), indent=1)
