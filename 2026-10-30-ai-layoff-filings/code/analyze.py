# Every number in the article comes from here. Inputs: $RAW (restructurings.json, ai_matches.tsv, fts_hits.json,
# completeness.json, join_filers.json, join_exhibits.json) and data/ai_codes.csv (hand codes).
# Outputs: data/summary.json, data/restructurings.csv, data/ai_codes.csv (codes + quoted sentences).
import csv, json, os, sys
from collections import defaultdict

RAW = sys.argv[1] if len(sys.argv) > 1 else "raw"
DATA = sys.argv[2] if len(sys.argv) > 2 else "data"
YEARS = range(2022, 2027)
YTD_END = "10-28"  # 1 Jan - 28 Oct in every year; 2026 data end on 28 Oct
TECH = lambda sic: sic and (7370 <= int(sic) <= 7374 or 3570 <= int(sic) <= 3579 or 3670 <= int(sic) <= 3679)

X = json.load(open(os.path.join(RAW, "restructurings.json")))
codes = {r["adsh"]: r for r in csv.DictReader(open(os.path.join(DATA, "ai_codes.csv"), encoding="utf-8"))}
quotes = defaultdict(list)
for r in csv.DictReader(open(os.path.join(RAW, "ai_matches.tsv"), encoding="utf-8"), delimiter="\t"):
    quotes[r["adsh"]].append(r["sentence"])
assert all(x["adsh"] in codes for x in X if x["ai_sentences"]), "an AI-matching filing has no hand code"


def code(x):
    # A hand code applies only while the 2.05 text still has the coded sentence (Dow's was in Item 8.01).
    return codes.get(x["adsh"], {}).get("code", "") if x["ai_sentences"] else ""


def is_ai(x):
    return any(c in code(x) for c in "WMD")


def pct(a, b):
    return 100.0 * a / b if b else 0.0


def folder_url(cik, adsh):
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/"


def wilson(k, n, z=1.96):
    """95% Wilson interval for k of n, in percent."""
    if not n:
        return 0.0, 0.0
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / (1 + z * z / n)
    return 100 * max(0.0, c - h), 100 * min(1.0, c + h)


def company_years(rows):
    """One row per company: AI if any of its workforce restructurings in the window is AI-coded."""
    by = defaultdict(list)
    for x in rows:
        by[x["cik"]].append(x)
    out = []
    for cik, xs in by.items():
        cs = "".join(code(x) for x in xs)
        out.append({"cik": cik, "name": xs[0]["name"], "sics": xs[0]["sics"], "ai": any(is_ai(x) for x in xs),
                    "W": "W" in cs, "M": "M" in cs, "D": "D" in cs, "reason": any(bool(x["reason_text"]) or is_ai(x) for x in xs),
                    "filings": [x["adsh"] for x in xs]})
    return out


def block(rows):
    wf = [x for x in rows if x["workforce"]]
    cy = company_years(wf)
    n, ai = len(cy), sum(c["ai"] for c in cy)
    reason = sum(c["reason"] for c in cy)
    tech = [c for c in cy if TECH((c["sics"] or [None])[0])]
    other = [c for c in cy if not TECH((c["sics"] or [None])[0])]
    lo, hi = wilson(ai, n)
    return {"ai_pct_lo": lo, "ai_pct_hi": hi,
            "companies_other": len(other), "companies_ai_other": sum(c["ai"] for c in other),
            "ai_rate_in_tech_pct": pct(sum(c["ai"] for c in tech), len(tech)),
            "ai_rate_in_other_pct": pct(sum(c["ai"] for c in other), len(other)),
            "cik_ai": sorted(c["cik"] for c in cy if c["ai"]), "cik_all": sorted(c["cik"] for c in cy),"filings": len(rows), "filings_workforce": len(wf), "filings_ai": sum(is_ai(x) for x in wf),
            "companies": n, "companies_reason": reason, "companies_ai": ai,
            "companies_W": sum(c["W"] for c in cy), "companies_M": sum(c["M"] for c in cy), "companies_D": sum(c["D"] for c in cy),
            "companies_W_only": sum(c["W"] and not c["M"] for c in cy), "companies_M_only": sum(c["M"] and not c["W"] for c in cy),
            "companies_WM": sum(c["W"] and c["M"] for c in cy),
            "ai_pct": pct(ai, n), "ai_pct_of_reason": pct(ai, reason), "reason_pct": pct(reason, n),
            "companies_tech": len(tech), "companies_ai_tech": sum(c["ai"] for c in tech),
            "tech_pct": pct(len(tech), n), "ai_tech_pct": pct(sum(c["ai"] for c in tech), ai),
            "ai_companies": sorted({c["name"] for c in cy if c["ai"]})}


