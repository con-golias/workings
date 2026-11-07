"""For every package with an install script: download the tarball (kept locally, not in workings), find the files the
install command runs plus the relative files they import (one level), and flag any that name an AI agent's config
path. Output ../data/scan.json (one row per package with flags and the matching lines)."""
import json, re, os, io, tarfile, posixpath, urllib.request, concurrent.futures as cf, sys, time
S = json.load(open("../data/install_scripts.json"))
os.makedirs("../data/tarballs", exist_ok=True)
PATH = re.compile(r"""\.claude\.json|\.claude[/\'"`]|claude_desktop_config|\.codex[/\'"`]|\.cursor[/\'"`]|\.gemini[/\'"`]|\.mcp\.json|windsurf|\.codeium|\.continue[/\'"`]|\.opencode|\.config/opencode|\.kiro[/\'"`]|\.amp[/\'"`]""", re.I)
WRITE = re.compile(r"writeFile|appendFile|copyFile|cpSync|\bcp\(|symlink|mkdir|createWriteStream|rename|outputFile|writeJson|>>?\s*[\"'$~]|\bcp -|\bln -s|\btee\b", re.I)
GRANT = re.compile(r"trusted_hash|trusted_content_hash|enableAllProjectMcpServers|bypassPermissions|dangerously-skip-permissions|skipDangerousModePermissionPrompt|\"allow\"\s*:|permissions\.allow|autoApprove|alwaysAllow|approval_policy|sandbox_mode", re.I)
IMP = re.compile(r"""(?:require\(|import\s*\(|from\s+|import\s+)['"](\.{1,2}/[^'"]+)['"]""")
def fetch(n, url):
    p = "../data/tarballs/" + n.replace("/", "__") + ".tgz"
    if not os.path.exists(p):
        for i in range(4):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "workings-research"}), timeout=120) as r: b = r.read()
                open(p, "wb").write(b); break
            except Exception:
                time.sleep(2 * (i + 1))
    return p
def resolve(files, base, rel):
    c = posixpath.normpath(posixpath.join(posixpath.dirname(base), rel))
    for cand in (c, c + ".js", c + ".cjs", c + ".mjs", c + "/index.js", c + ".ts"):
        if cand in files: return cand
def one(item):
    n, r = item
    if not r.get("install") or not r.get("tarball"): return None
    try:
        p = fetch(n, r["tarball"]); t = tarfile.open(p)
        files = {}
        for m in t.getmembers():
            if m.isfile() and m.size < 3_000_000:
                files[m.name.split("/", 1)[1] if "/" in m.name else m.name] = m
        cmd = " ".join(r["scripts"].values())
        roots = set()
        for f in re.findall(r"[\w@./-]+\.(?:c?js|mjs|sh|cjs|ts|py)\b", cmd):
            f = f.lstrip("./")
            if f in files: roots.add(f)
        seen, hits = set(), {}
        todo = [(f, 0) for f in roots]
        while todo:
            f, d = todo.pop()
            if f in seen: continue
            seen.add(f)
            txt = t.extractfile(files[f]).read().decode("utf8", "ignore")
            lines = [l for l in txt.splitlines() if PATH.search(l)]
            if lines: hits[f] = {"path_lines": [l.strip()[:220] for l in lines[:12]], "writes": bool(WRITE.search(txt)), "depth": d,
                                  "npx_latest": bool(re.search(r"npx (-y|--yes)|@latest", txt)),
                                  "self_trust": sorted(set(m.lower() for m in GRANT.findall(txt)))}
            if d < 1:
                for rel in IMP.findall(txt):
                    g = resolve(files, f, rel)
                    if g: todo.append((g, d + 1))
        cmdhit = bool(PATH.search(cmd))
        return n, {"files_read": sorted(seen), "hits": hits, "cmd_hit": cmdhit, "cmd": cmd[:300]}
    except Exception as e:
        return n, {"error": str(e)[:120]}
items = [(n, r) for n, r in S.items() if r.get("install")]
out = {}
with cf.ThreadPoolExecutor(12) as ex:
    for res in ex.map(one, items):
        if res: out[res[0]] = res[1]
json.dump(out, open("../data/scan.json", "w"), indent=0)
flag = [n for n, v in out.items() if v.get("hits") or v.get("cmd_hit")]
print("scanned", len(out), "errors", sum(1 for v in out.values() if "error" in v), "flagged", len(flag), file=sys.stderr)
