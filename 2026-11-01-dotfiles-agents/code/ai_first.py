# Month each agent repo first committed an agent file (claude/codex/opencode/gemini folder or an instructions file).
import json, os, subprocess
from concurrent.futures import ThreadPoolExecutor
env = dict(os.environ, GIT_NO_LAZY_FETCH="1")
AG = ["claude", "agentsmd", "codex", "opencode", "gemini", "aider"]
rows = [r for r in json.load(open("ai_rows.json")) if r["year"] == 2026 and r["commits"] > 0 and any(r[k] for k in AG)]
def one(r):
    d = os.path.join("full", r["repo"]); first = {}
    for k in AG:
        if not r[k]: continue
        ps = sorted(set(r["paths"][k]))
        out = subprocess.run(["git", "-C", d, "log", "--diff-filter=A", "--format=%as", "--reverse", "HEAD", "--"] + ps,
                             capture_output=True, text=True, env=env).stdout.split()
        if out: first[k] = out[0]
    return {"repo": r["repo"], "first": first}
with ThreadPoolExecutor(8) as ex: res = list(ex.map(one, rows))
json.dump(res, open("ai_first.json", "w"))
from collections import Counter
m = Counter(min(x["first"].values())[:7] for x in res if x["first"])
for k in sorted(m): print(k, m[k])
print(sum(1 for x in res if not x["first"]), "without a date")