S = {"pulled": json.load(open(os.path.join(RAW, "fts_hits.json")))["pulled"]}
hits = json.load(open(os.path.join(RAW, "fts_hits.json")))["filings"]
comp = json.load(open(os.path.join(RAW, "completeness.json")))
S["universe"] = {"candidates": len(hits), "tagged": sum("2.05" in f["items"] for f in hits), "restructurings": len(X),
                 "untagged_admitted": sum(not x["tagged"] for x in X), "exhibit_only": sum(x["exhibit_only"] for x in X),
                 "completeness_companies": comp["sample_companies"], "completeness_filings": comp["filings"],
                 "completeness_found": comp["found"],
                 "amendments_merged": sum(len(x.get("merged", [])) for x in X)}
S["universe"]["admitted"] = S["universe"]["restructurings"] + S["universe"]["amendments_merged"]
# Counted before the merge (an untagged original folded into its tagged amendment is still an untagged admission).
S["universe"]["untagged_admitted"] = S["universe"]["admitted"] - S["universe"]["tagged"]
S["ytd"] = {str(y): block([x for x in X if x["file_date"][:4] == str(y) and x["file_date"][5:] <= YTD_END]) for y in YEARS}
S["full"] = {str(y): block([x for x in X if x["file_date"][:4] == str(y)]) for y in YEARS if y < 2026}
S["ytd_2023_2025_ai"] = sum(S["ytd"][str(y)]["companies_ai"] for y in (2023, 2024, 2025))
S["ytd_2022_2025_ai"] = sum(S["ytd"][str(y)]["companies_ai"] for y in (2022, 2023, 2024, 2025))
S["codes_total"] = {c: sum(c in r["code"] for r in codes.values()) for c in ("W", "M", "D", "A", "B")}
S["codes_rows"] = len(codes)

# 2026 list for the table: company, date, code, first quoted sentence.
# One row per company (its first AI-coded filing of the year; Freshworks filed twice for one plan).
rows26, seen = [], set()
for x in sorted((x for x in X if "2026-01-01" <= x["file_date"] and x["file_date"][5:] <= YTD_END and x["workforce"] and is_ai(x)),
                key=lambda x: x["file_date"]):
    if x["cik"] not in seen:
        seen.add(x["cik"])
        rows26.append(x)
S["ai_2026"] = [{"company": x["name"].split("  (")[0], "date": x["file_date"], "code": code(x), "adsh": x["adsh"],
                 "sic": (x["sics"] or [""])[0], "url": folder_url(x["cik"], x["adsh"]),
                 "quote": next((q for q in quotes[x["adsh"]] if "artificial intelligence" in q.lower() or "AI" in q or "agentic" in q.lower()), "")[:400]}
                for x in rows26]
S["ai_2026_n"] = len(rows26)
assert S["ai_2026_n"] == S["ytd"]["2026"]["companies_ai"]

# Sensitivities.
exo = json.load(open(os.path.join(RAW, "exhibit_only.json")))
S["sens_exhibit_only_ai_2026"] = sum(1 for e in exo if e["date"] >= "2026" and e["workforce"] and e["ai"])
S["sens_exhibit_only_n"] = len(exo)
jc = list(csv.DictReader(open(os.path.join(DATA, "join_codes.csv"), encoding="utf-8")))
cik_of = {k: f"{v['cik']:010d}" for k, v in json.load(open(os.path.join(RAW, "join_filers.json"))).items()}
y26 = S["ytd"]["2026"]
extra = [r for r in jc if any(c in r["exhibit_code"] for c in "WMD") and cik_of[r["ticker"]] not in y26["cik_ai"]
         and cik_of[r["ticker"]] in y26["cik_all"]]
S["sens_with_exhibits_2026"] = {"added": [r["company"] for r in extra], "companies_ai": y26["companies_ai"] + len(extra),
                                "companies": y26["companies"], "ai_pct": pct(y26["companies_ai"] + len(extra), y26["companies"])}

