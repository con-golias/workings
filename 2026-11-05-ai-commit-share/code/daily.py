"""Daily totals (all commits) for a date range, to locate spikes. Usage: daily.py d0 d1 -> data/daily.jsonl (append)"""
import datetime as dt, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gh import search
d, e = dt.date.fromisoformat(sys.argv[1]), dt.date.fromisoformat(sys.argv[2])
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "daily.jsonl")
while d <= e:
    r = search(f"committer-date:{d}")
    c = search(f'"Co-Authored-By: Claude" committer-date:{d}')
    row = {"day": d.isoformat(), "all": r["total_count"], "all_inc": r["incomplete_results"], "claude": c["total_count"], "claude_inc": c["incomplete_results"]}
    open(out, "a").write(json.dumps(row) + "\n"); print(row, flush=True)
    d += dt.timedelta(1)
