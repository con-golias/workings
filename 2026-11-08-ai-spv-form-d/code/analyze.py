"""Every number for #16: ../data/summary.json.
Notices: Anthropic support article 'Unauthorized Anthropic stock sales and investment scams', published 11 Feb 2026; its
SPV sentence is in the earliest archived copy (Wayback 20260214003653). OpenAI 'Unauthorized OpenAI Equity Transactions',
published 16 Jul 2025; SPV language in the earliest archived copy (Wayback 20250717182032)."""
import json, collections, statistics as st
V = json.load(open("../data/vehicles.json"))
NOTICE = {"Anthropic": "2026-02-11", "OpenAI": "2025-07-16"}
MON = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
def agg(X):
    return {"vehicles": len(X), "raised": sum(v["amount_sold"] or 0 for v in X), "entries": int(sum(v["investors"] or 0 for v in X))}
S = {"labs": {}}
for t in ["Anthropic", "OpenAI", "xAI"]:
    X = [v for v in V if t in v["targets"]]
    d = agg(X)
    d["raised_m"] = round(d["raised"] / 1e6, 1)
    mins = [v["min_investment"] for v in X if v["min_investment"]]
    d.update(min_stated=len(mins), min_median=st.median(mins) if mins else None, min_lowest=min(mins) if mins else None,
             size_median_m=round(st.median([v["amount_sold"] for v in X if v["amount_sold"]]) / 1e6, 2),
             size_max_m=round(max(v["amount_sold"] or 0 for v in X) / 1e6, 1),
             c506=sum("06c" in v["exemptions"] for v in X), b506=sum("06b" in v["exemptions"] for v in X),
             hosts=collections.Counter(v["host"] or "(own LLC)" for v in X).most_common(6),
             first_sale_by_month=dict(sorted(collections.Counter((v["first_sale"] or "none")[:7] for v in X).items())),
             fees_n=sum(1 for v in X if (v["sales_commissions"] or 0) + (v["finders_fees"] or 0) > 0),
             fees_sum=sum((v["sales_commissions"] or 0) + (v["finders_fees"] or 0) for v in X))
    if t in NOTICE:
        n = NOTICE[t]
        a = agg([v for v in X if (v["first_sale"] or "") > n]); a["raised_m"] = round(a["raised"] / 1e6, 1)
        b = agg([v for v in X if v["first_filed"] > n]); b["raised_m"] = round(b["raised"] / 1e6, 1)
        d.update(notice=n, notice_text="%d %s %s" % (int(n[8:]), MON[int(n[5:7]) - 1], n[:4]), after_first_sale=a, after_first_filed=b,
                 no_first_sale=sum(1 for v in X if not v["first_sale"]))
    if t == "xAI":
        nb = [v for v in X if v["name"].startswith("NB Ventures")]
        d["nb"] = agg(nb); d["nb"]["raised_m"] = round(d["nb"]["raised"] / 1e6, 1)
        rest = [v for v in X if not v["name"].startswith("NB Ventures")]
        d["rest"] = agg(rest); d["rest"]["raised_m"] = round(d["rest"]["raised"] / 1e6, 1)
    S["labs"][t] = d
A = [v for v in V if "Anthropic" in v["targets"]]
S["labs"]["Anthropic"]["avg_entry"] = int(round(S["labs"]["Anthropic"]["raised"] / S["labs"]["Anthropic"]["entries"], -3))
S["anthropic_sydecar"] = sum(1 for v in A if v["host"] == "CGF2021 LLC")
S["anthropic_sydecar_after"] = sum(1 for v in A if v["host"] == "CGF2021 LLC" and (v["first_sale"] or "") > NOTICE["Anthropic"])
S["anthropic_after_may12_filed"] = sum(1 for v in A if v["first_filed"] >= "2026-05-12")
S["total"] = agg([v for v in V if set(v["targets"]) & {"Anthropic", "OpenAI"}]); S["total"]["raised_m"] = round(S["total"]["raised"] / 1e6, 1)
json.dump(S, open("../data/summary.json", "w"), indent=1)
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("first_sale_by_month",)} for k, v in S["labs"].items()}, indent=1)[:3500])
print({k: S[k] for k in S if k != "labs"})
