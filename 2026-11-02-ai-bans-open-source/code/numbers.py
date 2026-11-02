# Merges summary.json (analyze.py), placebo.json (placebo.py) and trailers.json (trailers.py) into numbers.json, with
# the derived values the text uses, so render.py resolves every {{token}} and check_numbers.py checks one file.
#   python numbers.py
import json, os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
S = json.load(open(os.path.join(D, "summary.json")))
P = json.load(open(os.path.join(D, "placebo.json")))
T = json.load(open(os.path.join(D, "trailers.json")))
ser = S["series"]
N = {"series": {p: {h: v["new"] for h, v in s.items()} for p, s in ser.items()}}
r2 = lambda x: round(x, 2)
for p, e in S["effects"].items():
    k = p.split("_")[0].lower()
    N[k] = {"ban": e["ban"], "own": r2(e["new"]["ratio"]), "compare": r2(e["new"]["compare_mean"]),
            "effect": r2(e["new"]["effect"]), "active_effect": r2(e["active"]["effect"]),
            "placebo": r2(P[p]["effect"]), "active_placebo": r2(P[p]["active"]["effect"]), "placebo_own": r2(P[p]["own"]), "placebo_compare": r2(P[p]["compare_mean"]),
            "before": e["before"], "after": e["after"]}
g = ser["gentoo_gentoo"]
# Gentoo without 2026-H1 (after it moved pull requests from GitHub to Codeberg, Feb 2026)
B, A = N["gentoo"]["before"], ["2024-H2", "2025-H1", "2025-H2"]
rat = lambda p: (sum(ser[p][h]["new"] for h in A) / len(A)) / (sum(ser[p][h]["new"] for h in B) / len(B))
cm = sum(rat(p) for p in ["NixOS_nixpkgs", "freebsd_freebsd-src", "torvalds_linux", "llvm_llvm-project"]) / 4
N["gentoo"]["effect_without_2026h1"] = r2(rat("gentoo_gentoo") / cm)
N["gentoo"]["new_2021_22"] = round(sum(g[h]["new"] for h in ["2021-H1", "2021-H2", "2022-H1"]) / 3)
N["gentoo"]["new_2023_25"] = round(sum(g[h]["new"] for h in ["2023-H1", "2023-H2", "2024-H1", "2024-H2", "2025-H1", "2025-H2"]) / 6)
q = ser["qemu_qemu"]
N["qemu"]["new_2026h1"] = q["2026-H1"]["new"]
N["qemu"]["max_before_2026"] = max(q[h]["new"] for h in q if h < "2026")
nb = ser["NetBSD_src"]
N["netbsd"]["min_new"] = min(nb[h]["new"] for h in nb); N["netbsd"]["max_new"] = max(nb[h]["new"] for h in nb)
lx = ser["torvalds_linux"]
N["linux"] = {"new_2026h1": lx["2026-H1"]["new"], "new_2026h2_partial": lx["2026-H2"]["new"],
              "min_2023_25": min(lx[h]["new"] for h in lx if "2023" <= h[:4] <= "2025"),
              "max_2023_25": max(lx[h]["new"] for h in lx if "2023" <= h[:4] <= "2025")}
lv = ser["llvm_llvm-project"]
N["llvm"] = {"new_2026h1": lv["2026-H1"]["new"]}
nx = ser["NixOS_nixpkgs"]
N["nixpkgs"] = {"new_2026h1": nx["2026-H1"]["new"]}
for repo, k in [("torvalds_linux", "linux"), ("llvm_llvm-project", "llvm"), ("NixOS_nixpkgs", "nixpkgs")]:
    a = T["allow"][repo]; N[k].update({"new_2026": a["new_2026"], "tagged_2026": a["tagged"], "tagged_pct": a["pct"]})
tot_new = sum(T["allow"][r]["new_2026"] for r in T["allow"]); tot_tag = sum(T["allow"][r]["tagged"] for r in T["allow"])
N["allow_total"] = {"new_2026": tot_new, "tagged": tot_tag, "pct": round(100 * tot_tag / tot_new, 1)}
for repo, k in [("qemu_qemu", "qemu"), ("NetBSD_src", "netbsd"), ("gcc-mirror_gcc", "gcc"), ("gentoo_gentoo", "gentoo")]:
    b = T["banned"][repo]
    N.setdefault(k, {}).update({"commits_after": b["commits_after"], "ai_commits": b["ai_commits"],
                                "ai_authors": len(b["authors"]), "ai_pct": round(100 * b["ai_commits"] / b["commits_after"], 1)})
N["gcc"]["ban"] = "2026-07-29"
# commits since 2018 per project: from the .log files if their folder is given (python numbers.py <logdir>)
import sys
if len(sys.argv) > 1:
    names = {"gentoo": "gentoo_gentoo", "nixpkgs": "NixOS_nixpkgs", "linux": "torvalds_linux", "llvm": "llvm_llvm-project",
             "qemu": "qemu_qemu", "freebsd": "freebsd_freebsd-src", "netbsd": "NetBSD_src", "gcc": "gcc-mirror_gcc"}
    N["commits"] = {k: sum(1 for _ in open(os.path.join(sys.argv[1], v + ".log"), encoding="utf-8", errors="replace")) for k, v in names.items()}
    json.dump(N["commits"], open(os.path.join(D, "commits.json"), "w"))
else:
    N["commits"] = json.load(open(os.path.join(D, "commits.json")))
json.dump(N, open(os.path.join(D, "numbers.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in N.items() if k != "series"}, indent=1))
