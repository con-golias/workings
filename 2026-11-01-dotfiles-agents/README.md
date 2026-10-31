# Research: AI agents in developers' public dotfiles, 2015–2026

> The evidence behind the [X Article](https://x.com/con_golias/status/2116558183669878800) *"AI agents moved into 3 in 10 developers' public dotfiles in under two years"* by
> Konstantinos Gkolias (@con_golias), published 31 Oct 2026. Data pulled 31 Oct 2026.

## The question

Dotfiles repositories hold the configuration people use to set up their own machines. Do they now set up AI coding
agents too, since when, and how fast did that spread compared with every other tool of the last ten years?

## Result

| Year | Repos with a commit that year | Set up an AI agent | 95% bootstrap range |
|---|---|---|---|
| 2024 | 2,414 | 0.04% (1) | 0.0–0.1% |
| 2025 | 2,637 | 8.6% | 7.6–9.7% |
| 2026 (to 31 Oct) | 2,683 | 29.8% | 28.1–31.5% |

- Same repositories, active in both 2024 and 2026 (1,600): 0 → 504 (31.5%).
- +21.2 points in 2026: the largest one-year rise of any signal measured over 2015–2026: all 63 in `measure2.py` give the same top 12 as the
  34 in `data/summary.json` (next after the agent configs: Ghostty, +13.9 in 2025).
- 2026 by agent: Claude 20.9%, AGENTS.md 14.9%, OpenCode 8.4%, Codex 4.5%, Gemini 1.2%, Aider 0.2%. Editor assistants
  (Cursor, Copilot) 4.2%.
- Every number is in `data/summary.json`.

## How

1. `code/list_all.py`: every public, non-fork repository with "dotfiles" in its name and ≥1 star, through GitHub search
   over creation-date windows small enough to return all results: 57,421 (`data/all_repos.json`).
2. `code/sample.py`: a uniform random 6,000, seed 2026 (`data/sample_6000.json`).
3. `code/clone.py`: partial bare clones (blobs ≤ 200 KB); 5,978 still downloadable.
4. `code/measure2.py`: the snapshot at the end of each year 2015–2025 and on 31 Oct 2026; config paths and the tools and
   themes named in the files, vendored code and prose excluded (`data/rows_full.json.gz`).
5. `code/ai_measure.py`: the agent signals, tightened after a hand check (`data/ai_rows.json.gz`).
   `code/handcheck.py` lists 20 random hits per agent for reading by hand.
6. `code/ai_analyze.py`, `code/ai_inside.py`, `code/ai_first.py`, `code/summary.py`: shares, bootstrap, the same-repo
   check, what the agent folders hold, the month of each repo's first agent file.

A repository counts in a year if it had at least one commit that year. An agent config is the owner's own
configuration for an agent: `.claude/` or `CLAUDE.md`, `AGENTS.md`, a Codex folder with config, rules, prompts, agents
or skills, an OpenCode folder or `opencode.json`, a Gemini folder with settings or `GEMINI.md`, `.aider.conf.yml`.
Plugin folders, vendored code, archives and `.local/src/` don't count.

## Run it

```bash
python3 code/list_all.py                                   # every dotfiles repo with >=1 star -> all_repos.json (gh CLI)
python3 code/sample.py                                     # the 6,000 sample -> sample_6000.json
python3 code/clone.py data/sample_6000.json full            # partial bare clones (about 28 GB)
python3 code/measure2.py full rows_full.json                # year-end snapshots 2015-2026
python3 code/test2.py rows_full.json test_full.json         # the test that failed first
python3 code/ai_measure.py full ai_rows.json                # the agent signals, 2022-2026
python3 code/ai_analyze.py ai_rows.json ai_summary.json     # shares, bootstrap, same-repo check
python3 code/ai_inside.py; python3 code/ai_first.py         # what agent folders hold; month of the first agent file
python3 code/summary.py . data/summary.json                 # every number in the article
```

`ai_inside.py`, `ai_first.py` and `handcheck.py` read `ai_rows.json` and the `full/` clones from the working directory.
`rows_full.json` and `ai_rows.json` are kept here gzipped (`data/*.json.gz`): `gunzip -k data/*.gz` first.

## The test that failed first

The research began with a different hypothesis: that tools now spread through setups faster than they used to. It was
written down before the full run (`test2.py`): tools emerging ≤2019 vs ≥2021, median years from 3% to 20% of active
repos, kept only if the newer ones were at least a year faster in ≥90% of 1,000 bootstrap resamples. It failed, in
the version first written and in the version amended after a dry run (median 4 vs 4 years; 86 of 1,000 resamples).
Result in `data/test_full.json`. The AI-agent finding was then tested on its own rules, also written first: a search for
prior work, a hand check (Claude 20/20, AGENTS.md 20/20, OpenCode 20/20, Codex 20/20, Gemini 19/20 after tightening),
a threshold (≥20% in 2026 with the lower bound ≥15%; ≤2% in 2024) and the same-repo check. It passed.

## Where it could be wrong

Only repositories named "dotfiles"; deleted repositories are invisible; 2026 is ten months; a config file means set up,
not used; agents under other names (`.pi/`, `.cursor/rules`) are not in the agent count, so it is a floor.

## Corrections

- **31 Oct 2026, hooks undercounted** (reported by [@0xeddiekim](https://x.com/0xeddiekim)): `ai_inside.py` counted a
  `hooks/` folder or a `hooks.json` file, but Claude Code usually defines hooks inside `settings.json` under a `"hooks"`
  key. `code/hooks_settings.py` also reads that key in the agent folders' settings files (and `[hooks` in TOML).
  Result: **228 of the 800 agent setups (28.5%) define hooks**, more than 1 in 4, not "1 in 6" (16.5%) as the article
  and its post say. 100 of them define hooks only in a settings file. Six random hits read by hand: all real hooks.
