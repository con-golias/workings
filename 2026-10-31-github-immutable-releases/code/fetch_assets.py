# All asset names of each latest release (collect.py kept only the download assets), so checksum and signature files
# can be recognised by analyze.py with one rule. Output: RAW/asset_names.json {repo: [names]}.
#   python3 code/fetch_assets.py RAW
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

RAW = sys.argv[1]
rows = json.load(open(os.path.join(RAW, "top.json")))["rows"] + json.load(open(os.path.join(RAW, "brew.json")))["rows"]
want = sorted({(r["repo"], r["tag"]) for r in rows if r.get("release") and r.get("downloads")})


def names(rt):
    repo, tag = rt
    r = subprocess.run(["gh", "api", f"repos/{repo}/releases/tags/{tag}", "--jq", "[.assets[].name]"], capture_output=True, text=True, encoding="utf-8")
    return repo, (json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None)


with ThreadPoolExecutor(6) as ex:
    out = dict(ex.map(names, want))
json.dump(out, open(os.path.join(RAW, "asset_names.json"), "w"))
print(len(out), "repos;", sum(v is None for v in out.values()), "failed")
