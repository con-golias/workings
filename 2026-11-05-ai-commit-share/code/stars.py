"""Stars (and created date, fork flag) for every repo in the given sample files, via aliased GraphQL (100 per call).
Usage: stars.py <out.json> <sample.jsonl>...  (resumable: repos already in out.json are skipped)"""
import json, os, subprocess, sys
out, files = sys.argv[1], sys.argv[2:]
have = json.load(open(out)) if os.path.exists(out) else {}
repos = sorted({json.loads(l)["repo"] for f in files for l in open(f, encoding="utf-8")} - set(have))
for i in range(0, len(repos), 100):
    chunk = repos[i:i + 100]
    q = "query{" + " ".join(f'r{j}:repository(owner:{json.dumps(r.split("/")[0])},name:{json.dumps(r.split("/")[1])}){{stargazerCount createdAt isFork}}'
                           for j, r in enumerate(chunk)) + "}"
    res = subprocess.run(["gh", "api", "graphql", "-f", f"query={q}"], capture_output=True, text=True, encoding="utf-8")
    data = json.loads(res.stdout or "{}").get("data") or {}
    for j, r in enumerate(chunk):
        have[r] = data.get(f"r{j}")  # None = gone/private now
    json.dump(have, open(out, "w"), indent=0)
print(len(have), "repos;", sum(v is None for v in have.values()), "unreachable")
