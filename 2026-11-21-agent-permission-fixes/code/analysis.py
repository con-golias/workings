# Every number in the article comes from here: data/summary.json.
# Inputs: data/claude-changelog.md (anthropics/claude-code CHANGELOG.md, read 20 Nov 2026), data/cc_times.json (npm
# publish time of each version), data/entries_coded.json (the single source of truth for the counted entries:
# keyword-proposed by code/recode_draft.py, hand-reviewed in code/apply_codes.py; analysis.py only reads it),
# data/adv_patched.tsv (GitHub advisory database, package @anthropic-ai/claude-code, first patched version).
#   python code/analysis.py
import collections, datetime as dt, json, os, re, statistics

here = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(here, "..", "data")
T = json.load(open(os.path.join(D, "cc_times.json")))
E = json.load(open(os.path.join(D, "entries_coded.json"), encoding="utf-8"))
log = open(os.path.join(D, "claude-changelog.md"), encoding="utf-8").read()
S = {"read_on": "2026-11-20"}

# changelog size: versions and bullets per month (by npm publish time)
secs = [(s.split("\n", 1)[0].strip(), s) for s in re.split(r"^## ", log, flags=re.M)[1:]]
bul = {v: sum(1 for x in s.split("\n")[1:] if x.strip().startswith(("-", "*"))) for v, s in secs}
S["changelog"] = {"versions": len(secs), "bullets": sum(bul.values()), "newest": secs[0][0], "oldest": secs[-1][0]}
v26 = [v for v, _ in secs if T.get(v, "").startswith("2026")]
S["changelog"]["sections_2026"] = len(v26)
S["npm_versions_2026"] = sum(1 for k, v in T.items() if re.match(r"^\d+\.\d+\.\d+$", k) and v.startswith("2026"))
S["changelog"]["bullets_2026"] = sum(bul[v] for v in v26)
bm = collections.Counter(); vm = collections.Counter()
for v, _ in secs:
    m = T.get(v, "?")[:7]; bm[m] += bul[v]; vm[m] += 1
S["changelog"]["bullets_mar_2025"] = bm["2025-03"]
S["changelog"]["bullets_sep_2026"] = bm["2026-09"]

# the counted entries; each text must sit verbatim under its version in the changelog
secmap = dict(secs)
for e in E:
    assert any(l.strip()[2:].strip() == e["text"].strip() for l in secmap[e["version"]].splitlines()), (e["version"], e["text"][:60])
y = [e for e in E if e["date"].startswith("2026")]
S["n_2026"] = len(y); S["n_all"] = len(E)
S["versions_with_fix"] = len({e["version"] for e in y})
S["share_sections_with_fix"] = round(100 * S["versions_with_fix"] / len(v26), 1)
# control x precondition, hand-coded (code/apply_codes.py); policy_admin = organisation settings that do not govern
# what the agent may do (telemetry, login method, proxy/CA, model list)
S["pre"] = {k: sum(e["pre"] == k for e in y) for k in ("none", "loosened", "auto_default", "sandbox_auto_allow")}
S["reverted"] = sum(e.get("reverted", False) for e in y)
S["pre_none_pct"] = round(100 * S["pre"]["none"] / len(y), 1)
S["platform"] = sum(e["platform"] for e in y)
S["none_not_platform"] = sum(e["pre"] == "none" and not e["platform"] for e in y)
ORDER = ["prompt", "deny_ask_rule", "policy", "sandbox", "containment", "hook", "trust_consent", "plan_mode", "injection", "policy_admin"]
S["controls"] = {c: {"n": sum(e["control"] == c for e in y), "none": sum(e["control"] == c and e["pre"] == "none" for e in y),
                     "loosened": sum(e["control"] == c and e["pre"] == "loosened" for e in y)} for c in ORDER}
S["n_without_admin"] = len(y) - S["controls"]["policy_admin"]["n"]
S["policy_all"] = S["controls"]["policy"]["n"] + S["controls"]["policy_admin"]["n"]
S["user_controls"] = sum(S["controls"][c]["n"] for c in ("deny_ask_rule", "sandbox", "hook", "plan_mode"))
S["mentions_symlink"] = sum(bool(re.search(r"symlink|link swapped|junction|\blink\b", e["text"], re.I)) for e in y)
S["mentions_rm"] = sum(bool(re.search(r"\brm\b|rm -rf|rmdir|dangerous-removal|dangerous removal", e["text"], re.I)) for e in y)

