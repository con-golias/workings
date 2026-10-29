# Fetches the primary 8-K document of every candidate filing and cuts out its Item 2.05 section.
# Input: $RAW/fts_hits.json. Output: $RAW/sections_v2.jsonl (one filing per line, with the document text; resumable).
import html, json, os, re, sys, time, urllib.request

UA = "Konstantinos Gkolias research contact@emarkss.com"
RAW = os.environ.get("RAW", "raw")
OUT = os.path.join(RAW, "sections_v2.jsonl")
HEAD = re.compile(r"item\s*2\s*\.\s*05", re.I)
# The section ends at the next item HEADING ("Item 7.01 Regulation FD", "ITEM 9.01. Financial ...") or at
# the signature block; an in-text reference ("as described under Item 8.01 of this report") does not end it.
NEXT = re.compile(r"(?<![A-Za-z,] )(?:Item|ITEM)\s*[1-9]\s*\.\s*\d\d\.?\s*[:\-–—]?\s*[A-Z][A-Za-z]|SIGNATURES?\b|Signatures?\s+Pursuant")


def get(url):
    for attempt in range(6):
        time.sleep(0.34 + 4 * attempt)
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read().decode("utf-8", "replace")
        except Exception as e:
            err = e
            if getattr(e, "code", None) == 404:
                break
    raise err


def plain(h):
    h = re.sub(r"(?is)<(script|style|ix:header).*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>", " ", h)
    t = html.unescape(re.sub(r"<[^>]+>", " ", h))
    t = t.replace("\xa0", " ").replace(" ", " ").replace("​", "")
    return re.sub(r"\s+", " ", t).strip()


def primary_doc(f):
    for fn, ft in f["docs"].items():
        if ft in ("8-K", "8-K/A"):
            return fn
    folder = f"https://www.sec.gov/Archives/edgar/data/{int(f['cik'])}/{f['adsh'].replace('-', '')}/"
    idx = get(folder + f"{f['adsh']}-index.htm")
    for row in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", idx):
        cells = re.findall(r"(?is)<td[^>]*>(.*?)</td>", row)
        if len(cells) >= 4 and re.sub(r"<[^>]+>|\s", "", cells[3]) in ("8-K", "8-K/A"):
            m = re.search(r'href="([^"]+)"', cells[2])
            if m:
                return m.group(1).split("/")[-1].replace("ix?doc=", "")
    return None


def section(t):
    best = ""
    for m in HEAD.finditer(t):
        rest = t[m.end():]
        n = NEXT.search(rest)
        # A heading followed straight away by another item is a cross-reference or a list, not the section.
        s = t[m.start(): m.end() + (n.start() if n else min(len(rest), 8000))]
        if len(s) > len(best):
            best = s
    return best


done = set()
if os.path.exists(OUT):
    done = {json.loads(l)["adsh"] for l in open(OUT, encoding="utf-8")}
filings = json.load(open(os.path.join(RAW, "fts_hits.json")))["filings"]
with open(OUT, "a", encoding="utf-8") as out:
    for i, f in enumerate(filings):
        if f["adsh"] in done:
            continue
        rec = {"adsh": f["adsh"], "cik": f["cik"], "name": f["name"], "sics": f["sics"], "form": f["form"],
               "file_date": f["file_date"], "items": f["items"]}
        try:
            fn = primary_doc(f)
            rec["doc"] = fn
            t = plain(get(f"https://www.sec.gov/Archives/edgar/data/{int(f['cik'])}/{f['adsh'].replace('-', '')}/{fn}")) if fn else ""
            rec["doc_len"] = len(t)
            rec["n_headings"] = len(HEAD.findall(t))
            rec["section"] = section(t)
            rec["text"] = t
        except Exception as e:
            rec["error"] = repr(e)
        out.write(json.dumps(rec) + "\n")
        out.flush()
        if i % 100 == 0:
            print(i, len(filings), file=sys.stderr, flush=True)
