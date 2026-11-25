# Cover data: every 2026 changelog bullet in publish order, month by month, and which ones are counted entries
# (with their check). Same parsing and dating as analysis.py. Writes data/cover_dots.json: per month a string,
# one character per bullet: "." a changelog line, "d" a deny/ask-rule entry, "x" any other counted entry.
import collections, json, os, re
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
T = json.load(open(os.path.join(D, "cc_times.json")))
E = json.load(open(os.path.join(D, "entries_coded.json"), encoding="utf-8"))
log = open(os.path.join(D, "claude-changelog.md"), encoding="utf-8").read()
secs = [(s.split("\n", 1)[0].strip(), s) for s in re.split(r"^## ", log, flags=re.M)[1:]]
hit = {(e["version"], e["text"].strip()): e["control"] for e in E}
months = collections.OrderedDict()
for v, s in sorted(((v, s) for v, s in secs if T.get(v, "").startswith("2026")), key=lambda p: T[p[0]]):
    m = T[v][:7]
    for x in s.split("\n")[1:]:
        if not x.strip().startswith(("-", "*")): continue
        c = hit.get((v, x.strip()[2:].strip()))
        months.setdefault(m, []).append("." if c is None else "d" if c == "deny_ask_rule" else "x")
out = {m: "".join(a) for m, a in months.items()}
json.dump(out, open(os.path.join(D, "cover_dots.json"), "w"), indent=0)
print({m: (len(a), a.count("d") + a.count("x"), a.count("d")) for m, a in out.items()})
print("lines", sum(map(len, out.values())), "entries", sum(a.count("d") + a.count("x") for a in out.values()), "deny", sum(a.count("d") for a in out.values()))
