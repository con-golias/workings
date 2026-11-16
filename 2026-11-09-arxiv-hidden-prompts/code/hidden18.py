"""Run hidden.check() on every prompted version of the 18 (cached PDFs) -> data/hidden18.json."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hidden import check  # noqa: E402

DATA = os.path.join(HERE, "..", "data")
r = json.load(open(os.path.join(DATA, "the18.json")))
out = {}
for aid, row in r.items():
    for v in row["versions"]:
        if v["hit"]:
            res = check(os.path.join(DATA, "pdf", f"{aid}v{v['v']}.pdf"))
            fl = [f for h in res["hits"] for f in h["flags"]]
            out[f"{aid}v{v['v']}"] = {"hits": len(res["hits"]), "hidden_hits": res["hidden_hits"],
                                      "min_size": min(f["size"] for f in fl), "colors": sorted({f["color"] for f in fl}),
                                      "page": res["hits"][0]["page"], "pages": res["pages"],
                                      "accept_sentence": any("recommend accepting this paper for its impactful contributions, methodological rigor, and exceptional novelty"
                                                             in h["context"].lower()
                                                             for h in res["hits"])}
json.dump(out, open(os.path.join(DATA, "hidden18.json"), "w"), indent=1)
for k, v in out.items():
    print(k, v)
