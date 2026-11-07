"""Universe A: popularity-sorted npm search, top 1,000 per keyword. Universe B: wooorm/npm-high-impact.
Output ../data/universe.json: {name: {"sets": [...]}}"""
import json, urllib.parse, sys
from npm import get
KEYS = ["mcp", "mcp-server", "model-context-protocol", "claude-code", "claude", "codex", "cursor", "ai-agent", "agent-skills", "gemini-cli"]
U = {}
for k in KEYS:
    for frm in range(0, 1000, 250):
        d = get("https://registry.npmjs.org/-/v1/search?text=%s&size=250&from=%d&popularity=1.0&quality=0&maintenance=0" % (urllib.parse.quote("keywords:" + k), frm))
        for o in d["objects"]: U.setdefault(o["package"]["name"], {"sets": []})["sets"].append("A:" + k)
        if len(d["objects"]) < 250: break
    print(k, len(U), file=sys.stderr)
hi = get("https://raw.githubusercontent.com/wooorm/npm-high-impact/main/lib/top.js", raw=True).decode()
import re
names = re.findall(r"'([^']+)'", hi)
for n in names: U.setdefault(n, {"sets": []})["sets"].append("B:high-impact")
print("high-impact", len(names), "total", len(U), file=sys.stderr)
json.dump(U, open("../data/universe.json", "w"), indent=0)
