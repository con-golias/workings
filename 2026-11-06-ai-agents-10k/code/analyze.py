"""Every number the article and the figures use, in one file: ../data/summary.json."""
import json, re, gzip, collections
R = [json.loads(l) for l in open("../data/sentences.jsonl", encoding="utf8")]
H = [json.loads(l) for l in open("../data/hits.jsonl", encoding="utf8")]
D = json.load(open("../data/denominators.json"))
V = json.load(open("../data/rogue_verified.json", encoding="utf8"))["verified"]
L = json.load(open("../data/copy_links.json", encoding="utf8"))
T = json.load(open("../data/themes.json", encoding="utf8"))
S = {}
S["corpus"] = {"files": len(H), "filings": len({h["adsh"] for h in H}), "sentences": len(R), "companies": len({r["cik"] for r in R}),
               "first_day": min(r["date"] for r in R), "last_day": max(r["date"] for r in R)}
yr = collections.defaultdict(set); q = collections.defaultdict(set)
for r in R:
    yr[r["date"][:4]].add(r["cik"]); q["%sQ%d" % (r["date"][:4], (int(r["date"][5:7]) - 1) // 3 + 1)].add(r["cik"])
S["companies_by_year"] = {k: len(v) for k, v in sorted(yr.items())}
S["filers_by_year"] = {k: D[k]["periodic_filers"] for k in D}
qs = []
for y in D:
    for k, n in D[y]["by_quarter"].items():
        qs.append({"q": k, "companies": len(q.get(k, ())), "filers": n, "pct": round(100 * len(q.get(k, ())) / n, 2)})
S["quarters"] = qs
S["share_2026"] = round(100 * len(yr["2026"]) / D["2026"]["periodic_filers"], 1)
S["share_2024"] = round(100 * len(yr["2024"]) / D["2024"]["periodic_filers"], 2)
# the verified set
V = sorted(V, key=lambda o: o["first_date"])
S["warn"] = {"n": len(V), "first": V[0]["group"], "first_date": V[0]["first_date"],
             "by_2025_end": sum(o["first_date"] <= "2025-12-31" for o in V),
             "by_half": {h: sum(1 for o in V if (o["first_date"][:4] + ("H1" if o["first_date"][5:7] <= "06" else "H2")) == h) for h in ("2025H2", "2026H1", "2026H2")},
             "since_oct1": sum(o["first_date"] >= "2026-10-01" for o in V),
             "list": [{"group": o["group"], "date": o["first_date"], "form": o["form"]} for o in V]}
S["warn"]["first_date_text"] = "4 November 2025"
S["warn"]["pct_of_agent_companies"] = round(100 * len(V) / S["corpus"]["companies"], 1)
cum, c = [], 0
for o in V: c += 1; cum.append({"date": o["first_date"], "n": c, "group": o["group"]})
S["warn"]["cumulative"] = cum
S["copies"] = {"n": len(L), "pct": round(100 * len(L) / len(V)), "pairs": L,
               "verbatim_25plus": sum(1 for p in L if p["longest_identical_words"] >= 25)}
S["phrase_uuas"] = {"phrase": "unintended or unauthorized actions", "first": "GoDaddy", "first_date": "2026-02-25", "companies": 12,
                    "names": ["GoDaddy", "Wix", "Fiverr", "Roblox", "Twilio", "Bandwidth", "Marvell", "Samsara", "Microsoft", "Apple", "Palantir", "Arista"]}
S["themes"] = {k: len(v) for k, v in T["themes"].items()}; S["themes_base"] = T["n_risk"]
SL = json.load(open("../data/sellers.json", encoding="utf8"))
S["sellers"] = {r["group"]: r.get("agent_sentences") for r in SL}
LK = json.load(open("../data/links.json", encoding="utf8"))
S["links"] = {re.sub(r"[^A-Za-z0-9]+", "_", k).strip("_"): v["url"] for k, v in LK.items()}
json.dump(S, open("../data/summary.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)
print(json.dumps({k: S[k] for k in ("corpus", "companies_by_year", "share_2026", "share_2024")}, indent=0))
print(json.dumps({k: v for k, v in S["warn"].items() if k not in ("list", "cumulative")}))
print(S["copies"]["n"], S["copies"]["pct"], S["copies"]["verbatim_25plus"]); print(S["themes"], S["themes_base"])
print([x for x in qs if x["q"] >= "2024Q1"])
