"""Weekly downloads (last week) for every flagged package. Output ../data/downloads.json."""
import json, urllib.parse, concurrent.futures as cf
from npm import get
SC = json.load(open("../data/scan.json"))
flag = [n for n, v in SC.items() if v.get("hits") or v.get("cmd_hit")]
def one(n):
    try: return n, get("https://api.npmjs.org/downloads/point/last-week/" + urllib.parse.quote(n, safe="@/"))["downloads"]
    except Exception: return n, None
with cf.ThreadPoolExecutor(8) as ex: D = dict(ex.map(one, flag))
json.dump(D, open("../data/downloads.json", "w"), indent=0)
print(len(D), sum(v or 0 for v in D.values()))
