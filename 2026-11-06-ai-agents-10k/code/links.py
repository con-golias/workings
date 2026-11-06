"""EDGAR URL of the first qualifying report for each verified company (and the sellers' annual reports)."""
import json
H = [json.loads(l) for l in open("../data/hits.jsonl", encoding="utf8")]
E = json.load(open("../data/rogue_efts.json", encoding="utf8"))
V = json.load(open("../data/rogue_verified.json", encoding="utf8"))["verified"]
def url(cik, _id):
    adsh, fn = _id.split(":", 1)
    return "https://www.sec.gov/Archives/edgar/data/%d/%s/%s" % (int(cik), adsh.replace("-", ""), fn)
idx = [(h["display_names"][0], h["file_date"], h["ciks"][0], h["id"], h["form"]) for h in H] + [(e["name"], e["date"], e["cik"], e["id"], e["form"]) for e in E]
out = {}
for o in V:
    m = next(x for x in idx if x[0] == o["edgar_name"] and x[1] == o["first_date"])
    out[o["group"]] = {"date": o["first_date"], "form": m[4], "url": url(m[2], m[3])}
for g, pat in [("Salesforce", "Salesforce"), ("ServiceNow", "ServiceNow"), ("UiPath", "UiPath"), ("Workday", "Workday")]:
    m = sorted([x for x in idx if pat in x[0] and x[4] == "10-K"], key=lambda x: x[1])[-1]
    out[g + " (annual)"] = {"date": m[1], "form": m[4], "url": url(m[2], m[3])}
json.dump(out, open("../data/links.json", "w"), indent=1)
for k, v in out.items(): print(k, v["date"], v["form"], v["url"])
