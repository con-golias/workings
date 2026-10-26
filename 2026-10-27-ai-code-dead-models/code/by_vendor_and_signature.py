import json, statistics as st, datetime as dt, re, collections
from registry import classify
A = [r for r in json.load(open("oct26_analysis.json"))["repos"] if r["fresh"]]
day = lambda s: dt.date.fromisoformat(s[:10])
claude = lambda r: any(s.startswith("Claude") for s in r["agent_sigs"])
other_agent = lambda r: r["agent_sigs"] and not claude(r)
def row(rs):
    n = len(rs)
    if n < 5: return f"n={n}"
    dying = sum(classify(r["default"])["status"] in ("retired", "scheduled") for r in rs)
    dead = sum(classify(r["default"])["status"] == "retired" for r in rs)
    ages = sorted((day(r["created"]) - day(classify(r["default"])["released"])).days / 30.44 for r in rs if classify(r["default"])["released"])
    return f"n={n:4d}  dead {100*dead/n:5.1f}%  dead-or-dying {100*dying/n:5.1f}%  median age {st.median(ages):4.1f} mo"
for v in ("anthropic", "openai", "google"):
    vr = [r for r in A if classify(r["default"])["vendor"] == v]
    print(v); print("  Claude-signed     ", row([r for r in vr if claude(r)])); print("  no agent signature", row([r for r in vr if not r["agent_sigs"]]))
# Claude-signed: which signing model; do older Claude versions write older models?
print("\nClaude-signed repos, default vendor openai: top defaults", collections.Counter(r["default"] for r in A if claude(r) and classify(r["default"])["vendor"]=="openai").most_common(10))
print("Claude-signed repos, default vendor anthropic: top defaults", collections.Counter(r["default"] for r in A if claude(r) and classify(r["default"])["vendor"]=="anthropic").most_common(10))
print("Claude-signed repos, default vendor google: top defaults", collections.Counter(r["default"] for r in A if claude(r) and classify(r["default"])["vendor"]=="google").most_common(10))
