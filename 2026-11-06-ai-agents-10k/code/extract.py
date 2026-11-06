"""Pull every sentence that names an AI agent out of each document. Output ../data/sentences.jsonl:
one row per (filing, sentence) with the filer, form, date and whether the sentence sits inside the Risk Factors section."""
import json, gzip, re, sys
AG = re.compile(r"\bAI[- ]agents?\b|\bagentic\b|\bautonomous (?:AI )?agents?\b|\bAI-powered agents?\b|\bAI-driven agents?\b|\bdigital agents?\b|\b(?:shopping|software|intelligent|virtual|coding|autonomous) agents?\b", re.I)
CORE = re.compile(r"\bAI[- ]agents?\b|\bartificial intelligence (?:\(.AI.\) )?agents?\b|\bagentic\b|\bautonomous (?:AI )?agents?\b|\bAI-powered agents?\b", re.I)
rows = [json.loads(l) for l in open("../data/hits.jsonl")]
def split_sents(t):
    t = re.sub(r"\s*\n\s*", " \n ", t)
    parts = re.split(r"(?<=[.!?;])\s+(?=[A-Z(\"“])| \n (?=[A-Z•●·\-(])", t)
    return [p.replace(" \n ", " ").strip() for p in parts if p.strip()]
def risk_spans(t):
    """Character spans of Risk Factors sections: from a 'Risk Factors' heading line to the next Item heading."""
    spans = []
    for m in re.finditer(r"(?im)^\s*(?:item\s*1a\.?|item\s*3\.?\s*d\.?|d\.)?\s*[-–—:.]?\s*risk factors\s*\.?\s*$", t):
        nxt = re.search(r"(?im)^\s*item\s*(?:1b|1c|2|4|5)\b", t[m.end():])
        end = m.end() + (nxt.start() if nxt else min(len(t) - m.end(), 400000))
        if end - m.end() > 5000: spans.append((m.start(), end))
    return spans
out = open("../data/sentences.jsonl", "w")
n = 0
for r in rows:
    adsh, fn = r["id"].split(":", 1)
    t = gzip.open("../data/docs/%s__%s.txt.gz" % (adsh, fn.replace("/", "_")), "rt", encoding="utf8").read()
    spans = risk_spans(t)
    pos = 0
    sents = split_sents(t)
    for j, s in enumerate(sents):
        i = t.find(s[:60], pos); pos = i if i >= 0 else pos
        if not CORE.search(s): continue
        if len(s) > 3000: s = s[:3000]
        in_rf = any(a <= pos < b for a, b in spans)
        out.write(json.dumps({"adsh": adsh, "file": fn, "form": r["form"], "date": r["file_date"], "period": r["period_ending"],
            "cik": r["ciks"][0], "name": r["display_names"][0], "sic": (r["sics"] or [None])[0], "risk_section": in_rf,
            "has_rf_section": bool(spans), "s": s, "next": " ".join(x[:1500] for x in sents[j+1:j+3])}) + "\n"); n += 1
print(n, "sentences", file=sys.stderr)
