# The agent shares by year with a bootstrap range, the same-repo check, and how many agents each repo sets up.
import json, sys, random
import numpy as np
from collections import Counter
rows = [r for r in json.load(open(sys.argv[1])) if r["commits"] > 0]
AG = ["claude", "agentsmd", "codex", "opencode", "gemini", "aider"]; ED = ["cursor", "copilot"]
YEARS = [2022, 2023, 2024, 2025, 2026]
agent = lambda r: any(r[k] for k in AG)
out = {"years": {}}
for y in YEARS:
    rs = [r for r in rows if r["year"] == y]; n = len(rs)
    out["years"][y] = {"active": n, "agents": sum(map(agent, rs)) / n, "editor": sum(any(r[k] for k in ED) for r in rs) / n,
                       "any": sum(agent(r) or any(r[k] for k in ED) for r in rs) / n, **{k: sum(r[k] for r in rs) / n for k in AG + ED}}
# Bootstrap 95% interval over repos for 2026 and 2024 agents share
for y in (2024, 2025, 2026):
    v = np.array([agent(r) for r in rows if r["year"] == y], float)
    rng = np.random.default_rng(2026); bs = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(1000)]
    out["years"][y]["agents_ci95"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
# Same-repo check: active in both 2024 and 2026
by = {}
for r in rows: by.setdefault(r["repo"], {})[r["year"]] = r
panel = [d for d in by.values() if 2024 in d and 2026 in d]
out["panel"] = {"n": len(panel), "agents_2024": sum(agent(d[2024]) for d in panel) / len(panel), "agents_2026": sum(agent(d[2026]) for d in panel) / len(panel)}
new = [d for d in by.values() if 2026 in d and 2024 not in d]
out["new_in_2026_or_dormant"] = {"n": len(new), "agents_2026": sum(agent(d[2026]) for d in new) / len(new)}
# How many agents per repo in 2026, and which combos
r26 = [r for r in rows if r["year"] == 2026]
k = Counter(sum(r[x] for x in ["claude", "codex", "opencode", "gemini", "aider"]) for r in r26 if agent(r))
out["tools_per_agent_repo_2026"] = dict(sorted(k.items()))
pairs = Counter(tuple(x for x in AG if r[x]) for r in r26 if agent(r)); out["combos_2026"] = [[list(c), n] for c, n in pairs.most_common(12)]
# What is inside: skills, hooks, subagents, commands, MCP, memory, settings (claude paths in 2026)
json.dump(out, open(sys.argv[2], "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str)[:3500])
