# Collects every 8-K (the "8-K" form filter also returns 8-K/A; "8-K,8-K/A" returns only amendments) that may carry an Item 2.05 (exit or disposal costs), 1 Jan 2022 - 28 Oct 2026,
# from EDGAR full-text search. Metadata only; no text is read here.
# Output: $RAW/fts_hits.json (all hits, grouped by accession)
import json, os, sys, time, urllib.parse, urllib.request

UA = "Konstantinos Gkolias research contact@emarkss.com"
RAW = os.environ.get("RAW", "raw")
QUERIES = ['"Exit or Disposal"', '"Item 2.05"', '"Costs Associated with Exit"']
# Monthly windows keep every query far below the 10,000-hit cap of the search API.
WINDOWS = [(f"{y}-{m:02d}-01", f"{y + (m == 12)}-{(m % 12) + 1:02d}-01") for y in range(2022, 2027) for m in range(1, 13)]
WINDOWS = [(a, b) for a, b in WINDOWS if a <= "2026-10-28"]


def get(params):
    url = "https://efts.sec.gov/LATEST/search-index?" + urllib.parse.urlencode(params)
    for attempt in range(6):
        time.sleep(0.35 + 4 * attempt)
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60))
        except Exception as e:
            err = e
    raise err


filings = {}
for start, end in WINDOWS:
    # enddt is inclusive in the API, so stop the day before the next window (and at 28 Oct 2026).
    stop = min(end, "2026-10-29")
    stop_day = time.strftime("%Y-%m-%d", time.gmtime(time.mktime(time.strptime(stop, "%Y-%m-%d")) - 43200))
    for q in QUERIES:
        frm = 0
        while True:
            d = get({"q": q, "forms": "8-K", "dateRange": "custom", "startdt": start, "enddt": stop_day, "from": frm})
            hits = d["hits"]["hits"]
            for h in hits:
                s = h["_source"]
                adsh, fn = h["_id"].split(":", 1)
                f = filings.setdefault(adsh, {"adsh": adsh, "cik": s["ciks"][0], "name": s["display_names"][0],
                                              "sics": s.get("sics"), "form": s.get("form"), "file_date": s["file_date"],
                                              "items": s.get("items") or [], "docs": {}, "queries": []})
                f["docs"][fn] = s.get("file_type")
                if q not in f["queries"]:
                    f["queries"].append(q)
            total = d["hits"]["total"]["value"]
            frm += len(hits)
            if not hits or frm >= total:
                break
    print(start, len(filings), file=sys.stderr, flush=True)

os.makedirs(RAW, exist_ok=True)
json.dump({"pulled": time.strftime("%Y-%m-%d"), "filings": list(filings.values())}, open(os.path.join(RAW, "fts_hits.json"), "w"), indent=0)
print("filings", len(filings), "tagged 2.05", sum("2.05" in f["items"] for f in filings.values()))
