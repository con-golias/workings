# Claude Code's share of public GitHub commits, checked against SemiAnalysis's 20% forecast

Workings for the X Article *"Claude Code grew 11.7× on GitHub and still trails the 1-in-5 forecast"* (Konstantinos Gkolias, [@con_golias](https://x.com/con_golias), November 2026).

## Rerun the core number

```bash
gh api -X GET search/commits -f q='"Co-Authored-By: Claude" committer-date:2026-11-03' --jq .total_count
gh api -X GET search/commits -f q='committer-date:2026-11-03' --jq .total_count
```

Divide the first by the second. Check `incomplete_results` too, and look at a sample of the day before you divide.

## Method

1. **Unit.** Commits whose message carries Claude Code's default co-author line (`Co-Authored-By: Claude`), in
   GitHub's commit-search index (public repositories, default branches only), by committer date (UTC). A floor on
   Claude Code's involvement, not a measure of who wrote the code.
2. **Series.** `code/series.py`: the first full week (Mon–Sun) of each month from March 2025 to August 2026, then every
   week from 31 August to 1 November 2026. `code/daily.py`: every day from 24 August to 3 November 2026 (and around
   1 June). A count flagged incomplete is replaced by the sum of single days.
3. **Checks.** Duplicates (`code/dup_sample.py`: 100 + 100 commits looked up by hash), stability (`code/repeat.py`: 5
   days × 4 rounds), spam (`code/closes.py`: 20 commits per sampled week), other agents' signatures and the Claude
   account's own commits (`code/closes.py`), stars and creation dates of sampled repositories (`code/stars.py`).
4. **Floods.** A week is excluded from the share when its 20-commit sample is over 10% gambling spam, its total is over
   150M, or its total is more than 1.3× its clean neighbours. Shares are reported for calm days only.
5. **Numbers.** `code/analyze.py` → `data/summary.json`; every number in the article is a token rendered from it.
   Conventions in `METHOD.md`.

## Results

| | |
|---|---:|
| Share, last full week (26 Oct–1 Nov 2026) | 13.8% (about 1 in 7) |
| Share, 22 calm days (13 Oct–3 Nov), median (range) | 14.1% (12.6–15.2%) |
| Share on 2 Feb 2026, the end of SemiAnalysis's chart, same search today | 2.9% |
| Claude Code commits per day, 2 Feb → 3 Nov 2026 | 151,531 → 1,768,584 (×11.7) |
| All commits in the index per day, same days | 5,152,864 → 13,345,545 (×2.6) |
| Largest spam-flood day | 218,143,544 commits (27 Sep 2026) |

## Not included, on purpose

The sampled commits and lookups (`data/sample_*`, `data/star_*`, `data/closes.json`, `data/dup_sample.json`, `data/stars.json`) name other people's repositories and quote their messages, so they
stay private. Every count can be reproduced with the queries in `code/`.
