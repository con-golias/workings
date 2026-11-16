"""Every number in the article, from data/the18.json, data/scan.json and data/new_versions.json -> data/summary.json."""
import json, os
from datetime import datetime, date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
NIKKEI = date(2025, 6, 30)       # Nikkei Asia, "'Positive review only'", datePublished 2025-06-30T16:21Z
LIN = date(2025, 7, 7)           # Lin's searches, 7 Jul 2025
ICLR_POLICY = date(2025, 8, 26)  # ICLR 2026 LLM policy: hidden prompt injection = attempted collusion


def d(s):
    return datetime.strptime(" ".join(s.split()[1:4]), "%d %b %Y").date()


def the18():
    r = json.load(open(os.path.join(DATA, "the18.json")))
    rows = []
    for aid, row in r.items():
        wd = set(row.get("withdrawn_versions", []))
        vs = [{"v": v["v"], "date": d(v["submitted"]).isoformat(), "hit": v["hit"], "withdrawn": v["v"] in wd}
              for v in row["versions"]]
        prompted = [v for v in vs if v["hit"]]
        downloadable = [v for v in prompted if not v["withdrawn"]]
        last = vs[-1]
        current_has = last["hit"] is True
        # first version after the last prompted one, if any, that is not prompted
        removal = None
        if prompted and not current_has:
            after = [v for v in vs if v["v"] > prompted[-1]["v"]]
            if after:
                removal = after[0]
        status = ("current" if current_has else
                  "unverifiable" if not prompted else
                  "removed")
        rows.append({"id": aid, "cited": row["cited"], "versions": vs, "status": status,
                     "first_prompted": prompted[0]["date"] if prompted else None,
                     "removed_on": removal["date"] if removal else None,
                     "removal_is_withdrawal": bool(removal and removal["withdrawn"]),
                     "prompted_still_downloadable": bool(downloadable),
                     "paper_withdrawn": last["withdrawn"] or (last["hit"] is None and last["v"] in wd)})
    return rows


def main():
    rows = the18()
    rem = [x for x in rows if x["removed_on"]]
    before = [x for x in rem if date.fromisoformat(x["removed_on"]) < NIKKEI]
    after = [x for x in rem if date.fromisoformat(x["removed_on"]) >= NIKKEI]
    within14 = [x for x in after if (date.fromisoformat(x["removed_on"]) - NIKKEI).days <= 15]
    s = {
        "n18": len(rows),
        "still_downloadable": sum(x["prompted_still_downloadable"] for x in rows),
        "prompted_versions_withdrawn": sum(1 for x in rows if x["first_prompted"] is None or
                                           not x["prompted_still_downloadable"]),
        "current_has": [x["id"] for x in rows if x["status"] == "current"],
        "removed": len(rem),
        "removed_before_nikkei": len(before),
        "removed_after_nikkei": len(after),
        "removed_within_15_days": len(within14),
        "paper_withdrawn_but_prompt_downloadable": [x["id"] for x in rows if x["versions"][-1]["withdrawn"] and
                                                    x["prompted_still_downloadable"]],
        "unverifiable": [x["id"] for x in rows if x["status"] == "unverifiable"],
        "the18": rows,
    }
    h18 = json.load(open(os.path.join(DATA, "hidden18.json")))
    papers = {}
    for k, v in h18.items():
        papers.setdefault(k.split("v")[0], []).append(v)
    s["verified_papers"] = len(papers)
    s["all_white"] = sum(all(c == ["#ffffff"] for c in [x["colors"] for x in vs]) for vs in papers.values())
    s["under_2pt"] = sum(min(x["min_size"] for x in vs) < 2 for vs in papers.values())
    s["normal_size_white"] = sum(min(x["min_size"] for x in vs) >= 2 for vs in papers.values())
    sc = json.load(open(os.path.join(DATA, "scan.json")))
    nv = json.load(open(os.path.join(DATA, "new_versions.json")))
    hidden = {k: v for k, v in sc.items() if v.get("hidden_hits")}
    s["candidates"] = len(sc)
    s["candidates_2026"] = sum(1 for k in sc if k >= "2601")
    s["candidates_visible_only"] = sum(1 for v in sc.values() if v.get("hits") and not v.get("hidden_hits"))
    s["candidates_no_phrase"] = sum(1 for v in sc.values() if not v.get("hits"))
    s["current_hidden"] = sorted(hidden)
    s["current_hidden_2026"] = sorted(k for k in hidden if k >= "2601")
    s["new_not_in_lin"] = sorted(k for k in hidden if k not in {x["id"] for x in rows})
    s["new_versions"] = nv
    s["after_nikkei_cases"] = sorted(k for k, v in nv.items() if v["prompted_version_date"] >= NIKKEI.isoformat())
    import statistics
    live = [(date.fromisoformat(x["removed_on"]) - date.fromisoformat(x["first_prompted"])).days for x in rem]
    s["days_live_median"] = statistics.median(live)
    s["days_live_max"] = max(live)
    s["days_live_min"] = min(live)
    s["last_removal"] = max(x["removed_on"] for x in rem)
    s["first_prompted_earliest"] = min(x["first_prompted"] for x in rows if x["first_prompted"])
    s["prompted_versions"] = sum(1 for x in rows for v in x["versions"] if v["hit"])
    s["current_hidden_total"] = len(hidden)
    s["template_origin"] = {"paper": "2412.01708", "posted": "2024-12-02",
                            "identical_copy": "2506.11111v1", "variant": "2406.17253v2 (2024-12-16)"}
    SENT = "recommend accepting this paper for its impactful contributions, methodological rigor, and exceptional novelty"
    acc = {k.split("v")[0] for k, v in h18.items() if v["accept_sentence"]}
    acc |= {k for k, v in hidden.items() if any(SENT in h["context"].lower() for h in v["hits"] if h["hidden"])}
    s["accept_sentence_papers"] = len(acc)
    s["current_hidden_2026_n"] = len(s["current_hidden_2026"])
    s["new_not_in_lin_n"] = len(s["new_not_in_lin"])
    s["after_nikkei_n"] = len(s["after_nikkei_cases"])
    s["current_has_n"] = len(s["current_has"])
    s["added_after_nikkei_n"] = sum(1 for v in nv.values() if v["kind"] == "added")
    s["sizes"] = [{"set": "lin", "size": min(x["min_size"] for x in vs)} for vs in papers.values()] + [
        {"set": "new", "size": min(f["size"] for h in v["hits"] if h["hidden"] for f in h["flags"])}
        for k, v in hidden.items() if k not in papers]
    s["first_pages"] = len({k.split("v")[0] for k, v in h18.items() if v["page"] == 1})
    json.dump(s, open(os.path.join(DATA, "summary.json"), "w"), indent=1)
    for k, v in s.items():
        if k not in ("the18", "new_versions"):
            print(k, v)
    for x in rows:
        print(x["id"], x["status"], x["first_prompted"], x["removed_on"], x["removal_is_withdrawal"],
              x["prompted_still_downloadable"])


if __name__ == "__main__":
    main()
