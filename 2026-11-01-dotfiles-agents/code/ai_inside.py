# What people keep in their agent folders (2026 snapshots of the 800 agent repos): every path under an agent folder.
import json, os, re, subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
env = dict(os.environ, GIT_NO_LAZY_FETCH="1")
VENDOR = r"(^|/)(node_modules|vendor|third_party|archive)/|\.local/src/"
AG = ["claude", "agentsmd", "codex", "opencode", "gemini", "aider"]
rows = [r for r in json.load(open("ai_rows.json")) if r["year"] == 2026 and r["commits"] > 0 and any(r[k] for k in AG)]
DIR = re.compile(r"(^|/)\.?(claude|codex|opencode|gemini|agents|pi/agent)/", re.I)
KIND = {"skills": r"(^|/)skills?/", "hooks": r"(^|/)hooks?(/|\.json$)", "subagents": r"(claude|codex|opencode|gemini)/(.*/)?agents?/(?!AGENTS\.md$)[^/]+\.(md|toml)$",
        "commands": r"(^|/)(commands?|prompts)/", "mcp": r"mcp", "settings": r"(settings[^/]*|config|opencode)\.(json|jsonc|toml)$",
        "statusline": r"statusline", "rules_folder": r"(^|/)rules/", "instructions": r"(CLAUDE|AGENTS|GEMINI)\.md$"}
def one(r):
    d = os.path.join("full", r["repo"])
    rev = subprocess.run(["git", "-C", d, "rev-list", "-1", "--before=2026-10-31T00:00:00", "HEAD"], capture_output=True, text=True).stdout.strip()
    fs = subprocess.run(["git", "-C", d, "ls-tree", "-r", "--name-only", rev], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.splitlines()
    fs = [f for f in fs if not re.search(VENDOR, f, re.I) and (DIR.search(f) or re.search(r"(CLAUDE|AGENTS|GEMINI)\.md$", f))]
    return {"repo": r["repo"], "n": len(fs), "kinds": [k for k, p in KIND.items() if any(re.search(p, f, re.I) and (DIR.search(f) or k == "instructions") for f in fs)]}
with ThreadPoolExecutor(8) as ex: res = list(ex.map(one, rows))
c = Counter(k for x in res for k in x["kinds"]); N = len(res)
out = {"agent_repos": N, "kinds": {k: [v, round(100 * v / N, 1)] for k, v in c.most_common()},
       "files_median": sorted(x["n"] for x in res)[N // 2], "files_p90": sorted(x["n"] for x in res)[int(N * .9)], "top": sorted(res, key=lambda x: -x["n"])[:10]}
json.dump(out, open("ai_inside.json", "w"), indent=1); print(json.dumps(out, indent=1)[:2500])
