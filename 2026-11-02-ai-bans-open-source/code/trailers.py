# AI-attribution trailers. (1) In banned projects after their ban: every commit whose trailer names an AI tool or model,
# listed for reading by hand. 'After the ban' = committed (landed) on or after the ban date. (2) In projects that allow AI: how many of 2026's new authors (first commit since 2018
# falls in 2026) tagged an AI tool on a 2026 commit.
#   python trailers.py <dir with <repo>.git and <repo>.log> <out trailers.json>
# Strict pattern: a trailer line Assisted-by | Co-authored-by | Co-developed-by | Generated-by | AI-used-for whose value
# names a tool, a model or a vendor (TOOL below). A Co-authored-by naming a person is not counted.
import collections, json, os, re, subprocess, sys

src, out = sys.argv[1], sys.argv[2]
BANS = {"qemu_qemu": "2025-06-24", "NetBSD_src": "2024-05-01", "gcc-mirror_gcc": "2026-07-29", "gentoo_gentoo": "2024-04-14"}
ALLOW = ["torvalds_linux", "llvm_llvm-project", "NixOS_nixpkgs"]
# Assisted-by / Generated-by / AI-used-for exist to name tools: any tool word counts (word boundaries).
TOOL = r"\b(claude|anthropic|gpt[-\w.]*|chatgpt|openai|codex|copilot|gemini|antigravity|cursor|llm|lollm|opencode|qwen|deepseek|kimi|grok|mistral|llama|aider|devin|windsurf|kiro|sonnet|opus|haiku|\w*clanker\w*)\b"
# Co-authored-by / Co-developed-by usually name people: only a vendor address or a capitalised product name counts
# (so "Devin Smith" or "Kirov" does not).
CO_TOOL = re.compile(r"@(anthropic\.com|openai\.com|cursor\.(com|sh)|google\.com\b.*gemini)|\b(Claude|Copilot|ChatGPT|GPT-\d[\w.]*|OpenAI|Codex|Gemini|Cursor Agent|Cursor|Anthropic|Antigravity|Devin AI|Kiro|Grok|Qwen|DeepSeek|Kimi|Aider|OpenCode|Windsurf)\b")
TRAILER = re.compile(r"^\s*(assisted-by|co-authored-by|co-developed-by|generated-by|ai-used-for)\s*:\s*(.+)$", re.I | re.M)
BOT = re.compile(r"\[bot\]|noreply@github\.com$|^bot@|-bot@|^r-ryantm|dependabot|renovate|github-actions", re.I)

def commits(repo, since):
    fmt = "%H%x1f%an%x1f%ae%x1f%cd%x1f%B%x1e"   # commit date: when it landed
    raw = subprocess.run(["git", "-C", os.path.join(src, repo + ".git"), "log", f"--since={since}", "--date=short", f"--format={fmt}"],
                         capture_output=True, check=True).stdout.decode("utf-8", "replace")
    for rec in raw.split("\x1e"):
        rec = rec.strip("\n")
        if rec.count("\x1f") >= 4:
            h, an, ae, ad, b = rec.split("\x1f", 4)
            yield h, an, ae.strip().lower(), ad, b

def ai_trailers(body):
    out = []
    for k, v in TRAILER.findall(body):
        co = k.lower().startswith("co-")
        if (CO_TOOL.search(v) if co else re.search(TOOL, v, re.I)):
            out.append(f"{k}: {v.strip()}")
    return out

R = {"banned": {}, "allow": {}}
for repo, ban in BANS.items():
    hits, n = [], 0
    for h, an, ae, ad, b in commits(repo, ban):
        if ad < ban: continue
        n += 1
        t = ai_trailers(b)
        if t: hits.append({"sha": h[:12], "author": an, "date": ad, "subject": b.strip().splitlines()[0][:100], "trailers": t})
    R["banned"][repo] = {"ban": ban, "commits_after": n, "ai_commits": len(hits),
                         "authors": collections.Counter(x["author"] for x in hits).most_common(), "commits": hits}
    print(f"{repo}: {len(hits)} of {n} commits since {ban} carry an AI trailer; authors {len(set(x['author'] for x in hits))}")

for repo in ALLOW:
    first = {}
    for line in open(os.path.join(src, repo + ".log"), encoding="utf-8", errors="replace"):
        p = line.rstrip("\n").split("|")
        if len(p) < 4: continue
        e, d = p[0].strip().lower(), p[2]
        if not e or BOT.search(e) or d < "2018-01-01": continue
        if e not in first or d < first[e]: first[e] = d
    new26 = {e for e, d in first.items() if d >= "2026-01-01"}
    tagged = set()
    for h, an, ae, ad, b in commits(repo, "2026-01-01"):
        if ad >= "2026-01-01" and ae in new26 and ai_trailers(b): tagged.add(ae)
    R["allow"][repo] = {"new_2026": len(new26), "tagged": len(tagged), "pct": round(100 * len(tagged) / len(new26), 1)}
    print(f"{repo}: {len(tagged)} of {len(new26)} new 2026 authors tagged an AI ({100*len(tagged)/len(new26):.1f}%)")
json.dump(R, open(out, "w"), indent=1)
