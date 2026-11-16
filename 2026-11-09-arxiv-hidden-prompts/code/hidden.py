"""Is a matched instruction hidden in the rendered PDF?

For every text span (PyMuPDF) that belongs to a reviewer-directed phrase match, record the fill colour, the font
size, the render mode (3 = invisible) and whether the span lies outside the page. Hidden = white or near-white
fill, size under 2 pt, invisible render mode, or off-page.
Usage: python -I hidden.py <pdf> ...   prints one JSON line per PDF.
"""
import json, os, re, sys

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from patterns import RX, norm  # noqa: E402


def spans(doc):
    for pno, page in enumerate(doc):
        rect = page.rect
        d = page.get_text("rawdict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        for b in d["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    txt = "".join(c["c"] for c in s.get("chars", []))
                    if not txt.strip():
                        continue
                    yield pno, txt, s, rect


def is_hidden(s, rect):
    c = s["color"]
    r, g, b = (c >> 16) & 255, (c >> 8) & 255, c & 255
    white = min(r, g, b) >= 240
    tiny = s["size"] < 2.0
    x0, y0, x1, y1 = s["bbox"]
    off = x1 < rect.x0 or x0 > rect.x1 or y1 < rect.y0 or y0 > rect.y1
    alpha = s.get("alpha", 255) == 0
    return {"white": white, "tiny": tiny, "offpage": off, "transparent": alpha, "size": round(s["size"], 2),
            "color": f"#{c:06x}"}


def check(path):
    doc = fitz.open(path)
    sp = list(spans(doc))
    # one long string with offsets back to spans
    buf, idx = [], []
    pos = 0
    for i, (pno, txt, s, rect) in enumerate(sp):
        t = norm(txt) + " "
        buf.append(t)
        idx.append((pos, pos + len(t), i))
        pos += len(t)
    full = "".join(buf)
    hits = []
    for m in RX.finditer(full):
        inv = [k for (a, b, k) in idx if a < m.end() and b > m.start()]
        flags = [is_hidden(sp[k][2], sp[k][3]) for k in inv]
        hidden = any(f["white"] or f["tiny"] or f["offpage"] or f["transparent"] for f in flags)
        hits.append({"page": sp[inv[0]][0] + 1 if inv else None, "phrase": m.group(0), "hidden": hidden,
                     "flags": flags[:3], "context": full[max(0, m.start() - 200): m.end() + 300]})
    return {"pdf": os.path.basename(path), "pages": len(doc), "hits": hits,
            "hidden_hits": sum(h["hidden"] for h in hits)}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for p in sys.argv[1:]:
        print(json.dumps(check(p), ensure_ascii=False))
