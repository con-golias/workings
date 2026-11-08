"""One row per vehicle (CIK) whose EDGAR name names OpenAI, Anthropic or xAI, from its latest Form D / D/A.
Excluded by reading: 'Anthropic Capital Fund, LP' (a 2021 hedge fund, unrelated to the company) and 'OpenAI Startup Fund
SPV IV, L.P.' (OpenAI's own fund, invests in other startups). Output ../data/vehicles.json."""
import json, re, collections
F = json.load(open("../data/filings.json"))
EXCL = {"Anthropic Capital Fund, LP", "OpenAI Startup Fund SPV IV, L.P."}
PAT = {"OpenAI": re.compile(r"\bopenai\b", re.I), "Anthropic": re.compile(r"\banthropic\b", re.I), "xAI": re.compile(r"\bxai\b", re.I)}
def host(name):
    m = re.search(r"(?:a\s+)?series\s+of\s+(.+)$", name, re.I)
    if m: return m.group(1).strip(" ,.")
    m = re.match(r"(.+?)(?:,|\s+-)\s+(?:series\b|anthropic|openai|xai)", name, re.I)
    return m.group(1).strip() if m else None
by = collections.defaultdict(list)
for r in F: by[r["cik"]].append(r)
V = []
for cik, rs in by.items():
    rs.sort(key=lambda r: (r["file_date"], r["adsh"]))
    last, first = rs[-1], rs[0]
    name = last["entity"] or last["name"]
    if name in EXCL: continue
    tg = [t for t, p in PAT.items() if p.search(name)]
    if not tg: continue
    V.append({"cik": cik, "name": name, "targets": tg, "host": host(name), "filings": len(rs), "first_filed": first["file_date"], "last_filed": last["file_date"],
              "first_sale": last["first_sale"], "amount_sold": last["amount_sold"], "offering_amount": last["offering_amount"], "investors": last["investors"],
              "min_investment": last["min_investment"], "sales_commissions": last["sales_commissions"], "finders_fees": last["finders_fees"],
              "fees_clarification": last["fees_clarification"], "non_accredited": last["non_accredited"], "exemptions": last["exemptions"],
              "fund_type": last["fund_type"], "jurisdiction": last["jurisdiction"], "sales_compensation": last["sales_compensation"], "related": last["related"],
              "adsh": last["adsh"]})
json.dump(V, open("../data/vehicles.json", "w"), indent=1)
for t in PAT:
    S = [v for v in V if t in v["targets"]]
    sold = sum(v["amount_sold"] or 0 for v in S); inv = sum(v["investors"] or 0 for v in S)
    mins = sorted(v["min_investment"] for v in S if v["min_investment"] is not None)
    print(f"{t}: {len(S)} vehicles, ${sold/1e6:,.1f}M sold, {inv:,.0f} investors, median min ${mins[len(mins)//2] if mins else None:,.0f}, min of mins {mins[0] if mins else None}")
    print("   first filed by year:", dict(sorted(collections.Counter(v['first_filed'][:4] for v in S).items())), "| 2026:", sum(v['first_filed']>='2026' for v in S))
    print("   hosts:", collections.Counter(v['host'] for v in S).most_common(5))
    fees=[v for v in S if (v['sales_commissions'] or 0)>0 or (v['finders_fees'] or 0)>0]
    print("   with commissions/fees reported:", len(fees), "sum $", sum((v['sales_commissions'] or 0)+(v['finders_fees'] or 0) for v in fees))
