# Sensitivity (pre-registered): restructurings whose Item 2.05 only points to an exhibit. Reads every EX-99 of
# those filings and lists AI sentences. Output: $RAW/exhibit_only.json
import html, json, os, re, sys, time, urllib.request
sys.stdout.reconfigure(encoding="utf-8")
UA = "Konstantinos Gkolias research contact@emarkss.com"
RAW = os.environ.get("RAW", "raw")
AI = re.compile(r"artificial intelligence|\bAI\b|agentic|generative|machine learning|intelligence tools", re.I)


def get(u):
    time.sleep(0.4)
    return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=60).read().decode("utf-8", "replace")


def plain(h):
    h = re.sub(r"(?is)<(script|style|ix:header).*?</\1>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h)).replace("\xa0", " "))


out = []
for x in json.load(open(os.path.join(RAW, "restructurings.json"))):
    if not x["exhibit_only"]:
        continue
    folder = f"https://www.sec.gov/Archives/edgar/data/{int(x['cik'])}/{x['adsh'].replace('-', '')}/"
    idx = get(folder + f"{x['adsh']}-index.htm")
    ai = []
    for row in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", idx):
        cells = re.findall(r"(?is)<td[^>]*>(.*?)</td>", row)
        m = re.search(r'href="([^"]+)"', cells[2]) if len(cells) >= 4 else None
        if m and re.sub(r"<[^>]+>|\s", "", cells[3]).startswith("EX-99"):
            t = plain(get(folder + m.group(1).split("/")[-1]))
            ai += [s[:300] for s in re.split(r"(?<=[.!?])\s", t) if AI.search(s)]
    out.append({"adsh": x["adsh"], "date": x["file_date"], "name": x["name"], "workforce": x["workforce"], "ai": ai[:5]})
    print(x["file_date"], x["name"][:40], "workforce", x["workforce"], "AI sentences", len(ai))
    for s in ai[:3]:
        print("   >", s)
json.dump(out, open(os.path.join(RAW, "exhibit_only.json"), "w"), indent=1)
