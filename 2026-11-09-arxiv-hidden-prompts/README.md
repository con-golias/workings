# Hidden reviewer instructions in arXiv papers, version by version

Workings for the X Article *"18 Papers Hid Prompt Injections for AI Reviewers. arXiv Still Serves 16 of Them"*
(Konstantinos Gkolias, [@con_golias](https://x.com/con_golias), November 2026).

Starting point: Z. Lin, "Hidden Prompts in Manuscripts Exploit AI-Assisted Peer Review", arXiv:2507.06185,
Communications of the ACM 69(7), 2026. Table 1 lists the 18 papers found on 7 July 2025.

## Rerun

Python 3.11, PyMuPDF, pdftotext (poppler). Set a User-Agent with your contact: `export ARXIV_UA="Your Name you@example.com"`.
Requests go only to `arxiv.org/abs` and `arxiv.org/pdf`, 15 s apart (arXiv's Crawl-delay). In `code/`:

| Step | Script | Output |
|---|---|---|
| 1. Version history of Lin's 18; every version's PDF; phrase match | `the18.py` (then `the18.py --withdrawn`) | `data/the18.json` |
| 2. Colour, size and position of each matched span in the prompted versions | `hidden18.py` (uses `hidden.py`) | `data/hidden18.json` |
| 3. Current PDF of each full-text-search result; hidden-or-quoted test | `scan.py` (reads `data/candidates.txt`) | `data/scan.json` (public copy: `data/public/`) |
| 4. Every number in the article | `analyze.py`, then `public.py` | `data/summary.json` (public copy: `data/public/`) |
| 5. Figures | `charts/figures.html` (+ `figures.mjs`) | `charts/*.png` |
| 6. Opening video (15 s) | `charts/video.html` (+ `video.mjs`, then ffmpeg) | `charts/video.mp4` |
| 7. Article text, every number filled from the summary | `render.py` | the article's text (not in this repository) |
| 8. Recheck of Lin's 18 and of the 7 current hidden cases, 16 Nov 2026 | `recheck.py` | nothing changed; its output names the 6 papers below, so it is not here |

PDFs are cached in `data/pdf/` and are not in this repository.

## What is and is not here

- Lin's 18 papers appear by arXiv identifier, as in Lin's published table.
- The 6 papers outside Lin's list that carry a hidden instruction in their current version are replaced by `new-1` to
  `new-6` in `data/public/` (summary, scan records without their text, version records), and left out of
  `data/public/candidates.txt`. Their field, version dates, font size and colour are kept. The 18 queries are in
  METHOD.md: rerunning them and steps 3–4 finds them again.

## Limits

A floor, not a rate: the full-text search finds only the phrases it is asked for. Instructions hidden in images, in
remapped fonts or in metadata are not detected. A version history shows when a line appeared, not who wrote it or why.
