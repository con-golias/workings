"""Every number the article and figures use: ../data/summary.json."""
import json
IS = json.load(open("../data/install_scripts.json")); SC = json.load(open("../data/scan.json"))
V = json.load(open("../data/verdicts.json", encoding="utf8"))["read"]; D = json.load(open("../data/downloads.json"))
PV = json.load(open("../data/postman_cli_versions.json"))
A = [n for n in IS if any(s.startswith("A:") for s in IS[n]["sets"])]; B = [n for n in IS if "B:high-impact" in IS[n]["sets"] and n not in A]
flag = lambda n: n in SC and (SC[n].get("hits") or SC[n].get("cmd_hit"))
S = {"A": {"n": len(A), "install": sum(1 for n in A if IS[n].get("install")), "flagged": sum(1 for n in A if flag(n))},
     "B": {"n": len(B), "reachable": sum(1 for n in B if not IS[n].get("missing")), "install": sum(1 for n in B if IS[n].get("install")), "flagged": sum(1 for n in B if flag(n)), "writers": 0}}
fl = [n for n in A if flag(n)]
S["A"]["flagged_downloads"] = sum(D.get(n) or 0 for n in fl)
S["read"] = {"n": len(V), "downloads": sum(v["downloads"] or 0 for v in V)}
S["read"]["share_of_flagged_downloads"] = round(100 * S["read"]["downloads"] / S["A"]["flagged_downloads"])
S["unread"] = {"n": len(fl) - len(V), "max_downloads": max((D.get(n) or 0) for n in fl if n not in {v["name"] for v in V})}
G = [v for v in V if v["scope"] == "global"]
dl = lambda X: sum(v["downloads"] or 0 for v in X)
S["global"] = {"n": len(G), "downloads": dl(G), "as_dependency": sum(not v["global_only"] for v in G), "as_dependency_downloads": dl([v for v in G if not v["global_only"]]),
               "no_optout": sum(not v["optout"] for v in G), "optout": sum(bool(v["optout"]) for v in G), "grant": sum(bool(v.get("grant")) for v in G),
               "what": {k: sum(k in v["what"] for v in G) for k in ["files", "settings", "mcp", "hooks", "instructions"]},
               "what_downloads": {k: dl([v for v in G if k in v["what"]]) for k in ["files", "settings", "mcp", "hooks", "instructions"]},
               "products": [v["name"] for v in G if v.get("product")], "top": max(G, key=lambda v: v["downloads"] or 0)["name"],
               "top_downloads": max(v["downloads"] or 0 for v in G)}
S["project"] = sum(v["scope"] == "project" for v in V); S["none"] = sum(v["scope"] == "none" for v in V); S["unclear"] = sum(v["scope"] == "unclear" for v in V)
byname = {v["name"]: v for v in V}
S["pkg"] = {k.replace("@", "").replace("/", "_").replace("-", "_"): byname[k]["downloads"] for k in ["postman-cli", "toga-ai", "claude-all-config", "karajan-code", "whatshell", "triflux", "@polymorphism-tech/morph-spec"]}
app = sorted([(v, d) for v, d in PV.items() if d["appends_instruction"]], key=lambda x: x[1]["time"])
S["postman"] = {"first": app[0][0], "first_date": app[0][1]["time"][:10], "versions": len(app), "latest": app[-1][0], "latest_date": app[-1][1]["time"][:10]}
S["node"] = {"v22": "10.9.9", "v24": "11.19.1", "v26": "11.20.0", "v27_alpha": "12.1.0", "npm12_date": "2026-07-08", "npm12_date_text": "8 July 2026", "npm12_latest": "12.2.2"}
import datetime
fmt = lambda d: datetime.date.fromisoformat(d).strftime("%-d %B %Y") if False else "%d %s %s" % (int(d[8:10]), ["January","February","March","April","May","June","July","August","September","October","November","December"][int(d[5:7])-1], d[:4])
S["postman"]["first_date_text"] = fmt(S["postman"]["first_date"]); S["postman"]["latest_date_text"] = fmt(S["postman"]["latest_date"])
json.dump(S, open("../data/summary.json", "w"), indent=1)
print(json.dumps(S, indent=1))
