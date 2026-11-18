# AI ranked a product page lower for one reason: it didn't know the brand. Rewriting barely helped

Workings for the X Article by Konstantinos Gkolias ([@con_golias](https://x.com/con_golias)), November 2026: a full read
of Monaco, Lenti, Pierri, "The Popular Get More Popular: Auditing Brand Bias in Generative Search",
[arXiv 2611.07614v1](https://arxiv.org/abs/2611.07614) (5 Nov 2026).

The paper released no data or code, so nothing here re-estimates its results. Every number comes from the paper.

| File | What |
|---|---|
| `data/paper_numbers.json` | every number the article uses, typed from the paper, each with the section, table or figure it comes from |
| `code/analysis.py` | derives the few computed values (one percentage, differences, minima and maxima) → `data/summary.json` |
| `code/render.py` | article text: every number is a token filled from `summary.json` (the text itself is not in this repository) |
| `charts/figures.html`, `figures.mjs` | the eight figures and the cover, drawn from `paper_numbers.json`, rendered with Playwright |
| `charts/gif-rank.html`, `gif.mjs`, `gif-rank.gif` | the opening animation: frames rendered with Playwright at 15 fps, assembled into a GIF with Pillow |

The code block in the article is a condensed excerpt of `code/analysis.py`; the values and the printed output are the
same. To redraw the animation: serve this folder, then `BASE=<url of the folder> PAGE=charts/gif-rank.html SEC=8
OUT=<frames dir> PW=<path to playwright> node charts/gif.mjs`, and join the frames with Pillow (64-colour palette,
66 ms per frame, last frame held 3.5 s).

## Easy to mix up

- **0.44 positions** is the gain from the page's real brand *and* real product name, against invented ones. The real
  brand alone, with the invented product, gains 0.30 (Table 2). The article and the figures use the 0.44 comparison.
- **38,400 controlled rankings** is the main experiment: 24 questions × 5 names × 4 texts × 20 orders × 4 models
  (Section 3.2). Section 3.2 also reports a further 9,600 rankings with real-product versions; the article does not
  count them.
- The popularity slope of 0.87 (web search off) and 0.89 (on) and the slope of 0.98 with no buyer description are
  **separate analyses** in Section 4.1, not one series.

Method and limits: `METHOD.md`.
