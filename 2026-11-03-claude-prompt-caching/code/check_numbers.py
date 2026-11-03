# Lists every number in article.md that does not appear in data/summary.json, so each one is either traced to the
# data or explained by hand (dates, years, ratios computed in the text) before the owner sees the draft.
#   python3 code/check_numbers.py
import json
import os
import re

here = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(here, "..", "data", "summary.json"), encoding="utf-8"))
known = set()


def walk(x):
    if isinstance(x, dict):
        for v in x.values():
            walk(v)
    elif isinstance(x, list):
        for v in x:
            walk(v)
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        if isinstance(x, float):
            known.add(f"{x:.1f}")
        for f in (x, round(x), round(x, 1)):
            known.add(f"{f:,}".rstrip("0").rstrip(".") if isinstance(f, float) else f"{f:,}")
            known.add(str(f).rstrip("0").rstrip(".") if isinstance(f, float) else str(f))


walk(S)
text = open(os.path.join(here, "..", "article.md"), encoding="utf-8").read()
text = re.sub(r"https?://\S+", "", text)  # links carry ids, not findings
text = re.sub(r"charts/\d\d-", "charts/", text)  # chart file numbers
miss = {}
for m in re.finditer(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", text):
    tok = m.group(0).rstrip(".,")
    if tok not in known:
        line = text.count("\n", 0, m.start()) + 1
        miss.setdefault(tok, []).append(line)
for tok, lines in sorted(miss.items(), key=lambda kv: kv[1][0]):
    print(f"{tok:>10}  lines {lines[:8]}")
print(len(miss), "numbers not found in summary.json (check each by hand)")
