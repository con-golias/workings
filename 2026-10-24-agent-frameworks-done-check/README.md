# Research: does the framework check the "done"?

> The evidence behind the X Article *"I read the code of 18 AI agent frameworks. None of them checks
> whether "done" is true."* by Konstantinos Gkolias (@con_golias), 24 Oct 2026.
> Research on public code, done 23 Oct 2026. Everything here can be rerun: repos, commits, commands
> and evidence are listed. Reproductions: `repro/`. Claim gate + tests: `claim-gate/`.

## The question

When an LLM agent built with a popular framework tells an end user that an action was done
("your refund is processed", "I've cancelled your order"), **does the framework itself check that
sentence against what the tools actually did?** Or is that left to the prompt and the developer?

## Why it matters (context, sourced in the article)

- False success is a large share of agent failures in customer-service settings (Advani 2026,
  arXiv 2606.09863: 45–48% of failures in single-control tau2-bench domains).
- A required status flag cut dishonest answers after tool failure from 14.10% to 0.87%
  (Sethi et al. 2026, arXiv 2609.14758). Their audit of nine frameworks looked at tool-failure
  guidance, not at checking the final claim. This research looks at the final claim.
- Courts attribute a chatbot's statements to the company deploying it (Moffatt v Air Canada,
  2024 BCCRT 149; Higher Regional Court of Hamm, 12 May 2026, as reported by DLA Piper, 15 Jun 2026).

## Selection (fixed before looking at results)

Agent / LLM-application frameworks in which a model calls tools on behalf of a user, with
**≥ 20,000 GitHub stars or ≥ 1,000,000 package downloads in the last 30 days**, not archived.
Data pulled 23 Oct 2026: stars from repos.ecosyste.ms (its last crawl, may lag GitHub by days),
downloads from pypistats.org (`last_month`) and api.npmjs.org (`last-month`, 19 Sep–18 Oct).
Download counts include CI and mirrors; they measure installs, not users.

Included (18): see `frameworks.csv` (`included=yes`), each audited at the commit listed there.

Excluded, with the reason:
- microsoft/agent-framework (14.2k stars, 190k downloads): below both thresholds.
- botpress/botpress (15.0k stars, 62k downloads of `@botpress/sdk`): below both thresholds.
- FlowiseAI/Flowise: marked archived in ecosyste.ms metadata (23 Oct).
- RasaHQ/rasa: the open-source repo's default branch is `3.6.x`; its LLM features ship in Rasa Pro
  (12.6k downloads of `rasa-pro`), not in the open-source repo.
- NVIDIA/NeMo-Guardrails, guardrails-ai/guardrails: guardrail **libraries**, not agent frameworks.
  Looked at separately as add-ons a developer can bolt on.

## The rubric (per framework)

- **Q1 Runtime output hook:** is there a documented mechanism that runs on the final user-facing
  output before it is returned and can block or rewrite it? Does it receive the run's tool
  calls/results, or only the final text?
- **Q2 Built-in claim check:** does the framework ship any concrete check (on or opt-in) that
  compares statements about completed actions with the run's actual tool calls/results?
- **Q3 Default:** is any semantic check on the final output on by default? (Schema validation of
  structured output is reported separately as "schema only".)
- **Q4 Tool failure:** what does the model receive by default when a tool raises?

Method: read the source at the audited commit (tests, examples and cookbooks excluded when deciding
what is "shipped"; docs cited where they define behaviour), keyword sweeps (guardrail,
hallucination, faithful, grounded, verify, claim, after_model, output processor, moderation) and
reading every hit that could be a check. Every finding cites file and line at the commit.

## Files

- `frameworks.csv` — selection data and audited commits.
- `stars.txt`, `shas.txt` — raw pulls.
- `findings.md` — per-framework answers with evidence (file:line, quote).
- `summary.csv` — one row per framework, the answers to Q1–Q4.
- `sources.md` — every external fact used in the article, where it was read and how sure it is.
- `verify-log.md` — every finding from the first-pass keyword sweeps, re-read by hand in the source.
- `repro/` — the LangChain Python vs JS reproduction, with pinned versions and the raw output.
- `claim-gate/` — the claim gate from the article and its seven tests.
