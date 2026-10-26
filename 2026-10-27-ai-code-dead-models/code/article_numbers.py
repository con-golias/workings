import json, collections, statistics as st, datetime as dt
from registry import classify
A = [r for r in json.load(open("oct26_analysis.json"))["repos"] if r["fresh"]]
oa = [r for r in A if classify(r["default"])["vendor"] == "openai"]
print("fresh", len(A), "openai", len(oa))
for d in ("2026-10-23", "2026-12-11", "2027-01-14", "2027-04-01"):
    k = sum((classify(r["default"])["shutdown"] or "9999") <= d for r in oa)
    print(f"  openai default shut down by {d}: {k} ({100*k/len(oa):.1f}%)")
st_ = collections.Counter(classify(r["default"])["status"] for r in oa); print("  status", st_)
c = collections.Counter(r["default"] for r in oa)
for m in ("gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-3.5-turbo", "gpt-4", "gpt-5", "gpt-5-mini", "gpt-6-luna", "gpt-6.1-sol", "gpt-6-astra", "gpt-6-sol"):
    print(f"  {m}: {c[m]} ({100*c[m]/len(oa):.1f}%) {classify(m)['status']} {classify(m)['shutdown']}")
g6 = sum(c[m] for m in c if m.startswith("gpt-6")); print("  any gpt-6*:", g6, f"{100*g6/len(oa):.1f}%")
# newest OpenAI model at the time vs default
day = lambda s: dt.date.fromisoformat(s[:10])
ages = [(day(r["created"]) - day(classify(r["default"])["released"])).days / 30.44 for r in oa if classify(r["default"])["released"] and classify(r["default"])["released"] <= r["created"]]
print("  openai median age", round(st.median(ages), 1), "share older than 12 months", round(100*sum(a > 12 for a in ages)/len(ages), 1))
for v in ("anthropic", "google"):
    vr = [r for r in A if classify(r["default"])["vendor"] == v]
    ages = [(day(r["created"]) - day(classify(r["default"])["released"])).days / 30.44 for r in vr if classify(r["default"])["released"] and classify(r["default"])["released"] <= r["created"]]
    print(v, len(vr), "median age", round(st.median(ages), 1), "older than 12 months", round(100*sum(a > 12 for a in ages)/len(ages), 1), "dead now", round(100*sum(classify(r["default"])["status"]=="retired" for r in vr)/len(vr),1))
# retired-at-creation defaults (born dead)
bd = [r for r in A if classify(r["default"], r["created"])["status"] == "retired"]
print("born dead (default already shut down on creation day):", len(bd), f"{100*len(bd)/len(A):.1f}%", collections.Counter(r["default"] for r in bd).most_common(8))
