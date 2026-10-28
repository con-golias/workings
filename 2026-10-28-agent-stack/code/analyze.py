# Every number in the article and the charts comes from here: data/summary.json.
#   python3 code/analyze.py <raw dir>     (raw dir holds the *_meta.json / *_hist.json files written by fetch_*.py)
#
# Groups
#   2024             TS/JS repositories created 1-24 Oct 2024 (search order: best match), package.json read at the
#                    last commit on or before 30 Nov 2024.
#   2026 (primary)   TS/JS repositories created 1-24 Oct 2026, same search, same order (best match), package.json at HEAD.
#   2026 (updated)   Same, searched in "recently updated" order: the robustness sample.
#   traced           A 2026 repository with any AI-tool trace: an agent co-author trailer in its last 50 commits
#                    (Claude, Cursor, Codex), an agent instruction file at the root (CLAUDE.md, .claude, AGENTS.md,
#                    .cursor, .cursorrules, .codex, GEMINI.md, .windsurfrules, .windsurf, .kiro, .trae), or an
#                    app-builder signature (lovable-tagger, an AI Studio / Lovable / Bolt / v0 README, .replit, .idx).
#   untraced         A 2026 repository with none of these. Not the same as "written by a person": Copilot leaves no
#                    trace we can read, and trailers can be switched off.
# Unit: one repository per owner (the first one seen), so a prolific account counts once.
# A share in a category is taken among the owners whose package.json lists at least one package of that category.
import json
import os
import random
import re
import sys

RAW = sys.argv[1] if len(sys.argv) > 1 else "raw"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "summary.json")
exec(open(os.path.join(HERE, "categories.py"), encoding="utf-8").read())  # CATS, deps_of, usable
exec(open(os.path.join(HERE, "tags.py"), encoding="utf-8").read())  # scaffold, markers, builder


