"""Every annual or quarterly report (10-K, 10-Q, 20-F, 40-F and amendments) filed 1 Jan 2022 - 5 Nov 2026 whose
text matches one of the agent phrases in EDGAR full-text search. One row per (filing, file) hit."""
import json, sys
from sec import efts
PHRASES = ['"artificial intelligence agent"', '"artificial intelligence agents"', '"AI agent"', '"AI agents"', '"agentic"', '"autonomous agent"', '"autonomous agents"', '"AI-powered agents"']
FORMS = ["10-K", "10-K/A", "10-Q", "10-Q/A", "20-F", "20-F/A", "40-F"]
rows = {}
for q in PHRASES:
  for form in FORMS:
    for (s, e) in [("2022-01-01", "2024-12-31"), ("2025-01-01", "2025-12-31"), ("2026-01-01", "2026-06-30"), ("2026-07-01", "2026-11-05")]:
        frm = 0
        while True:
            d = efts(q, form, s, e, frm)
            hits = d["hits"]["hits"]; total = d["hits"]["total"]["value"]
            for h in hits:
                r = rows.setdefault(h["_id"], {"id": h["_id"], **{k: h["_source"].get(k) for k in
                    ("adsh", "form", "file_type", "file_date", "period_ending", "ciks", "display_names", "sics", "biz_states", "inc_states")}, "phrases": []})
                if q not in r["phrases"]: r["phrases"].append(q)
            frm += len(hits)
            if not hits or frm >= total: break
        if total: print(q, form, s, e, total, file=sys.stderr)
with open("../data/hits.jsonl", "w") as f:
    for r in rows.values(): f.write(json.dumps(r) + "\n")
print(len(rows), "file hits,", len({r["adsh"] for r in rows.values()}), "filings", file=sys.stderr)
