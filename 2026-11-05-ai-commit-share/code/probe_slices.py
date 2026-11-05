import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gh import search
day = sys.argv[1]; hours = int(sys.argv[2])
for term in ["", '"Co-Authored-By: Claude" ']:
    tot, inc = 0, []
    for h in range(0, 24, hours):
        a, b = f"{day}T{h:02d}:00:00", f"{day}T{h+hours-1:02d}:59:59"
        r = search(f"{term}committer-date:{a}..{b}")
        tot += r["total_count"]; inc.append(r["incomplete_results"])
    print(repr(term), tot, inc, flush=True)
