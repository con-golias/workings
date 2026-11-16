"""The 18 arXiv papers Lin (2025, CACM 2026) found with hidden reviewer prompts on 7 July 2025.

For each paper: read every version from its /abs page, fetch each version's PDF (arxiv.org/pdf is allowed by
robots.txt; 15 s between requests, its Crawl-delay), extract text with pdftotext and record whether a
reviewer-directed instruction is present. Output: data/the18.json. PDFs cached in data/pdf/ (not published).
"""
import json, os, re, subprocess, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PDF = os.path.join(DATA, "pdf")
os.makedirs(PDF, exist_ok=True)
UA = os.environ.get("ARXIV_UA", "independent research (contact in repo README)")
DELAY = 15

# Lin, Table 1: id and the version Lin cites
LIN = ["2408.13940v3", "2403.08142v2", "2501.13461v1", "2212.08983v2", "2501.08667v1", "2506.00418v1",
       "2505.15075v1", "2406.17241v3", "2502.19918v2", "2506.03074v1", "2505.11718v1", "2407.16803v3",
       "2506.13901v1", "2506.01324v1", "2505.22998v1", "2406.17253v2", "2506.11111v1", "2505.16211v1"]

sys.path.insert(0, HERE)
from patterns import find_hits  # noqa: E402

_last = [0.0]
VERSION_WITHDRAWN = {}


def get(url):
    wait = DELAY - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                _last[0] = time.time()
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            _last[0] = time.time()
            if e.code in (403, 404, 410):
                return e.code, b""
            time.sleep(60 * (attempt + 1))
        except Exception:
            time.sleep(60 * (attempt + 1))
    return None, b""


def versions(aid):
    """[(version, date_string)] from the abs page's submission history."""
    st, body = get(f"https://arxiv.org/abs/{aid}")
    t = body.decode("utf-8", "ignore")
    hist = re.findall(r"\[v(\d+)\](?:</a>)?</strong>\s*([A-Za-z]{3}, \d{1,2} [A-Za-z]{3} \d{4} [\d:]+ UTC)", t)
    VERSION_WITHDRAWN[aid] = [int(v) for v in re.findall(
        r"\[v(\d+)\](?:</a>)?</strong>\s*[A-Za-z]{3}, [^<]*?UTC \([^)]*\)\s*(?:<em>)?\(withdrawn\)", t)]
    wd = "withdrawn" in t.lower() and "This paper has been withdrawn" in t
    title = re.search(r'<meta name="citation_title" content="([^"]+)"', t)
    return [(int(v), d) for v, d in hist], wd, (title.group(1) if title else "")


def pdf_text(aidv):
    path = os.path.join(PDF, aidv + ".pdf")
    if not os.path.exists(path) or os.path.getsize(path) < 1000:
        st, body = get(f"https://arxiv.org/pdf/{aidv}")
        if st != 200 or not body.startswith(b"%PDF"):
            return None, st
        open(path, "wb").write(body)
    out = subprocess.run(["pdftotext", "-q", path, "-"], capture_output=True)
    return out.stdout.decode("utf-8", "ignore"), 200


def refresh_withdrawn():
    """Second pass (7 Nov): mark versions arXiv lists as "(withdrawn)" (no PDF served)."""
    outp = os.path.join(DATA, "the18.json")
    res = json.load(open(outp))
    for aid, row in res.items():
        versions(aid)
        row["withdrawn_versions"] = VERSION_WITHDRAWN.get(aid, [])
        print(aid, row["withdrawn_versions"], flush=True)
    json.dump(res, open(outp, "w"), indent=1)


def main():
    outp = os.path.join(DATA, "the18.json")
    res = json.load(open(outp)) if os.path.exists(outp) else {}
    for cited in LIN:
        aid = cited.split("v")[0]
        if aid in res and res[aid].get("done"):
            continue
        hist, wd, title = versions(aid)
        row = {"cited": cited, "title": title, "withdrawn_notice": wd, "versions": []}
        for v, d in hist:
            text, st = pdf_text(f"{aid}v{v}")
            hits = find_hits(text) if text else None
            row["versions"].append({"v": v, "submitted": d, "status": st,
                                    "hit": bool(hits) if hits is not None else None,
                                    "snippets": hits[:3] if hits else []})
            print(aid, v, d, st, bool(hits), flush=True)
        row["done"] = True
        res[aid] = row
        json.dump(res, open(outp, "w"), indent=1)


if __name__ == "__main__":
    refresh_withdrawn() if "--withdrawn" in sys.argv else main()
