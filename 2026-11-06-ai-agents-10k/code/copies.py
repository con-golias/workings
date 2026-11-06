"""Find agent sentences that appear, near-verbatim, in the filings of two or more different companies.
Method: normalise words, take 8-word shingles, link two sentences from different CIKs when their shingle Jaccard >= 0.5
and both have >= 15 words; group links with union-find. Output ../data/copy_clusters.json, earliest filer first."""
import json, re, collections, itertools
R = [json.loads(l) for l in open("../data/sentences.jsonl")]
def words(s): return re.findall(r"[a-z0-9]+", s.lower().replace("artificial intelligence", "ai"))
def sh(w, k=8): return {" ".join(w[i:i+k]) for i in range(len(w) - k + 1)}
uniq = {}
for r in R:
    w = words(r["s"])
    if len(w) < 15: continue
    key = (r["cik"], " ".join(w))
    if key not in uniq: uniq[key] = dict(r, w=w, sh=sh(w), dates=[r["date"]])
    else: uniq[key]["dates"].append(r["date"])
items = list(uniq.values())
inv = collections.defaultdict(list)
for i, it in enumerate(items):
    for g in it["sh"]: inv[g].append(i)
par = list(range(len(items)))
def f(x):
    while par[x] != x: par[x] = par[par[x]]; x = par[x]
    return x
cand = collections.Counter()
for g, ids in inv.items():
    if len(ids) > 200: continue
    for a, b in itertools.combinations(ids, 2):
        if items[a]["cik"] != items[b]["cik"]: cand[(a, b)] += 1
for (a, b), c in cand.items():
    A, B = items[a]["sh"], items[b]["sh"]
    if len(A & B) / len(A | B) >= 0.5: par[f(a)] = f(b)
cl = collections.defaultdict(list)
for i in range(len(items)): cl[f(i)].append(i)
out = []
for ids in cl.values():
    ciks = {items[i]["cik"] for i in ids}
    if len(ciks) < 2: continue
    mem = sorted(({"name": items[i]["name"], "cik": items[i]["cik"], "first": min(items[i]["dates"]), "form": items[i]["form"],
                   "adsh": items[i]["adsh"], "file": items[i]["file"], "s": items[i]["s"]} for i in ids), key=lambda m: m["first"])
    first = {}
    for m in mem: first.setdefault(m["cik"], m)
    out.append({"companies": len(ciks), "members": list(first.values())})
out.sort(key=lambda c: -c["companies"])
json.dump(out, open("../data/copy_clusters.json", "w"), indent=1)
print(len(out), "clusters;", sum(c["companies"] for c in out), "company-sentences")
for c in out[:25]:
    m = c["members"]
    print("\n##", c["companies"], "companies | first:", m[0]["name"][:30], m[0]["first"], "| then:", ", ".join(x["name"].split("(")[0].strip()[:20] + " " + x["first"] for x in m[1:6]))
    print("   ", m[0]["s"][:300])
