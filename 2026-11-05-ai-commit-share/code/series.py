"""Weekly series (Mon-Sun, committer date, UTC) of all commits and of commits carrying Claude Code's co-author trailer
in GitHub's commit-search index. Window: week of 24 Feb 2025 (Claude Code launch) to week ending 1 Nov 2026.
Output: data/series.jsonl (appends; resumable)."""
import datetime as dt, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from count import count
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "series.jsonl")
done = set()
if os.path.exists(out):
    done = {json.loads(l)["week"] for l in open(out)}
# Amendment A1 (5 Nov 00:20): full weekly run took ~5 min/week. Sample instead: the first full week (Mon) of every
# month, Mar 2025 - Aug 2026, plus every week from 31 Aug 2026 to 26 Oct 2026.
weeks = []
for y, m in [(y, m) for y in (2025, 2026) for m in range(1, 13)]:
    d = dt.date(y, m, 1)
    d += dt.timedelta((7 - d.weekday()) % 7)
    if dt.date(2025, 3, 1) <= d < dt.date(2026, 8, 31):
        weeks.append(d)
w = dt.date(2026, 8, 31)
while w <= dt.date(2026, 10, 26):
    weeks.append(w); w += dt.timedelta(7)
for w in weeks:
    if w.isoformat() not in done:
        a, b = w.isoformat(), (w + dt.timedelta(6)).isoformat()
        all_ = count("", a, b); cl = count('"Co-Authored-By: Claude"', a, b)
        row = {"week": a, "all": all_[0], "all_method": list(all_[1:]), "claude": cl[0], "claude_method": list(cl[1:])}
        open(out, "a").write(json.dumps(row) + "\n")
        print(a, all_[0], cl[0], "%.2f%%" % (100 * cl[0] / max(all_[0], 1)), flush=True)
