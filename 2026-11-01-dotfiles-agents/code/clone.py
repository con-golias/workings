# Partial bare clones (blobs <= 200 KB) of each repo in a list, 8 at a time.
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
lst, dest = sys.argv[1], sys.argv[2]
repos = json.load(open(lst))
os.makedirs(dest, exist_ok=True)
env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
def one(r):
    d = os.path.join(dest, r["full_name"].replace("/", "__"))
    if os.path.isdir(d): return "have"
    try:
        p = subprocess.run(["git", "clone", "-q", "--bare", "--filter=blob:limit=200k", f"https://github.com/{r['full_name']}.git", d],
                           capture_output=True, text=True, timeout=300, env=env)
        return "ok" if p.returncode == 0 else "fail"
    except subprocess.TimeoutExpired:
        return "timeout"
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(one, repos))
from collections import Counter; print(Counter(res))
