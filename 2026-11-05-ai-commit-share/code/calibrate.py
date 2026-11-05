import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from count import count
for d0, d1 in [("2026-02-02", "2026-02-02"), ("2026-02-01", "2026-02-03"), ("2026-01-26", "2026-02-01")]:
    a = count("", d0, d1); c = count('"Co-Authored-By: Claude"', d0, d1)
    print(d0, d1, "all", a, "claude", c, "share %.2f%%" % (100 * c[0] / a[0]), flush=True)
