# Conventions

- **Universe:** EDGAR full-text search (`efts.sec.gov/LATEST/search-index`), forms 10-K, 10-K/A, 10-Q, 10-Q/A, 20-F,
  20-F/A, 40-F, filed 1 Jan 2022 – 5 Nov 2026, phrases "AI agent", "AI agents", "artificial intelligence agent(s)",
  "agentic", "autonomous agent(s)", "AI-powered agents". One row per matching document.
- **Company:** EDGAR CIK. Year and quarter by filing date.
- **Share of filers:** companies with an agent sentence in a quarter ÷ distinct CIKs filing one of those forms that
  quarter (EDGAR `full-index/<year>/QTR<n>/form.idx`). Q4 2026 is partial (to 5 Nov).
- **Agent sentence:** sentence split on `.`, `;`, `!`, `?` before a capital, or a line break before a capital or bullet;
  must match the agent regex in `code/extract.py`.
- **Shared wording:** longest run of identical words (case and punctuation ignored) between the two companies' warning
  passages (agent sentence + the two after it); counted at 8 words or more, containing an agent or action term.
- **Themes:** keyword rules in `code/themes.py`, applied to agent sentences that contain a risk word. Approximate.
- **Sellers:** latest 10-K in the corpus; agent sentences exclude legal uses ("employees and agents", "transfer agent",
  "attorneys-in-fact and agents").
