# New and active contributors per half-year, before and after each AI ban, against projects without a ban.
#   python analyze.py <dir with <repo>.log files> <out summary.json>
# Each .log line: author_email|author_name|author_date|commit_date (git log --format='%ae|%an|%ad|%cd' --date=short)
# Rules are pre-registered in ../README.md (Design): history from 2018-01-01, 2018-2019 burn-in, bots excluded,
# effect = (banned project's after/before ratio) / (mean ratio of the comparison projects, same calendar halves).
import sys, os, re, json, collections

BANNED = {"gentoo_gentoo": "2024-04-14", "NetBSD_src": "2024-05-01", "qemu_qemu": "2025-06-24"}
COMPARE = ["NixOS_nixpkgs", "freebsd_freebsd-src", "torvalds_linux", "llvm_llvm-project"]
LAST = "2026-H2"   # partial: data to 2 Nov 2026
BOT = re.compile(r"\[bot\]|noreply@github\.com$|^bot@|-bot@|^r-ryantm|dependabot|renovate|github-actions", re.I)

def half(d): return f"{d[:4]}-H{1 if d[5:7] <= '06' else 2}"
def halves(a, b):
    out, y, h = [], int(a[:4]), int(a[-1])
    while f"{y}-H{h}" <= b:
        out.append(f"{y}-H{h}"); y, h = (y, 2) if h == 1 else (y + 1, 1)
    return out

def series(path):
    first, active = {}, collections.defaultdict(set)
    for line in open(path, encoding="utf-8", errors="replace"):
        p = line.rstrip("\n").split("|")
        if len(p) < 4: continue
        email, date = p[0].strip().lower(), p[2]
        if not email or BOT.search(email) or date < "2018-01-01": continue
        if email not in first or date < first[email]: first[email] = date
        active[half(date)].add(email)
    new = collections.Counter(half(d) for d in first.values())
    return {h: {"new": new.get(h, 0), "active": len(active.get(h, ()))} for h in halves("2020-H1", LAST)}

src, out = sys.argv[1], sys.argv[2]
S = {name: series(os.path.join(src, name + ".log")) for name in list(BANNED) + COMPARE if os.path.exists(os.path.join(src, name + ".log"))}

def ratio(s, before, after, key):
    b = [s[h][key] for h in before]; a = [s[h][key] for h in after]
    return (sum(a) / len(a)) / (sum(b) / len(b)) if a and b and sum(b) else None

result = {"series": S, "effects": {}}
for name, ban in BANNED.items():
    if name not in S: continue
    bh = half(ban)
    allh = list(S[name])
    i = allh.index(bh)
    before = allh[max(0, i - 4):i]                 # four full halves before the ban's half
    after = [h for h in allh[i + 1:] if h != LAST] # full halves after the ban's half
    e = {"ban": ban, "before": before, "after": after}
    for key in ("new", "active"):
        r = ratio(S[name], before, after, key)
        comps = {c: ratio(S[c], before, after, key) for c in COMPARE if c in S}
        cm = [v for v in comps.values() if v]
        e[key] = {"ratio": r, "compare": comps, "compare_mean": sum(cm) / len(cm) if cm else None,
                  "effect": (r / (sum(cm) / len(cm))) if r and cm else None}
    result["effects"][name] = e
json.dump(result, open(out, "w"), indent=1)
for name, e in result["effects"].items():
    print(name, e["ban"], "before", e["before"], "after", e["after"])
    for key in ("new", "active"):
        x = e[key]; print(f"  {key}: own {x['ratio']:.2f}  compare mean {x['compare_mean']:.2f}  effect {x['effect']:.2f}  ", {k: round(v, 2) for k, v in x['compare'].items() if v})
