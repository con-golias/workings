# For each scanned repo that names a model ID: first page of commits (up to 100), and the AI coding-agent
# signatures in their messages (Co-Authored-By trailers, "Generated with ..." lines).
import sys, json, re, subprocess, concurrent.futures as cf
SIG = re.compile(r"Co-Authored-By:\s*([^<\n]+?)\s*<[^>]*(anthropic|openai|cursor|google|github|copilot|codex|gemini|devin|windsurf|codeium|aider|cline|kiro|jules|amazon)[^>]*>|Generated with \[?(Claude Code|Codex|Cursor|Gemini CLI|Aider|Devin|Copilot)", re.I)
def get(repo):
    r = subprocess.run(["gh", "api", f"repos/{repo}/commits?per_page=100"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0: return dict(repo=repo, ok=False)
    try: cs = json.loads(r.stdout)
    except Exception: return dict(repo=repo, ok=False)
    sigs = []
    for c in cs:
        msg = c["commit"]["message"]; d = c["commit"]["committer"]["date"]
        for m in SIG.finditer(msg): sigs.append(dict(date=d, who=(m.group(1) or m.group(3) or "").strip()))
    return dict(repo=repo, ok=True, ncommits=len(cs), first=cs[-1]["commit"]["committer"]["date"] if cs else None, sigs=sigs)
repos = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
# Only repositories that call an LLM with a literal model ID (same filter as analyze.py), to stay inside the API budget.
repos = [r["repo"] for r in repos if r.get("status") == "ok" and any(f["call"] and len(f["ids"]) <= 8 for f in r.get("files", []))]
with cf.ThreadPoolExecutor(6) as ex, open(sys.argv[2], "w", encoding="utf-8") as out:
    for x in ex.map(get, repos): out.write(json.dumps(x) + "\n")
print(sys.argv[2], len(repos))
