"""Crop the humanoid-by-application table and its note from Unitree's reply to the Shanghai Stock Exchange inquiry
(20 Mar 2026, SSE disclosure 002178_20260320_OE27.pdf), page image at 3x, and outline the guided-tours note.
Put the PDF at data/raw/unitree_OE27.pdf, then: python code/shot_unitree.py  ->  charts/shot-unitree-table.png"""
import os
import fitz  # PyMuPDF

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
doc = fitz.open(os.path.join(root, "data", "raw", "unitree_OE27.pdf"))
for pno in range(doc.page_count):
    page = doc[pno]
    if "73.60%" in page.get_text() and "企业导览" in page.get_text():
        break
else:
    raise SystemExit("page not found")
words_top = page.search_for("根据应用领域划分的收入构成情况如下")
note = page.search_for("约为 50-70%") or page.search_for("50-70%")
head = page.search_for("（2）人形机器人应用领域情况")
top = (head[0].y0 if head else words_top[0].y0) - 8
bottom = note[-1].y1 + 3
clip = fitz.Rect(page.rect.x0 + 40, top, page.rect.x1 - 40, bottom)
nl = page.search_for("其中企业导览的占比较高")
if nl:  # outline the note: "of which enterprise guided tours account for a higher share, about 50-70%"
    r = fitz.Rect(nl[0].x0 - 3, nl[0].y0 - 2, note[-1].x1 + 3, note[-1].y1 + 2)
    page.draw_rect(r, color=(0.435, 0.518, 0.588), width=1.6)
pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=clip)
pix.save(os.path.join(root, "charts", "shot-unitree-table.png"))
print("page", pno + 1, "clip", clip, pix.width, pix.height)
