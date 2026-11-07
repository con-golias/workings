"""Review sheet for the flagged agent-ecosystem packages: signals pulled from the install-time files, to be checked
by hand. Output ../data/sheet.json."""
import json, re, tarfile
SC = json.load(open("../data/scan.json")); IS = json.load(open("../data/install_scripts.json")); D = json.load(open("../data/downloads.json"))
SIG = {
 "hooks": r"\bhooks\b|SessionStart|PreToolUse|PostToolUse|UserPromptSubmit|session_start",
 "mcp": r"mcpServers|mcp_servers|\[mcp_servers",
 "statusline": r"statusLine|statusline",
 "files": r"skills|commands|agents[/\'\"]|CLAUDE\.md|AGENTS\.md|plugins",
 "guard_ci": r"process\.env\.CI\b|isCI|\bCI\b\s*[)=!]|is-ci|ci-info",
 "guard_global": r"npm_config_global",
 "guard_tty": r"isTTY|readline|inquirer|prompts\(|@clack|enquirer|confirm\(",
 "guard_env": r"process\.env\.[A-Z_]*(SKIP|DISABLE|NO_|OPT|QUIET|POSTINSTALL)[A-Z_]*",
 "backup": r"\.bak|\.bkp|backup",
}
SIG = {k: re.compile(v) for k, v in SIG.items()}
out = []
for n, v in SC.items():
    if not (v.get("hits") or v.get("cmd_hit")): continue
    if not any(s.startswith("A:") for s in IS[n]["sets"]): continue
    t = tarfile.open("../data/tarballs/" + n.replace("/", "__") + ".tgz")
    files = {m.name.split("/", 1)[1] if "/" in m.name else m.name: m for m in t.getmembers() if m.isfile()}
    txt = "\n".join(t.extractfile(files[f]).read().decode("utf8", "ignore") for f in v["files_read"] if f in files)
    sig = {k: bool(p.search(txt)) for k, p in SIG.items()}
    out.append({"name": n, "downloads": D.get(n), "description": IS[n].get("description", ""), "cmd": v["cmd"], "files": v["files_read"],
                "writes": any(h["writes"] for h in v["hits"].values()), "npx_latest": any(h["npx_latest"] for h in v["hits"].values()),
                "self_trust": sorted(set(x for h in v["hits"].values() for x in h["self_trust"])), **sig,
                "path_lines": [l for h in v["hits"].values() for l in h["path_lines"]][:6]})
out.sort(key=lambda r: -(r["downloads"] or 0))
json.dump(out, open("../data/sheet.json", "w"), indent=1)
print(len(out), "packages; total weekly downloads", sum(r["downloads"] or 0 for r in out))
print("writes+any guard none:", sum(1 for r in out if r["writes"] and not (r["guard_ci"] or r["guard_global"] or r["guard_tty"] or r["guard_env"])))
for r in out[:45]:
    g = "".join(c for c, k in (("C","guard_ci"),("G","guard_global"),("T","guard_tty"),("E","guard_env")) if r[k])
    w = "".join(c for c, k in (("H","hooks"),("M","mcp"),("S","statusline"),("F","files")) if r[k])
    print("%8s %-38s W=%d %-4s guard=%-4s npx=%d trust=%s | %s" % (r["downloads"], r["name"][:38], r["writes"], w, g, r["npx_latest"], ",".join(r["self_trust"])[:30], r["description"][:60]))
