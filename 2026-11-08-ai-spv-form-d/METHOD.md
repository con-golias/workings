# Conventions

- **Search:** EDGAR full-text search, forms `D` and `D/A` queried separately (combined form lists with a slash fail),
  2019-01-01 to 2026-11-06, phrase = the company name.
- **Vehicle:** one EDGAR CIK. Counted for a company when the entity name matches `\bAnthropic\b`, `\bOpenAI\b` or
  `\bxAI\b` (case-insensitive). Excluded by reading: "Anthropic Capital Fund, LP" (2021 hedge fund) and "OpenAI Startup
  Fund SPV IV, L.P." (OpenAI's own fund).
- **Amounts and investors:** from the latest filing per vehicle (`totalAmountSold`, `totalNumberAlreadyInvested`).
- **Minimum investment:** `minimumInvestmentAccepted`; 0 means none stated.
- **After the notice:** `dateOfFirstSale` later than the notice date. Secondary count by first filing date.
- **Host:** the master LLC named after "a Series of" in the entity name; CGF2021 LLC lists Sydecar among related persons
  and is signed by its administrator.
