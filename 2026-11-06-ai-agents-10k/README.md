# AI agents in SEC risk factors: who warns, who copied, who stays silent

Workings for the X Article *"52 companies now warn their AI agents may go off-script. One in four copied the warning"*
(Konstantinos Gkolias, [@con_golias](https://x.com/con_golias), November 2026).

## Rerun the core search

```bash
curl -s -A "your-name your@email" \
  'https://efts.sec.gov/LATEST/search-index?q=%22unintended%20or%20unauthorized%20actions%22&dateRange=custom&startdt=2001-01-01&enddt=2026-11-05' \
  | jq '[.hits.hits[]._source | {date: .file_date, form, who: .display_names[0]}] | sort_by(.date)'
```

The SEC asks automated clients to send a User-Agent with a contact and to stay under 10 requests a second.

## Pipeline (Python 3, standard library only)

| Step | Script | Output |
|---|---|---|
| 1. Every 10-K, 10-K/A, 10-Q, 10-Q/A, 20-F, 20-F/A, 40-F filed 2022-01-01 to 2026-11-05 matching an agent phrase | `code/fetch_index.py` | `data/hits.jsonl` |
| 2. Download each matching document, strip HTML | `code/fetch_docs.py` | `data/docs/` (not in this repo: 180 MB; rerun step 2) |
| 3. Every sentence naming an agent, plus the two after it | `code/extract.py` | `data/sentences.jsonl` |
| 4. Candidates for "an agent may act on its own" (net 1: action phrases near agent sentences) | `code/rogue.py` | `data/rogue_candidates.json` |
| 5. Candidates from the action phrases themselves, kept when an agent word is within 600 characters (net 2) | `code/rogue_efts.py` | `data/rogue_efts.json` |
| 6. The hand-verified set and its exclusions | `code/verified.py` | `data/rogue_verified.json` |
| 7. Shared wording between verified filers | `code/copy_links.py` | `data/copy_links.json` |
| 8. Approximate risk themes (keyword rules) | `code/themes.py` | `data/themes.json` |
| 9. Agent sentences in sellers' annual reports | `code/sellers.py` | `data/sellers.json` |
| 10. Filers per quarter (EDGAR form indexes) | `code/denominators.py` | `data/denominators.json` |
| 11. Links, then every number in the article | `code/links.py`, `code/analyze.py` | `data/links.json`, `data/summary.json` |
| 12. Figures | `charts/figures.html` (+ `charts/figures.mjs` with Playwright) | `charts/*.png` |

## The test

A company is counted when one of its periodic reports says that **an AI agent, or an agentic system, may itself take
an action that is wrong, unintended, unauthorised or outside its scope.** Inaccurate content alone does not count;
attackers using agents does not count unless the filing says the attacker makes the agent act. Each candidate passage was
read by hand, with its paragraph, on 5 November 2026. Parents and subsidiaries filing the same text (Barclays PLC and Barclays Bank PLC;
Prudential Financial and two Pruco Life entities) count once. Exclusions and reasons are in `data/rogue_verified.json`.

## Limits

- A floor: phrase-based nets miss warnings written in other words.
- Judgement: borderline cases are listed; a stricter or looser reader would move a few.
- Shared wording is not proof of copying; two filers may use the same law firm's template.
- EDGAR full-text search covers text documents, not PDF exhibits.
- "Agentic" is read as AI in every case.
