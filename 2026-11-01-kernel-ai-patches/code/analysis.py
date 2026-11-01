"""Every number in the article, from the parsed mainline history.
  python parse.py <bare clone> commits.json
  python target_dates.py commits.json ../data/target_dates.json   (optional: dates of bugs older than the clone)
  python analysis.py commits.json <bare clone> ../data [../data/target_dates.json]
Writes summary.json (all figures and tables), tagged_commits.csv (every commit carrying Assisted-by, with its
outcome) and monthly.csv. The test it applies was written down before this run (README.md, "The test, written down before the final run")."""
import collections, csv, datetime as dt, json, os, random, re, statistics, subprocess, sys

SRC, REPO, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
rows = json.load(open(SRC))
by = {r["h"]: r for r in rows}
DAY = 86400
UTC = dt.timezone.utc
ts = lambda y, m, d: int(dt.datetime(y, m, d, tzinfo=UTC).timestamp())
month = lambda t: dt.datetime.fromtimestamp(t, UTC).strftime("%Y-%m")

# --- resolve Fixes: and revert references (12-char prefixes by convention) --------------------------------------
pref = collections.defaultdict(list)
for h in by:
    pref[h[:8]].append(h)
resolved, ambiguous, missing = 0, 0, 0
def resolve(p):
    global resolved, ambiguous, missing
    c = [h for h in pref.get(p[:8], []) if h.startswith(p)]
    if len(c) == 1:
        resolved += 1; return c[0]
    if len(c) > 1: ambiguous += 1
    else: missing += 1
    return None
fixed_by = collections.defaultdict(list)     # target -> [fixing commit]
reverted_by = collections.defaultdict(list)
for r in rows:
    for p in set(r["fixes"]):
        t = resolve(p)
        if t and t != r["h"]: fixed_by[t].append(r)
    for p in set(r["rev"]):
        t = resolve(p)
        if t and t != r["h"]: reverted_by[t].append(r)

last = max(r["ct"] for r in rows)
START = ts(2026, 1, 1)
ai = lambda r: bool(r["ab"])
def fixed(r, days):
    return any(0 < f["ct"] - r["ct"] <= days * DAY for f in fixed_by.get(r["h"], []))
def reverted(r, days):
    return any(0 < f["ct"] - r["ct"] <= days * DAY for f in reverted_by.get(r["h"], []))
def window(days):
    return [r for r in rows if START <= r["ct"] <= last - days * DAY]
def rate(rs, days, fn=fixed):
    n = len(rs); k = sum(fn(r, days) for r in rs)
    return {"n": n, "k": k, "pct": round(100 * k / n, 3) if n else None}

S = {"as_of": dt.datetime.fromtimestamp(last, UTC).strftime("%Y-%m-%d %H:%M UTC"), "commits_parsed": len(rows),
     "first_commit": dt.datetime.fromtimestamp(min(r["ct"] for r in rows), UTC).strftime("%Y-%m-%d")}

# --- 1. releases ---------------------------------------------------------------------------------------------------
def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, check=True).stdout
REL = [("7.0", "v6.19", "v7.0"), ("7.1", "v7.0", "v7.1"), ("7.2", "v7.1", "v7.2"), ("7.3", "v7.2", "v7.3"),
       ("7.4 merge window", "v7.3", "HEAD")]
S["releases"] = []
try:  # kernel version tags; any other repository skips this block
    for name, a, b in REL:
        hs = git("rev-list", "--no-merges", f"{a}..{b}").split()
        n = len(hs); k = sum(1 for h in hs if h in by and ai(by[h]))
        S["releases"].append({"release": name, "commits": n, "tagged": k, "pct": round(100 * k / n, 2)})
    S["release_dates"] = {t: git("log", "-1", "--format=%cs", t).strip() for t in ("v7.0", "v7.1", "v7.2", "v7.3")}
except subprocess.CalledProcessError:
    print("no kernel version tags: per-release counts skipped", file=sys.stderr)

