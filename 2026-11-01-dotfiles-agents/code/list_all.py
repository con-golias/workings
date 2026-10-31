# Every public, non-fork repository with "dotfiles" in its name and at least one star, via GitHub search split into
# created-date windows small enough to return all results (search caps at 1,000 per query). Saves all_repos.json.
import json, subprocess, time, datetime as dt
Q = "dotfiles in:name fork:false stars:>=1"
def search(lo, hi, page, per=100):
    for attempt in range(6):
        r = subprocess.run(["gh", "api", "-X", "GET", "search/repositories", "-f", f"q={Q} created:{lo}..{hi}", "-f", f"per_page={per}", "-f", f"page={page}"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            time.sleep(2.1); return json.loads(r.stdout)
        time.sleep(30 * (attempt + 1))
    raise SystemExit(f"search failed {lo}..{hi} p{page}: {r.stderr[:200]}")
out, windows = {}, [(dt.date(2008, 1, 1), dt.date(2026, 10, 31))]
while windows:
    lo, hi = windows.pop()
    first = search(lo, hi, 1)
    n = first["total_count"]
    if n > 1000 and lo < hi:
        mid = lo + (hi - lo) / 2
        windows += [(lo, mid), (mid + dt.timedelta(days=1), hi)]; continue
    items = first["items"]
    for p in range(2, min(10, (n + 99) // 100) + 1):
        items += search(lo, hi, p)["items"]
    for i in items:
        out[i["full_name"]] = {k: i[k] for k in ("full_name", "stargazers_count", "size", "created_at", "pushed_at", "default_branch")} | {"owner": i["owner"]["login"]}
    print(lo, hi, n, len(out), flush=True)
json.dump(list(out.values()), open("all_repos.json", "w"))
print("done", len(out))
