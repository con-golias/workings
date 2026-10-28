# Every number in the article comes from here: data/summary.json.
#   python3 code/analyze.py <raw dir>
#
# Groups (all GitHub repositories created 1-24 Oct 2025; one repository per owner):
#   lovable   README contains the Lovable export template ("Lovable project" / lovable.dev/projects); census by day,
#             then a random 6,000 for the activity fetch.
#   aistudio  README contains the AI Studio export template ("Run and deploy your AI Studio app" / ai.studio/apps);
#             census, then a random 4,000. In Oct 2025, edits made inside AI Studio reached GitHub only when the user
#             pushed them, so its activity is a lower bound.
#   v0        README contains the v0 template ("stay in sync with your deployed chats"); full census.
#   baseline  random pages of GET /repositories?since=<id> inside the ID range of 1-24 Oct 2025, kept if not a fork,
#             with a root package.json, and with no builder signature in the README or commits.
# Activity = a commit not made by a dependency or CI bot (dependabot, renovate, github-actions, ...). Builder bots
# (lovable-dev[bot], v0[bot]) count: they are a person editing in the builder. Only the latest 30 commits are read.
import datetime as dt
import json
import os
import random
import re
import sys

RAW = sys.argv[1] if len(sys.argv) > 1 else "raw"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "summary.json")
load = lambda n: json.load(open(os.path.join(RAW, n), encoding="utf-8"))

BOT = re.compile(r"dependabot|renovate|github-actions|actions@github|pre-commit-ci|imgbot|snyk|greenkeeper|allcontributors|semantic-release|vercel\[bot\]|netlify\[bot\]", re.I)
# Other AI app tools that can also commit to a repository (not counted as "a person outside the builder").
OTHER_TOOL = re.compile(r"orchids-app|builderio-bot|builder-io|emergent-agent|replit|bolt|copilot-swe-agent|devin-ai", re.I)
BUILDER_BOT = re.compile(r"lovable-dev\[bot\]|gpt-engineer-app|v0\[bot\]", re.I)
BUILDER_LOGINS = {"v0", "lovable-dev[bot]", "v0[bot]"}
is_builder = lambda e, l, n: bool(BUILDER_BOT.search(e + l + n)) or l in BUILDER_LOGINS or n == "v0"
SIG = {"lovable": r"Welcome to your Lovable project|lovable\.dev/projects",
       "aistudio": r"Run and deploy your AI Studio app|ai\.studio/apps",
       "v0": r"stay in sync with your deployed chats"}
ANY_BUILDER = re.compile(r"Lovable project|lovable\.dev|AI Studio app|ai\.studio/apps|v0\.(dev|app)|bolt\.new|gpt-engineer-app|lovable-dev\[bot\]|v0\[bot\]", re.I)
P = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
RECENT = dt.datetime(2026, 7, 28, tzinfo=dt.timezone.utc)  # three months before the data was read (28 Oct 2026)

census = load("census_repos.json")
census_counts = load("census_counts.json")
act = load("builder_act.json")
v0act = load("v0_act.json")
v0counts = load("census_v0_counts.json")
base = load("base_act.json")
base_meta = load("base_meta.json")
online = {**load("online.json"), **{k: {**v, "g": "v0"} for k, v in load("online_v0.json").items()}}


def uploaded_old(a):
    # Oldest observed commit more than 14 days before the repository existed: an older project uploaded in October.
    # Only decidable when every commit was read (total <= 30).
    ds = [P(d) for d, *_ in a["commits"]]
    return bool(ds) and a["total"] <= len(a["commits"]) and min(ds) < P(a["created"]) - dt.timedelta(days=14)


def groups(drop_old=True):
    G = {}
    for g in ("lovable", "aistudio"):
        G[g] = [(r, a) for r, a in act.items() if a and census[r]["g"] == g and re.search(SIG[g], a["readme"] or "", re.I)]
    G["v0"] = [(r, a) for r, a in v0act.items() if a and re.search(SIG["v0"], a["readme"] or "", re.I)]
    nb = [(r, a) for r, a in base.items() if a and not a["fork"] and not ANY_BUILDER.search(a["readme"] or "")
          and not any(ANY_BUILDER.search(e + l + n) for _, e, l, n in a["commits"])]
    G["baseline"] = nb
    G["baseline_react"] = [(r, a) for r, a in nb if (base_meta.get(r) or {}).get("pkg") and '"react"' in base_meta[r]["pkg"]]
    if drop_old:
        G = {g: [(r, a) for r, a in rows if not uploaded_old(a)] for g, rows in G.items()}
    return G


def per_owner(rows):
    o = {}
    for r, a in rows:
        o.setdefault(r.split("/")[0], (r, a))
    return list(o.values())


def human(a):
    return [(P(d), e, l, n) for d, e, l, n in a["commits"] if not BOT.search(e + l + n)]


def last_human(a):
    h = human(a)
    return max(d for d, *_ in h) if h else None


def share(flags, B=2000, seed=1):
    if not flags:
        return None
    rnd = random.Random(seed)
    bs = sorted(sum(rnd.choices(flags, k=len(flags))) / len(flags) for _ in range(B))
    return {"pct": round(100 * sum(flags) / len(flags), 1), "n": len(flags),
            "lo": round(100 * bs[int(0.025 * B)], 1), "hi": round(100 * bs[int(0.975 * B)], 1)}


