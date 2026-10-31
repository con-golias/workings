# AI agent configs per year-end snapshot, 2022-2026, with signals tightened after the hand check (handcheck.py):
# codex / opencode / gemini must be config files of the tool (not a Dockerfile, an archive or another tool's skill);
# AGENTS.md under .local/src/ (vendored source) does not count.
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
CL, OUT = sys.argv[1], sys.argv[2]
YEARS = [2022, 2023, 2024, 2025, 2026]
env = dict(os.environ, GIT_NO_LAZY_FETCH="1")
VENDOR = r"(^|/)(plugins?|bundle|pack|plugged|oh-my-zsh|\.oh-my-zsh|node_modules|themes?|colors|autoload|vendor|third_party|submodules?|ports|archive)/|\.local/src/"
SIG = {
  "claude": r"(^|/)\.?claude/|(^|/)CLAUDE\.md$",
  "agentsmd": r"(^|/)AGENTS\.md$",
  "codex": r"(^|/)\.?codex/(.*/)?(config(\.example)?\.toml|AGENTS\.md|hooks\.json|rules/|prompts/|agents/|skills/)",
  "opencode": r"(^|/)\.?opencode/(.*/)?(opencode\.jsonc?|AGENTS\.md|agents?/|commands?/|skills/|instructions/|tui\.json)|opencode\.jsonc?$",
  "gemini": r"(^|/)\.?gemini/(.*/)?(settings\.json|GEMINI\.md|AGENTS\.md|hooks|mcp_config\.json)|(^|/)GEMINI\.md$",
  "aider": r"\.aider\.conf\.yml$",
  "cursor": r"(^|/)\.?cursor/|\.cursorrules$|(^|/)Cursor/User/",
  "copilot": r"(^|/)github-copilot/|(^|/)copilot(\.lua|-chat\.lua)$",
}
def run(a): return subprocess.run(a, capture_output=True, text=True, env=env, encoding="utf-8", errors="replace").stdout
def one(name):
    d = os.path.join(CL, name); rows = []
    for y in YEARS:
        end = f"{y}-12-31T23:59:59" if y < 2026 else "2026-10-31T00:00:00"
        rev = run(["git", "-C", d, "rev-list", "-1", f"--before={end}", "HEAD"]).strip()
        if not rev: continue
        n = int(run(["git", "-C", d, "rev-list", "--count", f"--since={y}-01-01", f"--before={end}", "HEAD"]).strip() or 0)
        files = [f for f in run(["git", "-C", d, "ls-tree", "-r", "--name-only", rev]).splitlines() if not re.search(VENDOR, f, re.I)]
        hit = {k: [f for f in files if re.search(p, f, re.I)][:3] for k, p in SIG.items()}
        rows.append({"repo": name, "year": y, "commits": n, **{k: bool(v) for k, v in hit.items()}, "paths": {k: v for k, v in hit.items() if v}})
    return rows
with ThreadPoolExecutor(8) as ex:
    allrows = [r for rs in ex.map(one, sorted(os.listdir(CL))) for r in rs]
json.dump(allrows, open(OUT, "w")); print(len(allrows))
