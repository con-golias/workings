# Per-repository results behind the article: data/repos.csv (one row per repository in every group, before the
# one-per-account step): group, repo, created, last change (dependency/deploy bots removed), commits, days from
# creation to last change, deployed URL, HTTP status on 28 Oct 2026.
#   python3 code/export_lists.py <raw dir>
import csv
import os
import sys

RAW = sys.argv[1] if len(sys.argv) > 1 else "raw"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [sys.argv[0], RAW]
src = open(os.path.join(HERE, "analyze.py"), encoding="utf-8").read().split('S = {"read_on"')[0]
exec(src)
with open(os.path.join(HERE, "..", "data", "repos.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["group", "repo", "created", "last_change", "commits", "days_to_last_change", "url", "http_status"])
    for g, rows in groups().items():
        if g == "baseline_react":
            continue
        for r, a in rows:
            lh = last_human(a)
            o = online.get(r) or {}
            w.writerow([g, r, a["created"], lh.isoformat() if lh else "", a["total"],
                        (lh - P(a["created"])).days if lh else "", o.get("url", ""), o.get("status", "")])
print("written")
