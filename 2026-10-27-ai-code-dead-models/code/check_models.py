# Fail the build when the code names a model the provider no longer serves.
# Asks each provider's own model list (the IDs your key can call today) and compares it with every
# model-ID string literal in the repository.   python check_models.py [path]   (exit 1 on a miss)
#   OPENAI_API_KEY / ANTHROPIC_API_KEY / GEMINI_API_KEY: only the providers with a key are checked.
import json, os, pathlib, re, sys, urllib.request

PAT = re.compile(r"""["'`]((?:gpt-[3-9](?:\.\d)?o?|o[1-4]|claude-|gemini-\d(?:\.\d)?)[A-Za-z0-9.\-]*)["'`]""")
EXT = {".py", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb", ".php", ".cs", ".yaml", ".yml", ".toml", ".json"}
SKIP = {"node_modules", ".git", "dist", "build", ".venv", "venv"}

def get(url, headers):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
        return json.load(r)

def served():
    ids = {}
    if k := os.environ.get("OPENAI_API_KEY"):
        ids["openai"] = {m["id"] for m in get("https://api.openai.com/v1/models", {"Authorization": f"Bearer {k}"})["data"]}
    if k := os.environ.get("ANTHROPIC_API_KEY"):
        ids["anthropic"] = {m["id"] for m in get("https://api.anthropic.com/v1/models?limit=1000",
                                                 {"x-api-key": k, "anthropic-version": "2023-06-01"})["data"]}
    if k := os.environ.get("GEMINI_API_KEY"):
        ids["google"] = {m["name"].removeprefix("models/") for m in
                         get(f"https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000&key={k}", {})["models"]}
    return ids

def vendor(mid):
    return "anthropic" if mid.startswith("claude") else "google" if mid.startswith("gemini") else "openai"

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
live, bad = served(), []
for p in root.rglob("*"):
    if p.suffix not in EXT or SKIP & set(p.parts) or not p.is_file():
        continue
    for n, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
        for mid in PAT.findall(line):
            v = vendor(mid)
            # Anthropic lists dated IDs; an undated alias is fine if a dated ID starts with it.
            if v in live and mid not in live[v] and not any(x.startswith(mid + "-") for x in live[v]):
                bad.append(f"{p}:{n}: {mid} is not served by {v}")
print("\n".join(bad) or f"ok: every model ID is served ({', '.join(live) or 'no keys set'})")
sys.exit(1 if bad else 0)
