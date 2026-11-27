# AI-written code in US copyright registrations

Workings for the X Article by Konstantinos Gkolias (@con_golias).

**Question.** In the US, AI-generated material has to be excluded from a copyright claim. Which software registrations
leave AI-written code out, who files them, what do they say, and how has that changed?

**Answer in numbers** (all in `data/summary.json`, catalogue read 25 November 2026):

- 267 registrations whose "Material Excluded" statement names AI and names code (240 Computer Files); 198 by 72
  organisations, 69 by people (counted, not named)
- per 1,000 Computer Files registrations: 0.7 in 2023 Q4, 34.2 in 2026 Q1 (55 of 1,608, about 1 in 29); without Adobe,
  1 in 39; in 2025, 92 of 5,813 (1 in 63)
- Adobe 40 (33: "Contains code created by AI agents during the coding workflow"), IBM 31, Applied Systems 24,
  Apple 18 (6 name Swift Assist; 10 exclude code "(if any)"), New Relic 8, Deloitte Development 5
- 21 name a tool (Copilot 8, Swift Assist 6, ChatGPT 5, Cursor, Gemini, Bolt 1 each); 2 give a percentage
- "C.O. correspondence" on AI-code registrations filed by people: 29 of 33 (Jan 2025 to Mar 2026), against 54 of 106
  in a random sample of all software registrations filed by people

Completeness: every Computer Files registration since October 2023 was also read in full (code/fullread.py; count in
`summary.json` → `full_read`); it found no AI-code registration the phrase search, the sweep and the sample had missed.

## Rerun

```bash
python code/fetch.py        # phrase search + full records (raw records are not in this repo: they hold addresses)
python code/sweep.py        # broad words under the Computer Files filter
python code/baseline.py     # random sample of all Computer Files registrations, Jan 2025 to Mar 2026
python code/fullread.py     # every Computer Files registration since Oct 2023 (long)
python code/denominator.py  # registrations per month and type of work
python code/analysis.py     # -> data/summary.json, data/code_registrations.csv
python code/lookup.py       # read one record yourself
```
Figures: serve the folder (`python -m http.server <port>`), then `BASE=http://127.0.0.1:<port>/charts PW=<playwright>
node charts/figures.mjs`.

## Files
- `code/analysis.py`: the counting rule, the hand decisions (each with its reason) and every number.
- `data/code_registrations.csv`: one row per counted registration: number, date, type of work, claimant (organisations
  only), the excluded and included statements, tools, title (organisations only), the Office's note, how it was found.
- `data/baseline.json`: the random sample (record id, organisation or person, note), for the correspondence comparison.
- `data/denominator.json`: registrations per month and type of work.
- `data/claimed_side.json`: three IBM registrations that put AI-generated code under Material Included.
- `METHOD.md`: what counts, how records were found, the checks, the limits.

Sources: US Copyright Office Public Records System (api.publicrecords.copyright.gov); 88 FR 16190 (16 March 2023);
Copyright and Artificial Intelligence, Part 2 (January 2025); Supreme Court docket 25-449.
