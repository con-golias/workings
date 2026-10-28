# For repositories that carry an agent instruction file, fetch its text (CLAUDE.md, AGENTS.md, .cursorrules,
# GEMINI.md; first 20 KB each), to test how often the developer named the stack for the agent.
#   python3 code/fetch_instructions.py <meta.json> <out.json>
import json
import os
import subprocess
import sys
import time

meta_f, dst = sys.argv[1], sys.argv[2]
M = json.load(open(meta_f, encoding="utf-8"))
FILES = ["CLAUDE.md", "AGENTS.md", ".cursorrules", "GEMINI.md"]
todo = [r for r, v in M.items() if v and v.get("pkg") and v["created"] >= "2026-10-01" and set(FILES) & set(v.get("root") or [])]
out = json.load(open(dst, encoding="utf-8")) if os.path.exists(dst) else {}
todo = [r for r in todo if r not in out]
F = " ".join(f'f{i}:object(expression:"HEAD:{f}"){{... on Blob{{text}}}}' for i, f in enumerate(FILES))
for i in range(0, len(todo), 30):
    chunk = todo[i:i + 30]
    q = "query{" + " ".join(f'r{k}:repository(owner:{json.dumps(r.split("/", 1)[0])},name:{json.dumps(r.split("/", 1)[1])}){{{F}}}'
                            for k, r in enumerate(chunk)) + "}"
    for att in range(5):
        p = subprocess.run(["gh", "api", "graphql", "-f", f"query={q}"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        try:
            d = json.loads(p.stdout)
        except Exception:
            d = {}
        if d.get("data"):
            break
        time.sleep(20 * (att + 1))
    data = (d or {}).get("data") or {}
    for k, r in enumerate(chunk):
        x = data.get(f"r{k}") or {}
        out[r] = "\n".join(((x.get(f"f{j}") or {}).get("text") or "")[:20000] for j in range(len(FILES)))
    if i % 300 == 0:
        json.dump(out, open(dst, "w", encoding="utf-8"))
        print(i, len(out), flush=True)
json.dump(out, open(dst, "w", encoding="utf-8"))
print("done", len(out))