# Join: TechCrunch's list (25 Jul 2026) of 2026 tech layoffs where employers cited AI.
jf = json.load(open(os.path.join(RAW, "join_filers.json")))
jx = json.load(open(os.path.join(RAW, "join_exhibits.json")))
S["join"] = {"listed_companies": 19, "foreign": ["Monday.com"], "us_filers": len(jf) - 1,
             "filed_205": sorted(k for k, v in jf.items() if v["205_2026"] and v["forms"].count("6-K") == 0),
             "no_205": sorted(k for k, v in jf.items() if not v["205_2026"] and "6-K" not in v["forms"])}
S["join"]["n_filed"] = len(S["join"]["filed_205"])
S["join"]["n_no"] = len(S["join"]["no_205"])

S["join"]["in_205"] = sorted(r["company"] for r in jc if any(c in r["item_2_05_code"] for c in "WMD"))
S["join"]["exhibit_only"] = sorted(r["company"] for r in jc if not any(c in r["item_2_05_code"] for c in "WMD")
                                   and any(c in r["exhibit_code"] for c in "WMD"))
S["join"]["neither"] = sorted(r["company"] for r in jc if not any(c in r["item_2_05_code"] + r["exhibit_code"] for c in "WMD"))
S["join"]["url"] = {r["ticker"]: folder_url(cik_of[r["ticker"]], r["adsh"]) for r in jc}
for k in ("in_205", "exhibit_only", "neither"):
    S["join"]["n_" + k] = len(S["join"][k])
assert S["join"]["n_in_205"] + S["join"]["n_exhibit_only"] + S["join"]["n_neither"] == S["join"]["n_filed"]

# "One in N" phrasings used in the text.
y = S["ytd"]["2026"]
S["one_in"] = {"all": round(y["companies"] / y["companies_ai"]),
               "tech": round(y["companies_tech"] / y["companies_ai_tech"]),
               "other": round(y["companies_other"] / y["companies_ai_other"])}
S["ratio_2026_vs_2025"] = y["ai_pct"] / S["ytd"]["2025"]["ai_pct"]

S["challenger"] = {"ai_jobs_ytd_sep_2026": 120136, "all_jobs_ytd_sep_2026": 573195, "ai_share_pct": 21,
                   "ai_jobs_sep_2026": 3961, "tech_jobs_ytd_sep_2026": 165925, "source_date": "2026-10-01"}

json.dump(S, open(os.path.join(DATA, "summary.json"), "w"), indent=1)

with open(os.path.join(DATA, "restructurings.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["adsh", "file_date", "company", "cik", "sic", "form", "tagged_2_05", "workforce", "reason_stated",
                "reason_keywords", "ai_code", "update_flag", "url"])
    for x in sorted(X, key=lambda x: x["file_date"]):
        w.writerow([x["adsh"], x["file_date"], x["name"].split("  (")[0], x["cik"], (x["sics"] or [""])[0], x["form"],
                    x["tagged"], x["workforce"], bool(x["reason_text"]) or is_ai(x), "|".join(x["reasons"]), code(x),
                    x.get("update", False),
                    f"https://www.sec.gov/Archives/edgar/data/{int(x['cik'])}/{x['adsh'].replace('-', '')}/"])

with open(os.path.join(DATA, "ai_codes.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["adsh", "file_date", "company", "code", "sentences", "note"])
    for a, r in codes.items():
        note = "" if quotes[a] else ("flagged by the first extraction; the sentence sits in another item of the 8-K "
                                     "(Dow: the press release under Item 8.01), so it is not counted")
        w.writerow([a, r["file_date"], r["company"], r["code"], " || ".join(quotes[a])[:2000], note])

for y in YEARS:
    b = S["ytd"][str(y)]
    print(y, f"companies {b['companies']}  AI {b['companies_ai']} ({b['ai_pct']:.1f}%)  W {b['companies_W']} M {b['companies_M']} D {b['companies_D']}"
             f"  reason {b['companies_reason']}  tech {b['tech_pct']:.0f}% / AI-tech {b['ai_tech_pct']:.0f}%")
print("join filed", S["join"]["filed_205"], "none", S["join"]["no_205"])