# --- 2. months: tag share of all commits and of bug fixes; Sashiko-reported fixes ----------------------------------
M = collections.OrderedDict()
for r in sorted((r for r in rows if r["ct"] >= START), key=lambda r: r["ct"]):
    m = M.setdefault(month(r["ct"]), dict(commits=0, tagged=0, fixes=0, fixes_tagged=0, fixes_sashiko=0, fixes_either=0,
                                          authors_tagged=set()))
    m["commits"] += 1; m["tagged"] += ai(r)
    if ai(r): m["authors_tagged"].add(r["ae"])
    if r["fixes"]:
        m["fixes"] += 1; m["fixes_tagged"] += ai(r); m["fixes_sashiko"] += r["sashiko"]; m["fixes_either"] += ai(r) or r["sashiko"]
for k, m in M.items():
    m["authors_tagged"] = len(m["authors_tagged"])
    m["pct_tagged"] = round(100 * m["tagged"] / m["commits"], 2)
    m["pct_fixes_tagged"] = round(100 * m["fixes_tagged"] / m["fixes"], 2)
    m["pct_fixes_either"] = round(100 * m["fixes_either"] / m["fixes"], 2)
S["months"] = M
with open(os.path.join(OUT, "monthly.csv"), "w", newline="") as f:
    w = csv.writer(f); cols = list(next(iter(M.values())).keys()); w.writerow(["month", *cols])
    for k, m in M.items(): w.writerow([k, *[m[c] for c in cols]])

# --- 3. who tags: authors, concentration, tools (descriptive only) -------------------------------------------------
tagged26 = [r for r in rows if ai(r) and r["ct"] >= START]
au = collections.Counter(r["ae"] for r in tagged26)
S["tagged_2026"] = len(tagged26)
S["tagged_authors"] = len(au)
S["top1_share"] = round(100 * au.most_common(1)[0][1] / len(tagged26), 1)
S["top10_share"] = round(100 * sum(c for _, c in au.most_common(10)) / len(tagged26), 1)
S["authors_with_1_tagged"] = sum(1 for c in au.values() if c == 1)
def tool(v):
    a = v.split(":")[0].split("#")[0].strip().lower()
    if "copilot" in a: return "GitHub Copilot"
    if "clanker" in a: return "Greg Kroah-Hartman's own tool"
    for key, lab in (("claude", "Claude Code"), ("codex", "Codex / OpenAI"), ("openai", "Codex / OpenAI"), ("gpt", "Codex / OpenAI"),
                     ("chatgpt", "Codex / OpenAI"), ("cursor", "Cursor"), ("antigravity", "Antigravity"), ("gemini", "Gemini CLI"),
                     ("opencode", "OpenCode")):
        if a.startswith(key): return lab
    if a in ("llm", "lollm", "ai", "unnamed") or a.startswith("llm"): return "Unnamed (\"LLM\")"
    return "Other"
tc = collections.Counter(tool(r["ab"][0]) for r in tagged26)
S["tools"] = tc.most_common()

# --- 4. the outcome: fixed later, within 30/60/90 days -------------------------------------------------------------
S["resolve"] = {"resolved": resolved, "ambiguous": ambiguous, "not_in_history": missing}
S["windows"] = {}
for d in (30, 60, 90):
    e = window(d)
    S["windows"][d] = {"cutoff": dt.datetime.fromtimestamp(last - d * DAY, UTC).strftime("%Y-%m-%d"),
        "tagged": rate([r for r in e if ai(r)], d), "untagged": rate([r for r in e if not ai(r)], d),
        "tagged_rev": rate([r for r in e if ai(r)], d, reverted), "untagged_rev": rate([r for r in e if not ai(r)], d, reverted),
        "tagged_fix": rate([r for r in e if ai(r) and r["fixes"]], d), "untagged_fix": rate([r for r in e if not ai(r) and r["fixes"]], d),
        "tagged_nonfix": rate([r for r in e if ai(r) and not r["fixes"]], d), "untagged_nonfix": rate([r for r in e if not ai(r) and not r["fixes"]], d)}

E = window(90)
# (b) same authors
A = collections.defaultdict(lambda: {"t": [0, 0], "u": [0, 0]})
for r in E:
    g = A[r["ae"]]["t" if ai(r) else "u"]; g[0] += 1; g[1] += fixed(r, 90)
