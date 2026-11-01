"""Where the AI-assisted fixes are, and what kind of bug their titles name. Fixes committed May-October 2026.
  python subsystems.py commits.json ../data/subsystems.json
Subsystem = the commit title's prefix up to the first colon. Bug kind = a keyword in the commit title (crude: a title
names the bug only sometimes)."""
import collections, datetime as dt, json, re, sys

rows = json.load(open(sys.argv[1]))
START = int(dt.datetime(2026, 5, 1, tzinfo=dt.timezone.utc).timestamp())
fx = [r for r in rows if r["fixes"] and r["ct"] >= START]
sub = lambda r: r["s"].split(":")[0].strip().lower() if ":" in r["s"] else "(none)"

per = collections.defaultdict(lambda: {"fixes": 0, "tagged": 0, "authors": collections.Counter()})
for r in fx:
    p = per[sub(r)]; p["fixes"] += 1
    if r["ab"]: p["tagged"] += 1; p["authors"][r["an"]] += 1
big = [(k, v) for k, v in per.items() if v["fixes"] >= 80]
rank = sorted(big, key=lambda kv: -kv[1]["tagged"] / kv[1]["fixes"])
row = lambda k, v: {"subsystem": k, "fixes": v["fixes"], "tagged": v["tagged"], "pct": round(100 * v["tagged"] / v["fixes"], 1),
                    "tagging_authors": len(v["authors"]),
                    "top_author": v["authors"].most_common(1)[0][0] if v["authors"] else None,
                    "top_author_tagged": v["authors"].most_common(1)[0][1] if v["authors"] else 0}
out = {"subsystems_with_80_fixes": len(big), "top": [row(k, v) for k, v in rank[:12]], "bottom": [row(k, v) for k, v in rank[-6:]]}

KINDS = [("Use-after-free", r"use[- ]after[- ]free|\buaf\b"), ("NULL dereference", r"\bnull\b"), ("Memory leak", r"\bleaks?\b"),
         ("Race or locking", r"\brace\b|deadlock|\block(ing|s)?\b|\bmutex|spinlock|\brcu\b"),
         ("Out of bounds or overflow", r"overflow|out[- ]of[- ]bounds|\boob\b|bounds|underflow")]
G = {"tagged": [r for r in fx if r["ab"]], "sashiko": [r for r in fx if r["sashiko"] and not r["ab"]],
     "other": [r for r in fx if not r["ab"] and not r["sashiko"]]}
out["kinds"] = {name: {g: round(100 * sum(1 for r in rs if re.search(rx, r["s"], re.I)) / len(rs), 1) for g, rs in G.items()}
                for name, rx in KINDS}
out["kinds_n"] = {g: len(rs) for g, rs in G.items()}
json.dump(out, open(sys.argv[2], "w"), indent=1)
print(json.dumps(out, indent=1)[:2500])
