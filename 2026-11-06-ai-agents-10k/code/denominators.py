"""How many distinct companies filed a 10-K, 10-Q, 20-F or 40-F in each year (EDGAR quarterly form indexes)."""
import json, re, collections
from sec import get
FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A", "20-F", "20-F/A", "40-F"}
out = {}
for y in (2022, 2023, 2024, 2025, 2026):
    ciks = set(); annual = set(); months = collections.defaultdict(set); quarters = collections.defaultdict(set)
    for q in (1, 2, 3, 4):
        try: b = get("https://www.sec.gov/Archives/edgar/full-index/%d/QTR%d/form.idx" % (y, q), raw=True).decode("latin1")
        except Exception: continue
        for line in b.splitlines():
            form = line[:12].strip()
            if form in FORMS:
                m = re.search(r"\s(\d{3,10})\s+(\d{4}-\d{2}-\d{2})\s", line)
                if m:
                    ciks.add(m.group(1)); months[m.group(2)[:7]].add(m.group(1)); quarters["%sQ%d" % (m.group(2)[:4], (int(m.group(2)[5:7]) - 1) // 3 + 1)].add(m.group(1))
                    if form in ("10-K", "20-F", "40-F"): annual.add(m.group(1))
    out[y] = {"periodic_filers": len(ciks), "annual_filers": len(annual), "by_month": {k: len(v) for k, v in sorted(months.items())}, "by_quarter": {k: len(v) for k, v in sorted(quarters.items())}}
    print(y, len(ciks), len(annual))
json.dump(out, open("../data/denominators.json", "w"), indent=1)