both = {a: v for a, v in A.items() if v["t"][0] and v["u"][0]}
def ratio(keys):
    tn = sum(both[a]["t"][0] for a in keys); tk = sum(both[a]["t"][1] for a in keys)
    un = sum(both[a]["u"][0] for a in keys); uk = sum(both[a]["u"][1] for a in keys)
    return (tk / tn) / (uk / un) if un and uk and tn else None
keys = sorted(both)
rng = random.Random(2026); boots = []
for _ in range(1000):
    x = ratio([rng.choice(keys) for _ in keys])
    if x is not None: boots.append(x)
boots.sort()
S["same_authors"] = {"authors": len(both),
    "tagged": {"n": sum(v["t"][0] for v in both.values()), "k": sum(v["t"][1] for v in both.values())},
    "untagged": {"n": sum(v["u"][0] for v in both.values()), "k": sum(v["u"][1] for v in both.values())},
    "ratio": round(ratio(keys), 3), "ci95": [round(boots[24], 3), round(boots[974], 3)]}
for g in ("tagged", "untagged"):
    S["same_authors"][g]["pct"] = round(100 * S["same_authors"][g]["k"] / S["same_authors"][g]["n"], 3)
# (c) subsystem-matched: subject prefix up to the first colon
sub = lambda r: r["s"].split(":")[0].strip().lower() if ":" in r["s"] else "(none)"
U = collections.defaultdict(lambda: [0, 0])
for r in E:
    if not ai(r): U[sub(r)][0] += 1; U[sub(r)][1] += fixed(r, 90)
m_ = [r for r in E if ai(r) and U[sub(r)][0] >= 20]
S["subsystem_matched"] = {"tagged_matched": len(m_), "observed": sum(fixed(r, 90) for r in m_),
                          "expected": round(sum(U[sub(r)][1] / U[sub(r)][0] for r in m_), 1)}
# (d) month-standardised
UM = collections.defaultdict(lambda: [0, 0])
for r in E:
    if not ai(r): UM[month(r["ct"])][0] += 1; UM[month(r["ct"])][1] += fixed(r, 90)
t_ = [r for r in E if ai(r)]
S["month_standardised"] = {"observed": sum(fixed(r, 90) for r in t_),
                           "expected": round(sum(UM[month(r["ct"])][1] / UM[month(r["ct"])][0] for r in t_), 1)}
S["by_month_90"] = {}
for r in E:
    g = S["by_month_90"].setdefault(month(r["ct"]), {"t": [0, 0], "u": [0, 0]})["t" if ai(r) else "u"]
    g[0] += 1; g[1] += fixed(r, 90)
# (e) type-standardised (added after review, not part of the verdict): fix vs non-fix commits weighted by the rest's rates
UT = {True: [0, 0], False: [0, 0]}
for r in E:
    if not ai(r): UT[bool(r["fixes"])][0] += 1; UT[bool(r["fixes"])][1] += fixed(r, 90)
S["type_standardised"] = {"observed": sum(fixed(r, 90) for r in t_),
                          "expected": round(sum(UT[bool(r["fixes"])][1] / UT[bool(r["fixes"])][0] for r in t_), 1)}

# the verdict, as written in the README before the final run
W90 = S["windows"][90]
le = [W90["tagged"]["pct"] <= W90["untagged"]["pct"], S["same_authors"]["tagged"]["pct"] <= S["same_authors"]["untagged"]["pct"],
      S["subsystem_matched"]["observed"] <= S["subsystem_matched"]["expected"], S["month_standardised"]["observed"] <= S["month_standardised"]["expected"]]
hi = S["same_authors"]["ci95"][1]
S["verdict"] = ("less often" if all(le) and hi < 1.0 else "no more often" if all(le) and hi < 1.25 else "report the ratio")
S["verdict_checks"] = {"a_b_c_d_le": le, "ci_upper": hi}

# who fixed the tagged commits that were fixed
ff = [f for r in tagged26 for f in fixed_by.get(r["h"], [])]
S["fixes_of_tagged"] = {"fixing_commits": len(ff), "fixer_tagged": sum(ai(f) for f in ff), "fixer_sashiko": sum(f["sashiko"] for f in ff),
                        "same_author": sum(f["ae"] == by[t]["ae"] for r in tagged26 for t in [r["h"]] for f in fixed_by.get(t, []))}

