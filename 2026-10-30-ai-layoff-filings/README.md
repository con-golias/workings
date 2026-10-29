# Research: what companies tell the SEC when they cut jobs, and how often AI is the reason

> The evidence behind the [X Article](https://x.com/con_golias/status/2115889545593905175) *"AI went from zero to one in ten companies' SEC layoff filings in three years"* by Konstantinos Gkolias (@con_golias), published 29 Oct 2026. Data as of 28 Oct 2026.

## The question

When a company listed in the US commits to a layoff with material costs, it files Item 2.05 of Form 8-K, which asks
for "the facts and circumstances leading to the expected action". How often does that text give AI as a reason,
and how has that changed since 2022?

## Result

Companies that filed an Item 2.05 workforce restructuring, 1 January to 28 October of each year, and those whose
Item 2.05 text gives AI as part of the reason (read by hand). 95% Wilson intervals.

| Year | Companies | Named AI | Share | 95% interval |
|---|---|---|---|---|
| 2022 | 157 | 0 | 0.0% | 0.0 to 2.4% |
| 2023 | 309 | 0 | 0.0% | 0.0 to 1.2% |
| 2024 | 235 | 2 | 0.9% | 0.2 to 3.0% |
| 2025 | 179 | 4 | 2.2% | 0.9 to 5.6% |
| 2026 | 152 | 15 | 9.9% | 6.1 to 15.6% |

- **2026 split:** 7 "AI does the work", 6 "the money goes to AI", 2 both.
- **Tech:** 11 of 43 tech companies (SIC 7370–7374, 3570–3579, 3670–3679) vs 4 of 109 others.
- **With attachments counted** (Block's shareholder letter, Snap's memo): 17 of 152.
- **TechCrunch's list** of 2026 AI-related layoffs (25 Jul): of 18 US filers, 10 filed no Item 2.05 in 2026; of
  the 8 that did, 4 name AI in the Item 2.05 text, 2 only in an attachment, 2 in neither.
- Full years: 2022 and 2023 each have one case in November (iBio, Sarcos), both pivots to selling AI.

## Rules

- **Universe:** every 8-K that EDGAR full-text search finds for "Exit or Disposal", "Item 2.05" or "Costs
  Associated with Exit", filed 1 Jan 2022 – 28 Oct 2026, kept if EDGAR tags Item 2.05 or the primary document has a
  real Item 2.05 heading.
- **Text read:** only the Item 2.05 section of the primary document (to the next item heading or the signatures).
  Exhibits are not read for the count; when the section only points to another item of the same 8-K, that item is
  read.
- **Layoff:** the section mentions employees, headcount, workforce, positions, roles, severance, jobs, personnel or
  staff.
- **AI:** "artificial intelligence", "AI", "agentic", "generative", "machine learning" or "automation" flags a
  section; every flagged section was read by hand and coded (does the work / money goes to AI / hurts demand /
  automation without AI / not a reason). Only the first three count as AI.
- **Unit:** a company once per year.

## Checks

- **Completeness:** 1,000 random listed companies; EDGAR lists 153 Item 2.05 8-Ks for them in the window; all 153
  are in the set.
- **Extraction:** 20 random sections checked by hand against the documents; the end rule was fixed twice (Lyft cut
  short; Dow's press release read in), and everything was rerun.
- **Vocabulary sweep** (LLM, GenAI, ChatGPT, copilot, "A.I."): no additional filings.
- Every rule and every change to a rule is dated in the article's notes.

## Limits

- Item 2.05 exists only for material charges: Amazon, Microsoft, Meta, Alphabet, Salesforce and others filed none in
  2026.
- Absence of AI in the text is not denial; presence is what the company was willing to sign, not proof of cause.
- The codes were made by one reader in one pass; every sentence is in `data/ai_codes.csv` to recode.
- SIC codes on EDGAR are current, not historical.
- Data end on 28 October 2026; November and December are missing for 2026.

## Files

- `data/summary.json`: every number in the article.
- `data/restructurings.csv`: all 1,527 restructurings, with date, company, SIC, flags, AI code and EDGAR link.
- `data/ai_codes.csv`: the 51 flagged filings, their hand code and the sentences.
- `data/join_codes.csv`: the TechCrunch-list companies, where AI appears (Item 2.05, attachment, press).

## Rerun

Python 3.11+, free SEC access only. SEC asks for a declared User-Agent; edit `UA` in each script to your own
contact, and keep to their rate limit.

```
export RAW=raw
python3 code/collect_universe.py
python3 code/extract_sections.py
python3 code/completeness.py company_tickers.json 1000   # https://www.sec.gov/files/company_tickers.json
python3 code/code_sections.py                            # writes raw/ai_matches.tsv for the hand-read
# hand codes go in data/ai_codes.csv (adsh, file_date, company, code)
python3 code/exhibit_only.py
python3 code/join_filers.py company_tickers.json
python3 code/join_exhibits.py
python3 code/analyze.py raw data
```

EDGAR's search index and filings can change, so a rerun may differ slightly. Every filing used is listed with its
link in `data/restructurings.csv`.
