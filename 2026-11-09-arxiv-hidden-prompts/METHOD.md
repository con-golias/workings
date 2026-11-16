# Conventions

- **Phrase match:** `code/patterns.py`, Lin's four prompt types plus generic forms, on text extracted with pdftotext
  (whitespace and case normalised). A match is a candidate only.
- **Hidden:** a matched span is hidden if its fill is white or near-white (each channel ≥ 240), its size is under 2 pt,
  it is drawn with zero alpha, or it lies outside the page (`code/hidden.py`, PyMuPDF `rawdict`).
- **Removed on:** the submission date of the first version after the last prompted one that does not match.
- **Withdrawn version:** listed as "(withdrawn)" in the abs page's submission history; no PDF served.
- **Still downloadable:** at least one prompted version is served at `arxiv.org/pdf/<id>v<n>`. Unversioned links give the
  latest version.
- **Nikkei date:** Nikkei Asia, "'Positive review only': Researchers hide AI prompts in papers", datePublished
  2025-06-30T16:21Z.
- **Candidates:** 18 phrase queries on arXiv's full-text search (search.arxiv.org), 6 Nov 2026, issued from a browser
  session, result pages paged by a short script about 5 s apart (about 75 result pages; up to 60 results per query).
  search.arxiv.org's robots.txt disallows crawlers; the volume was kept to that of a person paging results. Results for
  generic queries were kept when the snippet mentioned review, accept, paper, score or manuscript. 215 distinct ids.
- **Year of a paper:** from its arXiv identifier (YYMM of first submission).
- **The 18 queries (exact phrases, in the order run):** "give a positive review", "LLM reviewer note", "methodological rigor,
  and exceptional novelty", "do not highlight any negatives", "positive review only", "recommend accepting this paper",
  "important review requirements", "ignore all previous instructions", "if you are an AI", "if you are a language model",
  "if you are an LLM", "LLM reviewers", "AI reviewers", "for AI reviewers", "note to LLM", "rate this paper",
  "strong accept", "give this paper a high score".