# --- 5. what the AI-assisted fixes fix: age of the bug (needs full history) ----------------------------------------
# Commits older than the clone: author dates from target_dates.py (GitHub), if present.
TD = {}
if len(sys.argv) > 4:
    for k, val in json.load(open(sys.argv[4])).items():
        if val: TD[k] = (val[0], int(dt.datetime.fromisoformat(val[1].replace("Z", "+00:00")).timestamp()))
def target_at(p):
    c = [h for h in pref.get(p[:8], []) if h.startswith(p)]
    if len(c) == 1: return c[0], by[c[0]]["at"]
    if p[:12] in TD and TD[p[:12]][0].startswith(p): return TD[p[:12]]
    return None
def ages(rs):
    out = []
    for r in rs:
        for p in set(r["fixes"]):
            t = target_at(p)
            if t: out.append((r["ct"] - t[1]) / (365.25 * DAY))
    return out
fx = [r for r in rows if r["fixes"] and r["ct"] >= ts(2026, 5, 1)]
groups = {"tagged": [r for r in fx if ai(r)], "sashiko": [r for r in fx if r["sashiko"] and not ai(r)],
          "other": [r for r in fx if not ai(r) and not r["sashiko"]]}
S["bug_age"] = {}
for g, rs in groups.items():
    a = sorted(ages(rs))
    S["bug_age"][g] = {"fixes": len(rs), "targets": len(a), "median_years": round(statistics.median(a), 2),
                       "share_over_5y": round(100 * sum(x > 5 for x in a) / len(a), 1), "share_over_10y": round(100 * sum(x > 10 for x in a) / len(a), 1), "mean_years": round(sum(a) / len(a), 2),
                       "share_under_1y": round(100 * sum(x < 1 for x in a) / len(a), 1),
                       "stable_pct": round(100 * sum(r["stable"] for r in rs) / len(rs), 1)}
# age distribution buckets for the figure
B = [(0, 1, "< 1 year"), (1, 2, "1–2"), (2, 5, "2–5"), (5, 10, "5–10"), (10, 99, "10+")]
S["bug_age_buckets"] = {g: [round(100 * sum(lo <= x < hi for x in ages(rs)) / max(1, len(ages(rs))), 1) for lo, hi, _ in B]
                        for g, rs in groups.items()}
S["bug_age_labels"] = [b[2] for b in B]
oldest = max(((r["ct"] - t[1]) / (365.25 * DAY), r["h"][:12], r["s"], t[0][:12], dt.datetime.fromtimestamp(t[1], UTC).strftime("%Y-%m-%d"))
             for r in groups["tagged"] for p in set(r["fixes"]) for t in [target_at(p)] if t)
S["oldest_tagged_fix"] = {"years": round(oldest[0], 1), "fix": oldest[1], "subject": oldest[2], "bug": oldest[3], "bug_date": oldest[4]}

# --- per-commit table for the tagged commits ---------------------------------------------------------------------
with open(os.path.join(OUT, "tagged_commits.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["sha", "commit_date", "author_email", "subject", "assisted_by", "is_fix", "fixed_within_90d", "eligible_90d",
                "later_fixes", "reverted"])
    for r in sorted((r for r in rows if ai(r)), key=lambda r: r["ct"]):
        w.writerow([r["h"], dt.datetime.fromtimestamp(r["ct"], UTC).strftime("%Y-%m-%d"), r["ae"], r["s"], " | ".join(r["ab"]),
                    int(bool(r["fixes"])), int(fixed(r, 90)), int(START <= r["ct"] <= last - 90 * DAY),
                    " ".join(f["h"][:12] for f in fixed_by.get(r["h"], [])), int(bool(reverted_by.get(r["h"])))])

json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1, default=list)
print(json.dumps({k: S[k] for k in ("releases", "windows", "same_authors", "subsystem_matched", "month_standardised",
                                    "verdict", "verdict_checks", "bug_age", "fixes_of_tagged", "resolve", "tools",
                                    "top1_share", "top10_share", "tagged_authors", "oldest_tagged_fix")}, indent=1, default=list))
