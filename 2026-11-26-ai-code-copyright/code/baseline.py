# Baseline for the "C.O. correspondence" note: a random sample of ALL Computer Files registrations, 2025-01 to 2026-03.
# For each month: the count of Computer Files registrations, then 4 random pages of 10 (pages drawn in a fixed order
# from a fixed seed, before any parallel step, so the sample can be reproduced). Then the full record of each, since the
# note is only there. Writes data/baseline.json (per record: id, organisation or person, note, has an excluded statement).
#   python code/baseline.py
import calendar, json, os, random, re, time, urllib.parse, urllib.request, concurrent.futures as cf
B = "https://api.publicrecords.copyright.gov/search_service_external/"
here = os.path.dirname(os.path.abspath(__file__))
# organisation: a company-like claimant name, or an author who is an "employer for hire" (same rule as analysis.py)
ORG = re.compile(r"\b(LLC|Inc|Corporation|Corp|Ltd|Limited|GmbH|Company|Co\b|LLP|PBC|Studios?|Media|Publishing|Records|Group|AG|S\.?A\.?|B\.?V\.?|PLC|Technologies|Systems|Labs?)\b")
def get(u):
    for k in range(6):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "curl/8.0"}), timeout=90))
        except Exception: time.sleep(2 + 2 * k)
def q(ym, per=1, page=1):
    y, m = map(int, ym.split("-")); end = f"{y}-{m:02d}-{calendar.monthrange(y, m)[1]:02d}"
    return {"query": "*", "field_type": "keyword", "records_per_page": per, "page_number": page, "type_of_work": "computer_file",
            "date_field": "registration_date_as_date", "start_date": f"{ym}-01 00:00:00", "end_date": f"{end} 23:59:59"}
SAVE = os.path.join(here, "..", "data", "raw", "baseline"); os.makedirs(SAVE, exist_ok=True)
months = [f"{y}-{m:02d}" for y in (2025, 2026) for m in range(1, 13) if (y, m) <= (2026, 3)]
hits = {ym: get(B + "simple_search_dsl?" + urllib.parse.urlencode(q(ym)))["metadata"]["hit_count"] for ym in months}
rng = random.Random(20261125)
pages = {ym: sorted(rng.sample(range(1, max(2, hits[ym] // 10) + 1), min(4, max(1, hits[ym] // 10)))) for ym in months}
ids = []
for ym in months:
    for p in pages[ym]:
        d = get(B + "simple_search_dsl?" + urllib.parse.urlencode(q(ym, 10, p)))
        ids += [(ym, h["hit"]["public_records_id"]) for h in (d or {}).get("data") or []]
def full(x):
    ym, i = x
    d = get(B + "search_unique_record?" + urllib.parse.urlencode({"query": i}))
    r = ((d or {}).get("data") or [{}])[0]; r = r.get("hit", r)
    nt = r.get("copyright_note") or []; nt = " ".join(nt) if isinstance(nt, list) else nt
    cl = [c.get("claimant_full_name", "") for c in r.get("claimants_list") or []]
    json.dump(d, open(os.path.join(SAVE, i + ".json"), "w"))   # raw record kept locally (git-ignored: addresses)
    hire = any("hire" in (a.get("author_work_for_hire_statement") or "").lower() for a in r.get("author_statement_list") or [])
    return {"month": ym, "id": i, "type": r.get("type_of_work_to_english"), "org": any(ORG.search(c) for c in cl) or hire,
            "co": "C.O. correspondence" in nt, "excluded": bool(r.get("material_excluded_statement"))}
with cf.ThreadPoolExecutor(4) as ex:
    recs = list(ex.map(full, ids))
rows = [r for r in recs if r["type"] == "Computer Files"]
pc = lambda xs: {"n": len(xs), "co": sum(r["co"] for r in xs), "pct": round(100 * sum(r["co"] for r in xs) / len(xs), 1) if xs else None}
res = {"months": hits, "pages": pages, "all": pc(rows), "orgs": pc([r for r in rows if r["org"]]), "people": pc([r for r in rows if not r["org"]]),
       "with_excluded": pc([r for r in rows if r["excluded"]]), "records": rows}
json.dump(res, open(os.path.join(here, "..", "data", "baseline.json"), "w"), indent=1)
print({k: res[k] for k in ("all", "orgs", "people", "with_excluded")})