# per quarter, per 100 changelog bullets
Q = {"Q1": ("2026-01", "2026-03"), "Q2": ("2026-04", "2026-06"), "Q3": ("2026-07", "2026-09"), "Q4": ("2026-10", "2026-11")}
S["quarters"] = {}
for q, (a, z) in Q.items():
    f = sum(1 for e in y if a <= e["date"][:7] <= z); bb = sum(bm[m] for m in bm if a <= m <= z); vv = sum(vm[m] for m in vm if a <= m <= z)
    S["quarters"][q] = {"fixes": f, "bullets": bb, "versions": vv, "per_100_bullets": round(100 * f / bb, 2), "per_version": round(f / vv, 2)}
S["quarters"]["Q4"]["note"] = "1 Oct to 19 Nov (2.1.329); partial quarter"
top = collections.Counter(e["version"] for e in y).most_common(5)
S["top_releases"] = top
S["autumn"] = {"n": sum(1 for e in y if "2026-09" <= e["date"][:7] <= "2026-11")}
S["top3"] = {"n": sum(n for _, n in top[:3]), "names": ", ".join(v for v, _ in top[:3])}
S["months"] = dict(sorted(collections.Counter(e["date"][:7] for e in y).items()))

# advisories
adv = [l.split("\t") for l in open(os.path.join(D, "adv_patched.tsv"), encoding="utf-8").read().split("\n") if l]
lag = []
A = []
for g, pub, sev, pv, summ in adv:
    rel = T.get(pv, "")[:10]
    d = (dt.date.fromisoformat(pub) - dt.date.fromisoformat(rel)).days if rel else None
    A.append({"ghsa": g, "published": pub, "severity": sev, "patched": pv, "patched_release": rel, "lag_days": d, "summary": summ})
    if d is not None: lag.append(d)
S["advisories"] = {"n_database": len(A), "published_2026": sum(a["published"].startswith("2026") for a in A),
                   "lag_median_days": statistics.median(lag), "lag_min": min(lag), "lag_max": max(lag), "lag_n": len(lag),
                   "high": sum(a["severity"] == "high" for a in A)}
h1 = [a for a in A if "2026-01" <= a["patched_release"][:7] <= "2026-06"]
S["h1"] = {"fixes": sum(1 for e in y if "2026-01" <= e["date"][:7] <= "2026-06"), "advisories": len(h1)}
S["advisories_patching_h2"] = sum(a["patched_release"] >= "2026-07" for a in A)
ro = [l.split("\t") for l in open(os.path.join(D, "adv_repo_only.tsv"), encoding="utf-8").read().split("\n") if l]
cli = [r for r in ro if r[3] == "Claude Code"]
S["advisories_repo_only"] = {"n": len(ro), "claude_code": len(cli), "desktop": len(ro) - len(cli)}
S["advisories_total_repo_page"] = len(A) + len(ro)
S["advisories_claude_code"] = len(A) + len(cli)
for g, pub, summ, prod, pv in cli:
    rel = T.get(pv, "")[:10]
    A.append({"ghsa": g, "published": pub, "severity": None, "patched": pv, "patched_release": rel, "lag_days": (dt.date.fromisoformat(pub) - dt.date.fromisoformat(rel)).days, "summary": summ, "repo_only": True})
lag = [a["lag_days"] for a in A if a["lag_days"] is not None]
S["advisories"].update({"lag_median_days": statistics.median(lag), "lag_min": min(lag), "lag_max": max(lag), "lag_n": len(lag), "n_claude_code": len(A), "published_2026": sum(a["published"].startswith("2026") for a in A)})
h1 = [a for a in A if "2026-01" <= a["patched_release"][:7] <= "2026-06"]
S["h1"]["advisories"] = len(h1)
S["advisories_patching_h2"] = sum(a["patched_release"] >= "2026-07" for a in A)
J = [l.split(chr(9)) for l in open(os.path.join(D, "advisory_join.tsv"), encoding="utf-8").read().splitlines()[1:] if l]
S["join"] = {"advisories_2026_releases": len(J), "clear": sum(r[3] == "clear" for r in J), "partial": sum(r[3] == "partial" for r in J), "possible": sum(r[3] == "possible" for r in J),
             "none": sum(r[3] == "none" for r in J), "no_section": sum(r[3] == "no_section" for r in J),
             "h1_clear": sum(r[3] == "clear" and r[2] < "2026-07" for r in J), "h1_partial": sum(r[3] == "partial" and r[2] < "2026-07" for r in J),
             "h1_possible": sum(r[3] == "possible" and r[2] < "2026-07" for r in J), "h1_none": sum(r[3] == "none" and r[2] < "2026-07" for r in J)}
