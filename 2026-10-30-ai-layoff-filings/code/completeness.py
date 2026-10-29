# Completeness check: for a random sample of listed companies, EDGAR's own list of their Item 2.05 8-Ks
# (submissions JSON) against the filings found by full-text search. Output: $RAW/completeness.json
import json, os, random, sys, time, urllib.request

UA = "Konstantinos Gkolias research contact@emarkss.com"
RAW = os.environ.get("RAW", "raw")
ours = {f["adsh"] for f in json.load(open(os.path.join(RAW, "fts_hits.json")))["filings"]}
tickers = json.load(open(sys.argv[1]))  # SEC company_tickers.json
ciks = sorted({v["cik_str"] for v in tickers.values()})
random.seed(20261029)
sample = random.sample(ciks, int(sys.argv[2]) if len(sys.argv) > 2 else 600)
truth, found = [], 0
for c in sample:
    time.sleep(0.34)
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(f"https://data.sec.gov/submissions/CIK{c:010d}.json", headers={"User-Agent": UA}), timeout=60))
    except Exception:
        continue
    r = d["filings"]["recent"]
    for i in range(len(r["form"])):
        if r["form"][i] in ("8-K", "8-K/A") and "2.05" in r["items"][i] and "2022-01-01" <= r["filingDate"][i] <= "2026-10-28":
            hit = r["accessionNumber"][i] in ours
            found += hit
            truth.append({"cik": c, "name": d["name"], "adsh": r["accessionNumber"][i], "date": r["filingDate"][i], "found": hit})
json.dump({"sample_companies": len(sample), "filings": len(truth), "found": found, "missed": [t for t in truth if not t["found"]]},
          open(os.path.join(RAW, "completeness.json"), "w"), indent=1)
print("sample", len(sample), "2.05 filings", len(truth), "found", found)
