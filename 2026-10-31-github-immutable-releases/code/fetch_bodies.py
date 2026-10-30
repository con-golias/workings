# Release notes of the latest release for every repo in a list, so a checksum printed in the notes (a 64-hex SHA-256)
# counts as "something to check" too. Output: RAW/bodies.json {repo: body}.
#   python3 code/fetch_bodies.py RAW
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

RAW = sys.argv[1]
rows = json.load(open(os.path.join(RAW, "top.json")))["rows"] + json.load(open(os.path.join(RAW, "brew.json")))["rows"]
want = sorted({(r["repo"], r["tag"]) for r in rows if r.get("release") and r.get("downloads")})


def body(rt):
    repo, tag = rt
    r = subprocess.run(["gh", "api", f"repos/{repo}/releases/tags/{tag}", "--jq", ".body"], capture_output=True, text=True, encoding="utf-8")
    return repo, (r.stdout if r.returncode == 0 else None)


with ThreadPoolExecutor(6) as ex:
    out = dict(ex.map(body, want))
json.dump(out, open(os.path.join(RAW, "bodies.json"), "w"))
print(len(out), "bodies;", sum(v is None for v in out.values()), "failed")
