# Research: new Claude agents on GitHub and prompt caching

> The evidence behind the X Article *"Two in three new Claude agents on GitHub pay full price for the same tokens, every turn"* by Konstantinos Gkolias (@con_golias). Data read on 3 November 2026.

## The question

On Anthropic's Messages API, prompt caching is off unless the request sets `cache_control`; OpenAI and Google cache by
default. Among new agents built on Claude, how many never turn it on? And what does that cost per turn?

## Result

- Universe: the 718 repositories created on GitHub in October 2026 (keyword search, forks excluded) whose default model
  is Claude, from the sample of an earlier piece (`2026-10-27-ai-code-dead-models/data/per_repo.csv`). 710 cloned at a
  recorded commit (`data/scan.csv`, column `sha`; every path in it opens as
  `github.com/<repo>/blob/<sha>/<path>#L<n>`), 8 gone (`data/missing.txt`).
- Scan (final rule): 212 agents, 126 with no caching marker (59.4%). First rule 59.8%, loose rule 57.7%, every direct
  API caller 67.4%.
- Hand check of 90 projects (seed 20261103): about 147 real agents among the 710, **65.9% without caching**, 95%
  interval 52.4–77.3% (stratified bootstrap, 20,000 resamples).
- Live tests (Claude Haiku 5.5 and Sonnet 5.5): the same requests without and with one top-level `cache_control`.
  Longest run, Sonnet 5.5, 20 turns: turn 20 = 54,340 tokens billed in full without caching; 2 in full + 2,865 written
  + 51,473 read with it; input cost 83.1% lower. Ten-turn runs: 68.1–78.8% lower. A 6-minute pause cut a run's saving
  from 68.1% to 57.7%. A repeat sent identical token totals. Spend: $2.39 including a stopped first attempt.
- Every number is in `data/summary.json`.

## Design (written before the full run, amended once, both recorded)

- **Agent:** a source file calls the Messages API directly (official SDKs, raw `/v1/messages`, LangChain
  `ChatAnthropic`, Vercel `@ai-sdk/anthropic`, LiteLLM with a Claude model) and, in that same file, handles a tool loop
  (`tool_use`, `tool_result`, `bind_tools`, `create_react_agent`, `AgentExecutor`, tool runner, `stopWhen`, `maxSteps`…)
  with tools defined there. Test, spec, mock and fixture paths are not calling files.
- **Caching on:** `cache_control`, `cacheControl`, `cache_control_injection_points`, `AnthropicPromptCachingMiddleware`,
  `cachePoint` or `cache_point` anywhere in source or config. `ephemeral` alone does not count.
- **Amendment 1 (after the first run, before the second):** the first rule also accepted `stop_reason` as a loop sign;
  it found more agents (445) than the loose rule (378), which is impossible for a correct rule. Six random extra cases
  were all `stop_reason` used for a refusal check, a log line, a type or a test. The first rule's result is kept as
  column `agent_v1`; the loose rule as `agent_loose`.
- **Hand check:** 30 agents with a marker, 30 without, 15 from first-rule-only and 15 from loose-rule-only, drawn with
  `random.Random(20261103)` from the sorted lists (`code/sample.py`). The two outside groups overlap, so for the estimate
  the loose group is restricted to repositories outside the first-rule group: its pool becomes 51 and its sample 6
  (`summary.json → handcheck.loose_minus_v2`). Verdicts and notes: `data/handcheck_verdicts.csv`.
  Conventions, applied to both sides: the unit is the project; caching counts only if a real agent sets it on its own
  request (not a comment, a separate demo, a test, a type or a copied SDK); a chat that only uses Anthropic's server
  tools, or one forced tool call for structured output, is not an agent. One project on Managed Agents (caching always
  on) is counted as cached.

## How

1. Clone each repository in `data/universe.txt` with `git clone --depth 1`; record `git rev-parse HEAD`.
2. `python -I code/scan.py <repos_dir> <shas.csv> data/scan.csv` reads every file from git's object store at the
   recorded commit (no checkout, so paths Windows can't write are still read).
3. `python -I code/sample.py data/scan.csv data/handcheck_sample.csv` draws the hand-check sample.
4. `python -I code/analyze.py` → `data/summary.json` (shares, hand-check estimate, live-test costs, quoted figures).
5. Live tests (`ANTHROPIC_API_KEY` set):
   `python -I code/live_test.py small data/live/small.json` · `… large data/live/large.json` (Haiku 5.5, defaults);
   `… small data/live/sonnet-small.json --model claude-sonnet-5-5` (and `large`, and `sonnet-small-repeat.json`);
   `… small data/live/sonnet-long.json --model claude-sonnet-5-5 --sections 19 --paras 18`;
   `… small data/live/haiku-ttl-gap.json --gap-after 5 --gap-seconds 360`. The second
   pass replays the first pass's requests byte for byte with `cache_control` added; both passes send the same total
   input tokens, which the script asserts in `analyze.py`.
6. `python -I code/render.py` fills the article's numbers from `summary.json`; `code/check_numbers.py` lists any
   number in the text not found there. Figures: `charts/figures.html` (static), `charts/anim.html` (opening video),
   `charts/usage.html` (the usage table).
7. `code/probe_optin.py`, `code/probe_volatile.py`, `code/probe_sample_160.txt`: the 160-repository pilot that came
   before the full run; superseded by `scan.py`.

## Limits

The scan reads code at one commit, not runtime behaviour; the hand check is 90 projects, hence the wide interval; the
sample comes from GitHub keyword search of new repositories, mostly personal, learning and experimental projects; chats
that use only server tools are left out; 25 projects reach Claude through OpenRouter or an OpenAI-style client and are
not classified; prompt size could not be measured for agents that build their prompt at run time; the live test is
one task on one model, and the Sonnet and Opus figures reprice the same token counts at list prices of 3 November 2026.
A first live attempt on Sonnet 5.5 was stopped part way and is kept in `data/live/sonnet-5-5-first-attempt-stopped.log`.
