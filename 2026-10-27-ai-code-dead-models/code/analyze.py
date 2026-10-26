# Which model IDs new AI repositories call, and the status of each ID on the day the repository was created
# and on 26 Oct 2026.   python analyze.py <scan.jsonl> <trailers.jsonl> <out_prefix>
# Counted: model-ID string literals in source files that also contain an LLM API call (CALL in scan.py).
# Dropped: catalog files (more than MAXIDS distinct IDs: price tables, model pickers) and repositories whose
# call-site files are byte-identical to an earlier repository's (template copies).
# "Fresh": the oldest commit on the repository's first page of commits is within FRESH days of its creation,
#   so the code was written then, not uploaded from an older project.
# "Default model": the ID with the most occurrences across the repository's call-site files.
import sys, json, re, collections, statistics as st, datetime as dt, csv
from registry import classify, TODAY
MAXIDS, FRESH = 8, 14
AGENT = re.compile(r"^(Claude|GPT-|Codex|Cursor|Copilot$|Copilot Autofix|Devin|Gemini|Jules|Kiro|Aider|Windsurf)", re.I)
day = lambda s: dt.date.fromisoformat(s[:10])

scan = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
tr = {t["repo"]: t for t in (json.loads(l) for l in open(sys.argv[2], encoding="utf-8")) if t.get("ok")}
ok = [r for r in scan if r.get("status") == "ok"]
seen, repos, dupes = set(), [], 0
for r in sorted(ok, key=lambda r: r["created"]):
    calls = [f for f in r["files"] if f["call"] and len(f["ids"]) <= MAXIDS]
    cnt = collections.Counter()
    for f in calls: cnt.update(f.get("n") or {i: 1 for i in f["ids"]})
    if not cnt: continue
    fp = tuple(sorted(f["h"] for f in calls))
    if fp in seen: dupes += 1; continue
    seen.add(fp)
    t = tr.get(r["repo"], {})
    sigs = [s["who"] for s in t.get("sigs", []) if AGENT.match(s["who"]) and "[bot]" not in s["who"]]
    first = t.get("first")
    repos.append(dict(repo=r["repo"], created=r["created"][:10], ids=sorted(cnt), default=cnt.most_common(1)[0][0],
                      agents_cfg=r.get("agents", []), agent_sigs=sorted(set(sigs)),
                      fresh=bool(first) and t.get("ncommits", 0) < 100 and (day(first) - day(r["created"])).days >= -FRESH))
print(f"scanned {len(ok)} repositories; {len(repos)} call an LLM with a literal model ID ({dupes} template copies dropped)")

def pct(a, n): return f"{a} ({100 * a / n:.1f}%)" if n else "0"
def summarise(rs, label):
    n = len(rs)
    if not n: print(f"\n[{label}] n=0"); return {}
    S = lambda r, d: [classify(i, d)["status"] for i in r["ids"]]
    o = dict(n=n)
    o["retired_at_creation"] = sum("retired" in S(r, r["created"]) for r in rs)
    o["retired_now"] = sum("retired" in S(r, TODAY) for r in rs)
    o["dying_now"] = sum(any(s in ("retired", "scheduled") for s in S(r, TODAY)) for r in rs)
    o["default_retired_now"] = sum(classify(r["default"])["status"] == "retired" for r in rs)
    o["default_dying_now"] = sum(classify(r["default"])["status"] in ("retired", "scheduled") for r in rs)
    o["default_unknown"] = sum(classify(r["default"])["status"] == "unknown" for r in rs)
    ages = []
    for r in rs:
        rel = classify(r["default"])["released"]
        if rel and rel <= r["created"]: ages.append((day(r["created"]) - day(rel)).days / 30.44)
    o["default_age_median_months"] = round(st.median(ages), 1) if ages else None
    print(f"\n[{label}] n={n}")
    for k in ("retired_at_creation", "retired_now", "dying_now", "default_retired_now", "default_dying_now", "default_unknown"):
        print(f"  {k}: {pct(o[k], n)}")
    print(f"  default model age at creation, median months: {o['default_age_median_months']} (n={len(ages)})")
    c = collections.Counter(r["default"] for r in rs)
    print("  top defaults:", ", ".join(f"{k} {v} [{classify(k)['status'][:3]}]" for k, v in c.most_common(15)))
    return o

out = {}
out["all"] = summarise(repos, "all")
fresh = [r for r in repos if r["fresh"]]
out["fresh"] = summarise(fresh, "fresh (code written this month)")
out["not_fresh"] = summarise([r for r in repos if not r["fresh"]], "not fresh (older code uploaded)")
for v in ("openai", "anthropic", "google"):
    out[f"fresh_{v}"] = summarise([r for r in fresh if classify(r["default"])["vendor"] == v], f"fresh, default is {v}")
out["fresh_agent_signed"] = summarise([r for r in fresh if r["agent_sigs"]], "fresh, commits co-signed by an AI coding agent")
out["fresh_not_signed"] = summarise([r for r in fresh if not r["agent_sigs"]], "fresh, no agent signature")
out["fresh_cfg"] = summarise([r for r in fresh if r["agents_cfg"]], "fresh, agent config file present")

# Fingerprint: for repositories signed by exactly one agent family, what is the newest OpenAI / any model they name?
print("\n[fingerprint] agent signature -> repos, median release date of newest named model, share whose default is dying")
g = collections.defaultdict(list)
for r in fresh:
    for s in r["agent_sigs"]:
        g[re.sub(r"\s*\(.*\)$", "", s)].append(r)
for k, rs in sorted(g.items(), key=lambda kv: -len(kv[1])):
    if len(rs) < 5: continue
    newest = [max((classify(i)["released"] for i in r["ids"] if classify(i)["released"]), default=None) for r in rs]
    newest = sorted(x for x in newest if x)
    dying = sum(classify(r["default"])["status"] in ("retired", "scheduled") for r in rs)
    print(f"  {k:32s} n={len(rs):4d}  newest named: median {newest[len(newest)//2] if newest else '-'}  default dying: {pct(dying, len(rs))}")
# The clock: share of fresh repositories whose default model is shut down on or before each date.
dates = sorted({classify(r["default"])["shutdown"] for r in fresh if classify(r["default"])["shutdown"]})
clock = [dict(date=d, share=round(100 * sum((classify(r["default"])["shutdown"] or "9999") <= d for r in fresh) / len(fresh), 1)) for d in dates if d >= "2026-10-01"]
before = round(100 * sum((classify(r["default"])["shutdown"] or "9999") < "2026-10-01" for r in fresh) / len(fresh), 1)
print("\n[clock] fresh repos whose default is shut down by date; before 1 Oct:", before, "%")
for c in clock: print("  ", c["date"], c["share"], "%")
top = collections.Counter(r["default"] for r in fresh).most_common(12)
out["chart"] = dict(n_fresh=len(fresh), before_oct=before, clock=clock,
                    top=[dict(id=k, n=v, share=round(100 * v / len(fresh), 1), **classify(k)) for k, v in top])
json.dump(dict(summary=out, repos=repos), open(sys.argv[3] + "_analysis.json", "w"), indent=0)
with open(sys.argv[3] + "_per_repo.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["repo", "created", "fresh", "default_model", "default_status", "all_ids", "agent_signatures", "agent_config_files"])
    for r in repos: w.writerow([r["repo"], r["created"], r["fresh"], r["default"], classify(r["default"])["status"], " ".join(r["ids"]), "; ".join(r["agent_sigs"]), " ".join(r["agents_cfg"])])
