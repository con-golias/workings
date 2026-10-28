# Writes the per-repository lists behind the article: data/repos_2024.csv and data/repos_2026.csv
# (repository, created, group, trace kinds, dependency count, the packages of the article's categories it lists).
#   python3 code/export_lists.py <raw dir>
import csv
import json
import os
import sys

RAW = sys.argv[1] if len(sys.argv) > 1 else "raw"
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "categories.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "tags.py"), encoding="utf-8").read())
PK = sorted({p for v in CATS.values() for p in v})
load = lambda n: json.load(open(os.path.join(RAW, n), encoding="utf-8"))
out = os.path.join(HERE, "..", "data")

m24 = load("ctl24_meta.json")
with open(os.path.join(out, "repos_2024.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["repo", "created", "package_json_as_of", "n_deps", "category_packages"])
    for r, d, v in usable(m24, since="2024-10-01"):
        if v["created"] < "2024-11-01":
            w.writerow([r, v["created"], v.get("asof"), len(d), " ".join(p for p in PK if p in d)])

for name, meta, hist in (("repos_2026.csv", "ctlbm_meta.json", "ctlbm_hist.json"), ("repos_2026_recently_updated.csv", "ctl_meta.json", "ctl_hist.json")):
    m, h = load(meta), load(hist)
    with open(os.path.join(out, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["repo", "created", "group", "traces", "n_deps", "category_packages"])
        for r, d, v in usable(m):
            x = h.get(r) or {}
            kinds = (["trailer:" + k for k in ("claude", "cursor", "codex") if x.get(k)] + ["file:" + k for k in sorted(markers(v))]
                     + ["builder:" + k for k in sorted(builder(r, d, v, x.get("readme")))])
            w.writerow([r, v["created"], "traced" if kinds else "untraced", " ".join(kinds), len(d), " ".join(p for p in PK if p in d)])
print("written")
