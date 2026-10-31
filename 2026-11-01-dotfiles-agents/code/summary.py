# One summary.json with every number the article and its figures use.
import json, re, sys
from collections import Counter
S = sys.argv[1]
ai = json.load(open(f"{S}/ai_summary.json")); ins = json.load(open(f"{S}/ai_inside.json")); first = json.load(open(f"{S}/ai_first.json"))
sh = json.load(open(f"{S}/test_full.json"))["shares"]
best = []
for k, s in sh.items():
    ys = sorted(s, key=int); g = max((float(s[b]) - float(s[a]), b, float(s[a]), float(s[b])) for a, b in zip(ys, ys[1:]))
    best.append({"signal": k, "rise": round(g[0] * 100, 1), "year": int(g[1]), "from": round(g[2] * 100, 1), "to": round(g[3] * 100, 1)})
y = ai["years"]
ag = lambda d: round(d["agents"] * 100, 1)
best.append({"signal": "any_agent", "rise": round(ag(y["2026"]) - ag(y["2025"]), 1), "year": 2026, "from": ag(y["2025"]), "to": ag(y["2026"])})
best.sort(key=lambda b: -b["rise"])
a = {(r["repo"]): r for r in json.load(open(f"{S}/ai_rows.json")) if r["year"] == 2026 and r["commits"] > 0}
f = {r["repo"]: r for r in json.load(open(f"{S}/rows_full.json")) if r["year"] == 2026 and r["commits"] > 0}
AG = ["claude", "agentsmd", "codex", "opencode", "gemini", "aider"]; has = lambda r: any(r[k] for k in AG)
who = []
for t in ["zed", "brewfile", "wezterm", "ghostty", "vscode", "nix", "neovim", "vim", "kitty", "hyprland", "emacs"]:
    yes = [n for n in a if n in f and f[n][t]]; no = [n for n in a if n in f and not f[n][t]]
    who.append({"tool": t, "n": len(yes), "with": round(100 * sum(has(a[n]) for n in yes) / len(yes), 1), "without": round(100 * sum(has(a[n]) for n in no) / len(no), 1)})
months = Counter(min(x["first"].values())[:7] for x in first if x["first"])
out = {"population": 57421, "sample": 6000, "cloned": 5978, "active_any_year": 5633,
       "years": {k: v for k, v in y.items() if k != "thresholds"}, "panel": ai["panel"], "newcomers": ai["new_in_2026_or_dormant"],
       "agent_repos_2026": ins["agent_repos"], "two_or_more": sum(v for k, v in ai["tools_per_agent_repo_2026"].items() if int(k) >= 2),
       "combos_2026": ai["combos_2026"], "inside": ins["kinds"], "files_median": ins["files_median"], "files_p90": ins["files_p90"],
       "biggest_rise": best[:12], "who": who, "first_month": dict(sorted(months.items())),
       "decade": {k: {y: round(float(v) * 100, 1) for y, v in sh[k].items()} for k in ("neovim", "fzf", "ghostty", "eza", "catppuccin", "alacritty")},
       "decade_test": {"original": "drop, bootstrap 0/1000", "amended": "drop, median 4 vs 4 years, bootstrap 86/1000"}}
json.dump(out, open(sys.argv[2], "w"), indent=1)
print(json.dumps({k: out[k] for k in ("panel", "two_or_more", "biggest_rise")}, indent=0)[:1500])