def load(name):
    p = os.path.join(RAW, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def traced(r, d, v, h):
    h = h or {}
    return bool(h.get("claude") or h.get("cursor") or h.get("codex") or markers(v) or builder(r, d, v, h.get("readme")))


def groups_2026(meta, hist):
    rows = usable(meta)
    t = [x for x in rows if traced(x[0], x[1], x[2], hist.get(x[0]))]
    u = [x for x in rows if not traced(x[0], x[1], x[2], hist.get(x[0]))]
    return rows, t, u


def per_owner(rows, cond=lambda d: True):
    seen = {}
    for r, d, v in rows:
        if cond(d):
            seen.setdefault(r.split("/")[0], d)
    return list(seen.values())


def share(rows, cat, pkg, cond=lambda d: True, B=2000, seed=1):
    pk = CATS[cat]
    L = [d for d in per_owner(rows, lambda d: cond(d) and any(x in d for x in pk))]
    if not L:
        return None
    hit = [1 if pkg in d else 0 for d in L]
    rnd = random.Random(seed)
    boot = sorted(sum(rnd.choices(hit, k=len(hit))) / len(hit) for _ in range(B))
    return {"pct": round(100 * sum(hit) / len(hit), 1), "n": len(hit),
            "lo": round(100 * boot[int(0.025 * B)], 1), "hi": round(100 * boot[int(0.975 * B)], 1)}


def dist(rows, cat, cond=lambda d: True):
    pk = CATS[cat]
    L = per_owner(rows, lambda d: cond(d) and any(x in d for x in pk))
    return {"n": len(L), "shares": {p: round(100 * sum(1 for d in L if p in d) / len(L), 1) for p in pk} if L else {}}


REACT = lambda d: "react" in d
ANY = lambda d: True
ROWS = [  # (key, category, package, condition, label)
    ("axios", "data fetching", "axios", REACT, "React apps: axios"),
    ("tanstack", "data fetching", "@tanstack/react-query", REACT, "React apps: TanStack Query"),
    ("mongoose", "ORM / query builder", "mongoose", ANY, "Database layer: mongoose (MongoDB)"),
    ("drizzle", "ORM / query builder", "drizzle-orm", ANY, "Database layer: drizzle"),
    ("prisma", "ORM / query builder", "@prisma/client", ANY, "Database layer: prisma"),
    ("firebase", "backend-as-a-service", "firebase", ANY, "Hosted backend: firebase"),
    ("supabase", "backend-as-a-service", "@supabase/supabase-js", ANY, "Hosted backend: supabase"),
    ("redux", "state management", "@reduxjs/toolkit", REACT, "React apps: Redux Toolkit"),
    ("zustand", "state management", "zustand", REACT, "React apps: zustand"),
    ("jest", "unit test runner", "jest", ANY, "Unit tests: jest"),
    ("vitest", "unit test runner", "vitest", ANY, "Unit tests: vitest"),
    ("zod", "schema validation", "zod", ANY, "Validation: zod"),
    ("tailwind", "CSS", "tailwindcss", ANY, "Styling: tailwindcss"),
    ("lucide", "icons", "lucide-react", ANY, "Icons: lucide-react"),
    ("react_icons", "icons", "react-icons", ANY, "Icons: react-icons"),
    ("styled", "CSS", "styled-components", ANY, "Styling: styled-components"),
    ("emotion", "CSS", "@emotion/react", ANY, "Styling: @emotion/react"),
    ("webpack", "bundler/dev server", "webpack", ANY, "Bundler: webpack"),
    ("vite", "bundler/dev server", "vite", ANY, "Bundler: vite"),
    ("next", "React meta-framework", "next", ANY, "React framework: next"),
    ("eslint", "linter", "eslint", ANY, "Linter: eslint"),
    ("prettier", "formatter", "prettier", ANY, "Formatter: prettier"),
]


def table(groups):
    out = {}
    for key, cat, pkg, cond, label in ROWS:
        out[key] = {"label": label, **{g: share(rows, cat, pkg, cond) for g, rows in groups.items()}}
    return out


S = {}
m24 = load("ctl24_meta.json")
g24 = [x for x in usable(m24, since="2024-10-01") if x[2]["created"] < "2024-11-01"]
asof = [v.get("asof", "") for v in m24.values() if v]
S["sample_2024"] = {"searched": len(m24), "resolved": len(asof), "usable": len(g24),
                    "owners": len(per_owner(g24)), "asof_after_nov30": sum(1 for a in asof if a > "2024-11-30T23:59:59Z"),
                    "asof_in_oct_nov": sum(1 for a in asof if "2024-10-01" <= a <= "2024-11-30T23:59:59Z"),
                    "agent_marker_files": sum(1 for r, d, v in g24 if markers(v))}

mb, hb = load("ctlbm_meta.json"), load("ctlbm_hist.json")
rb, tb, ub = groups_2026(mb, hb)
mu, hu = load("ctl_meta.json"), load("ctl_hist.json")
ru, tu, uu = groups_2026(mu, hu)
for k, (m, rows, t, u) in {"sample_2026": (mb, rb, tb, ub), "sample_2026_updated": (mu, ru, tu, uu)}.items():
    S[k] = {"searched": len(m), "usable": len(rows), "owners": len(per_owner(rows)),
            "traced": len(t), "untraced": len(u), "traced_owners": len(per_owner(t)), "untraced_owners": len(per_owner(u)),
            "traced_pct": round(100 * len(t) / len(rows), 1) if rows else None}

S["rows"] = table({"y2024": g24, "untraced": ub, "traced": tb})
S["rows_updated"] = table({"y2024": g24, "untraced": uu, "traced": tu})

# Template clones: many owners can create the same project from one tutorial or template (identical dependency set).
# Keep one repository per identical set of dependency names, then one per owner, and recompute.
def dedup(rows):
    seen, out = set(), []
    for x in rows:
        key = frozenset(x[1])
        if key not in seen:
            seen.add(key)
            out.append(x)
    return out


S["clones"] = {g: {"repos": len(rows), "unique_dep_sets": len(dedup(rows))} for g, rows in
               {"y2024": g24, "untraced": ub, "traced": tb}.items()}
S["rows_dedup"] = table({"y2024": dedup(g24), "untraced": dedup(ub), "traced": dedup(tb)})

# 2024 with the same file-based tests as 2026 (no commit history or README was read for 2024).
S["sample_2024"]["file_traces"] = sum(1 for r, d, v in g24 if markers(v) or builder(r, d, v, None))
S["sample_2024"]["file_traces_pct"] = round(100 * S["sample_2024"]["file_traces"] / len(g24), 1)

# Gemini SDK check: AI Studio exports often leave no README banner; drop @google/genai repos from "untraced".
S["rows_untraced_no_genai"] = table({"untraced": [x for x in ub if "@google/genai" not in x[1]],
                                     "genai_only": [x for x in ub if "@google/genai" in x[1]]})

# Project depth: dependency-count tertiles over the primary 2026 sample.
counts = sorted(len(d) for _, d, _ in rb)
c1, c2 = counts[len(counts) // 3], counts[2 * len(counts) // 3]
S["depth_cuts"] = [c1, c2]
med = lambda xs: sorted(xs)[len(xs) // 2] if xs else None
S["median_deps"] = {"untraced": med([len(d) for _, d, _ in ub]), "traced": med([len(d) for _, d, _ in tb]),
                    "y2024": med([len(d) for _, d, _ in g24])}
t3 = lambda d: "@trpc/server" in d or "@t3-oss/env-nextjs" in d
S["t3"] = {"traced": sum(1 for _, d, _ in tb if t3(d)), "untraced": sum(1 for _, d, _ in ub if t3(d)),
           "y2024": sum(1 for _, d, _ in g24 if t3(d))}
S["depth"] = {}
for name, (lo, hi) in {"low": (0, c1), "mid": (c1, c2), "high": (c2, 10 ** 9)}.items():
    f = lambda rows, lo=lo, hi=hi: [x for x in rows if lo <= len(x[1]) < hi]
    S["depth"][name] = table({"untraced": f(ub), "traced": f(tb)})

# Full distributions for the categories the article discusses.
S["dist"] = {}
for cat, cond in [("ORM / query builder", ANY), ("data fetching", REACT), ("backend-as-a-service", ANY),
                  ("state management", REACT), ("unit test runner", ANY), ("schema validation", ANY), ("CSS", ANY),
                  ("icons", ANY), ("bundler/dev server", ANY), ("React meta-framework", ANY), ("linter", ANY), ("formatter", ANY)]:
    S["dist"][cat] = {g: dist(rows, cat, cond) for g, rows in {"y2024": g24, "untraced": ub, "traced": tb}.items()}

# Agent co-author samples (commit search): confirmation only.
for name, trailer in [("agent", "claude"), ("cursor", "cursor"), ("codex", "codex")]:
    m, h = load(f"{name}_meta.json"), load(f"{name}_hist.json")
    rows = [x for x in usable(m) if h.get(x[0]) and h[x[0]]["n"] and h[x[0]][trailer] / h[x[0]]["n"] >= 0.5]
    S[f"strict_{trailer}"] = {"searched": len(m), "strict": len(rows), "owners": len(per_owner(rows)),
                              "rows": table({"strict": rows}) if len(rows) >= 100 else None}

# Scaffold and builder counts in the primary sample.
S["scaffold"] = {g: {} for g in ("traced", "untraced")}
for g, rows, H in (("traced", tb, hb), ("untraced", ub, hb)):
    for r, d, v in rows:
        for t in scaffold(d, v, H.get(r)) or {"none"}:
            S["scaffold"][g][t] = S["scaffold"][g].get(t, 0) + 1
S["trace_kinds"] = {}
for r, d, v in tb:
    h = hb.get(r) or {}
    kinds = (["trailer:" + k for k in ("claude", "cursor", "codex") if h.get(k)] + ["file:" + m for m in markers(v)]
             + ["builder:" + b for b in builder(r, d, v, h.get("readme"))])
    for k in set(kinds):
        S["trace_kinds"][k] = S["trace_kinds"].get(k, 0) + 1

# Instruction files: did the developer name the library for the agent? A traced project is "pinned" in a category
# if its CLAUDE.md / AGENTS.md / .cursorrules / GEMINI.md names any package of that category.
INSTR = load("ctlbm_instr.json")
PIN = {"data fetching": r"axios|tanstack|react-query|react query|\bswr\b|apollo",
       "ORM / query builder": r"drizzle|prisma|mongoose|mongodb|kysely|typeorm|sequelize",
       "backend-as-a-service": r"firebase|supabase|convex|clerk|appwrite|pocketbase"}
S["instructions"] = {"traced_with_file": sum(1 for r, _, _ in tb if r in INSTR)}
for cat, rx in PIN.items():
    pinned = {r for r, _, _ in tb if r in INSTR and re.search(rx, INSTR[r], re.I)}
    users = [x for x in tb if any(p in x[1] for p in CATS[cat])]
    S["instructions"][cat] = {"users": len(users), "users_with_file": sum(1 for r, _, _ in users if r in INSTR),
                              "users_pinned": sum(1 for r, _, _ in users if r in pinned)}
    unp = [x for x in tb if x[0] not in pinned]
    for key, c2, pkg, cond, _ in ROWS:
        if c2 == cat:
            S["instructions"].setdefault("unpinned_rows", {})[key] = share(unp, c2, pkg, cond)

# Derived figures the text states in words (ratios, point changes), computed here so none is typed by hand.
S["derived"] = {}
for key, row in S["rows"].items():
    a, u, t = ((row.get(g) or {}).get("pct") for g in ("y2024", "untraced", "traced"))
    if None in (a, u, t):
        continue
    S["derived"][key] = {"change_2024_to_traced": round(t - a, 1), "gap_untraced_traced": round(t - u, 1),
                         "ratio_2024_over_traced": round(a / t, 1) if t else None,
                         "ratio_traced_over_2024": round(t / a, 1) if a else None,
                         "ratio_untraced_over_traced": round(u / t, 1) if t else None}

# The default pick in each category among traced repositories (descriptive: "what an agent-built app ships with").
S["default_stack"] = {}
for cat, d in S["dist"].items():
    sh = d["traced"]["shares"]
    if sh:
        top = max(sh, key=sh.get)
        S["default_stack"][cat] = {"pkg": top, "pct": sh[top], "n": d["traced"]["n"],
                                   "pct_2024": d["y2024"]["shares"].get(top), "pct_untraced": d["untraced"]["shares"].get(top)}

json.dump(S, open(OUT, "w", encoding="utf-8"), indent=1)
print("wrote", OUT)
