# article.src.md -> article.md. Every data number in the text is a token {{path}} read from data/summary.json:
# {{a.b}}, {{x|,}} (thousands separator), {{x|0}} (no decimals, half up), {{x|2}} (two decimals, for ratios).
# Fails on any token that does not resolve, so no number is typed by hand.
#   python3 code/render.py
import json
import os
import re
import sys

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(here, "..")
S = json.load(open(os.path.join(root, "data", "summary.json"), encoding="utf-8"))
src = open(os.path.join(root, "article.src.md"), encoding="utf-8").read()
bad = []


def get(path):
    x = S
    for part in path.split("."):
        if isinstance(x, dict) and part in x:
            x = x[part]
        elif isinstance(x, list) and part.isdigit() and int(part) < len(x):
            x = x[int(part)]
        else:
            raise KeyError(path)
    return x


def sub(m):
    path, fmt = (m.group(1).split("|") + [""])[:2]
    try:
        x = get(path.strip())
    except KeyError:
        bad.append(path)
        return m.group(0)
    if fmt == ",":
        return f"{x:,}"
    if fmt == "2":
        return f"{x:.2f}"
    if fmt == "0":
        # Round half up, as the charts do (JavaScript toFixed), so 78.5 is 79 in both.
        from decimal import Decimal, ROUND_HALF_UP
        return f"{int(Decimal(str(x)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)):,}"
    if isinstance(x, float):
        return f"{x:.1f}"
    return str(x)


out = re.sub(r"(?<!\$)\{\{([A-Za-z_][\w.]*(?:\|[,02])?)\}\}", sub, src)  # not ${{ }} in YAML examples
if bad:
    sys.exit("unresolved: " + ", ".join(sorted(set(bad))))
open(os.path.join(root, "article.md"), "w", encoding="utf-8").write(out)
print("article.md written,", len(re.findall(r"\b\w+\b", out)), "words")
