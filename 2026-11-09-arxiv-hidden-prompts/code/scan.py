"""Candidates from arXiv's full-text search (search.arxiv.org): 18 phrase queries issued from a logged-out browser
session on 6 Nov 2026, result pages paged by a short script about 5 s apart (about 75 result pages in all, up to 60
results per query); ids in data/candidates.txt. For each: fetch the current PDF (arxiv.org/pdf/<id>, 15 s apart) and run
hidden.check(). Output: data/scan.json (one record per id). PDFs cached in data/pdf/ (not published).
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import the18  # noqa: E402  (shared polite fetcher)
from hidden import check  # noqa: E402

DATA = os.path.join(HERE, "..", "data")


def main():
    ids = open(os.path.join(DATA, "candidates.txt")).read().split()
    outp = os.path.join(DATA, "scan.json")
    res = json.load(open(outp)) if os.path.exists(outp) else {}
    for aid in ids:
        if aid in res:
            continue
        path = os.path.join(the18.PDF, aid + ".pdf")
        if not os.path.exists(path):
            st, body = the18.get(f"https://arxiv.org/pdf/{aid}")
            if st != 200 or not body.startswith(b"%PDF"):
                res[aid] = {"status": st}
                json.dump(res, open(outp, "w"), indent=1)
                continue
            open(path, "wb").write(body)
        try:
            r = check(path)
        except Exception as e:  # damaged PDF
            r = {"error": str(e)}
        r["status"] = 200
        res[aid] = r
        print(aid, len(r.get("hits", [])), r.get("hidden_hits"), flush=True)
        json.dump(res, open(outp, "w"), indent=1)


if __name__ == "__main__":
    main()
