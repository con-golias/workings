"""Re-check before publication (16 Nov 2026): has anything changed since the 6-7 Nov run?

For Lin's 18 and the 7 papers whose current version hides an instruction:
  1. re-read the /abs page: version list and versions marked "(withdrawn)";
  2. download again (fresh, not from the cache) every prompted version of the 18 that was served on 7 Nov, and the
     current PDF of the 7, and re-run hidden.check() on each.
Same politeness as the first run: arxiv.org/abs and /pdf only, 15 s apart. Output: data/recheck.json (with the date).
PDFs go to data/pdf_recheck/ (not published).
"""
import datetime, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import the18  # noqa: E402  (shared polite fetcher)
from hidden import check  # noqa: E402

DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(DATA, "pdf_recheck")
os.makedirs(OUT, exist_ok=True)


def fetch(aidv):
    path = os.path.join(OUT, aidv + ".pdf")
    st, body = the18.get(f"https://arxiv.org/pdf/{aidv}")
    if st != 200 or not body.startswith(b"%PDF"):
        return st, None
    open(path, "wb").write(body)
    try:
        r = check(path)
    except Exception as e:  # damaged PDF
        r = {"error": str(e)}
    return st, r


def main():
    s = json.load(open(os.path.join(DATA, "summary.json")))
    t18 = json.load(open(os.path.join(DATA, "the18.json")))
    res = {"checked_utc": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M"), "the18": {}, "current_hidden": {}}
    outp = os.path.join(DATA, "recheck.json")
    for aid, row in t18.items():
        hist, wd, _ = the18.versions(aid)
        old_n = len(row["versions"])
        rec = {"versions_then": old_n, "versions_now": len(hist), "withdrawn_versions": the18.VERSION_WITHDRAWN.get(aid, []),
               "paper_withdrawn_notice": wd, "prompted": {}}
        for v in row["versions"]:
            if v.get("hit") and v.get("status") == 200:
                st, r = fetch(f"{aid}v{v['v']}")
                rec["prompted"][v["v"]] = {"status": st, "hidden_hits": (r or {}).get("hidden_hits")}
                print(aid, v["v"], st, (r or {}).get("hidden_hits"), flush=True)
        res["the18"][aid] = rec
        json.dump(res, open(outp, "w"), indent=1)
    for aid in s["current_hidden"]:
        hist, wd, _ = the18.versions(aid)
        st, r = fetch(aid)
        res["current_hidden"][aid] = {"versions_now": len(hist), "status": st, "hidden_hits": (r or {}).get("hidden_hits"),
                                      "withdrawn_versions": the18.VERSION_WITHDRAWN.get(aid, [])}
        print("current", aid, len(hist), st, (r or {}).get("hidden_hits"), flush=True)
        json.dump(res, open(outp, "w"), indent=1)
    print("done", flush=True)


if __name__ == "__main__":
    main()
