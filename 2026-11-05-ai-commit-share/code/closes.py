"""Closing checks (5 Nov ~01:35). One run, all logged to data/closes.json.
1. spam check per series week (2 random days x 10 commits)  2. author:claude and overlap with the trailer (3 Nov)
3. other agents' signatures on 3 Nov (count + 5 items)       4. the author's own commits with the trailer on 3 Nov
5. reachability of two spam SHAs"""
import datetime as dt, json, os, random, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gh import search
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
SPAM = re.compile(r"彩|信誉平台|财经|welcome购")
random.seed(20261105)
out = {"weeks": {}, "agents": {}, "owner": {}, "spam_sha": []}

def save():
    json.dump(out, open(os.path.join(D, "closes.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

for l in open(os.path.join(D, "series.jsonl")):
    w = dt.date.fromisoformat(json.loads(l)["week"])
    n = s = 0
    for day in random.sample(range(7), 2):
        d = w + dt.timedelta(day); h = random.randrange(24)
        r = search(f"committer-date:{d}T{h:02d}:00:00..{d}T{h:02d}:59:59", per_page=100, page=random.randint(1, 5))
        items = r["items"]; random.shuffle(items)
        for i in items[:10]:
            n += 1; s += bool(SPAM.search(i["commit"]["message"]))
    out["weeks"][w.isoformat()] = {"n": n, "spam": s}
    print("week", w, n, s, flush=True); save()

AG = {
    "claude_author": "author:claude",
    "claude_author_and_trailer": 'author:claude "Co-Authored-By: Claude"',
    "cursor": '"cursoragent@cursor.com"',
    "copilot_agent": "author-name:Copilot",
    "jules": 'author-name:"google-labs-jules[bot]"',
    "devin": 'author-name:"devin-ai-integration[bot]"',
    "lovable": 'author-name:"gpt-engineer-app[bot]"',
    "codex_connector": 'author-name:"chatgpt-codex-connector[bot]"',
    "codex_trailer": '"Co-authored-by: Codex"',
    "aider": '"aider@aider.chat"',
    "amp": '"amp@ampcode.com"',
    "opencode": '"noreply@opencode.ai"',
    "gemini_trailer": '"Co-authored-by: Gemini"',
}
for k, q in AG.items():
    r = search(f"{q} committer-date:2026-11-03", per_page=5)
    out["agents"][k] = {"q": q, "n": r["total_count"], "inc": r["incomplete_results"],
                        "items": [{"repo": i["repository"]["full_name"], "author": i["commit"]["author"]["name"],
                                   "email": i["commit"]["author"]["email"], "msg": i["commit"]["message"][:300]} for i in r["items"]]}
    print("agent", k, r["total_count"], flush=True); save()

for k, q in {"owner_trailer": 'committer:con-golias "Co-Authored-By: Claude"', "owner_all": "committer:con-golias",
             "owner_author_trailer": 'author:con-golias "Co-Authored-By: Claude"'}.items():
    r = search(f"{q} committer-date:2026-11-03")
    out["owner"][k] = r["total_count"]; print(k, r["total_count"], flush=True)
save()

S = [json.loads(l) for l in open(os.path.join(D, "sample_all_0924.jsonl"), encoding="utf-8")]
for x in [x for x in S if SPAM.search(x["message"])][:3]:
    r = subprocess.run(["gh", "api", f"repos/{x['repo']}/commits/{x['sha']}", "--jq", ".sha"], capture_output=True, text=True)
    out["spam_sha"].append({"repo": x["repo"], "sha": x["sha"], "reachable": r.returncode == 0, "err": r.stderr[:120]})
save(); print("done")