S = {"read_on": "2026-10-28", "recent_since": "2026-07-28"}
S["census"] = {"lovable": sum(1 for v in census.values() if v["g"] == "lovable"),
               "aistudio": sum(1 for v in census.values() if v["g"] == "aistudio"),
               "v0": len(v0act),
               "reported_lovable": sum(v or 0 for k, v in census_counts.items() if k.startswith("lovable|")),
               "reported_aistudio": sum(v or 0 for k, v in census_counts.items() if k.startswith("aistudio|")),
               "reported_v0": sum(v or 0 for v in v0counts.values()),
               "max_per_day": max([v or 0 for v in census_counts.values()] + [v or 0 for v in v0counts.values()])}
S["baseline_sample"] = {"pages": len(load("base_pages.json")), "repos": len(base_meta),
                        "in_window": sum(1 for v in base_meta.values() if v and "2025-10-01" <= v["created"] < "2025-10-25"),
                        "with_package_json": len(base),
                        "with_builder_signature": len(base) - len(groups(drop_old=False)["baseline"])}
STRICT = re.compile("|".join(SIG.values()), re.I)
_sig = [a for r, a in base.items() if a and not a["fork"] and (ANY_BUILDER.search(a["readme"] or "") or any(ANY_BUILDER.search(e + l + n) for _, e, l, n in a["commits"]))]
S["baseline_sample"]["builder_strict_template"] = sum(1 for a in _sig if STRICT.search(a["readme"] or ""))
S["baseline_sample"]["builder_bot_commits"] = sum(1 for a in _sig if not STRICT.search(a["readme"] or "") and any(BUILDER_BOT.search(e + l + n) for _, e, l, n in a["commits"]))
S["baseline_sample"]["builder_mention_only"] = len(_sig) - S["baseline_sample"]["builder_strict_template"] - S["baseline_sample"]["builder_bot_commits"]
S["baseline_sample"]["builder_strict_pct"] = round(100 * (S["baseline_sample"]["builder_strict_template"] + S["baseline_sample"]["builder_bot_commits"]) / S["baseline_sample"]["with_package_json"], 1)
S["baseline_sample"]["builder_share_pct"] = round(100 * S["baseline_sample"]["with_builder_signature"] / S["baseline_sample"]["with_package_json"], 1)

G0 = groups(drop_old=False)
G = groups()
S["uploaded_old"] = {g: len(G0[g]) - len(G[g]) for g in G}
S["groups"] = {}
for g, rows in G.items():
    L = per_owner(rows)
    spans = []
    for r, a in L:
        lh = last_human(a)
        spans.append((lh - P(a["created"])).days if lh else -1)
    d = {"repos": len(rows), "owners": len(L),
         "median_commits": sorted(a["total"] for _, a in L)[len(L) // 2],
         "survival": {str(k): share([1 if s >= k else 0 for s in spans]) for k in (1, 7, 30, 90, 180)},
         "recent": share([1 if (last_human(a) and last_human(a) >= RECENT) else 0 for _, a in L]),
         "same_day_only": share([1 if 0 <= s < 1 else 0 for s in spans]),
         "over_30_commits_pct": round(100 * sum(1 for _, a in L if a["total"] > 30) / len(L), 1)}
    # Deployed and still answering, one year on (HTTP 200 on the homepage or a deploy URL in the README).
    dep = [r for r, _ in L if r in online]
    d["deployed"] = share([1 if r in online else 0 for r, _ in L])
    d["online_of_deployed"] = share([1 if online[r]["status"] == 200 else 0 for r in dep])
    d["online_and_untouched_since"] = share([1 if online[r]["status"] == 200 and not (last_human(a) and last_human(a) >= RECENT) else 0
                                             for r, a in L if r in online])
    if g in ("lovable", "v0"):
        # Did anyone push code the builder didn't write, after the first day? (Most outside commits on day one are the
        # repository being set up; a later one is someone working outside the builder.)
        d["hand_commit_after_day1"] = share([1 if any(not is_builder(e, l, n) and not OTHER_TOOL.search(e + l + n)
                                                      and dd > P(a["created"]) + dt.timedelta(days=1)
                                                      for dd, e, l, n in human(a)) else 0 for _, a in L])
        d["other_tool_commit"] = share([1 if any(OTHER_TOOL.search(e + l + n) for _, e, l, n in human(a)) else 0 for _, a in L])
    S["groups"][g] = d

# Derived figures stated in words.
gs = S["groups"]
S["derived"] = {
    "builder_apps_followed": gs["lovable"]["owners"] + gs["v0"]["owners"],
    "per_day": {g: round(S["census"][g] / 24) for g in ("lovable", "aistudio", "v0")},
    "no_change_after_30": {g: round(100 - gs[g]["survival"]["30"]["pct"], 1) for g in ("lovable", "v0", "baseline", "baseline_react")},
    "online_range": [min(gs[g]["online_of_deployed"]["pct"] for g in ("lovable", "v0", "aistudio", "baseline_react")),
                     max(gs[g]["online_of_deployed"]["pct"] for g in ("lovable", "v0", "aistudio", "baseline_react"))],
    # Deedy (Menlo Ventures) put Lovable at ~5M projects a month in Aug 2026 (third-party figure, embedded in the piece).
    "lovable_github_per_month": round(S["census"]["lovable"] / 24 * 30),
    "lovable_github_one_in": round(5_000_000 / (S["census"]["lovable"] / 24 * 30), -1),
    "gap_30_lovable_vs_react": round(gs["baseline_react"]["survival"]["30"]["pct"] - gs["lovable"]["survival"]["30"]["pct"], 1),
}
json.dump(S, open(OUT, "w", encoding="utf-8"), indent=1)
print("wrote", OUT)
