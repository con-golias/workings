# Research: which models does new AI code call?

> The evidence behind the [X Article](https://x.com/con_golias/status/2114750216809140276) *"Two in three new AI apps built on OpenAI default to a model OpenAI is
> switching off"* by Konstantinos Gkolias (@con_golias), 26 Oct 2026. Data collected and counted on 26 Oct 2026.

## The question

On 23 October 2026 OpenAI switched off `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo`, the first GPT-4o, `o1`, `o3-mini`
and `o4-mini`; on 14 January 2027 it switches off GPT-4o, GPT-4o mini, GPT-4.1 and GPT-4.1 mini. **What do the AI
repositories created this month call, and how much of it is already dead or dated to die?** And does code
co-written by a coding agent pick newer models?

## Result (2,377 repositories, created 1–24 Oct 2026, code written that month)

| Default model is from | Repositories | Default dead or with a shutdown date | Already dead | Median age of default at creation |
|---|---|---|---|---|
| OpenAI | 721 | **65.5%** | 10.4% | **18.2 months** |
| Anthropic | 718 | 19.1% | 10.4% | 1.5 months |
| Google | 938 | 16.1% | 9.3% | 4.2 months |

- Most common OpenAI default: `gpt-4o-mini`, 23.6% of the 721 (shuts down 14 Jan 2027). Its named replacement,
  `gpt-6-luna`, is the default in 7.6% and costs less ($0.10/$0.50 vs $0.15/$0.60 per 1M tokens).
- The clock for the 721: 10.4% dead today, 19.1% after 11 Dec 2026, 64.5% after 14 Jan 2027.
- 172 repositories (7.2%) were dead on arrival: their default had been switched off before the repository existed.

**Coding-agent signatures** (`Co-Authored-By` trailers in the latest 100 commits):

| Code that calls | Signed by Claude | No agent signature |
|---|---|---|
| Anthropic: default dead or dying / median age | 6.8% / 0.8 months (n=309) | 28.6% / 4.3 months (n=398) |
| OpenAI: default dead or dying / median age | 67.5% / 17.8 months (n=120) | 64.5% / 18.2 months (n=583) |

"No agent signature" is not "written by a person": Codex rarely signs commits (3 repositories here), so its effect
cannot be measured with this data.

**Earlier cohorts** (repositories last pushed within 30 days of creation): median age of the default model.

| | Oct 2025 | Apr 2026 | Oct 2026 |
|---|---|---|---|
| OpenAI | 14.8 months | 20.7 | 18.2 |
| Anthropic | 15.4 | 6.0 | 1.5 |
| Google | 3.9 | 9.6 | 4.2 |

## Method

1. `collect.py`: GitHub search, `created:<day> fork:false` × 7 terms (openai, anthropic, llm, gemini, chatgpt,
   claude, "ai agent"), first 100 results per term per day. 16,130 repositories for 1–24 Oct 2026.
2. `scan.py`: streams each default-branch archive and records model-ID string literals in source files, whether the
   file also calls an LLM API, agent instruction files, and a hash per file. 12,838 scanned (2,647 empty or over
   80 MB, 645 unavailable).
3. `trailers.py`: latest 100 commits of each repository that calls a model; agent signatures; oldest commit.
4. `analyze.py`: drops catalogue files (more than 8 model IDs) and byte-identical template copies (109); keeps
   "fresh" repositories (fewer than 100 commits, oldest commit at most 14 days before creation): 2,377. Default
   model = the ID with most occurrences in call-site files.
5. `registry.py`: status of every model ID on 26 Oct 2026, from the OpenAI, Anthropic and Google deprecation pages
   and OpenAI's changelog. One rule per model family, with release and shutdown dates.
6. `by_vendor_and_signature.py`, `article_numbers.py`, `cohorts.py`: the remaining numbers in the article.
7. `check_models.py`: the build check from the article (fails when the code names a model the provider no longer
   serves; uses your own API keys).

## What this does not show

- **A sample, not a census.** Best-match search, 100 per term per day. Results are reported per vendor because the
  mix between vendors depends on the search terms.
- **"Default" is a definition.** A project may choose its model from configuration at runtime; the literal in the
  code may be a fallback. A fallback still runs when the configuration is missing.
- **Small projects.** Many are experiments and learning projects, not production systems.
- **Signatures.** A Claude signature means Claude Code was used in at least one of the latest 100 commits, not that
  it wrote the model name. Selection: people who use Claude Code may prefer Claude.
- **Status can change** if a vendor moves a date or repoints an alias.

## Files

- `data/per_repo.csv`: one row per repository that calls a model by name (all 2,667; `fresh` marks the 2,377).
- `data/summary.json`: the summary used in the article.
- `data/cohort_2025_10.txt`, `data/cohort_2026_04.txt`: the earlier cohorts.

## Rerun

```sh
cd code
python collect.py 2026-10-01 2026-10-24 ../raw/c.jsonl     # needs the GitHub CLI (gh), logged in
python scan.py ../raw/c.jsonl ../raw/s.jsonl
python trailers.py ../raw/s.jsonl ../raw/t.jsonl
python analyze.py ../raw/s.jsonl ../raw/t.jsonl ../raw/oct26
```

Needs Python 3 and the GitHub CLI. Search results change over time, so a rerun on a later day returns a different
sample; the per-repository table is the record of this one.
