# The companies on TechCrunch's running list (25 Jul 2026) of 2026 tech layoffs where AI came up: which forms they
# file (8-K or foreign 6-K) and their Item 2.05 8-Ks of 2026. Input: the SEC's company_tickers.json.
# Output: $RAW/join_filers.json
#   python3 code/join_filers.py company_tickers.json
import json, os, sys, time, urllib.request

UA = "Konstantinos Gkolias research contact@emarkss.com"
RAW = os.environ.get("RAW", "raw")
LIST = "MNDY MSFT ORCL GTLB GOOGL INTU META CSCO NET GM COIN PYPL SNAP IBM TEAM DELL XYZ CRM AMZN".split()
tickers = {v["ticker"]: v["cik_str"] for v in json.load(open(sys.argv[1])).values()}
out = {}
for tk in LIST:
    c = tickers[tk]
    time.sleep(0.5)
    d = json.load(urllib.request.urlopen(urllib.request.Request(f"https://data.sec.gov/submissions/CIK{c:010d}.json", headers={"User-Agent": UA})))
    r = d["filings"]["recent"]
    forms = sorted({f for f in r["form"] if f in ("10-K", "20-F", "40-F", "6-K", "8-K")})
    hits = [(r["filingDate"][i], r["form"][i], r["accessionNumber"][i]) for i in range(len(r["form"]))
            if r["form"][i].startswith("8-K") and "2.05" in r["items"][i] and r["filingDate"][i] >= "2026-01-01"]
    out[tk] = {"cik": c, "name": d["name"], "forms": forms, "205_2026": hits}
    print(tk, forms, hits)
os.makedirs(RAW, exist_ok=True)
json.dump(out, open(os.path.join(RAW, "join_filers.json"), "w"), indent=1)
