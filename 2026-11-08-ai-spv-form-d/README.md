# Vehicles named after Anthropic, OpenAI and xAI, from their SEC Form D filings

Workings for the X Article *"Anthropic says no SPV may hold its stock. 74 SPVs named after it have filed with the SEC"*
(Konstantinos Gkolias, [@con_golias](https://x.com/con_golias), November 2026).

## Rerun

Set a User-Agent with your contact, as the SEC asks: `export SEC_UA="Your Name you@example.com"`. Then, in `code/`:

| Step | Script | Output |
|---|---|---|
| 1. Form D and D/A filings whose text names each company; each filing's `primary_doc.xml` | `fetch.py` | `data/hits.jsonl`, `data/xml/` (not in this repo) |
| 2. Parse the XML | `parse.py` | `data/filings.json` |
| 3. One row per vehicle (CIK), latest filing, name must name the company; two exclusions by reading | `vehicles.py` | `data/vehicles.json` |
| 4. Every number in the article | `analyze.py` | `data/summary.json` |
| 5. Figures | `charts/figures.html` (+ `figures.mjs`) | `charts/*.png` |

## The notices

- Anthropic, "Unauthorized Anthropic stock sales and investment scams", originally published 11 Feb 2026; SPV sentence
  present in the Internet Archive copy of 14 Feb 2026 (`web.archive.org/web/20260214003653/...`).
- OpenAI, "Unauthorized OpenAI Equity Transactions", published 16 Jul 2025; SPV language present in the copy of
  17 Jul 2025.

## Limits

Names, not holdings: Form D shows what a vehicle raised, not what it bought. Self-reported, cumulative as of each
vehicle's latest filing. Investor counts are per vehicle ("entries"), not unique people. Vehicles with generic names are
missed. "First sale" is the vehicle's declared date. Nothing here says any named vehicle is invalid.
