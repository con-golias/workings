# Stream each repo's tarball (codeload), record model-ID string literals per source file, call-site evidence,
# AI-coding-agent config files, and a content hash per matching file. Nothing is written to disk but the JSONL.
import sys, re, io, tarfile, json, hashlib, urllib.request, concurrent.futures as cf
EXT = (".py",".js",".mjs",".cjs",".ts",".tsx",".jsx",".go",".rs",".java",".kt",".rb",".php",".cs",".ipynb",".yaml",".yml",".toml",".env",".example",".json",".sh",".swift",".dart",".vue",".svelte")
SKIP = ("node_modules/","/dist/","/build/","/.venv/","/venv/","site-packages/","package-lock.json","pnpm-lock","yarn.lock","/vendor/",".min.js","/.next/")
PAT = re.compile(r"""["'`](gpt-[3-9](?:\.[0-9])?o?(?:-[A-Za-z0-9.]+)*|o[1-4](?:-(?:mini|pro|preview|high|low))?(?:-20\d\d-\d\d-\d\d)?|chatgpt-4o-latest|text-davinci-00[0-9]|claude-(?:[1-3](?:[-.][0-9])?-(?:opus|sonnet|haiku)|instant(?:-1(?:.[0-9])?)?|2(?:\.[01])?|(?:opus|sonnet|haiku|fable|mythos)-[0-9](?:-[0-9])?)(?:-[0-9]{8}|-latest|-0)?|gemini-[0-9](?:\.[0-9])?-(?:pro|flash|ultra|nano)[A-Za-z0-9.-]*)["'`]""")
CALL = re.compile(r"chat\.completions|responses\.create|messages\.create|generate_?[Cc]ontent|ChatOpenAI|ChatAnthropic|ChatGoogleGenerativeAI|GenerativeModel|OpenAI\(|Anthropic\(|GoogleGenAI|genai\.|/v1/chat|/v1/messages|/v1/responses|generativelanguage|createChatCompletion|streamText|generateText|init_chat_model|litellm\.completion")
AGENT = {"claude": re.compile(r"(^|/)(CLAUDE\.md|\.claude/)"), "agents_md": re.compile(r"(^|/)AGENTS\.md$"), "cursor": re.compile(r"(^|/)(\.cursor/|\.cursorrules$)"),
         "copilot": re.compile(r"(^|/)\.github/(copilot-instructions\.md|instructions/)"), "gemini": re.compile(r"(^|/)GEMINI\.md$"), "windsurf": re.compile(r"(^|/)\.windsurf"),
         "codex": re.compile(r"(^|/)\.codex/"), "kiro": re.compile(r"(^|/)\.kiro/"), "cline": re.compile(r"(^|/)\.clinerules")}
def scan(row):
    name, branch, size = row["repo"], row["branch"], int(row.get("size") or 0)
    base = dict(repo=name, created=row["created"], pushed=row["pushed"], stars=row.get("stars"), lang=row.get("lang"))
    if size == 0 or size > 80000: return dict(base, status="skip_size")
    try:
        req = urllib.request.Request(f"https://codeload.github.com/{name}/tar.gz/{branch}", headers={"User-Agent": "research"})
        data = urllib.request.urlopen(req, timeout=90).read()
        files, agents, n = [], set(), 0
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as t:
            for m in t:
                p = m.name.split("/", 1)[-1] if "/" in m.name else ""
                for k, rx in AGENT.items():
                    if rx.search(p): agents.add(k)
                if not m.isfile() or m.size > 2_000_000: continue
                if any(s in m.name for s in SKIP) or not p.lower().endswith(EXT): continue
                n += 1
                b = t.extractfile(m).read(); txt = b.decode("utf-8", "ignore")
                found = PAT.findall(txt); ids = sorted(set(found))
                if ids: files.append(dict(path=p, ids=ids, n={i: found.count(i) for i in ids}, call=bool(CALL.search(txt)), h=hashlib.sha1(b).hexdigest()[:12]))
        return dict(base, status="ok", nfiles=n, agents=sorted(agents), files=files)
    except Exception as e:
        return dict(base, status="err:" + type(e).__name__)
rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
with cf.ThreadPoolExecutor(16) as ex, open(sys.argv[2], "w", encoding="utf-8") as out:
    for r in ex.map(scan, rows): out.write(json.dumps(r) + "\n")
print(sys.argv[2], "done")