S["recall_sample"] = {"releases": 10, "bullets": 461, "counted": 27, "missed": 8, "recall_pct": round(100 * 27 / 35), "without_2_1_321": {"counted": 25, "missed": 5, "recall_pct": round(100 * 25 / 30)}, "found_lines_added": False}
S["revert_note"] = "2.1.259 Read() deny rules on Bash arguments, reverted in 2.1.260 (over-blocked npm run build)"
S["advisory_list"] = A
# CVE ids from the GitHub advisory database export (column 2)
G = [l.split("\t") for l in open(os.path.join(D, "gadv__anthropic-ai_claude-code.tsv"), encoding="utf-8").read().splitlines() if l]
S["advisories"]["with_cve"] = sum(r[1].startswith("CVE-") for r in G)
# autumn releases: entries per release, Sep-Nov 2026 (figure 7)
aut = collections.Counter(e["version"] for e in y if "2026-09" <= e["date"][:7] <= "2026-11")
S["months_bullets"] = {m: bm[m] for m in sorted(bm) if m.startswith("2026")}
S["months_per_100"] = {m: round(100 * S["months"].get(m, 0) / bm[m], 2) for m in S["months_bullets"]}
rm = [e for e in y if re.search(r"\brm\b|rm -rf|rmdir|dangerous-removal|dangerous removal", e["text"], re.I)]
S["rm_pre"] = dict(collections.Counter(e["pre"] for e in rm))
S["autumn"].update({"sections": sum(vm[m] for m in vm if "2026-09" <= m <= "2026-11"), "releases_with_entry": len(aut), "per_release": sorted(aut.values(), reverse=True),
                    "versions": [v for v, _ in aut.most_common()]})
# symlink entries by layer (figure 3), assigned by hand after reading all 25 (version, start of text)
HAND = {"file tools": [("2.1.69", "Fixed symlink bypass"), ("2.1.251", "Fixed file tools"), ("2.1.251", "Fixed Grep and Glob"),
                       ("2.1.280", "Fixed writes through"), ("2.1.290", "Fixed an `@`-mention"), ("2.1.290", "Fixed an image read"),
                       ("2.1.292", "Fixed a notebook")],
        "settings, CLAUDE.md, config folder": [("2.1.216", "Fixed workflow saves"), ("2.1.282", "Fixed CLAUDE.md"),
                       ("2.1.290", "Fixed a project `CLAUDE.md`"), ("2.1.290", "Fixed edits to the file"), ("2.1.309", "Fixed profile store")],
        "worktrees and sessions": [("2.1.205", "Fixed Windows worktree"), ("2.1.212", "Fixed worktree creation"),
                       ("2.1.217", "Fixed background session"), ("2.1.232", "Hardened the auto-generated")],
        "the OS sandbox": [("2.1.299", "Fixed sandboxed commands on macOS"), ("2.1.299", "Fixed sandbox glob"), ("2.1.309", "Fixed macOS sandbox")],
        "permission rules on a path": [("2.1.89", "Fixed `Edit(//path"), ("2.1.268", "Fixed deny and ask permission rules on symlinked")],
        "plugins": [("2.1.257", "Fixed plugins being able"), ("2.1.265", "Fixed a plugin path")],
        "shell commands": [("2.1.232", "Fixed a Windows permission bypass")],
        "undo (/rewind)": [("2.1.319", "Fixed a case where `/rewind`")]}
sl = [e for e in y if re.search(r"symlink|link swapped|junction|\blink\b", e["text"], re.I)]
lay = {}
for name, keys in HAND.items():
    for v, start in keys:
        hit = [e for e in sl if e["version"] == v and e["text"].startswith(start)]
        assert len(hit) == 1, (v, start)
    lay[name] = len(keys)
assert sum(lay.values()) == len(sl), (sum(lay.values()), len(sl))
S["symlink_layers"] = lay

# "Check your own version" section: counted 2026 fixes that shipped after a given version (code/which_fixes.py)
def _k(v): return tuple(int(x) for x in v.split("."))
S["behind"] = {v.replace(".", "_"): {"n": sum(_k(e["version"]) > _k(v) for e in y), "date": T.get(v, "")[:10]} for v in ("2.1.200", "2.1.250", "2.1.300")}
S["deny_named_in_row"] = sum(e["control"] == "deny_ask_rule" and bool(re.search(r"\bdeny|denied|disallowed", e["text"], re.I)) for e in y)
json.dump(S, open(os.path.join(D, "summary.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in S.items() if k != "advisory_list"}, indent=1)[:3500])

# Public copy for readers and which_fixes.py: the coded rows without the changelog text (a short SHA-1 instead).
import hashlib
json.dump([{"version": e["version"], "date": e["date"], "control": e["control"], "pre": e["pre"], "platform": e["platform"],
            "text_sha1": hashlib.sha1(e["text"].encode("utf-8")).hexdigest()[:12]} for e in E],
          open(os.path.join(D, "entries_public.json"), "w", encoding="utf-8"), indent=1)
