"""Public copies of the records that name the papers outside Lin's list: their ids become new-1..new-6
(order of first prompted version). Writes data/public/{scan,new_versions,summary}.json."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(DATA, "public")
os.makedirs(OUT, exist_ok=True)
S = json.load(open(os.path.join(DATA, "summary.json")))
NV = json.load(open(os.path.join(DATA, "new_versions.json")))
SC = json.load(open(os.path.join(DATA, "scan.json")))
order = sorted(S["new_not_in_lin"], key=lambda k: NV[k]["prompted_version_date"])
alias = {k: f"new-{i + 1}" for i, k in enumerate(order)}


def scrub(x):
    s = json.dumps(x, ensure_ascii=False)
    for k, a in alias.items():
        s = s.replace(k, a)
    return json.loads(s)


NVp = {k: {kk: vv for kk, vv in v.items() if kk != "note"} for k, v in NV.items()}
S = dict(S, new_versions=NVp)
json.dump(scrub(NVp), open(os.path.join(OUT, "new_versions.json"), "w"), indent=1)
json.dump(scrub(S), open(os.path.join(OUT, "summary.json"), "w"), indent=1)
# scan records: hidden ones scrubbed; their context text is dropped (it would find the paper in one search)
pub = {}
for k, v in SC.items():
    v = dict(v)
    if k in alias:
        v["hits"] = [{kk: vv for kk, vv in h.items() if kk != "context"} for h in v.get("hits", [])]
        v.pop("pdf", None)
    pub[alias.get(k, k)] = v
json.dump(pub, open(os.path.join(OUT, "scan.json"), "w"), indent=1)
# candidates list without the six
c = [x for x in open(os.path.join(DATA, "candidates.txt")).read().split() if x not in alias]
open(os.path.join(OUT, "candidates.txt"), "w").write(" ".join(c) + "\n")
print(len(alias), "aliased;", len(pub), "scan records;", len(c), "candidates")
