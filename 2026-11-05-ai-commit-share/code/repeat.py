"""Is total_count stable? Ask the same day several times, a few minutes apart. -> data/repeat.jsonl"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gh import search
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "repeat.jsonl")
days = ["2026-02-02", "2026-09-21", "2026-10-08", "2026-10-20", "2026-11-03"]
for rnd in range(4):
    for d in days:
        for term in ["", '"Co-Authored-By: Claude" ']:
            r = search(f"{term}committer-date:{d}")
            row = {"round": rnd, "t": time.strftime("%H:%M:%S"), "day": d, "term": term.strip(), "n": r["total_count"], "inc": r["incomplete_results"]}
            open(out, "a").write(json.dumps(row) + "\n"); print(row, flush=True)
    time.sleep(60)
