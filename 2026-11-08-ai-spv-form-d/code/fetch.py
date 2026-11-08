"""Form D / D/A filings whose text names an AI lab (EDGAR full-text search), then each filing's primary_doc.xml.
Outputs ../data/hits.jsonl and ../data/xml/<adsh>.xml (local cache, not in workings)."""
import json, os, sys
from sec import efts, get
T = ["OpenAI", "Anthropic", "xAI", "SpaceX", "Perplexity", "Mistral", "Anysphere", "Databricks", "Scale AI", "Safe Superintelligence", "Thinking Machines", "Cursor"]
os.makedirs("../data/xml", exist_ok=True)
rows = {}
for t in T:
    for form in ("D", "D/A"):
        frm = 0
        while True:
            d = efts('"%s"' % t, form, "2019-01-01", "2026-11-06", frm); h = d["hits"]["hits"]
            for x in h:
                s = x["_source"]; adsh = x["_id"].split(":")[0]
                r = rows.setdefault(adsh, {"adsh": adsh, "form": s["form"], "file_date": s["file_date"], "cik": s["ciks"][0], "name": s["display_names"][0], "terms": []})
                if t not in r["terms"]: r["terms"].append(t)
            frm += len(h)
            if not h or frm >= d["hits"]["total"]["value"]: break
    print(t, sum(1 for r in rows.values() if t in r["terms"]), file=sys.stderr)
with open("../data/hits.jsonl", "w") as f:
    for r in rows.values(): f.write(json.dumps(r) + "\n")
n = 0
for r in rows.values():
    p = "../data/xml/%s.xml" % r["adsh"]
    if os.path.exists(p): continue
    url = "https://www.sec.gov/Archives/edgar/data/%d/%s/primary_doc.xml" % (int(r["cik"]), r["adsh"].replace("-", ""))
    try: open(p, "wb").write(get(url, raw=True)); n += 1
    except Exception as e: print("ERR", r["adsh"], e, file=sys.stderr)
print(len(rows), "filings;", n, "xml fetched", file=sys.stderr)
