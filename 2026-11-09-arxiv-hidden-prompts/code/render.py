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
    if fmt == "W":
        return ["Zero","One","Two","Three","Four","Five","Six","Seven","Eight","Nine","Ten"][x]
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


def d(s):
    m = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{int(s[8:])} {m[int(s[5:7]) - 1]} {s[:4]}"


def table18():
    """[TABLE: the18] -> Lin's 18 papers (public ids), one row each, from summary.json."""
    rows = ["| Paper (arXiv) | Hidden line first posted | Clean version posted | Version with the line, today |", "|---|---|---|---|"]
    for r in sorted(S["the18"], key=lambda r: (r["first_prompted"] or "9999", r["id"])):
        link = f"[{r['id']}](https://arxiv.org/abs/{r['id']})"
        if r["status"] == "unverifiable":
            # The version Lin cites is withdrawn (no PDF). Dates from the version history (data/the18.json).
            T = json.load(open(os.path.join(root, "data", "the18.json"), encoding="utf-8"))[r["id"]]
            import datetime
            iso = lambda s: datetime.datetime.strptime(s.strip()[5:16].strip(), "%d %b %Y").strftime("%Y-%m-%d")
            cited_v = int(r["cited"].split("v")[-1])
            first = next(v for v in T["versions"] if v["v"] == cited_v)
            clean = next((v for v in T["versions"] if v["v"] > cited_v and v["status"] == 200 and v["hit"] is False), None)
            rows.append(f"| {link} | {d(iso(first['submitted']))} (per Lin) | {d(iso(clean['submitted'])) if clean else 'none (paper withdrawn)'} | version withdrawn, not served |")
            continue
        clean = d(r["removed_on"]) if r["removed_on"] else "**never**"
        today = "still served" + (" (paper withdrawn)" if r["paper_withdrawn"] else "") if r["prompted_still_downloadable"] else "not served"
        rows.append(f"| {link} | {d(r['first_prompted'])} | {clean} | {today} |")
    return "\n".join(rows)


# Derived counts (from summary.json, not typed by hand).
S["versions_total"] = sum(len(x["versions"]) for x in S["the18"])
S["removed_still_served"] = sum(1 for x in S["the18"] if x["prompted_still_downloadable"] and x["removed_on"])
src = src.replace("[TABLE: the18]", table18())
out = re.sub(r"\{\{([A-Za-z_][\w.]*(?:\|[,02W])?)\}\}", sub, src)  # not ${{ }} in YAML examples
if bad:
    sys.exit("unresolved: " + ", ".join(sorted(set(bad))))
open(os.path.join(root, "article.md"), "w", encoding="utf-8").write(out)
print("article.md written,", len(re.findall(r"\b\w+\b", out)), "words")
