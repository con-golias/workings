# Deploy URLs (homepage, or the first deploy-host link in the README) for every fetched repository.
#   RAW=raw python3 code/extract_urls.py   -> $RAW/urls.json and $RAW/urls_v0.json
import json, os, re
os.chdir(os.environ.get("RAW", "raw"))
URL = re.compile(r'https?://[A-Za-z0-9.-]+\.(?:lovable\.app|vercel\.app|netlify\.app|web\.app|firebaseapp\.com|pages\.dev|github\.io|onrender\.com|railway\.app|run\.app|replit\.app|bolt\.host|surge\.sh|fly\.dev)[^\s)\]"\'<>]*', re.I)
def urls(act):
    out = []
    for r, a in act.items():
        if not a:
            continue
        c = ([a["home"]] if a["home"] else []) + URL.findall(a["readme"] or "")
        if c:
            out.append((r, c[0].rstrip(".,")))
    return out
census = json.load(open("census_repos.json"))
b = json.load(open("builder_act.json"))
by = {}
for r, u in urls(b):
    by.setdefault(census[r]["g"], []).append((r, u))
by["baseline"] = urls(json.load(open("base_act.json")))
json.dump(by, open("urls.json", "w"))
json.dump({"v0x": urls(json.load(open("v0_act.json")))}, open("urls_v0.json", "w"))
print({k: len(v) for k, v in by.items()})
