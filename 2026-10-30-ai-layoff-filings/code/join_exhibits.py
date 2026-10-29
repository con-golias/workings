# For each join company that filed an Item 2.05 in 2026: where does AI appear? The 2.05 text, another
# exhibit of the same 8-K (press release, memo), or neither. Output: $RAW/join_exhibits.json
import html, json, os, re, sys, time, urllib.request
sys.stdout.reconfigure(encoding="utf-8")
UA = "Konstantinos Gkolias research contact@emarkss.com"
RAW = os.environ.get("RAW", "raw")
AI = re.compile(r"artificial intelligence|\bAI\b|agentic|intelligence tools|generative|machine learning", re.I)


def get(u):
    time.sleep(0.4)
    return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=60).read().decode("utf-8", "replace")


def plain(h):
    h = re.sub(r"(?is)<(script|style|ix:header).*?</\1>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h)).replace("\xa0", " "))


join = json.load(open(os.path.join(RAW, "join_filers.json")))
X = {x["adsh"]: x for x in json.load(open(os.path.join(RAW, "restructurings.json")))}
out = {}
for tk, j in join.items():
    for d, form, adsh in j["205_2026"]:
        adshs = [adsh] + (["0001477333-26-000033"] if tk == "NET" else [])  # Cloudflare's untagged original 8-K
        for a in adshs:
            folder = f"https://www.sec.gov/Archives/edgar/data/{j['cik']}/{a.replace('-', '')}/"
            idx = get(folder + f"{a}-index.htm")
            docs = []
            for row in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", idx):
                cells = re.findall(r"(?is)<td[^>]*>(.*?)</td>", row)
                if len(cells) >= 4:
                    typ = re.sub(r"<[^>]+>|\s", "", cells[3])
                    m = re.search(r'href="([^"]+)"', cells[2])
                    if m and typ.startswith("EX-99"):
                        docs.append((typ, m.group(1).split("/")[-1]))
            body = X.get(a, {}).get("body", "")
            rec = {"ticker": tk, "adsh": a, "date": d, "in_205": [s for s in re.split(r"(?<=\.)\s", body) if AI.search(s)][:4], "exhibits": {}}
            for typ, fn in docs:
                t = plain(get(folder + fn))
                rec["exhibits"][f"{typ} {fn}"] = {"len": len(t), "ai": [s[:400] for s in re.split(r"(?<=[.!?])\s", t) if AI.search(s)][:6]}
            out[a] = rec
            print(f"\n## {tk} {d} {a}\n  2.05: {rec['in_205'][:2]}")
            for k, v in rec["exhibits"].items():
                print(f"  {k} len={v['len']} ai={len(v['ai'])}")
                for s in v["ai"][:3]:
                    print("     >", s[:260])
json.dump(out, open(os.path.join(RAW, "join_exhibits.json"), "w"), indent=1)
