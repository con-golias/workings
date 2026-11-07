"""Hand verdicts (6 Nov 2026) for the 55 most-downloaded flagged agent packages, read in their install-time code.
scope: global = writes into a user-level agent config or folder (~/.claude*, ~/.codex, ~/.cursor, ~/.gemini,
~/.config/opencode, Claude Desktop config); project = writes into the project's .claude/.cursor/...; none = only prints,
checks or reads; unclear = could not settle from the code.
what: instructions (CLAUDE.md / AGENTS.md / rules), hooks (commands the agent runs later), mcp (server entries),
settings (env, permissions, statusline, plugins, output style), files (skills, commands, agents copied in).
global_only: the write runs only on `npm install -g` (npm_config_global checked); False = also when installed as a dependency.
optout: an environment variable stops it.  grant: the package also grants itself trust or permissions.
product: what the package is for, when it is not an agent add-on (the Postman shape)."""
import json
V = {
 "whatshell": dict(scope="global", what=["files"], global_only=False, optout=True),
 "postman-cli": dict(scope="global", what=["instructions"], global_only=True, optout=False, product="API client CLI"),
 "toga-ai": dict(scope="global", what=["settings", "files"], global_only=False, optout=True, note="telemetry env in ~/.claude/settings.json: prompts, responses, tool details to the vendor's OTLP collector"),
 "@nanonets/graft": dict(scope="none"), "@codyswann/lisa": dict(scope="project", what=["settings", "files"], global_only=False, optout=False),
 "@muggleai/works": dict(scope="global", what=["mcp", "files"], global_only=True, optout=False),
 "@trailhq/trail-code": dict(scope="none"), "aidevops": dict(scope="none"),
 "triflux": dict(scope="global", what=["hooks", "settings", "files"], global_only=False, optout=False, grant=True, note="writes Codex hooks with trusted_hash entries (ensure-codex-hooks.mjs:160); permission rules in ~/.claude/settings.json (native-peer-permissions.mjs:423)"),
 "@su-record/vibe": dict(scope="global", what=["hooks", "instructions"], global_only=True, optout=True),
 "local-mcp": dict(scope="global", what=["mcp"], global_only=True, optout=True),
 "passoff": dict(scope="global", what=["files"], global_only=False, optout=True),
 "karajan-code": dict(scope="global", what=["mcp"], global_only=False, optout=False),
 "@minhspark/codex-mcp-bridge": dict(scope="global", what=["mcp"], global_only=True, optout=True),
 "@ooples/token-optimizer-mcp": dict(scope="none", note="stopped writing hooks after issue #449; now prints a hint"),
 "sprag-cli": dict(scope="none"), "@karajan-family/code": dict(scope="global", what=["mcp"], global_only=False, optout=False),
 "aicodeman": dict(scope="none"),
 "claude-all-config": dict(scope="global", what=["files", "mcp", "settings"], global_only=False, optout=False, grant=True, note="overwrites ~/.claude/settings.json with permissions.allow Bash(*), Write(*), Edit(*), mcp__*; Gemini settings autoAccept true with 'never ask permission' system prompt; Codex config.toml approval_policy = \"never\" (postinstall.js:270-284, 406-431, 500)"),
 "@kaitranntt/ccs": dict(scope="global", what=["settings"], global_only=False, optout=False, note="creates an empty ~/.claude/settings.json if missing"),
 "@tpsdev-ai/flair-mcp": dict(scope="none"), "@acedatacloud/skills": dict(scope="none"), "great-cto": dict(scope="none"),
 "xlsx-for-ai": dict(scope="global", what=["mcp"], global_only=True, optout=False),
 "@polymorphism-tech/morph-spec": dict(scope="global", what=["settings"], global_only=False, optout=False, grant=True, note="statusline + permissions it adds to Claude settings (claude-settings-manager.js)"),
 "@babylonjs-toolkit/agent": dict(scope="global", what=["hooks", "files"], global_only=True, optout=False),
 "devez-vibe": dict(scope="global", what=["files"], global_only=False, optout=False),
 "0xray": dict(scope="none"), "@astudioplus/codegraph-mcp": dict(scope="none"), "@essentialai/cogent-bridge": dict(scope="unclear"),
 "pm-claude-skills": dict(scope="none"),
 "peaks-loop": dict(scope="global", what=["files", "settings"], global_only=False, optout=True),
 "@ciandt-flow/flow-ai-obs": dict(scope="global", what=["hooks"], global_only=False, optout=False),
 "@leviyuan/lodestar": dict(scope="none", note="removes its own old skills"),
 "agent-security-scanner-mcp": dict(scope="none"),
 "thetacog-mcp": dict(scope="global", what=["files", "hooks"], global_only=False, optout=True),
 "novahiz": dict(scope="global", what=["settings", "files"], global_only=False, optout=False, note="postinstall passes --yes"),
 "@volter/supercode": dict(scope="unclear"), "@antoneeo/course-creator": dict(scope="unclear"),
 "nori-skillsets": dict(scope="global", what=["settings"], global_only=False, optout=False, note="removes stale hook entries"),
 "nansen-cli": dict(scope="global", what=["files"], global_only=True, optout=False, product="crypto analytics and DEX trading CLI"),
 "@jelou/cli": dict(scope="none"),
 "@agentgates/cli": dict(scope="global", what=["instructions"], global_only=False, optout=False, product="wallet operations CLI"),
 "moflo": dict(scope="project", what=["hooks", "files"], global_only=False, optout=False),
 "grok-faf-mcp": dict(scope="none"),
 "tmux-ide": dict(scope="global", what=["files", "settings"], global_only=True, optout=False),
 "overmind-mcp": dict(scope="none"), "claude-faf-mcp": dict(scope="none"),
 "claude-glm-agent": dict(scope="global", what=["files"], global_only=False, optout=False),
 "@optima-chat/dev-skills": dict(scope="global", what=["files"], global_only=False, optout=False),
 "@usebitl/cli": dict(scope="unclear"),
 "@jenga-ai/agent": dict(scope="project", what=["files"], global_only=False, optout=False),
 "@nordsym/apiclaw": dict(scope="none"),
 "greprag": dict(scope="global", what=["files"], global_only=False, optout=False),
 "omnishpilot": dict(scope="global", what=["files"], global_only=True, optout=True),
}
SH = json.load(open("../data/sheet.json"))
top = SH[:55]
assert set(r["name"] for r in top) == set(V), set(r["name"] for r in top) ^ set(V)
out = []
for r in top:
    v = dict(V[r["name"]]); v.update(name=r["name"], downloads=r["downloads"], description=r["description"], npx_latest=r["npx_latest"])
    out.append(v)
json.dump({"criterion": __doc__, "read": out}, open("../data/verdicts.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)
G = [v for v in out if v["scope"] == "global"]; P = [v for v in out if v["scope"] == "project"]
dl = lambda S: sum(v["downloads"] or 0 for v in S)
print("read", len(out), "downloads", dl(out)); print("global", len(G), dl(G), "| project", len(P), dl(P), "| none", sum(v["scope"] == "none" for v in out), "| unclear", sum(v["scope"] == "unclear" for v in out))
for k in ["instructions", "hooks", "mcp", "settings", "files"]: print(" ", k, sum(k in v.get("what", []) for v in G))
print(" as dependency too:", sum(not v["global_only"] for v in G), dl([v for v in G if not v["global_only"]]))
print(" no opt-out:", sum(not v["optout"] for v in G), "| grant:", sum(bool(v.get("grant")) for v in G), "| products:", [v["name"] for v in G if v.get("product")])
