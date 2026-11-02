# Placebo check (post-hoc amendment, disclosed in ../NOTES.md): the same effect as analyze.py, with a fake ban date
# two years before the real one, four full halves before it and four full halves after it (all before the real ban).
#   python placebo.py <dir with <repo>.log files> <out placebo.json>
import collections, json, os, re, sys

BANNED = {"gentoo_gentoo": "2024-04-14", "NetBSD_src": "2024-05-01", "qemu_qemu": "2025-06-24"}
COMPARE = ["NixOS_nixpkgs", "freebsd_freebsd-src", "torvalds_linux", "llvm_llvm-project"]
BOT = re.compile(r"\[bot\]|noreply@github\.com$|^bot@|-bot@|^r-ryantm|dependabot|renovate|github-actions", re.I)

def half(d): return f"{d[:4]}-H{1 if d[5:7] <= '06' else 2}"

def new_by_half(path, key="new"):
    first, active = {}, collections.defaultdict(set)
    for line in open(path, encoding="utf-8", errors="replace"):
        p = line.rstrip("\n").split("|")
        if len(p) < 4: continue
        email, date = p[0].strip().lower(), p[2]
        if not email or BOT.search(email) or date < "2018-01-01": continue
        if email not in first or date < first[email]: first[email] = date
        active[half(date)].add(email)
    if key == "active": return collections.Counter({h: len(s) for h, s in active.items()})
    return collections.Counter(half(d) for d in first.values())

def shift(h, n):  # move a half-year label by n halves
    y, k = int(h[:4]), int(h[-1]) - 1
    t = y * 2 + k + n
    return f"{t // 2}-H{t % 2 + 1}"

src, out = sys.argv[1], sys.argv[2]
res = {}
for key in ("new", "active"):
  N = {n: new_by_half(os.path.join(src, n + ".log"), key) for n in list(BANNED) + COMPARE}
  for name, ban in BANNED.items():
    fake = f"{int(ban[:4]) - 2}{ban[4:]}"
    fh = half(fake)
    before = [shift(fh, -i) for i in range(4, 0, -1)]
    after = [shift(fh, i) for i in range(1, 5)]
    r = lambda s: (sum(s[h] for h in after) / 4) / (sum(s[h] for h in before) / 4) if sum(s[h] for h in before) else None
    own = r(N[name]); comps = {c: r(N[c]) for c in COMPARE}
    cm = [v for v in comps.values() if v]
    d = {"fake_ban": fake, "before": before, "after": after, "own": own, "compare": comps,
         "compare_mean": sum(cm) / len(cm), "effect": own / (sum(cm) / len(cm))}
    if key == "new": res[name] = d
    else: res[name]["active"] = d
    print(f"{key} {name}: fake ban {fake}, own {own:.2f}, compare mean {sum(cm)/len(cm):.2f}, placebo effect {d['effect']:.2f}")
json.dump(res, open(out, "w"), indent=1)
