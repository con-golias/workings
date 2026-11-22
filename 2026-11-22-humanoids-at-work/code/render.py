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
    parts = path.split(".")
    while parts:
        part = parts.pop(0)
        if isinstance(x, dict) and part not in x and ".".join([part] + parts) in x:
            part, parts = ".".join([part] + parts), []  # a key that itself holds a dot (e.g. "CLAUDE.md")
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
    if fmt == "1":
        return f"{x:.1f}".replace("-", "−")
    if fmt == "2":
        return f"{x:.2f}"
    if fmt == "0":
        # Round half up, as the charts do (JavaScript toFixed), so 78.5 is 79 in both.
        from decimal import Decimal, ROUND_HALF_UP
        return f"{int(Decimal(str(x)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)):,}"
    if isinstance(x, float):
        # Paper values are typed with the precision the paper reports: print them as typed (0.44, 0.022, -0.001).
        return repr(x).replace("-", "−")
    return str(x)


out = re.sub(r"\{\{([A-Za-z_][^{}|]*?(?:\|[,012])?)\}\}", sub, src)
if "{{" in out:
    sys.exit("token left unrendered: " + out[out.index("{{"):][:80])  # not ${{ }} in YAML examples
if bad:
    sys.exit("unresolved: " + ", ".join(sorted(set(bad))))
left = re.findall(r"\[(?:TODO[^\]]*|EMBED: TBD|OWNER[^\]]*)\]", out)
if left:
    print("OPEN MARKERS:", left)
    if "--final" in sys.argv:
        sys.exit("open markers left; not final")
open(os.path.join(root, "article.md"), "w", encoding="utf-8").write(out)
print("article.md written,", len(re.findall(r"\b\w+\b", out)), "words")
