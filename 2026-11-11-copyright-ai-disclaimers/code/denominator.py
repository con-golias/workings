# Total registrations per month and type of work, 2022-01 to 2026-10: the denominator for every share.
# A wildcard query with a registration-date range returns the catalogue's full histogram for that range.
#   python3 code/denominator.py   -> data/denominator.json
import json, os, time, urllib.parse, urllib.request
B = "https://api.publicrecords.copyright.gov/search_service_external/simple_search_dsl?"
out = {}
for y in range(2022, 2027):
    for m in range(1, 13):
        if (y, m) > (2026, 10):
            break
        import calendar
        end = f"{y}-{m:02d}-{calendar.monthrange(y, m)[1]:02d}"  # last day, 23:59:59: a record dated the 1st counts once
        q = {"query": "*", "field_type": "keyword", "records_per_page": 1, "page_number": 1,
             "date_field": "registration_date_as_date", "start_date": f"{y}-{m:02d}-01 00:00:00",
             "end_date": f"{end} 23:59:59"}
        for k in range(6):
            try:
                d = json.load(urllib.request.urlopen(urllib.request.Request(B + urllib.parse.urlencode(q), headers={"User-Agent": "curl/8.0"}), timeout=90))
                break
            except Exception:
                time.sleep(3 + 3 * k)
        h = d["metadata"]["histogram"]["filtered"]
        out[f"{y}-{m:02d}"] = {"total": h["type_of_record"].get("registration", 0), "type_of_work": h["type_of_work"]}
        print(y, m, out[f"{y}-{m:02d}"]["total"], flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "denominator.json"), "w"), indent=1)
