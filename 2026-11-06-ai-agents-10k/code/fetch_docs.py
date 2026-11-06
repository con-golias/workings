"""Download each hit document from EDGAR Archives and keep its plain text (gzip) under ../data/docs/ (local only)."""
import json, os, re, gzip, html, sys, concurrent.futures as cf
from sec import get
os.makedirs("../data/docs", exist_ok=True)
rows = [json.loads(l) for l in open("../data/hits.jsonl")]
def text_of(b):
    s = b.decode("utf8", "ignore")
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h\d|td)>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s
def one(r):
    adsh, fn = r["id"].split(":", 1)
    out = "../data/docs/%s__%s.txt.gz" % (adsh, fn.replace("/", "_"))
    if os.path.exists(out): return 0
    cik = str(int(r["ciks"][0]))
    url = "https://www.sec.gov/Archives/edgar/data/%s/%s/%s" % (cik, adsh.replace("-", ""), fn)
    try:
        b = get(url, raw=True)
    except Exception as e:
        print("ERR", url, e, file=sys.stderr); return 1
    with gzip.open(out, "wt", encoding="utf8") as f: f.write(text_of(b))
    return 0
with cf.ThreadPoolExecutor(6) as ex: errs = sum(ex.map(one, rows))
print("done, errors:", errs, file=sys.stderr)
