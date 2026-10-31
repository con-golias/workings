# 20 random 2026 hits per agent signal: the matched paths in each repo's 2026 snapshot (read by hand; the result is in the README).
import json, os, re, random, subprocess, sys
sys.path.insert(0, "."); 
src = open("measure2.py", encoding="utf-8").read()
PATHS = eval(src.split("PATHS = ")[1].split("\nTOKENS")[0]); VENDOR = re.search(r'VENDOR = (r".*?")\n', src).group(1); VENDOR = eval(VENDOR)
rows = [r for r in json.load(open("rows_full.json")) if r["year"] == 2026 and r["commits"] > 0]
env = dict(os.environ, GIT_NO_LAZY_FETCH="1")
rng = random.Random(7)
out = {}
for sig in ["ai_claude", "ai_agentsmd", "ai_opencode", "ai_codex", "ai_gemini"]:
    hits = [r["repo"] for r in rows if r[sig]]; pick = rng.sample(hits, min(20, len(hits)))
    out[sig] = []
    for name in pick:
        d = os.path.join("full", name)
        rev = subprocess.run(["git", "-C", d, "rev-list", "-1", "--before=2026-10-31T00:00:00", "HEAD"], capture_output=True, text=True).stdout.strip()
        files = [f for f in subprocess.run(["git", "-C", d, "ls-tree", "-r", "--name-only", rev], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.splitlines() if not re.search(VENDOR, f, re.I)]
        m = [f for f in files if re.search(PATHS[sig], f, re.I)]
        out[sig].append((name, rev, len(m), m[:4]))
    print(f"== {sig}: {len(hits)} hits in 2026")
    for name, rev, k, m in out[sig]: print(f"  {name:45s} {k:3d}  {m}")
json.dump(out, open("handcheck.json", "w"))
