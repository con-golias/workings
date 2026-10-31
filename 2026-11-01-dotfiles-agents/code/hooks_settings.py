# Agent folders that define hooks inside a settings file ("hooks" key), not only in a hooks/ folder or hooks.json.
import json, os, re, subprocess
from concurrent.futures import ThreadPoolExecutor
env = dict(os.environ, GIT_NO_LAZY_FETCH="1")
AG = ["claude", "agentsmd", "codex", "opencode", "gemini", "aider"]
rows = [r for r in json.load(open("ai_rows.json")) if r["year"] == 2026 and r["commits"] > 0 and any(r[k] for k in AG)]
DIR = re.compile(r"(^|/)\.?(claude|codex|opencode|gemini)/", re.I)
VENDOR = re.compile(r"(^|/)(node_modules|vendor|third_party|archive)/|\.local/src/", re.I)
def one(r):
    d = os.path.join("full", r["repo"])
    rev = subprocess.run(["git", "-C", d, "rev-list", "-1", "--before=2026-10-31T00:00:00", "HEAD"], capture_output=True, text=True).stdout.strip()
    fs = subprocess.run(["git", "-C", d, "ls-tree", "-r", "--name-only", rev], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.splitlines()
    fs = [f for f in fs if DIR.search(f) and not VENDOR.search(f)]
    path_hooks = any(re.search(r"(^|/)hooks?(/|\.json$)", f, re.I) for f in fs)
    sett = [f for f in fs if re.search(r"settings[^/]*\.jsonc?$|opencode\.jsonc?$|config\.toml$", f, re.I)]
    key_hooks = False
    if sett:
        out = subprocess.run(["git", "-C", d, "grep", "-l", "-E", r'"hooks"\s*:|^\s*\[hooks', rev, "--"] + sett, capture_output=True, text=True, env=env).stdout
        key_hooks = bool(out.strip())
    return path_hooks, key_hooks
with ThreadPoolExecutor(8) as ex: res = list(ex.map(one, rows))
N = len(res); p = sum(a for a, b in res); k = sum(b for a, b in res); u = sum(a or b for a, b in res); only = sum(b and not a for a, b in res)
print(N, "agent repos | path hooks", p, f"{100*p/N:.1f}%", "| hooks key in a settings file", k, f"{100*k/N:.1f}%", "| either", u, f"{100*u/N:.1f}%", "| settings only", only)
