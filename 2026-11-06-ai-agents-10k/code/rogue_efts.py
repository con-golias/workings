"""Second net for the 'agent acts on its own' risk, independent of the agent-phrase corpus: search EDGAR full text for
the action phrases themselves, open each hit and keep it when an agent word sits within 600 characters of the phrase."""
import json, re, gzip, os, html
from sec import efts, get
PH = ['"unintended or unauthorized actions"', '"unintended or unauthorised actions"', '"unauthorized actions"', '"unauthorised actions"',
      '"outside of their intended scope"', '"beyond their intended scope"', '"outside the scope of their instructions"',
      '"exceeding permissions"', '"conceal activity"', '"conceal actions"', '"take unintended actions"', '"erroneous, irreversible"',
      '"acting without supervision"', '"without human oversight"']
FORMS = ["10-K", "10-Q", "20-F", "40-F", "10-K/A"]
AGW = re.compile(r"\bagents?\b|agentic|autonomous (AI|systems)", re.I)
hits = {}
for q in PH:
    for f in FORMS:
        frm = 0
        while True:
            d = efts(q, f, "2024-01-01", "2026-11-05", frm); h = d["hits"]["hits"]
            for x in h: hits.setdefault(x["_id"], (x["_source"], set()))[1].add(q)
            frm += len(h)
            if not h or frm >= d["hits"]["total"]["value"]: break
print(len(hits), "documents")
def text(src, _id):
    adsh, fn = _id.split(":", 1)
    p = "../data/docs/%s__%s.txt.gz" % (adsh, fn.replace("/", "_"))
    if os.path.exists(p): return gzip.open(p, "rt", encoding="utf8").read()
    b = get("https://www.sec.gov/Archives/edgar/data/%d/%s/%s" % (int(src["ciks"][0]), adsh.replace("-", ""), fn), raw=True).decode("utf8", "ignore")
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<[^>]+>", " ", re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", b)))).replace("\xa0", " ")
    with gzip.open(p, "wt", encoding="utf8") as fo: fo.write(t)
    return t
out = []
for _id, (src, qs) in hits.items():
    t = text(src, _id).replace("\n", " ")
    for q in qs:
        for m in re.finditer(re.escape(q.strip('"')), t, re.I):
            w = t[max(0, m.start() - 600): m.end() + 300]
            if AGW.search(w):
                out.append({"cik": src["ciks"][0], "name": src["display_names"][0], "date": src["file_date"], "form": src["form"],
                            "id": _id, "phrase": q, "window": w}); break
json.dump(out, open("../data/rogue_efts.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)
first = {}
for o in sorted(out, key=lambda o: o["date"]): first.setdefault(o["cik"], o)
print(len(first), "companies")
for o in first.values(): print(o["date"], o["form"], o["name"][:45], "|", o["phrase"])
