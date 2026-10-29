# Builds the restructuring set from the extracted sections and applies the pre-registered keyword rules.
# Input: $RAW/sections_v2.jsonl. Output: $RAW/restructurings.json, $RAW/ai_matches.tsv (for the hand-read).
import csv, json, os, re, sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sec205

RAW = os.environ.get("RAW", "raw")
ITEM = r"(?:Item|ITEM)\s*{}\s*\.\s*{}"
TITLE = re.compile(r"^(?:Item|ITEM)\s*2\s*\.\s*05\.?\s*[:\-–—]?\s*(?:Costs?\s+Associated|Exit\s+or\s+Disposal)", re.I)
POINTER = re.compile(r"(?:Item|ITEM)\s*([1-9])\s*\.\s*(\d\d)")
EXHIBIT = re.compile(r"Exhibit\s*99", re.I)
# A filing that reports on a plan announced before (unit rule, NOTES 29 Oct).
UPDATE = re.compile(r"previously (?:announced|disclosed|reported)", re.I)
MONTHS = "January February March April May June July August September October November December".split()
FIRST_DATE = re.compile(r"\b(?:On|In|on|in) (" + "|".join(MONTHS) + r")(?: (\d{1,2}),)? (\d{4})")


def is_update(x):
    """True when the section reports a plan announced earlier: 'previously announced', or its first date
    ('In May 2026, the Company announced…') lies more than 30 days before the filing."""
    head = x["body"][:700]
    if UPDATE.search(head):
        return True
    m = FIRST_DATE.search(head)
    if not m:
        return False
    d = date(int(m.group(3)), MONTHS.index(m.group(1)) + 1, int(m.group(2) or 28))
    return (date.fromisoformat(x["file_date"]) - d).days > 30

# Pre-registered keyword lists (NOTES.md, 29 Oct).
WORKFORCE = re.compile(r"employee|headcount|workforce|positions|roles|reduction in force|\bRIF\b|severance|jobs|personnel|staff", re.I)
REASONS = {
    "cost": re.compile(r"cost|efficien|expense|margin|profitab|savings|streamlin|operating model|leaner", re.I),
    "realign": re.compile(r"align|priorit|focus|strateg|reorgani|realloc|invest|transform", re.I),
    "demand": re.compile(r"demand|macro|economic|market conditions|tariff|decline in revenue|volume", re.I),
    "integration": re.compile(r"acquisition|merger|integrat|combined company|synerg", re.I),
}
PURPOSE = re.compile(r"designed to|intended to|in order to|in an effort to|aimed at|with the goal|purpose|objective|"
                     r"as part of|because|due to|in light of|in response to|to (?:reduce|lower|improve|better|align|realign|"
                     r"streamline|focus|prioriti|accelerate|position|support|enable|drive|simplify|optimi|right-size|rebalance|"
                     r"reallocate|invest|fund|achieve|enhance|increase|preserve|extend|conserve|adapt|respond)", re.I)
# Legal boilerplate that matches a purpose word but states no motive (found in the 30-section hand-read).
BOILER = re.compile(r"not currently contemplated|forward-looking|actual results|risks and uncertainties|safe harbor|"
                    r"undertakes no obligation|could cause|may differ materially", re.I)
AI = re.compile(r"artificial intelligence|\bAI\b|agentic|generative|machine learning|automation", re.I)
# Boilerplate words that every 2.05 contains regardless of motive; removed before the reason test.
STOCK = re.compile(r"Costs Associated with Exit or Disposal Activities|restructuring (?:costs|charges)|"
                   r"cost(?:s)? associated with|(?:estimated|total|pre-tax|cash|non-cash) (?:costs|charges)|"
                   r"costs? (?:of|related to|in connection with)", re.I)


def item_section(t, a, b):
    return sec205.item_section(t, re.compile(ITEM.format(a, b)))


def sentences(s):
    return [x.strip() for x in re.split(r"(?<=[.;])\s+(?=[A-Z(“\"])", s) if x.strip()]


rows = [json.loads(l) for l in open(os.path.join(RAW, "sections_v2.jsonl"), encoding="utf-8")]
recs = []
for r in rows:
    # Re-cut from the stored text with the shared rule (a heading after a title word such as
    # "Section 8 - Other Events Item 8.01" ends the section; "under Item 8.01" does not). Dow 2026, 29 Oct.
    sec = sec205.item_section(r.get("text", ""))
    tagged = "2.05" in r["items"]
    real = bool(TITLE.match(sec)) and len(sec) > 150
    if not (tagged or real):
        continue
    body, pointed, exhibit_only = sec, [], False
    if len(sec) < 600:
        for a, b in POINTER.findall(sec[12:]):
            if (a, b) != ("2", "05"):
                extra = item_section(r.get("text", ""), a, b)
                if extra:
                    pointed.append(f"{a}.{b}")
                    body += " " + extra
        exhibit_only = not pointed and bool(EXHIBIT.search(sec))
    recs.append({k: r[k] for k in ("adsh", "cik", "name", "sics", "form", "file_date", "items")} |
                {"tagged": tagged, "section_len": len(sec), "pointed_to": pointed, "exhibit_only": exhibit_only,
                 "body": body})

# One restructuring per company and announcement: an amendment or repeat within 30 days merges into the first.
recs.sort(key=lambda x: (x["cik"], x["file_date"]))
merged = []
for x in recs:
    p = merged[-1] if merged else None
    if p and p["cik"] == x["cik"] and (date.fromisoformat(x["file_date"]) - date.fromisoformat(p["file_date"])).days <= 30:
        p.setdefault("merged", []).append(x["adsh"])
        if len(x["body"]) > len(p["body"]):
            p["body"] = x["body"]
        p["tagged"] = p["tagged"] or x["tagged"]
        continue
    # An update of a plan announced earlier is merged into that plan's first filing when it is in the set.
    # Updates are flagged, not merged: in a 12-case hand check the rule mistook about 4 new decisions for
    # updates (Post Holdings, Olin, Starbucks). The headline unit is the company-year instead (analyze.py).
    x["update"] = is_update(x)
    merged.append(x)

with open(os.path.join(RAW, "ai_matches.tsv"), "w", encoding="utf-8", newline="") as tsv:
    w = csv.writer(tsv, delimiter="\t")
    w.writerow(["adsh", "file_date", "name", "sentence"])
    for x in merged:
        text = x["body"]
        x["workforce"] = bool(WORKFORCE.search(text))
        # Reasons are looked for only in sentences that state a purpose or a cause, never in the cost amounts.
        why = " ".join(s for s in sentences(text) if PURPOSE.search(s) and not BOILER.search(s))
        clean = STOCK.sub(" ", why)
        x["reason_text"] = why[:3000]
        x["reasons"] = [k for k, rx in REASONS.items() if rx.search(clean)]
        x["ai_sentences"] = [s for s in sentences(text) if AI.search(s)]
        for s in x["ai_sentences"]:
            w.writerow([x["adsh"], x["file_date"], x["name"][:60], s[:1200]])

json.dump(merged, open(os.path.join(RAW, "restructurings.json"), "w"), indent=0)
print("restructurings", len(merged), "workforce", sum(x["workforce"] for x in merged),
      "with AI sentence", sum(bool(x["ai_sentences"]) for x in merged), "untagged admitted",
      sum(not x["tagged"] for x in merged), "exhibit only", sum(x["exhibit_only"] for x in merged))
