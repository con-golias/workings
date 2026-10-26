# Repos created on given days that match AI keywords (GitHub search, best match, first 100 per query).
import sys, json, subprocess, datetime as dt, time
start, end, out = sys.argv[1], sys.argv[2], sys.argv[3]
KW = ["openai", "anthropic", "llm", "gemini", "chatgpt", "claude", "\"ai agent\""]
seen = {}
d = dt.date.fromisoformat(start)
while d <= dt.date.fromisoformat(end):
    for kw in KW:
        q = f"{kw} created:{d} fork:false"
        for attempt in range(4):
            r = subprocess.run(["gh", "api", "-X", "GET", "search/repositories", "-f", f"q={q}", "-f", "per_page=100"], capture_output=True, text=True, encoding="utf-8", errors="replace")
            if r.returncode == 0: break
            time.sleep(30)
        try: items = json.loads(r.stdout)["items"]
        except Exception: items = []
        for it in items:
            seen.setdefault(it["full_name"], dict(repo=it["full_name"], branch=it["default_branch"], size=it["size"], lang=it["language"],
                created=it["created_at"], pushed=it["pushed_at"], stars=it["stargazers_count"], kw=kw))
        time.sleep(2.1)
    d += dt.timedelta(days=1)
with open(out, "w", encoding="utf-8") as f:
    for v in seen.values(): f.write(json.dumps(v) + "\n")
print(out, len(seen))
