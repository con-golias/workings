# Method

- Read arXiv 2611.07614v1 in full (HTML version: body and appendices A–F) on 8 Nov 2026.
- Every number used in the article is typed into `data/paper_numbers.json` with its reference. Computed values:
  the persona reduction (0.98 − 0.80) / 0.98 = 18%; the range of the brand gain across models (Table E.1); the largest
  rewrite effect in any by-model or by-sector cell (Table E.1).
- Study 1 and Study 2 are reported separately: Study 1 = live engines (gpt-5.5, gemini-3.6-flash, perplexity/sonar),
  search on and off; Study 2 = four models ranking five pages given in-context, **web search off**.
- Related work read from abstracts only (8 Nov 2026): Aggarwal et al. 2311.09735 (GEO, "up to 40%" visibility, a
  different unit from rank); SafeGEO 2606.28356; Chu and Hou 2606.17443. Their numbers are not compared one-to-one.
- Limits carried in the article: Italy, Rome, four sectors, one time; APIs; Study 2 search-off; target page chosen near
  rank 3; 38% brand-recognition leak (upper bound); Gemini searched in 44% of search-on calls; Perplexity Travel
  exception; 36.2% is of checked mentions with search-on and a match does not prove cause.
