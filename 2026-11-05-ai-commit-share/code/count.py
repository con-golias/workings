"""count(term, d0, d1): commits in GitHub's commit-search index with committer date in [d0, d1] (YYYY-MM-DD, inclusive)
matching term. Accept the single query if complete; otherwise sum per-day queries (per-6h if a day is incomplete).
Returns (count, method, n_incomplete_slices)."""
import datetime as dt, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gh import search


def _q(term, a, b):
    r = search(f"{term}committer-date:{a}..{b}".strip())
    return r["total_count"], r["incomplete_results"]


def count(term, d0, d1):
    term = (term + " ") if term else ""
    n, inc = _q(term, d0, d1)
    if not inc:
        return n, "single", 0
    days = [dt.date.fromisoformat(d0) + dt.timedelta(i) for i in range((dt.date.fromisoformat(d1) - dt.date.fromisoformat(d0)).days + 1)]
    tot, bad = 0, 0
    for d in days:
        m, inc = _q(term, d.isoformat(), d.isoformat())
        bad += inc  # A1: an incomplete day is kept and counted in `bad` (probes: incomplete totals within ~1-2%)
        tot += m
    return tot, "sliced", bad, n


if __name__ == "__main__":
    print(count(sys.argv[1], sys.argv[2], sys.argv[3]))
