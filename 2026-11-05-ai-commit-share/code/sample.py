"""Sample commits from the index for one day (random hours, random result pages) and keep what describes them:
repo, author/committer login and type, message. Usage: sample.py <day> <term|''> <n_hours> <per_hour> <out.jsonl>"""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gh import search
day, term, nh, per, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
random.seed(f"{day}{term}")
term = (term + " ") if term else ""
with open(out, "w", encoding="utf-8") as f:
    for h in random.sample(range(24), nh):
        r = search(f"{term}committer-date:{day}T{h:02d}:00:00..{day}T{h:02d}:59:59", per_page=100, page=random.randint(1, 10))
        items = r["items"]; random.shuffle(items)
        for i in items[:per]:
            f.write(json.dumps({"sha": i["sha"], "repo": i["repository"]["full_name"], "hour": h,
                                "author": (i.get("author") or {}).get("login"), "author_type": (i.get("author") or {}).get("type"),
                                "committer": (i.get("committer") or {}).get("login"), "committer_type": (i.get("committer") or {}).get("type"),
                                "author_name": i["commit"]["author"]["name"], "committer_name": i["commit"]["committer"]["name"],
                                "message": i["commit"]["message"][:2000]}) + "\n")
print("done", out)
